from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, StarTools, register
from astrbot.api.all import AstrBotConfig
from astrbot.api import logger

from .database.battlefield_database import BattleFieldDataBase
from .database.battlefield_db_service import BattleFieldDBService
from .core.plugin_logic import BattlefieldPluginLogic
from .core.api_handlers import ApiHandlers

import aiohttp


@register(
    "astrbot_plugin_battlefield_tool",  # name
    "SHOOTING_STAR_C",  # author
    "战地风云战绩查询插件",  # desc
    "v2.0.1",  # version
)
class BattlefieldTool(Star):

    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.config = config
        self.wake_prefix = context.get_config().get("wake_prefix")

        self.default_game = config.get("default_game", "bfv")
        self.timeout_config = config.get("timeout_config", 15)
        self.img_quality = config.get("img_quality", 90)
        self.ssc_token = config.get("ssc_token", "")
        self.evaluation_provider = config.get("evaluation_provider", None)
        self.bf_prompt = config.get("bf_prompt",
                                    "请根据以下评判标准和数据从多个方面评价用户的游戏水平，注意要结合人设和上下文，保证对话不冲突，1.K/D(击杀/死亡比):薯薯:小于1，Pro:大于2.5说明： 高KD是Pro哥基础，但单纯KD高可能是架枪蹲人。Pro哥的KD是在高强度突击和救点中打出来的。2.KPM(每分钟击杀):薯薯:小于0.7，Pro:大于1.5说明： 这是衡量你击杀效率的关键指标。KPM低而KD高，大概率是喜欢偷偷地躲起来蹲人，可以适当调侃这些胆小鬼。3.命中率&爆头率这个指标要综合判断，不能直接根据这个参数判断是不是pro哥命中率要根据枪械来看，喷子命中即使超过100%也是正常的，其他种类枪械正常玩家也不会太高爆头率狙击枪超过90%也可以算正常玩家过低的爆头率可能是载具玩家两个指标都超过50%很有可能是挂钩，遇到挂钩直接开喷，谨慎使用，枪械数据量较少时可能是巧合4.急救数神医专属指标5.载具注意击杀和摧毁，击杀特别多但摧毁特别少的那就是捞薯凶手、恐怖铁皮人(只能用来调侃坦克)补充：可以根据玩家使用武器、载具、飞机的偏好分为不同的Pro哥")

        self.bf_data_path = StarTools.get_data_dir("battleField_tool_plugin")
        self.db = BattleFieldDataBase(self.bf_data_path)  # 初始化数据库
        self.db_service = BattleFieldDBService(self.db)  # 初始化数据库服务
        self._session = None
        self.default_platform = "pc"  # 默认平台
        self.plugin_logic = BattlefieldPluginLogic(self.db_service, self.default_game, self.timeout_config,
                                                   self.img_quality,
                                                   self._session, self.bf_prompt, self.default_platform)
        self.api_handlers = ApiHandlers(self.plugin_logic, self.html_render, self.timeout_config, self.ssc_token,
                                        self._session)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        self._session = aiohttp.ClientSession()
        await self.db.initialize()  # 添加数据库初始化调用
        self.plugin_logic._session = self._session  # 更新handlers中的session
        self.api_handlers._session = self._session  # 更新api_handlers中的session

    @filter.command("stat")
    async def bf_stat(self, event: AstrMessageEvent):
        """查询用户数据"""

        request_data = await self.plugin_logic.handle_player_data_request(event, ["stat"])

        if request_data.error_msg:
            yield event.plain_result(request_data.error_msg)
            return
        logger.info(f"玩家id:{request_data.ea_name}，所查询游戏:{request_data.game}")

        if request_data.game in ["bf2042", "bf6"]:
            result = await self.api_handlers.handle_btr_game(event, request_data, "stat").__anext__()
            if not "http" in result:
                yield event.plain_result(result)
            else:
                yield event.image_result(result)
        else:
            result = await self.api_handlers.fetch_gt_data(event, request_data, "stat", "all").__anext__()
            yield event.image_result(result)

    @filter.command("weapons", alias=["武器"])
    async def bf_weapons(self, event: AstrMessageEvent):
        """查询用户武器数据"""
        request_data = await self.plugin_logic.handle_player_data_request(event, ["weapons", "武器"])

        if request_data.error_msg:
            yield event.plain_result(request_data.error_msg)
            return

        logger.info(f"玩家id:{request_data.ea_name}，所查询游戏:{request_data.game}")

        if request_data.game in ["bf2042", "bf6"]:
            result = await self.api_handlers.handle_btr_game(event, request_data, "weapons").__anext__()
            yield event.image_result(result)
        else:
            result = await self.api_handlers.fetch_gt_data(event, request_data, "weapons", "weapons").__anext__()
            yield event.image_result(result)

    @filter.command("vehicles", alias=["载具"])
    async def bf_vehicles(self, event: AstrMessageEvent):
        """查询载具数据"""
        request_data = await self.plugin_logic.handle_player_data_request(event, ["vehicles", "载具"])

        if request_data.error_msg:
            yield event.plain_result(request_data.error_msg)
            return

        logger.info(f"玩家id:{request_data.ea_name}，所查询游戏:{request_data.game}")
        if request_data.game in ["bf2042", "bf6"]:
            result = await self.api_handlers.handle_btr_game(event, request_data, "vehicles").__anext__()
            yield event.image_result(result)
        else:
            result = await self.api_handlers.fetch_gt_data(event, request_data, "vehicles", "vehicles").__anext__()
            yield event.image_result(result)

    @filter.command("soldiers", alias=["士兵"])
    async def bf_soldier(self, event: AstrMessageEvent):
        """查询士兵数据 (仅限bf2042,bf6)"""
        request_data = await self.plugin_logic.handle_player_data_request(event, ["soldiers", "士兵"])

        if request_data.error_msg:
            yield event.plain_result(request_data.error_msg)
            return

        if request_data.game not in ['bf2042', 'bf6']:
            yield event.plain_result("士兵查询仅支持战地2042、bf6。")
            return

        logger.info(f"玩家id:{request_data.ea_name}，所查询游戏:{request_data.game}")
        result = await self.api_handlers.handle_btr_game(event, request_data, "soldiers").__anext__()
        yield event.image_result(result)

    @filter.command("recent", alias=["最近", "战报"])
    async def bf_recent(self, event: AstrMessageEvent):
        """查询最近战局数据 (仅限bf6)"""
        # 获取provider
        if not self.evaluation_provider:
            error_msg = "锐评功能未配置，请在插件设置中指定 Provider ID。"
            logger.warning(error_msg)
            yield error_msg
            return
        provider = self.context.get_provider_by_id(self.evaluation_provider)
        if not provider:
            error_msg = f"无法找到 ID 为 '{self.evaluation_provider}' 的 Provider 实例。"
            logger.error(error_msg)
            yield error_msg
            return


        request_data = await self.plugin_logic.handle_player_data_request(event, ["recent", "最近", "战报"])
        if request_data.error_msg:
            yield event.plain_result(request_data.error_msg)
            return

        if request_data.game != "bf6":
            yield event.plain_result("最近战局查询仅支持战地bf6。")
            return
        logger.info(f"玩家id:{request_data.ea_name}，所查询游戏:{request_data.game}")

        result,next_page = await self.api_handlers.handle_btr_matches(event, request_data,provider).__anext__()
        yield event.image_result(result)
        if next_page:
            prefix = ""
            if len(self.wake_prefix) > 0:
                prefix = self.wake_prefix[0]
            yield event.plain_result("下一页")
            yield event.plain_result(f"{prefix}{next_page}")

    @filter.command("servers", alias=["服务器"])
    async def bf_servers(self, event: AstrMessageEvent):
        """查询服务器数据"""
        request_data = await self.plugin_logic.handle_player_data_request(event, ["servers", "服务器"])

        if request_data.error_msg:
            yield event.plain_result(request_data.error_msg)
            return

        if request_data.game in ["bf2042", "bf6"]:
            yield event.plain_result("暂不支持bf2042、bf6的服务器查询")
            return

        if request_data.server_name is None:
            yield event.plain_result("请提供服务器名称进行查询哦~")  # 优化提示信息
            return

        logger.info(f"查询服务器:{request_data.server_name}，所查询游戏:{request_data.game}")
        servers_data = await self.api_handlers.fetch_gt_servers_data(
            request_data, self.timeout_config, self._session
        )

        result = await self.plugin_logic.process_api_response(
            event, servers_data, "servers", request_data.game, self.html_render
        ).__anext__()
        yield result

    @filter.command("bind", alias=["绑定"])
    async def bf_bind(self, event: AstrMessageEvent):
        """绑定本插件默认查询的用户"""
        request_data = await self.plugin_logic.handle_player_data_request(event, ["bind", "绑定"])
        if request_data.error_msg:
            yield event.plain_result(request_data.error_msg)
            return
        # 持久化绑定数据
        msg = await self.db_service.upsert_user_bind(request_data.qq_id, request_data.ea_name, request_data.pider)
        yield event.plain_result(msg)

    @filter.llm_tool(name="bf_tool_bind")
    async def bf_tool_bind(self, event: AstrMessageEvent, ea_name: str, user_id: str = None):
        """
            用户绑定默认查询的EA账户名
            Args:
                ea_name (string): 绑定的账户名，必填
                user_id (string): 用户帮别人绑定的用户id
        """
        if not user_id:
            # 获取用户
            user_id = event.get_sender_id()
        return await self.db_service.upsert_user_bind(user_id, ea_name, "")

    @filter.llm_tool(name="bf_tool_stat")
    async def bf_tool_stat(self, event: AstrMessageEvent, user_id: str = None, game: str = None, ea_name: str = None):
        """
            战地风云系列查询战绩
            Args:
                user_id (string): 用户查询别人战绩时填写的id，用户没有指明就不要填，函数会自动查询
                game (string):  游戏代号(可选bf4、bf1、bfv、bf2042、bf6)，用户没有指明就不要填，函数会自动查询
                ea_name (string): 查询其他人时EA的账户名，注意是EA账户名，不是用户id，用户没有指明就不要填，函数会自动查询
        """
        logger.debug(f"""{ea_name},{user_id},{game}""")
        request_data = await self.plugin_logic.handle_player_llm_request(event, ea_name, user_id, game)
        if request_data.error_msg:
            yield request_data.error_msg
            return
        logger.info(f"玩家id:{request_data.ea_name}，所查询游戏:{request_data.game}")
        if request_data.game in ["bf2042", "bf6"]:
            result = await self.api_handlers.handle_btr_game(event, request_data, "stat", True).__anext__()
            yield result
        else:
            result = await self.api_handlers.fetch_gt_data(event, request_data, "stat", "all", True).__anext__()
            yield result

    @filter.command("bf_init")
    async def bf_init(self, event: AstrMessageEvent):
        """同一机器人不同会话渠道配置不同的默认查询"""
        message_str = event.message_str
        session_channel_id = self.plugin_logic.get_session_channel_id(event)

        if not event.is_private_chat():
            # 群聊只能机器人管理员设置渠道绑定命令
            if not event.is_admin():
                yield event.plain_result(
                    "没有权限哦，群聊只能机器人管理员使用[bf_init]命令呢"
                )
                return

            session_channel_id = event.get_group_id()

        # 解析命令，直接提取游戏代号
        command_prefix = ["bf_init"]
        clean_str = message_str
        for prefix in command_prefix:
            clean_str = clean_str.replace(prefix, "")
        default_game = clean_str.strip()

        if not default_game:
            yield event.plain_result("不能设置空哦~")
        else:
            # 持久化渠道数据
            msg = await self.db_service.upsert_session_channel(
                session_channel_id, default_game
            )
            yield event.plain_result(msg)

    @filter.command("bf_help")
    async def bf_help(self, event: AstrMessageEvent):
        """显示战地插件帮助信息"""
        prefix = ""
        if len(self.wake_prefix) > 0:
            prefix = self.wake_prefix[0]

        help_msg = f"""战地风云插件使用帮助：
1. 账号绑定
命令: {prefix}bind [ea_name] 或 {prefix}绑定 [ea_name]
参数: ea_name - 您的EA账号名
示例: {prefix}bind ExamplePlayer

2. 默认查询设置
命令: {prefix}bf_init [游戏代号]
参数: 游戏代号 {", ".join(self.plugin_logic.SUPPORTED_GAMES)}
注意: 私聊都能使用，群聊中仅bot管理员可用

3. 战绩查询
命令: {prefix}stat [ea_name],game=[游戏代号]
参数:
  ea_name - EA账号名(可选，已绑定则可不填)
  game - 游戏代号(可选)
示例: {prefix}stat ExamplePlayer,game=bf1

4. 武器统计
命令: {prefix}weapons [ea_name],game=[游戏代号] 或 {prefix}武器 [ea_name],game=[游戏代号]
参数同上
示例: {prefix}weapons ExamplePlayer,game=bfv

5. 载具统计
命令: {prefix}vehicles [ea_name],game=[游戏代号] 或 {prefix}载具 [ea_name],game=[游戏代号]
参数同上
示例: {prefix}vehicles ExamplePlayer

6. 士兵查询
命令: {prefix}soldier [ea_name],game=bf2042 或 {prefix}士兵 [ea_name],game=bf2042
参数:
  ea_name - EA账号名(可选，已绑定则可不填)
  game - 游戏代号(必填，且必须为bf2042、bf6)
示例: {prefix}soldier ExamplePlayer,game=bf2042

7. 服务器查询
命令: {prefix}servers [server_name],game=[游戏代号] 或 {prefix}服务器 [server_name],game=[游戏代号]
参数:
  server_name - 服务器名称(必填)
  game - 游戏代号(可选)
示例: {prefix}servers 服务器名称,game=bf1

注: 实际使用时不需要输入[]。
"""
        yield event.plain_result(help_msg)

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件卸载/停用时会调用。"""
        if self._session:
            await self._session.close()
