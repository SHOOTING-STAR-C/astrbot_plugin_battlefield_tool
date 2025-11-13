from astrbot.api.event import AstrMessageEvent
from astrbot.api import logger

from ..core.request_util import (gt_request_api, btr_request_api)
from ..core.plugin_logic import PlayerDataRequest, BattlefieldPluginLogic
from ..core.utils import format_datetime_string
from ..core.exceptions import (
    NetworkError, APIError, DataParseError, TimeoutError, UserInputError,
    GameNotSupportedForOperationError, MultipleUsersError, PrivateDataError, NoDataError
)
from ..core.decorators import handle_exceptions


class ApiHandlers:
    def __init__(self, plugin_logic: BattlefieldPluginLogic, html_render_func, timeout_config: int, ssc_token: str,
                 session,wake_prefix):
        self.plugin_logic = plugin_logic
        self.html_render = html_render_func
        self.timeout_config = timeout_config
        self.ssc_token = ssc_token
        self._session = session
        self.wake_prefix = wake_prefix

    async def fetch_gt_data(self, event: AstrMessageEvent, request_data: PlayerDataRequest, data_type: str,
                            prop: str = None, is_llm: bool = False):
        """
        根据游戏类型获取数据并处理响应 (非bf6/bf2042)。
        """
        api_data = await gt_request_api(
            request_data.game,
            prop,
            {"name": request_data.ea_name, "lang": request_data.lang, "platform": self.plugin_logic.default_platform},
            self.timeout_config,
            session=self._session,
        )

        async for result in self.plugin_logic.process_api_response(
                event, api_data, data_type, request_data.game, self.html_render, is_llm
        ):
            yield result

    async def _fetch_btr_data(self, event: AstrMessageEvent, request_data: PlayerDataRequest, data_type: str):
        """
        根据游戏类型获取数据并处理响应 (bf6/bf2042)。
        """
        btr_prop_map = {
            "stat": "/player/stat",
            "weapons": "/player/weapons",
            "vehicles": "/player/vehicles",
            "soldiers": "/player/soldiers",
            "bf6_stat": "/bf6/stat",
        }
        btr_prop = btr_prop_map.get(data_type)
        if btr_prop is None:
            raise InvalidParameterError("data_type", data_type, "stat, weapons, vehicles, soldiers, bf6_stat")

        # 士兵查询仅限bf2042
        if data_type == "soldier" and request_data.game != "bf2042":
            raise GameNotSupportedForOperationError(request_data.game, "士兵查询", ["bf2042"])

        api_data = await btr_request_api(
            btr_prop,
            {"player_name": request_data.ea_name, "game": request_data.game, "pider": request_data.pider},
            self.timeout_config,
            self.ssc_token,
            session=self._session,
        )
        yield api_data

    async def _fetch_btr_matches_data(self, event: AstrMessageEvent, request_data: PlayerDataRequest, update_hash: str):
        api_data = await btr_request_api(
            "/bf6/matches",
            {"player_name": request_data.ea_name, "update_hash": update_hash},
            self.timeout_config,
            self.ssc_token,
            session=self._session,
        )
        yield api_data

    async def handle_btr_game(self, event: AstrMessageEvent, request_data: PlayerDataRequest, prop,
                              is_llm: bool = False):
        """处理BTR游戏（bf2042, bf6）的统计数据查询"""
        stat_data = None
        weapon_data = []
        vehicle_data = []
        soldier_data = []

        if request_data.game == "bf6":
            # 使用 async for 来正确捕获异常
            async for data in self._fetch_btr_data(event, request_data, "bf6_stat"):
                stat_data = data

            # 处理多用户情况
            if isinstance(stat_data, list):
                raise MultipleUsersError(stat_data,self.wake_prefix,request_data.ea_name)

            # 处理正常数据
            result_data = stat_data.get("segments")
            for result in result_data:
                if result["type"] == "kit":
                    soldier_data.append(result)
                    continue
                if result["type"] == "weapon":
                    weapon_data.append(result)
                    continue
                if result["type"] == "vehicle":
                    vehicle_data.append(result)
                    continue
        else:
            # 使用 async for 来正确捕获异常
            async for data in self._fetch_btr_data(event, request_data, "stat"):
                stat_data = data

            if prop in ["stat", "weapons"]:
                async for data in self._fetch_btr_data(event, request_data, "weapons"):
                    weapon_data = data

            if prop in ["stat", "vehicles"]:
                async for data in self._fetch_btr_data(event, request_data, "vehicles"):
                    vehicle_data = data

            if prop in ["stat", "soldiers"]:
                async for data in self._fetch_btr_data(event, request_data, "soldiers"):
                    soldier_data = data

        async for result in self.plugin_logic.handle_btr_response(prop, request_data.game,
                                                                  self.html_render, stat_data, weapon_data,
                                                                  vehicle_data, soldier_data, is_llm):
            yield result

    async def handle_btr_matches(self, event: AstrMessageEvent, request_data: PlayerDataRequest, provider,
                                 is_llm: bool = False):
        """查询bf6的最近战局统计数据"""
        next_page = ""

        # 使用 async for 来正确捕获异常
        async for data in self._fetch_btr_data(event, request_data, "bf6_stat"):
            # 处理多用户情况
            if isinstance(data, list):
                raise MultipleUsersError(data,self.wake_prefix,request_data.ea_name)

            # 处理正常数据
            update_hash = data.get("metadata").get("updateHash")
            # request_data.ea_name = data.get("platformInfo").get("platformUserHandle")

            # 使用 async for 来正确捕获异常
            async for matches_data in self._fetch_btr_matches_data(event, request_data, update_hash):
                if request_data.page > 1:
                    page = request_data.page - 1
                else:
                    page = 0

                # 检查是否有足够的数据
                if len(matches_data.get("matches")) < request_data.page:
                    raise NoDataError("战局数据")

                stats_data = matches_data.get("matches")[page].get("segments")[0].get("stats")
                matches_timestamp = format_datetime_string(
                    matches_data.get("matches")[page].get("metadata").get("timestamp"))
                weapon_data = matches_data.get("matches")[page].get("segments")[0].get("metadata").get("weapons")
                vehicle_data = matches_data.get("matches")[page].get("segments")[0].get("metadata").get("vehicles")
                soldier_data = matches_data.get("matches")[page].get("segments")[0].get("metadata").get("kits")
                mode_data = matches_data.get("matches")[page].get("segments")[0].get("metadata").get("gamemodes")
                maps_data = matches_data.get("matches")[page].get("segments")[0].get("metadata").get("levels")

                async for result in self.plugin_logic.handle_btr_matches_response("bf6", request_data.ea_name,
                                                                                  self.html_render,
                                                                                  stats_data,
                                                                                  weapon_data, vehicle_data,
                                                                                  soldier_data,
                                                                                  mode_data, maps_data,
                                                                                  matches_timestamp,
                                                                                  provider):
                    total_page = len(matches_data.get("matches"))
                    if request_data.page < 25 and request_data.page < len(matches_data.get("matches")):
                        if request_data.pider:
                            next_page = f"战报 {request_data.ea_name},game=bf6,pider={request_data.pider},page={request_data.page + 1}"
                        else:
                            next_page = f"战报 {request_data.ea_name},game=bf6,page={request_data.page + 1}"
                    yield result, next_page,total_page

    async def fetch_gt_servers_data(self, request_data: PlayerDataRequest, timeout_config: int, session):
        """
        获取GT服务器数据。
        """
        servers_data = await gt_request_api(
            request_data.game,
            "servers",
            {
                "name": request_data.server_name,
                "lang": request_data.lang,
                "platform": self.plugin_logic.default_platform,
                "region": "all",
                "limit": 30,
            },
            timeout_config,
            session=session,
        )
        return servers_data

    async def check_ea_name(self, request_data: PlayerDataRequest, timeout_config: int, session):
        """检查ea_name正确性，并返回pid"""
        stats_data = await gt_request_api(
            "bfv",
            "stats",
            {
                "name": request_data.ea_name,
                "platform": self.plugin_logic.default_platform,
            },
            timeout_config,
            session=session,
        )
        if stats_data is None:
            return stats_data.get("userId")
        else:
            return None
