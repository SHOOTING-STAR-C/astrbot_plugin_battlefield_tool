from typing import Dict, Any, Callable

from ...constants.battlefield_constants import ImageUrls

class BtrImageGenerator:
    """图片生成工具类，负责将各种数据转换为图片"""
    
    def __init__(self, img_quality: int = 90):
        """
        初始化图片生成器
        Args:
            img_quality: 图片质量，默认90
        """
        self.img_quality = img_quality
    
    async def generate_main_btr_data_pic(self, game: str, html_render_func: Callable,
                                    html_builder_func: Callable,stat_data,weapon_data,vehicle_data,soldier_data) -> str:
        """将查询的全部数据转为图片
        Args:
            game: 游戏代号
            html_render_func: HTML渲染函数
            html_builder_func: HTML构建函数
            stat_data: 查询到的统计数据等
            weapon_data: 查询到的武器数据等
            vehicle_data: 查询到的载具数据等
            soldier_data: 查询到的士兵数据等
        Returns:
            返回生成的图片URL
        """
        html = await html_builder_func(stat_data,weapon_data,vehicle_data,soldier_data, game)
        url = await html_render_func(
            html,
            {},
            True,
            {
                "timeout": 10000,
                "quality": self.img_quality,
                "clip": {**ImageUrls.COMMON_CLIP_PARAMS, "height": 2353},
            },
        )
        return url

    async def generate_weapons_btr_data_pic(self, game: str, html_render_func: Callable,
                                            html_builder_func: Callable,stat_data,weapon_data,vehicle_data,soldier_data) -> str:
        """将查询的武器数据转为图片
        Args:
            game: 游戏代号
            html_render_func: HTML渲染函数
            html_builder_func: HTML构建函数
            stat_data: 查询到的统计数据等
            weapon_data: 查询到的武器数据等
            vehicle_data: 查询到的载具数据等
            soldier_data: 查询到的士兵数据等
        Returns:
            返回生成的图片URL
        """
        html = await html_builder_func(stat_data,weapon_data,vehicle_data,soldier_data, game)
        url = await html_render_func(
            html,
            {},
            True,
            {
                "timeout": 10000,
                "quality": self.img_quality,
                "clip": {**ImageUrls.COMMON_CLIP_PARAMS, "height": 20000},
            },
        )
        return url
    
    async def generate_vehicles_btr_data_pic(self, game: str, html_render_func: Callable,
                                             html_builder_func: Callable,stat_data,weapon_data,vehicle_data,soldier_data) -> str:
        """将查询的载具数据转为图片
        Args:
            game: 游戏代号
            html_render_func: HTML渲染函数
            html_builder_func: HTML构建函数
            stat_data: 查询到的统计数据等
            weapon_data: 查询到的武器数据等
            vehicle_data: 查询到的载具数据等
            soldier_data: 查询到的士兵数据等
        Returns:
            返回生成的图片URL
        """
        html = await html_builder_func(stat_data,weapon_data,vehicle_data,soldier_data, game)
        url = await html_render_func(
            html,
            {},
            True,
            {
                "timeout": 10000,
                "quality": self.img_quality,
                "clip": {**ImageUrls.COMMON_CLIP_PARAMS, "height": 20000},
            },
        )
        return url


    async def generate_soldiers_btr_data_pic(self, game: str, html_render_func: Callable,
                                             html_builder_func: Callable,stat_data,weapon_data,vehicle_data,soldier_data) -> str:
        """将查询的载具数据转为图片
        Args:
            game: 游戏代号
            html_render_func: HTML渲染函数
            html_builder_func: HTML构建函数
            stat_data: 查询到的统计数据等
            weapon_data: 查询到的武器数据等
            vehicle_data: 查询到的载具数据等
            soldier_data: 查询到的士兵数据等
        Returns:
            返回生成的图片URL
        """
        html = await html_builder_func(stat_data,weapon_data,vehicle_data,soldier_data, game)
        url = await html_render_func(
            html,
            {},
            True,
            {
                "timeout": 10000,
                "quality": self.img_quality,
                "clip": {**ImageUrls.COMMON_CLIP_PARAMS, "height": 10000},
            },
        )
        return url


    async def generate_matches_btr_data_pic(self, game: str,ea_name, html_render_func: Callable,
                                             html_builder_func: Callable,stat_data,weapon_data,vehicle_data,soldier_data,mode_data,maps_data,matches_timestamp,provider) -> str:
            """将查询的全部数据转为图片
            Args:
                game: 游戏代号
                ea_name: 玩家名称
                html_render_func: HTML渲染函数
                html_builder_func: HTML构建函数
                stat_data: 查询到的统计数据等
                weapon_data: 查询到的武器数据等
                vehicle_data: 查询到的载具数据等
                soldier_data: 查询到的士兵数据等
                mode_data: 查询到的模式数据等
                maps_data: 查询到的地图数据等
                matches_timestamp: 战报时间
                provider: LLM供应商
            Returns:
                返回生成的图片URL
            """
            html = await html_builder_func(ea_name,stat_data,weapon_data,vehicle_data,soldier_data,mode_data,maps_data, game,matches_timestamp,provider)
            url = await html_render_func(
                html,
                {},
                True,
                {
                    "timeout": 10000,
                    "quality": self.img_quality,
                    # "clip": {**ImageUrls.COMMON_CLIP_PARAMS, "height": 2353},
                },
            )
            return url
    
    # async def generate_servers_btr_data_pic(self, data: Dict[str, Any], game: str, html_render_func: Callable,
    #                                    html_builder_func: Callable) -> str:
    #     """将查询的服务器数据转为图片
    #     Args:
    #         data: 查询到的服务器数据等
    #         game: 游戏代号
    #         html_render_func: HTML渲染函数
    #         html_builder_func: HTML构建函数
    #     Returns:
    #         返回生成的图片URL
    #     """
    #     # 数据量较少时设置高度
    #     height = 10000
    #     if data["servers"] is not None and len(data["servers"]) == 1:
    #         height = 450
    #     elif data["servers"] is not None and len(data["servers"]) == 2:
    #         height = 620
    #
    #     html = html_builder_func(data, game)
    #     url = await html_render_func(
    #         html,
    #         {},
    #         True,
    #         {
    #             "timeout": 10000,
    #             "quality": self.img_quality,
    #             "clip": {**ImageUrls.COMMON_CLIP_PARAMS, "height": height},
    #         },
    #     )
    #     return url
