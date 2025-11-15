from astrbot.api import logger
from ...constants.battlefield_constants import (ImageUrls, BackgroundColors, GameMappings, TemplateConstants)
from ...models.btr_entities import PlayerStats, Weapon, Vehicle, Soldier, Modes, Maps
from ..image_util import get_image_base64

import time

# 获取模板
templates = TemplateConstants.get_templates()
MAIN_TEMPLATE = templates["btr_main"]
WEAPONS_TEMPLATE = templates["btr_weapons"]
VEHICLES_TEMPLATE = templates["btr_vehicles"]
SOLDIERS_TEMPLATE = templates["btr_soldiers"]
MATCHES_TEMPLATE = templates["btr_matches"]

base_prompt = "你是一个战地风云游戏前线记者，根据以下游戏数据生成一个标题和内容，要足够炸裂并吸引眼球，评判标准kd<2是薯条,kpm<1是薯条此标准仅适用于除大逃杀以外的模式。可以适当调侃薯条，格式要求标题和内容要用'&&&'分开，字数保持在500-800个字，注意回复要用纯文本，且不使用md等格式"



def sort_list_of_dicts(list_of_dicts, key):
    """降序排序，支持点分隔的嵌套键，如果值为零就删除该项"""

    def get_nested_value(d, k_path):
        keys = k_path.split('.')
        current_value = d
        for key_part in keys:
            if isinstance(current_value, dict) and key_part in current_value:
                current_value = current_value[key_part]
            else:
                # 如果路径无效，返回一个默认值，例如0，以便排序不会失败
                return 0
        return current_value

    # 先过滤掉值为零的项
    filtered_list = [d for d in list_of_dicts if get_nested_value(d, key) != 0]

    # 然后对过滤后的列表进行降序排序
    return sorted(filtered_list, key=lambda k: get_nested_value(k, key), reverse=True)


async def btr_main_html_builder(stat_data: dict, weapons_data, vehicles_data, soldier_data, game: str) -> str:
    """
        构建主要html
        Args:
            stat_data: 查询到的统计数据字典
            weapons_data: 查询到的武器数据字典
            vehicles_data: 查询到的载具数据字典
            soldier_data: 查询到的士兵数据字典
            game: 所查询的游戏
        Returns:
            构建的Html
    """
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF2042_BACKGROUND_COLOR)
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    weapons_data = sort_list_of_dicts(weapons_data, "stats.kills.value")
    vehicles_data = sort_list_of_dicts(vehicles_data, "stats.kills.value")
    soldier_data = sort_list_of_dicts(soldier_data, "stats.kills.value")

    if game == "bf6":
        stat_entity = await PlayerStats.from_bf6_dict(stat_data)

        # 循环创建武器、载具、士兵对象列表
        weapons_entities = [await Weapon.from_bf6_dict(weapon_dict) for weapon_dict in weapons_data[:3]]
        vehicles_entities = [await Vehicle.from_bf6_dict(vehicle_dict) for vehicle_dict in vehicles_data[:3]]
        soldiers_entities = [await Soldier.from_bf6_dict(soldier_dict) for soldier_dict in soldier_data[:1]]
        banner = GameMappings.BANNERS.get(game, ImageUrls.BF6_BANNER).get(soldiers_entities[0].soldier_name)

    else:
        banner = GameMappings.BANNERS.get(game, ImageUrls.BF2042_BANNER)
        stat_entity = PlayerStats.from_btr_dict(stat_data)

        # 循环创建武器、载具、士兵对象列表
        weapons_entities = [Weapon.from_btr_dict(weapon_dict) for weapon_dict in weapons_data[:3]]
        vehicles_entities = [Vehicle.from_btr_dict(vehicle_dict) for vehicle_dict in vehicles_data[:3]]
        soldiers_entities = [Soldier.from_btr_dict(soldier_dict) for soldier_dict in soldier_data[:1]]
    stat_entity.avatar = ImageUrls().DEFAULT_AVATAR

    html = MAIN_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        stat_entity=stat_entity,
        weapon_data=weapons_entities,
        vehicle_data=vehicles_entities,
        soldier_data=soldiers_entities,
        game=game,
        background_color=background_color,
    )
    return html


async def btr_weapons_html_builder(stat_data: dict, weapons_data, vehicles_data, soldier_data, game: str) -> str:
    """
        构建武器html
        Args:
            stat_data: 查询到的统计数据字典
            weapons_data: 查询到的武器数据字典
            vehicles_data: 查询到的载具数据字典
            soldier_data: 查询到的士兵数据字典
            game: 所查询的游戏
        Returns:
            构建的Html
    """
    # 排序
    weapons_data = sort_list_of_dicts(weapons_data, "stats.kills.value")
    soldier_data = sort_list_of_dicts(soldier_data, "stats.kills.value")
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF2042_BACKGROUND_COLOR)
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 创建对象
    if game == "bf6":
        stat_entity = await PlayerStats.from_bf6_dict(stat_data)

        # 循环创建对象列表
        weapons_entities = [await Weapon.from_bf6_dict(weapon_dict) for weapon_dict in weapons_data]
        soldiers_entities = [await Soldier.from_bf6_dict(soldier_dict) for soldier_dict in soldier_data[:1]]
        banner = GameMappings.BANNERS.get(game, ImageUrls.BF6_BANNER).get(soldiers_entities[0].soldier_name)
    else:
        banner = GameMappings.BANNERS.get(game, ImageUrls.BF2042_BANNER)
        stat_entity = PlayerStats.from_btr_dict(stat_data)

        # 循环创建对象列表
        weapons_entities = [Weapon.from_btr_dict(weapon_dict) for weapon_dict in weapons_data]
    stat_entity.avatar = ImageUrls().DEFAULT_AVATAR

    html = WEAPONS_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        stat_entity=stat_entity,
        weapon_data=weapons_entities,
        game=game,
        background_color=background_color,
    )
    return html


async def btr_vehicles_html_builder(stat_data: dict, weapons_data, vehicles_data, soldier_data, game: str) -> str:
    """
        构建载具html
        Args:
            stat_data: 查询到的统计数据字典
            weapons_data: 查询到的武器数据字典
            vehicles_data: 查询到的载具数据字典
            soldier_data: 查询到的士兵数据字典
            game: 所查询的游戏
        Returns:
            构建的Html
    """
    # 创建对象

    vehicles_data = sort_list_of_dicts(vehicles_data, "stats.kills.value")
    soldier_data = sort_list_of_dicts(soldier_data, "stats.kills.value")
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF2042_BACKGROUND_COLOR)
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 创建对象
    if game == "bf6":
        stat_entity = await PlayerStats.from_bf6_dict(stat_data)

        # 循环创建对象列表
        vehicles_entities = [await Vehicle.from_bf6_dict(vehicle_dict) for vehicle_dict in vehicles_data]
        soldiers_entities = [await Soldier.from_bf6_dict(soldier_dict) for soldier_dict in soldier_data[:1]]
        banner = GameMappings.BANNERS.get(game, ImageUrls.BF6_BANNER).get(soldiers_entities[0].soldier_name)
    else:
        stat_entity = PlayerStats.from_btr_dict(stat_data)
        banner = GameMappings.BANNERS.get(game, ImageUrls.BF2042_BANNER)
        # 循环创建对象列表
        vehicles_entities = [Vehicle.from_btr_dict(vehicle_dict) for vehicle_dict in vehicles_data]
    stat_entity.avatar = ImageUrls().DEFAULT_AVATAR

    html = VEHICLES_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        stat_entity=stat_entity,
        vehicle_data=vehicles_entities,
        game=game,
        background_color=background_color,
    )
    return html


async def btr_soldier_html_builder(stat_data: dict, weapons_data, vehicles_data, soldier_data, game: str) -> str:
    """
        构建士兵html
        Args:
            stat_data: 查询到的统计数据字典
            weapons_data: 查询到的武器数据字典
            vehicles_data: 查询到的载具数据字典
            soldier_data: 查询到的士兵数据字典
            game: 所查询的游戏
        Returns:
            构建的Html
    """
    soldier_data = sort_list_of_dicts(soldier_data, "stats.kills.value")
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF2042_BACKGROUND_COLOR)
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if game == "bf6":
        stat_entity = await PlayerStats.from_bf6_dict(stat_data)

        # 循环创建对象列表
        soldiers_entities = [await Soldier.from_bf6_dict(soldier_dict) for soldier_dict in soldier_data]
        banner = GameMappings.BANNERS.get(game, ImageUrls.BF6_BANNER).get(soldiers_entities[0].soldier_name)
    else:
        banner = GameMappings.BANNERS.get(game, ImageUrls.BF2042_BANNER)
        stat_entity = PlayerStats.from_btr_dict(stat_data)
        # 循环创建士兵对象列表
        soldiers_entities = [Soldier.from_btr_dict(soldier_dict) for soldier_dict in soldier_data]

    stat_entity.avatar = ImageUrls().DEFAULT_AVATAR

    html = SOLDIERS_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        stat_entity=stat_entity,
        soldier_data=soldiers_entities,
        game=game,
        background_color=background_color,
    )
    return html


async def btr_matches_html_builder(ea_name: str, stat_data: dict, weapons_data, vehicles_data, soldier_data, mode_data,
                                   maps_data, game: str, matches_timestamp, provider) -> str:
    """
        构建战报html
        Args:
            ea_name: ea_name
            stat_data: 查询到的统计数据字典
            weapons_data: 查询到的武器数据字典
            vehicles_data: 查询到的载具数据字典
            soldier_data: 查询到的士兵数据字典
            mode_data: 查询到的模式数据字典
            maps_data: 查询到的地图数据字典
            game: 所查询的游戏
            matches_timestamp: 战报时间
            provider: LLM供应商实例
        Returns:
            构建的Html
    """
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    bf6_background = await get_image_base64(ImageUrls.BF6_BACKGROUND)

    weapons_data = sort_list_of_dicts(weapons_data, "stats.kills")
    vehicles_data = sort_list_of_dicts(vehicles_data, "stats.kills")
    soldier_data = sort_list_of_dicts(soldier_data, "stats.timePlayed")
    mode_data = sort_list_of_dicts(mode_data, "stats.matchesPlayed")
    maps_data = sort_list_of_dicts(maps_data, "stats.matchesPlayed")

    stat_entity = await PlayerStats.from_bf6_matches_dict(stat_data, ea_name)

    # 循环创建武器、载具、士兵对象列表
    weapons_entities = [await Weapon.from_bf6_matches_dict(weapon_dict) for weapon_dict in weapons_data]
    vehicles_entities = [await Vehicle.from_bf6_matches_dict(vehicle_dict) for vehicle_dict in vehicles_data]
    soldiers_entities = [await Soldier.from_bf6_matches_dict(soldier_dict) for soldier_dict in soldier_data]
    modes_entities = [await Modes.from_bf6_matches_dict(mode_dict) for mode_dict in mode_data]
    maps_entities = [await Maps.from_bf6_matches_dict(maps_dict) for maps_dict in maps_data]

    # 计算最近地图胜场
    map_total = " // ".join(
        [f"{map_entity.map_name} {map_entity.matches_won} W-{map_entity.matches_lost} L" for map_entity in
         maps_entities])

    win_num = 0
    lost_num = 0
    matches_num = 0
    # 计算最近模式胜场
    for mode_entity in modes_entities:
        win_num += mode_entity.matches_won
        lost_num += mode_entity.matches_lost
        matches_num += mode_entity.matches_played

    prompt = build_prompt(stat_entity, weapons_entities, vehicles_entities, soldiers_entities, modes_entities, maps_entities, map_total)
    try:
        llm_resp = await provider.text_chat(system_prompt = base_prompt,prompt=prompt)
    except Exception as e:
        logger.error(e)
        llm_resp = " &&& "


    resp_arr = ["",""]
    if llm_resp and llm_resp.completion_text:
        resp_arr = llm_resp.completion_text.strip().split("&&&")

    html = MATCHES_TEMPLATE.render(
        bf6_background=bf6_background,
        update_time=update_time,
        stat_entity=stat_entity,
        weapon_data=weapons_entities[:3],
        vehicle_data=vehicles_entities[:3],
        soldier_data=soldiers_entities[:2],
        mode_data=modes_entities[:3],
        maps_entities=maps_entities,
        map_total=map_total,
        win_num=win_num,
        lost_num=lost_num,
        matches_num=matches_num,
        matches_timestamp=matches_timestamp,
        game=game,
        llm_total=resp_arr,
    )
    return html


def build_prompt(stat_entity, weapons_data, vehicles_data, soldier_data, mode_data, maps_data, map_total):
    """构建提示词prompt"""

    recent_prompt = f"玩家{stat_entity.user_name}（名字发给你什么样，你就写什么样子，禁止翻译）"


    if map_total:
        recent_prompt = f"{recent_prompt}最近游玩地图{map_total}"

    recent_prompt = f"{recent_prompt},击杀{stat_entity.kills}名敌军，其中{stat_entity.player_kills}名敌方玩家，平均每分钟击杀{stat_entity.kills_per_minute}，K/D{stat_entity.kill_death}，死亡{stat_entity.deaths}，助攻{stat_entity.assists}，破坏了{stat_entity.vehicles_destroyed}辆载具"

    mode_prompt = "游玩模式"
    if mode_data:
        for mode_entity in mode_data:
            mode_prompt += f"{mode_entity.mode_name}，胜利{mode_entity.matches_won}，失败{mode_entity.matches_lost}"
        recent_prompt += mode_prompt

    soldier_prompt = ""
    if soldier_data:
        for soldier_entity in soldier_data:
            soldier_prompt += f"使用{soldier_entity.soldier_name}兵，击杀了{soldier_entity.kills}敌军，K/D{soldier_entity.kd_ratio}，死亡{soldier_entity.deaths}次，助攻{soldier_entity.assists}，救助了{soldier_entity.revives}名队友"
        recent_prompt += soldier_prompt
    weapons_prompt = ""
    if weapons_data:
        for weapon_entity in weapons_data:
            weapons_prompt += f"使用{weapon_entity.category}{weapon_entity.weapon_name}击杀了{weapon_entity.kills}名敌军,每分钟平均击杀{weapon_entity.kills_per_minute},造成了{weapon_entity.damage_dealt}点伤害，爆头率{weapon_entity.headshot_percentage}"
        recent_prompt += weapons_prompt

    vehicles_prompt = ""
    if vehicles_data:
        for vehicle_entity in vehicles_data:
            vehicles_prompt += f"使用{vehicle_entity.category}{vehicle_entity.vehicle_name}击杀了{vehicle_entity.kills},每分钟平均击杀{vehicle_entity.kills_per_minute}，造成了{vehicle_entity.damage_dealt}点伤害，摧毁了{vehicle_entity.destroyed_with}辆载具"
        recent_prompt += vehicles_prompt

    return recent_prompt
