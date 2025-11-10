from astrbot.api.event import AstrMessageEvent
from astrbot.api import logger

from ..core.request_util import (gt_request_api, btr_request_api)
from ..core.plugin_logic import PlayerDataRequest, BattlefieldPluginLogic
from ..core.utils import format_datetime_string


class ApiHandlers:
    def __init__(self, plugin_logic: BattlefieldPluginLogic, html_render_func, timeout_config: int, ssc_token: str,
                 session):
        self.plugin_logic = plugin_logic
        self.html_render = html_render_func
        self.timeout_config = timeout_config
        self.ssc_token = ssc_token
        self._session = session

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

        result = await self.plugin_logic.process_api_response(
            event, api_data, data_type, request_data.game, self.html_render, is_llm
        ).__anext__()
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
            yield event.plain_result(f"不支持的游戏类型 '{data_type}' 用于bf6/bf2042查询。")
            return

        # 士兵查询仅限bf2042
        if data_type == "soldier" and request_data.game != "bf2042":
            yield event.plain_result("士兵查询目前仅支持战地2042。")
            return

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
            data_iterator = self._fetch_btr_data(event, request_data, "bf6_stat")
            try:
                data = await data_iterator.__anext__()
                stat_data = data
                if isinstance(data, list):
                    user_info_list = []
                    for user in data:
                        handle = user.get("platformUserHandle", "未知")
                        identifier = user.get("platformUserIdentifier", "未知")
                        user_info_list.append(f"用户名: {handle}, platformUserIdentifier: {identifier}")
                    yield "查询到多个用户：\n" + "\n".join(
                        user_info_list) + "\n请先使用 stat pider=pider 查询各个战绩确认哪个是您，然后使用bind pider=pider绑定您的pid"
                    return
                elif isinstance(data,str) and "私有的" in data:
                    yield data
                    return
                else:
                    result_data = data.get("segments")
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
            except StopAsyncIteration:
                pass

        else:
            stat_data = await self._fetch_btr_data(event, request_data, "stat").__anext__()

            if prop in ["stat", "weapons"]:
                weapon_data = await self._fetch_btr_data(event, request_data, "weapons").__anext__()

            if prop in ["stat", "vehicles"]:
                vehicle_data = await self._fetch_btr_data(event, request_data, "vehicles").__anext__()

            if prop in ["stat", "soldiers"]:
                soldier_data = await self._fetch_btr_data(event, request_data, "soldiers").__anext__()

        result = await self.plugin_logic.handle_btr_response(prop, request_data.game,
                                                             self.html_render, stat_data, weapon_data,
                                                             vehicle_data, soldier_data, is_llm).__anext__()
        yield result

    async def handle_btr_matches(self, event: AstrMessageEvent, request_data: PlayerDataRequest, provider,
                                 is_llm: bool = False):
        """查询bf6的最近战局统计数据"""
        next_page = ""
        data_iterator = self._fetch_btr_data(event, request_data, "bf6_stat")
        data = await data_iterator.__anext__()
        if isinstance(data, list):
            user_info_list = []
            for user in data:
                handle = user.get("platformUserHandle", "未知")
                identifier = user.get("platformUserIdentifier", "未知")
                user_info_list.append(f"用户名: {handle}, platformUserIdentifier: {identifier}")
            yield "查询到多个用户：\n" + "\n".join(
                user_info_list) + "\n请先使用 stat pider=pider 查询各个战绩确认哪个是您，然后使用bind pider=pider绑定您的pid",next_page
            return
        elif isinstance(data,str) and "私有的" in data:
            yield data,next_page
            return
        else:
            update_hash = data.get("metadata").get("updateHash")
            matches_data = await self._fetch_btr_matches_data(event, request_data, update_hash).__anext__()
            if request_data.page > 1:
                page = request_data.page - 1
            else:
                page = 0

            if len(matches_data.get("matches")) < request_data.page:
                yield "暂无数据",next_page
                return

            stats_data = matches_data.get("matches")[page].get("segments")[0].get("stats")
            matches_timestamp = format_datetime_string(
                matches_data.get("matches")[page].get("metadata").get("timestamp"))
            weapon_data = matches_data.get("matches")[page].get("segments")[0].get("metadata").get("weapons")
            vehicle_data = matches_data.get("matches")[page].get("segments")[0].get("metadata").get("vehicles")
            soldier_data = matches_data.get("matches")[page].get("segments")[0].get("metadata").get("kits")
            mode_data = matches_data.get("matches")[page].get("segments")[0].get("metadata").get("gamemodes")
            maps_data = matches_data.get("matches")[page].get("segments")[0].get("metadata").get("levels")

            result = await self.plugin_logic.handle_btr_matches_response("bf6", request_data.ea_name, self.html_render,
                                                                         stats_data,
                                                                         weapon_data, vehicle_data, soldier_data,
                                                                         mode_data, maps_data, matches_timestamp,
                                                                         provider).__anext__()

            if request_data.page < 25 and request_data.page <= len(matches_data.get("matches")):
                if request_data.pider:
                    next_page = f"战报 {request_data.ea_name},game=bf6,pider={request_data.pider},page={request_data.page + 1}"
                else:
                    next_page = f"战报 {request_data.ea_name},game=bf6,page={request_data.page + 1}"
            yield result, next_page

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
