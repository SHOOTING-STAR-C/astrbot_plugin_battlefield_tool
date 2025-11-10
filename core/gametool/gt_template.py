from astrbot.api import logger
from ...constants.battlefield_constants import (ImageUrls, BackgroundColors, GameMappings, TemplateConstants)
from ...models.gt_entities import PlayerStats, Weapon, Vehicle, Server # 导入实体类
from ..image_util import get_image_base64

from typing import List, Dict, Any

import time

# 获取模板
templates = TemplateConstants.get_templates()
MAIN_TEMPLATE = templates["gt_main"]
WEAPONS_TEMPLATE = templates["gt_weapons"]
VEHICLES_TEMPLATE = templates["gt_vehicles"]
SERVERS_TEMPLATE = templates["gt_servers"]
WEAPON_CARD = templates["gt_weapon_card"]
VEHICLE_CARD = templates["gt_vehicle_card"]
SERVER_CARD = templates["gt_server_card"]


def sort_list_of_dicts(list_of_dicts, key):
    """降序排序"""
    return sorted(list_of_dicts, key=lambda k: k[key], reverse=True)


def prepare_weapons_data(d: dict, lens: int, game: str) -> List[Weapon]:
    """提取武器数据，格式化使用时间，并返回 Weapon 对象列表"""
    weapons_list_raw = d.get("weapons", [])
    weapons_list_raw = sort_list_of_dicts(weapons_list_raw, "kills")
    
    weapons_objects = []
    for w_data in weapons_list_raw[:lens]:
        if w_data.get("kills", 0) > 0:
            # 创建 Weapon 对象
            weapon = Weapon.from_dict(w_data)
            weapons_objects.append(weapon)
            
    return weapons_objects

def prepare_vehicles_data(d: dict, lens: int) -> List[Vehicle]:
    """提取载具数据，格式化使用时间，并返回 Vehicle 对象列表"""
    vehicles_list_raw = d.get("vehicles", [])
    vehicles_list_raw = sort_list_of_dicts(vehicles_list_raw, "kills")

    vehicles_objects = []
    for v_data in vehicles_list_raw[:lens]:
        if v_data.get("kills", 0) > 0:
            # 处理图片URL
            v_data["image"] = img_repair_vehicles(v_data.get("vehicleName", "").lower(), v_data.get("image", ""))
            # 创建 Vehicle 对象
            vehicle = Vehicle.from_dict(v_data)
            vehicles_objects.append(vehicle)
            
    return vehicles_objects

def img_repair_vehicles(item_name:str,url:str):
    """处理问题图片"""
    for item in ImageUrls.ERROR_IMG:
        if item["name"] == item_name:
            return item["repair_url"]
    return url



async def gt_main_html_builder(raw_data: dict, game: str) -> str:
    """
    构建主要html
    Args:
        raw_data: 查询到的原始数据字典
        game: 所查询的游戏
    Returns:
        构建的Html
    """
    banner = GameMappings.BANNERS.get(game, ImageUrls.BFV_BANNER)
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BFV_BACKGROUND_COLOR)

    # 预处理原始数据，使其符合 PlayerStats.from_gt_dict 的期望
    processed_data = raw_data.copy()
    if processed_data.get("avatar"):
        processed_data["avatar"] = await get_image_base64(processed_data["avatar"])
    else:
        processed_data["avatar"] = ImageUrls().DEFAULT_AVATAR

    processed_data["__hours_played"] = str(round(processed_data.get("secondsPlayed", 0) / 3600, 1))
    processed_data["revives"] = int(processed_data.get("revives", 0))
    processed_data["longest_head_shot"] = int(processed_data.get("longest_head_shot", 0))

    # 创建 PlayerStats 对象
    player_stats = PlayerStats.from_gt_dict(processed_data)
    
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(processed_data["__update_time"]))

    # 整理武器和载具数据，返回实体对象列表
    weapons_objects = prepare_weapons_data(processed_data, 3, game)
    vehicles_objects = prepare_vehicles_data(processed_data, 3)

    html = MAIN_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        d=player_stats, # 传递 PlayerStats 对象的字典表示
        weapon_data=weapons_objects,
        vehicle_data=vehicles_objects,
        game=game,
        background_color=background_color,
    )
    return html


async def gt_weapons_html_builder(raw_data: dict, game: str) -> str:
    """
    构建武器html
    Args:
        raw_data: 查询到的原始数据字典
        game: 所查询的游戏
    Returns:
        构建的Html
    """
    banner = GameMappings.BANNERS.get(game, ImageUrls.BFV_BANNER)
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF3_BACKGROUND_COLOR)

    # 预处理原始数据，使其符合 PlayerStats.from_gt_dict 的期望
    processed_data = raw_data.copy()
    if processed_data.get("avatar"):
        processed_data["avatar"] = await get_image_base64(processed_data["avatar"])
    else:
        processed_data["avatar"] = ImageUrls().DEFAULT_AVATAR
    
    # 计算 hours_played 并添加到 processed_data，以便 PlayerStats.from_gt_dict 使用
    processed_data["__hours_played"] = str(round(processed_data.get("secondsPlayed", 0) / 3600, 1))
    processed_data["revives"] = int(processed_data.get("revives", 0))
    processed_data["longest_head_shot"] = int(processed_data.get("longest_head_shot", 0))

    # 创建 PlayerStats 对象
    player_stats = PlayerStats.from_gt_dict(processed_data)

    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(processed_data["__update_time"]))

    # 整理武器数据，返回实体对象列表
    weapons_objects = prepare_weapons_data(processed_data, 50, game)

    html = WEAPONS_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        d=player_stats,
        weapon_data=weapons_objects,
        game=game,
        background_color=background_color,
    )
    return html


async def gt_vehicles_html_builder(raw_data: dict, game: str) -> str:
    """
    构建载具html
    Args:
        raw_data: 查询到的原始数据字典
        game: 所查询的游戏
    Returns:
        构建的Html
    """
    banner = GameMappings.BANNERS.get(game, ImageUrls.BFV_BANNER)
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF3_BACKGROUND_COLOR)

    # 预处理原始数据，使其符合 PlayerStats.from_gt_dict 的期望
    processed_data = raw_data.copy()
    if processed_data.get("avatar"):
        processed_data["avatar"] = await get_image_base64(processed_data["avatar"])
    else:
        processed_data["avatar"] = ImageUrls().DEFAULT_AVATAR
    
    # 计算 hours_played 并添加到 processed_data，以便 PlayerStats.from_gt_dict 使用
    processed_data["__hours_played"] = str(round(processed_data.get("secondsPlayed", 0) / 3600, 1))
    processed_data["revives"] = int(processed_data.get("revives", 0))
    processed_data["longest_head_shot"] = int(processed_data.get("longest_head_shot", 0))

    # 创建 PlayerStats 对象
    player_stats = PlayerStats.from_gt_dict(processed_data)

    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(processed_data["__update_time"]))

    # 整理载具数据，返回实体对象列表
    vehicles_objects = prepare_vehicles_data(processed_data, 50)

    html = VEHICLES_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        d=player_stats, # 传递 PlayerStats 对象的字典表示
        vehicle_data=vehicles_objects,
        game=game,
        background_color=background_color,
    )
    return html


async def gt_servers_html_builder(raw_data: Dict[str, Any], game: str) -> str:
    """
    构建服务器html
    Args:
        raw_data: 查询到的原始数据字典
        game: 所查询的游戏
    Returns:
        构建的Html
    """
    banner = GameMappings.BANNERS.get(game, ImageUrls.BFV_BANNER)
    logo = GameMappings.LOGOS.get(game, ImageUrls.BF3_LOGO)
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF3_BACKGROUND_COLOR)
    update_time = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(raw_data["__update_time"])
    )

    servers_list_raw = raw_data.get("servers", [])
    servers_objects = [Server.from_dict(s_data) for s_data in servers_list_raw]

    html = SERVERS_TEMPLATE.render(
        banner=banner,
        logo=logo,
        update_time=update_time,
        servers_data=servers_objects,
        game=game,
        background_color=background_color,
    )
    return html
