from astrbot.api import logger
from ...models.btr_entities import PlayerStats, Weapon, Vehicle, Soldier

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


async def btr_main_llm_builder(stat_data: dict, weapons_data, vehicles_data, soldier_data, game: str, bf_prompt: str) -> str:
    """
        构建LLM能够理解的Prompt
        Args:
            stat_data: 查询到的统计数据字典
            weapons_data: 查询到的武器数据字典
            vehicles_data: 查询到的载具数据字典
            soldier_data: 查询到的士兵数据字典
            game: 所查询的游戏
            bf_prompt: 默认评价提示词
        Returns:
            构建的Html
    """
    weapons_data = sort_list_of_dicts(weapons_data, "stats.kills.value")
    vehicles_data = sort_list_of_dicts(vehicles_data, "stats.kills.value")
    soldier_data = sort_list_of_dicts(soldier_data, "stats.kills.value")
    if game == "bf6":
        # 创建对象
        stat_entity = await PlayerStats.from_bf6_dict(stat_data)

        # 循环创建武器、载具、士兵对象列表
        weapons_entities = [await Weapon.from_bf6_dict(weapon_dict) for weapon_dict in weapons_data[:2]]
        vehicles_entities = [await Vehicle.from_bf6_dict(vehicle_dict) for vehicle_dict in vehicles_data[:2]]
        soldiers_entities = [await Soldier.from_bf6_dict(soldier_dict) for soldier_dict in soldier_data[:1]]
    else:
        # 创建对象
        stat_entity = PlayerStats.from_btr_dict(stat_data)

        # 循环创建武器、载具、士兵对象列表
        weapons_entities = [Weapon.from_btr_dict(weapon_dict) for weapon_dict in weapons_data[:2]]
        vehicles_entities = [Vehicle.from_btr_dict(vehicle_dict) for vehicle_dict in vehicles_data[:2]]
        soldiers_entities = [Soldier.from_btr_dict(soldier_dict) for soldier_dict in soldier_data[:1]]

    llm_text = f"""{bf_prompt}，{game}中{stat_entity.to_llm_text()}"""

    if weapons_entities:
        for weapon in weapons_entities:
            llm_text += weapon.to_llm_text()
    if vehicles_entities:
        for vehicle in vehicles_entities:
            llm_text += vehicle.to_llm_text()
    if soldiers_entities:
        for soldier in soldiers_entities:
            if game == "bf6":
                llm_text += soldier.to_llm_bf6_text()
            else:
                llm_text += soldier.to_llm_text()

    logger.debug(llm_text)

    return llm_text
