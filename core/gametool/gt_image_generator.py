from typing import Dict, Any, Callable

# 定义图片裁剪的通用参数
from ...constants.battlefield_constants import ImageUrls


class GtImageGenerator:
    """图片生成工具类，负责将各种数据转换为图片"""
    
    def __init__(self, img_quality: int = 90):
        """
        初始化图片生成器
        Args:
            img_quality: 图片质量，默认90
        """
        self.img_quality = img_quality
    
    async def generate_main_gt_data_pic(self, data: Dict[str, Any], game: str, html_render_func: Callable, 
                                    html_builder_func: Callable) -> str:
        """将查询的全部数据转为图片
        Args:
            data: 查询到的战绩数据等
            game: 游戏代号
            html_render_func: HTML渲染函数
            html_builder_func: HTML构建函数
        Returns:
            返回生成的图片URL
        """
        html = await html_builder_func(data, game)
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
    
    async def generate_weapons_gt_data_pic(self, data: Dict[str, Any], game: str, html_render_func: Callable,
                                       html_builder_func: Callable) -> str:
        """将查询的武器数据转为图片
        Args:
            data: 查询到的武器数据等
            game: 游戏代号
            html_render_func: HTML渲染函数
            html_builder_func: HTML构建函数
        Returns:
            返回生成的图片URL
        """
        html = await html_builder_func(data, game)
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
    
    async def generate_vehicles_gt_data_pic(self, data: Dict[str, Any], game: str, html_render_func: Callable,
                                        html_builder_func: Callable) -> str:
        """将查询的载具数据转为图片
        Args:
            data: 查询到的载具数据等
            game: 游戏代号
            html_render_func: HTML渲染函数
            html_builder_func: HTML构建函数
        Returns:
            返回生成的图片URL
        """
        html = await html_builder_func(data, game)
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
    
    async def generate_servers_gt_data_pic(self, data: Dict[str, Any], game: str, html_render_func: Callable,
                                       html_builder_func: Callable) -> str:
        """将查询的服务器数据转为图片
        Args:
            data: 查询到的服务器数据等
            game: 游戏代号
            html_render_func: HTML渲染函数
            html_builder_func: HTML构建函数
        Returns:
            返回生成的图片URL
        """
        # 数据量较少时设置高度
        height = 10000
        if data["servers"] is not None and len(data["servers"]) == 1:
            height = 500
        elif data["servers"] is not None and len(data["servers"]) == 2:
            height = 670
            
        html = await html_builder_func(data, game)
        url = await html_render_func(
            html,
            {},
            True,
            {
                "timeout": 10000,
                "quality": self.img_quality,
                "clip": {**ImageUrls.COMMON_CLIP_PARAMS, "height": height},
            },
        )
        return url
