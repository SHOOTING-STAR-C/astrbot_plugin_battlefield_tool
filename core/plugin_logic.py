from astrbot.api.event import AstrMessageEvent
from astrbot.api import logger

from typing import Union, Pattern
from ..database.battlefield_db_service import (
    BattleFieldDBService,
)
from .gametool.gt_template import (
    gt_main_html_builder,
    gt_weapons_html_builder,
    gt_vehicles_html_builder,
    gt_servers_html_builder,
)
from .btr.btr_template import (
    btr_main_html_builder,
    btr_weapons_html_builder,
    btr_vehicles_html_builder,
    btr_soldier_html_builder,
    btr_matches_html_builder,
)

from .gametool.gt_llm import gt_main_llm_builder
from .btr.btr_llm import btr_main_llm_builder
from .gametool.gt_image_generator import GtImageGenerator
from .btr.btr_image_generator import BtrImageGenerator

from ..models.player_data import PlayerDataRequest

import re
import time


class BattlefieldPluginLogic:
    def __init__(self, db_service: BattleFieldDBService, default_game: str, timeout_config: int, img_quality: int,
                 session, bf_prompt: str, default_platform: str = "pc"):
        self.db_service = db_service
        self.default_game = default_game
        self.timeout_config = timeout_config
        self.img_quality = img_quality
        self._session = session
        self.default_platform = default_platform  # 添加默认平台配置
        self.LANG_CN = "zh-cn"
        self.LANG_TW = "zh-tw"
        self.bf_prompt = bf_prompt
        self.SUPPORTED_GAMES = ["bf4", "bf1", "bfv", "bf6", "bf2042"]
        self.STAT_PATTERN = re.compile(
            r"^([\w-]*)(?:[，,]?game=([\w\-+.]+))?(?:[，,]?pider=([\w\-+.]+))?(?:[，,]?page=(\d+))?$"
        )
        # self.STAT_PATTERN = re.compile(
        #     r"^([\w-]*)(?:[，,]?game=([\w\-+.]+))?$"
        # )
        self.gt_image_generator = GtImageGenerator(img_quality)
        self.btr_image_generator = BtrImageGenerator(img_quality)

    def get_session_channel_id(self, event: AstrMessageEvent) -> str:
        """根据事件类型获取会话渠道ID"""
        if not event.is_private_chat():
            return event.get_group_id()
        return event.get_sender_id()

    async def _resolve_game_tag(self, game_input: Union[str, None], session_channel_id: str) -> tuple[
        Union[str, None], Union[str, None]]:
        """
        解析游戏代号，获取默认值并进行验证。
        Returns:
            tuple: (game_tag, error_message)
        """
        game = game_input
        error_msg = None

        if game is None:
            bd_game = await self.db_service.query_session_channel(session_channel_id)
            if bd_game is None:
                game = self.default_game
            else:
                game = bd_game["default_game_tag"]

        if game == 'bf5':
            game = 'bfv'
        if game == '2042':
            game = 'bf2042'

        if game not in self.SUPPORTED_GAMES:
            error_msg = (
                f"服务器 '{game}' 未找到\n"
                f"• 请检查游戏代号是否正确\n"
                f"• 可用代号: {'、'.join(self.SUPPORTED_GAMES)}"
            )
            game = None  # 确保在错误时返回None
        return game, error_msg

    async def _resolve_ea_name(self, ea_name_input: Union[str, None], qq_id: str) -> tuple[
        Union[str, None], Union[str, None], Union[str, None]]:
        """
        解析EA账号名，获取默认值。
        Returns:
            tuple: (ea_name, error_message)
        """
        ea_name = ea_name_input
        pider = ""
        error_msg = None

        if ea_name is None:
            bind_data = await self.db_service.query_bind_user(qq_id)
            if bind_data is None:
                error_msg = "请先使用bind [ea_name]绑定"
            else:
                ea_name = bind_data.get("ea_name")
                pider = bind_data.get("ea_id", None)
        return ea_name, pider, error_msg

    async def handle_btr_response(self, data_type, game, html_render_func, stat_data, weapon_data: list = None,
                                  vehicle_data=None, soldier_data=None, is_llm: bool = False,
                                  ):
        """处理bf6/bf2042等新API的响应逻辑"""
        if is_llm:
            yield await btr_main_llm_builder(stat_data, weapon_data, vehicle_data, soldier_data, game, self.bf_prompt)
        else:
            handler_map = {
                "stat": (self.btr_image_generator.generate_main_btr_data_pic, btr_main_html_builder),
                "weapons": (self.btr_image_generator.generate_weapons_btr_data_pic, btr_weapons_html_builder),
                "vehicles": (self.btr_image_generator.generate_vehicles_btr_data_pic, btr_vehicles_html_builder),
                "soldiers": (self.btr_image_generator.generate_soldiers_btr_data_pic, btr_soldier_html_builder),
            }

            generator_func, html_builder_func = handler_map[data_type]

            pic_url = await generator_func(game, html_render_func, html_builder_func, stat_data, weapon_data,
                                           vehicle_data,
                                           soldier_data)
            yield pic_url

    async def handle_btr_matches_response(self, game,ea_name, html_render_func, stat_data, weapon_data, vehicle_data,
                                 soldier_data, mode_data,maps_data,matches_timestamp,provider):

        pic_url = await self.btr_image_generator.generate_matches_btr_data_pic(game,ea_name, html_render_func,
                                                                               btr_matches_html_builder, stat_data,
                                                                               weapon_data, vehicle_data, soldier_data,
                                                                               mode_data,maps_data,matches_timestamp,provider)
        yield pic_url

    def _handle_error_response(self, api_data: dict) -> Union[str, None]:
        """统一处理API响应中的错误信息"""
        if api_data is None:
            return "API调用失败，没有响应任何信息"
        if api_data.get("code") != 200:
            errors = api_data.get("errors")
            if errors and isinstance(errors, list) and len(errors) > 0:
                return errors[0]
            return "API返回未知错误"
        return None

    async def process_api_response(self, event, api_data, data_type, game, html_render_func, is_llm: bool = False):
        """处理API响应通用逻辑"""
        if is_llm:
            yield gt_main_llm_builder(api_data, game, self.bf_prompt)
        else:
            error_msg = self._handle_error_response(api_data)
            if error_msg:
                yield event.plain_result(error_msg)
                return

            api_data["__update_time"] = time.time()

            # 根据数据类型调用对应的图片生成方法
            handler_map = {
                "stat": (self.gt_image_generator.generate_main_gt_data_pic, gt_main_html_builder),
                "weapons": (self.gt_image_generator.generate_weapons_gt_data_pic, gt_weapons_html_builder),
                "vehicles": (self.gt_image_generator.generate_vehicles_gt_data_pic, gt_vehicles_html_builder),
                "servers": (self.gt_image_generator.generate_servers_gt_data_pic, gt_servers_html_builder),
            }

            generator_func, html_builder_func = handler_map[data_type]
            pic_url = await generator_func(api_data, game, html_render_func, html_builder_func)
            if isinstance(pic_url, str) and "http" in pic_url:
                yield event.plain_result(pic_url)
            else:
                yield pic_url

    async def handle_player_data_request(
            self, event: AstrMessageEvent, str_to_remove_list: list
    ) -> PlayerDataRequest:
        """
        从消息中提取参数
        Args:
            event: AstrMessageEvent
            str_to_remove_list: 去除指令
        Returns:
            PlayerDataRequest: 包含所有提取参数的数据类实例
        """
        message_str = event.message_str
        lang = self.LANG_CN
        qq_id = event.get_sender_id()
        session_channel_id = self.get_session_channel_id(event)
        error_msg = None
        ea_name = None
        game = None
        server_name = None
        pider = ""
        page = 0

        try:
            # 解析命令
            ea_name, game, pider, page = await self._parse_input_regex(
                str_to_remove_list, self.STAT_PATTERN, message_str
            )
            # 由于共用解析方法所以这里赋个值
            if str_to_remove_list == ["servers", "服务器"]:
                server_name = ea_name

            # 处理游戏代号
            game, game_error = await self._resolve_game_tag(game, session_channel_id)
            if game_error:
                error_msg = game_error
                raise ValueError(error_msg)  # 抛出异常以便被捕获

            # 处理EA账号名
            if not ea_name and not pider:
                ea_name, pider, ea_name_error = await self._resolve_ea_name(ea_name, qq_id)
                if ea_name_error:
                    error_msg = ea_name_error
                    raise ValueError(error_msg)  # 抛出异常以便被捕获

            # 战地1使用繁中
            if game == "bf1":
                lang = self.LANG_TW
        except Exception as e:
            error_msg = str(e)

        return PlayerDataRequest(
            message_str=message_str,
            lang=lang,
            qq_id=qq_id,
            pider=pider,
            ea_name=ea_name,
            game=game,
            server_name=server_name,
            error_msg=error_msg,
            page=page,
        )

    async def handle_player_llm_request(self, event: AstrMessageEvent, ea_name: str = None, user_id: str = None,
                                        game: str = None):
        """解析LLM请求参数、构建PlayerDataRequest"""
        session_channel_id = self.get_session_channel_id(event)
        lang = self.LANG_CN

        # 处理EA_NAME
        ea_name_temp = None
        error_msg = None
        pider = None
        if ea_name:
            ea_name_temp = ea_name
        else:
            user_id = user_id if user_id else event.get_sender_id()
            bind_data = await self.db_service.query_bind_user(user_id)
            if bind_data is None:
                error_msg = f"根据以下信息回复用户结合你的人格设定，保证上下问不冲突，没有找到{user_id}绑定的账户，请让用户先使用bind [ea_name]绑定或让用户告诉你信息你帮他绑定"
            else:
                ea_name_temp = bind_data["ea_name"]
                pider = bind_data["ea_id"]
        # 处理游戏代号
        game, game_error = await self._resolve_game_tag(game, session_channel_id)
        if game_error:
            error_msg = game_error

        # 战地1使用繁中
        if game == "bf1":
            lang = self.LANG_TW
        return PlayerDataRequest(
            message_str=event.message_str,
            lang=lang,
            qq_id=user_id,
            pider=pider,
            ea_name=ea_name_temp,
            game=game,
            server_name="",
            error_msg=error_msg,
        )

    @staticmethod
    async def _parse_input_regex(
            str_to_remove_list: list[str],
            pattern: Union[Pattern[str], None],
            base_string: str,
    ):
        """私有方法：从base_string中移除str_to_remove_list并去空格，然后根据正则取出参数
        Args:
            str_to_remove_list: 需要移除的子串list
            base_string: 原始字符串
        Returns:
            处理后的字符串
        """
        # 移除目标子串和空格
        for str_to_remove in str_to_remove_list:
            base_string = base_string.replace(str_to_remove, "")
        clean_str = base_string.replace(" ", "")
        # 用正则提取输入的参数
        if pattern is not None:
            match = pattern.match(clean_str.strip())
            if not match:
                raise ValueError("格式错误，正确格式：[用户名][,game=游戏名]")
            ea_name = match.group(1) or None
            game = match.group(2)
            pider = match.group(3) or ""
            page = int(match.group(4)) if match.group(4) else 1
        else:
            ea_name = clean_str.strip()
            game = None
            pider = ""
            page = 1
        return ea_name, game, pider, page
