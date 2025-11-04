from typing import List, Optional, Dict, Any

from ..core.image_util import get_image_base64
from ..core.utils import format_large_number


class PlayerStats:
    """
    基本统计类
    """

    def __init__(self,
                 avatar: str,  # 玩家头像URL
                 user_name: str,  # 玩家用户名
                 level: str,  # 玩家等级
                 rank_img: str,  # 等级图片
                 hours_played: str,  # 游戏时间（小时）

                 dmg_per_min: str,  # 每分钟伤害
                 dmg_per_min_percentile: str,  # 每分钟伤害
                 kill_death: str,  # KD
                 kill_death_percentile: str,  # KD_PER
                 kills_per_minute: str,  # 每分钟击杀数
                 kills_per_minute_percentile: str,  # 每分钟击杀数_排名
                 headshot_percentage: str,  # 爆头率

                 human_kd_ratio: str,  # 对玩家KD
                 human_kd_ratio_percentile: str,  # 对玩家KD排名
                 kills: int,  # 击杀
                 kills_percentile: str,  # 击杀排名
                 player_kills: int,  # 击杀玩家
                 player_kills_percentile: int,  # 击杀玩家排名
                 assists: str,  # 助攻
                 deaths: str,  # 死亡
                 kills_per_match: str,  # 场均击杀
                 wl_percentage: str,  # 胜率

                 wins: str,  # 胜利场次
                 wins_percentile: str,  # 胜利场次
                 losses: str,  # 失败场次
                 damage_dealt: str,  # 伤害
                 damage_per_match: str,  # 场均伤害
                 revives: str,  # 急救
                 vehicles_destroyed: str,  # 载具破坏
                 score_per_minute: str,  # 每分钟得分
                 score: str,  # 总得分
                 ):
        self.avatar = avatar
        self.user_name = user_name
        self.level = level
        self.rank_img = rank_img
        self.hours_played = hours_played
        self.dmg_per_min = dmg_per_min
        self.dmg_per_min_percentile = dmg_per_min_percentile
        self.kill_death = kill_death
        self.kill_death_percentile = kill_death_percentile
        self.headshot_percentage = headshot_percentage
        self.kills_per_minute = kills_per_minute
        self.kills_per_minute_percentile = kills_per_minute_percentile
        self.human_kd_ratio = human_kd_ratio
        self.human_kd_ratio_percentile = human_kd_ratio_percentile
        self.kills = kills
        self.kills_percentile = kills_percentile
        self.player_kills = player_kills
        self.player_kills_percentile = player_kills_percentile
        self.assists = assists
        self.deaths = deaths
        self.kills_per_match = kills_per_match
        self.wl_percentage = wl_percentage
        self.wins = wins
        self.wins_percentile = wins_percentile
        self.losses = losses
        self.damage_dealt = damage_dealt
        self.damage_per_match = damage_per_match
        self.revives = revives
        self.vehicles_destroyed = vehicles_destroyed
        self.score_per_minute = score_per_minute
        self.score = score

    @classmethod
    def from_btr_dict(cls, data: Dict[str, Any]):
        """从btr字典创建 PlayerStats 实例"""
        return cls(
            avatar=data.get("avatar", ""),
            user_name=data.get("platformInfo").get("platformUserHandle", "--"),
            level=data.get("segments")[0].get("stats").get("level").get("displayValue"),
            rank_img="",
            hours_played=str(round(data.get("segments")[0].get("stats").get("timePlayed").get("value") / 3600, 1)),

            dmg_per_min=data.get("segments")[0].get("stats").get("dmgPerMin").get("value"),
            dmg_per_min_percentile=100,
            kill_death=data.get("segments")[0].get("stats").get("kdRatio").get("displayValue"),
            kill_death_percentile=100,
            headshot_percentage=data.get("segments")[0].get("stats").get("headshotPercentage").get("displayValue"),
            kills_per_minute=data.get("segments")[0].get("stats").get("killsPerMinute").get("displayValue"),
            kills_per_minute_percentile=100,

            human_kd_ratio=data.get("segments")[0].get("stats").get("humanKdRatio").get("displayValue"),
            kills=data.get("segments")[0].get("stats").get("kills").get("value"),
            kills_percentile=round(100 - data.get("segments")[0].get("stats").get("kills").get("percentile", 0), 2),
            assists=data.get("segments")[0].get("stats").get("assists").get("value"),
            deaths=data.get("segments")[0].get("stats").get("deaths").get("value"),
            kills_per_match=data.get("segments")[0].get("stats").get("killsPerMatch").get("value"),
            wl_percentage=data.get("segments")[0].get("stats").get("wlPercentage").get("displayValue"),

            wins=data.get("segments")[0].get("stats").get("wins").get("displayValue"),
            wins_percentile=round(100 - data.get("segments")[0].get("stats").get("wins").get("percentile", 0), 2),
            losses=data.get("segments")[0].get("stats").get("losses").get("displayValue"),
            damage_dealt=format_large_number(data.get("segments")[0].get("stats").get("damageDealt").get("value")),
            damage_per_match=data.get("segments")[0].get("stats").get("damagePerMatch").get("value"),
            revives=data.get("segments")[0].get("stats").get("revives").get("value"),
            vehicles_destroyed=data.get("segments")[0].get("stats").get("vehiclesDestroyed").get("displayValue"),
            score_per_minute="",
            score="",
            human_kd_ratio_percentile=100,
            player_kills=0,
            player_kills_percentile=0,
        )

    @classmethod
    async def from_bf6_dict(cls, data: Dict[str, Any]):
        # 获取等级图片
        level = data.get("segments")[0].get("stats").get("careerPlayerRank").get("displayValue")
        rank_img = PlayerStats.get_rank_image(level)
        image = ""
        if rank_img:
            image = await get_image_base64(rank_img)

        return cls(
            avatar=data.get("avatar", ""),
            user_name=data.get("platformInfo").get("platformUserHandle", "--"),
            level=level,
            rank_img=image,
            hours_played=str(round(data.get("segments")[0].get("stats").get("timePlayed").get("value") / 3600, 1)),

            dmg_per_min=data.get("segments")[0].get("stats").get("damagePerMinute").get("value"),
            dmg_per_min_percentile=round(
                100 - data.get("segments")[0].get("stats").get("damagePerMinute").get("percentile", 0), 2),
            kill_death=data.get("segments")[0].get("stats").get("kdRatio").get("displayValue"),
            kill_death_percentile=round(100 - data.get("segments")[0].get("stats").get("kdRatio").get("percentile", 0),
                                        2),
            headshot_percentage=data.get("segments")[0].get("stats").get("headshotPercentage").get("value"),
            kills_per_minute=data.get("segments")[0].get("stats").get("killsPerMinute").get("value"),
            kills_per_minute_percentile=round(
                100 - data.get("segments")[0].get("stats").get("killsPerMinute").get("percentile", 0), 2),
            human_kd_ratio=data.get("segments")[0].get("stats").get("playerKd").get("displayValue"),
            human_kd_ratio_percentile=round(
                100 - data.get("segments")[0].get("stats").get("playerKd").get("percentile", 0), 2),
            kills=data.get("segments")[0].get("stats").get("kills").get("value"),
            kills_percentile=round(100 - data.get("segments")[0].get("stats").get("kills").get("percentile", 0), 2),
            player_kills=data.get("segments")[0].get("stats").get("playerKills").get("value", 0),
            player_kills_percentile=round(
                100 - data.get("segments")[0].get("stats").get("playerKills").get("percentile", 0), 2),
            assists=data.get("segments")[0].get("stats").get("assists").get("value"),
            deaths=data.get("segments")[0].get("stats").get("deaths").get("value"),
            kills_per_match=data.get("segments")[0].get("stats").get("killsPerMatch").get("value"),
            wl_percentage=data.get("segments")[0].get("stats").get("wlPercentage").get("displayValue"),

            wins=data.get("segments")[0].get("stats").get("matchesWon").get("displayValue"),
            wins_percentile=round(100 - data.get("segments")[0].get("stats").get("matchesWon").get("percentile", 0), 2),
            losses=data.get("segments")[0].get("stats").get("matchesLost").get("displayValue"),
            damage_dealt=format_large_number(data.get("segments")[0].get("stats").get("damageDealt").get("value")),
            damage_per_match=data.get("segments")[0].get("stats").get("damagePerMatch").get("value"),
            revives=data.get("segments")[0].get("stats").get("revives").get("value"),
            vehicles_destroyed=data.get("segments")[0].get("stats").get("vehiclesDestroyed").get("value"),
            score_per_minute=data.get("segments")[0].get("stats").get("scorePerMinute").get("value"),
            score=format_large_number(data.get("segments")[0].get("stats").get("score").get("value")),

        )

    @classmethod
    async def from_bf6_matches_dict(cls, data: Dict[str, Any],user_name):
        return cls(
            avatar=data.get("avatar", ""),
            user_name=user_name,
            level="",
            rank_img="",
            hours_played=str(round(data.get("timePlayed").get("value") / 60, 1)),

            dmg_per_min=data.get("damagePerMinute").get("value"),
            dmg_per_min_percentile=100,
            kill_death=data.get("kdRatio").get("displayValue"),
            kill_death_percentile=100,
            headshot_percentage=data.get("headshotPercentage").get("value"),
            kills_per_minute=data.get("killsPerMinute").get("value"),
            kills_per_minute_percentile=100,
            human_kd_ratio=data.get("playerKd").get("displayValue"),
            human_kd_ratio_percentile=100,
            kills=data.get("kills").get("value"),
            kills_percentile=100,
            player_kills=data.get("playerKills").get("value", 0),
            player_kills_percentile=100,
            assists=data.get("assists").get("value"),
            deaths=data.get("deaths").get("value"),
            kills_per_match=data.get("killsPerMatch").get("value"),
            wl_percentage=data.get("wlPercentage").get("displayValue"),

            wins=data.get("matchesWon").get("displayValue"),
            wins_percentile=100,
            losses=data.get("matchesLost").get("displayValue"),
            damage_dealt=format_large_number(data.get("damageDealt").get("value")),
            damage_per_match=data.get("damagePerMatch").get("value"),
            revives=data.get("revives").get("value"),
            vehicles_destroyed=data.get("vehiclesDestroyed").get("value"),
            score_per_minute=data.get("scorePerMinute").get("value"),
            score=format_large_number(data.get("score").get("value")),

        )

    @staticmethod
    def get_rank_image(level):
        int_level = int(level)
        formatted_level = ""

        if int_level <= 50:
            formatted_level = f"{int_level:03d}"
        elif 50 < int_level <= 90:
            # 5级一档，例如 56 -> 055
            formatted_level = f"{int_level // 5 * 5:03d}"
        elif 90 < int_level <= 490:
            # 10级一档，例如 123 -> 120
            formatted_level = f"{int_level // 10 * 10:03d}"
        elif 490 < int_level <= 5000:
            # 500级一档，例如 700 -> 500, 1200 -> 1000, 3200 -> 3000
            # 确保等级不会超过 5000
            calculated_level = min(int_level // 500 * 500, 5000)
            formatted_level = f"{calculated_level:03d}"
        else:
            # 超过 5000 级的，统一使用 5000 级的图片
            formatted_level = "5000"

        return f"http://tutu.shooting-star-c.top/i/2025/10/13/t_ui_rank_{formatted_level}_lg.png"

    def to_llm_text(self) -> str:
        """预处理 PlayerStats 方便 llm 理解"""
        return f"""用户{self.user_name}生涯总共击杀{self.kills}名敌军，总击杀世界排名{self.kills_percentile}%，击杀死亡比值(K/D):{self.kill_death},平均每分钟击杀(KPM):{self.kills_per_minute}，胜场:{self.wins}，急救了{self.revives}位士兵，爆头率：{self.headshot_percentage},总游玩时间，{self.hours_played}小时，破坏了{self.vehicles_destroyed}辆载具。"""

    # def __repr__(self):
    #     return f"PlayerStats(user_name='{self.user_name}', rank={self.level}, ...)"


class Weapon:
    """武器类"""

    def __init__(self,
                 weapon_name: str,  # 武器名字
                 category: str,  # 类别
                 image_url: str,  # 图标url
                 image: str,  # 图标base64s
                 kills: int,  # 击杀
                 kills_per_minute: str,  # kp
                 shots_accuracy: str,  # 命中率
                 headshot_percentage: str,  # 爆头率
                 dmg_per_min: str,  # 每分钟伤害
                 damage_dealt: str,  # 总伤害
                 shots_fired: str,  # 击发
                 shots_hit: str,  # 命中
                 scoped_kills: str,  # 范围击杀
                 hipfire_kills: str,  # 腰射击杀
                 headshot_kills: str,  # 爆头击杀
                 time_played: str,  # 使用时间
                 multi_kills: str,  # 多重击杀
                 body_kills: str,  # 身体击杀
                 deployments: str,  # 部署次数
                 ):
        self.weapon_name = weapon_name
        self.category = category
        self.image_url = image_url
        self.image = image
        self.kills = kills
        self.kills_per_minute = kills_per_minute
        self.shots_accuracy = shots_accuracy
        self.headshot_percentage = headshot_percentage
        self.dmg_per_min = dmg_per_min
        self.damage_dealt = damage_dealt
        self.shots_fired = shots_fired
        self.shots_hit = shots_hit
        self.scoped_kills = scoped_kills
        self.hipfire_kills = hipfire_kills
        self.headshot_kills = headshot_kills
        self.time_played = time_played
        self.multi_kills = multi_kills
        self.body_kills = body_kills
        self.deployments = deployments

    @classmethod
    def from_btr_dict(cls, data: Dict[str, Any]):
        """从btr字典创建 Weapon 实例"""
        return cls(
            weapon_name=data.get("metadata").get("name", "--"),
            category=Weapon._get_category(data.get("metadata").get("category", "--")),
            image_url="",
            image="",
            kills=data.get("stats").get("kills").get("value", 0),
            kills_per_minute=data.get("stats").get("killsPerMinute").get("displayValue", "--"),
            shots_accuracy=data.get("stats").get("shotsAccuracy").get("displayValue", "--"),
            headshot_percentage=data.get("stats").get("headshotPercentage").get("displayValue", "--"),
            dmg_per_min=data.get("stats").get("dmgPerMin").get("displayValue", "--"),
            damage_dealt=data.get("stats").get("damageDealt").get("displayValue", "--"),
            shots_fired=data.get("stats").get("shotsFired").get("displayValue", "--"),
            shots_hit=data.get("stats").get("shotsHit").get("displayValue", "--"),
            scoped_kills=data.get("stats").get("scopedKills").get("displayValue", "--"),
            hipfire_kills=data.get("stats").get("hipfireKills").get("value", "--"),
            headshot_kills=data.get("stats").get("headshotKills").get("value", "--"),
            time_played=str(round(data.get("stats").get("timePlayed").get("value", 0) / 3600, 1)),
            multi_kills=data.get("stats").get("multiKills").get("displayValue", "--"),
            body_kills=data.get("stats").get("bodyKills").get("displayValue", "--"),
            deployments=data.get("stats").get("deployments").get("displayValue", "--"),
        )

    @classmethod
    async def from_bf6_dict(cls, data: Dict[str, Any]):
        image_url = Weapon._get_category(data.get("metadata").get("imageUrl", ""))
        image = ""
        if image_url:
            image = await get_image_base64(image_url)
        return cls(
            weapon_name=data.get("metadata").get("name", "--"),
            category=Weapon._get_category(data.get("metadata").get("categoryName", "--")),
            image_url=image_url,
            image=image,
            kills=data.get("stats").get("kills").get("value", 0),
            kills_per_minute=data.get("stats").get("killsPerMinute").get("displayValue", "--"),
            shots_accuracy=data.get("stats").get("shotsAccuracy").get("displayValue", "--"),
            headshot_percentage=data.get("stats").get("headshotPercentage").get("displayValue", "--"),
            damage_dealt=data.get("stats").get("damageDealt").get("displayValue", "--"),
            shots_fired=data.get("stats").get("shotsFired").get("displayValue", "--"),
            shots_hit=data.get("stats").get("shotsHit").get("displayValue", "--"),
            headshot_kills=data.get("stats").get("headshotKills").get("displayValue", "--"),
            time_played=str(round(data.get("stats").get("timePlayed").get("value", 0) / 3600, 1)),
            multi_kills=data.get("stats").get("multiKills").get("displayValue", "--"),
            body_kills=data.get("stats").get("bodyKills").get("displayValue", "--"),

            deployments="",
            dmg_per_min="",
            scoped_kills="",
            hipfire_kills="",
        )
    @classmethod
    async def from_bf6_matches_dict(cls, data: Dict[str, Any]):
        image_url = Weapon._get_category(data.get("metadata").get("imageUrl", ""))
        image = ""
        if image_url:
            image = await get_image_base64(image_url)
        return cls(
            weapon_name=data.get("metadata").get("name", "--"),
            category=Weapon._get_category(data.get("metadata").get("categoryName", "--")),
            image_url=image_url,
            image=image,
            kills=data.get("stats").get("kills", 0),
            kills_per_minute=data.get("stats").get("killsPerMinute", "--"),
            shots_accuracy=data.get("stats").get("shotsAccuracy", "--"),
            headshot_percentage=data.get("stats").get("headshotPercentage", "--"),
            damage_dealt=data.get("stats").get("damageDealt", "--"),
            shots_fired=data.get("stats").get("shotsFired", "--"),
            shots_hit=data.get("stats").get("shotsHit", "--"),
            headshot_kills=data.get("stats").get("headshotKills", "--"),
            time_played=str(round(data.get("stats").get("timePlayed", 0) / 60, 1)),
            multi_kills=data.get("stats").get("multiKills", "--"),
            body_kills=data.get("stats").get("bodyKills", "--"),

            deployments="",
            dmg_per_min="",
            scoped_kills="",
            hipfire_kills="",
        )

    @staticmethod
    def _get_category(category_name):
        category_map = {
            "LMG": "轻机枪",
            "Assault Rifles": "突击步枪",
            "Sniper Rifles": "狙击步枪",
            "Carbines": "卡宾枪",
            "PDW": "冲锋枪",
            "DMR": "精确射手步枪",
            "Bolt Action": "狙击步枪",
            "Lever-Action Carbines": "多功能",
            "Shotguns": "霰弹枪",
            "Pistols": "手枪",
            "SMG": "冲锋枪",
        }
        return category_map.get(category_name, category_name)

    def to_llm_text(self) -> str:
        """预处理 Weapon 方便 llm 理解"""
        return f"""使用{self.category}{self.weapon_name}{self.time_played}小时，总共击杀了{self.kills}名敌军，该武器平均每分钟击杀{self.kills_per_minute}，爆头率{self.headshot_percentage},命中率{self.shots_accuracy}"""

    def __repr__(self):
        return f"Weapon(weapon_name='{self.weapon_name}', category='{self.category}', kills={self.kills})"


class Vehicle:
    def __init__(self,
                 vehicle_name: str,  # 武器名字
                 category: str,  # 类别
                 image_url: str,  # 图标url
                 image: str,  # 图标base64s
                 kills: int,  # 击杀
                 kills_per_minute: str,  # kp
                 time_played: str,  # 使用时间
                 damage_dealt: str,  # 总伤害
                 damage_dealt_to: str,  # 总伤害
                 destroyed: str,  # 摧毁
                 destroyed_with: str,  # 摧毁
                 passenger_assists: str,  # 乘客助攻
                 driver_assists: str,  # 驾驶员助攻
                 road_kills: str,  # 撞死
                 assists: str,  # 助攻
                 multi_kills: str,  # 多重击杀
                 distance_traveled: str,  # 行驶距离
                 call_ins: str,  # callIns
                 deployments: str,  # 部署
                 dmg_per_min: str,  # 部署
                 ):
        self.vehicle_name = vehicle_name
        self.category = category
        self.image_url = image_url
        self.image = image
        self.kills = kills
        self.kills_per_minute = kills_per_minute
        self.time_played = time_played
        self.damage_dealt = damage_dealt
        self.damage_dealt_to = damage_dealt_to
        self.destroyed = destroyed
        self.destroyed_with = destroyed_with
        self.passenger_assists = passenger_assists
        self.driver_assists = driver_assists
        self.road_kills = road_kills
        self.assists = assists
        self.multi_kills = multi_kills
        self.distance_traveled = distance_traveled
        self.call_ins = call_ins
        self.deployments = deployments
        self.dmg_per_min = dmg_per_min

    @classmethod
    def from_btr_dict(cls, data: Dict[str, Any]):
        """从btr字典创建 Vehicle 实例"""
        return cls(
            vehicle_name=Vehicle._get_vehicle_category(data.get("metadata").get("name", "--")),
            category=Vehicle._get_category(data.get("metadata").get("category", "--")),
            image_url="",
            image="",
            kills=data.get("stats").get("kills").get("value", 0),
            kills_per_minute=data.get("stats").get("killsPerMinute").get("displayValue", "--"),
            time_played=str(round(data.get("stats").get("timePlayed").get("value", 0) / 3600, 1)),
            damage_dealt=data.get("stats").get("damageDealt").get("displayValue", "--"),
            damage_dealt_to=data.get("stats").get("damageDealtTo").get("displayValue", "--"),
            destroyed=data.get("stats").get("destroyed").get("displayValue", "--"),
            destroyed_with=data.get("stats").get("destroyedWith").get("displayValue", "--"),
            passenger_assists=data.get("stats").get("passengerAssists").get("displayValue", "--"),
            driver_assists=data.get("stats").get("driverAssists").get("displayValue", "--"),
            road_kills=data.get("stats").get("roadKills").get("displayValue", "--"),
            assists=data.get("stats").get("assists").get("displayValue", "--"),
            multi_kills=data.get("stats").get("multiKills").get("displayValue", "--"),
            distance_traveled=data.get("stats").get("distanceTraveled").get("displayValue", "--"),
            call_ins=data.get("stats").get("callIns").get("displayValue", "--"),
            deployments=data.get("stats").get("deployments").get("displayValue", "--"),
            dmg_per_min=data.get("stats").get("dmgPerMin").get("displayValue", "--"),
        )

    @classmethod
    async def from_bf6_dict(cls, data: Dict[str, Any]):
        image_url = data.get("metadata").get("imageUrl", "")
        image = ""
        if image_url:
            image = await get_image_base64(image_url)
        return cls(
            vehicle_name=Vehicle._get_vehicle_category(data.get("metadata").get("name", "--")),
            category=Vehicle._get_category(data.get("metadata").get("categoryName", "--")),
            image_url=image_url,
            image=image,
            kills=data.get("stats").get("kills").get("value", 0),
            kills_per_minute=data.get("stats").get("killsPerMinute").get("displayValue", "--"),
            time_played=str(round(data.get("stats").get("timePlayed").get("value", 0) / 3600, 1)),
            damage_dealt=data.get("stats").get("damageDealt").get("displayValue", "--"),
            damage_dealt_to=data.get("stats").get("damageDealtTo").get("displayValue", "--"),

            destroyed_with=data.get("stats").get("destroyedWith").get("displayValue", "--"),
            destroyed=data.get("stats").get("destroyedOfType").get("displayValue", "--"),
            passenger_assists=data.get("stats").get("passengerAssists", "--").get("displayValue", "--"),
            driver_assists=data.get("stats").get("driverAssists").get("displayValue", "--"),
            road_kills=data.get("stats").get("roadKills").get("displayValue", "--"),
            assists=data.get("stats").get("assists").get("displayValue", "--"),
            multi_kills=data.get("stats").get("multiKills").get("displayValue", "--"),
            distance_traveled=data.get("stats").get("distanceTraveled").get("displayValue", "--"),
            call_ins=data.get("stats").get("callIns").get("displayValue", "--"),
            deployments=data.get("stats").get("deployments").get("displayValue", "--"),

            dmg_per_min="",
        )
    @classmethod
    async def from_bf6_matches_dict(cls, data: Dict[str, Any]):
        image_url = data.get("metadata").get("imageUrl", "")
        image = ""
        if image_url:
            image = await get_image_base64(image_url)
        return cls(
            vehicle_name=Vehicle._get_vehicle_category(data.get("metadata").get("name", "--")),
            category=Vehicle._get_category(data.get("metadata").get("categoryName", "--")),
            image_url=image_url,
            image=image,
            kills=data.get("stats").get("kills", 0),
            kills_per_minute=data.get("stats").get("killsPerMinute", "--"),
            time_played=str(round(data.get("stats").get("timePlayed", 0) / 60, 1)),
            damage_dealt=data.get("stats").get("damageDealt", "--"),
            damage_dealt_to=data.get("stats").get("damageDealtTo", "--"),

            destroyed_with=data.get("stats").get("destroyedWith", "--"),
            destroyed=data.get("stats").get("destroyedOfType", "--"),
            passenger_assists=data.get("stats").get("passengerAssists", "--"),
            driver_assists=data.get("stats").get("driverAssists", "--"),
            road_kills=data.get("stats").get("roadKills", "--"),
            assists=data.get("stats").get("assists", "--"),
            multi_kills=data.get("stats").get("multiKills", "--"),
            distance_traveled=data.get("stats").get("distanceTraveled", "--"),
            call_ins=data.get("stats").get("callIns", "--"),
            deployments=data.get("stats").get("deployments", "--"),

            dmg_per_min="",
        )

    @staticmethod
    def _get_category(category_name):
        category_map = {
            # bf2042
            "Land": "地载",
            "Amphibious": "两栖载具",
            "In-World": "地图载具",
            "Plane": "空载",
            "Helicopter": "旋翼",
            "Stationary": "定点武器",
            # bf6
            "Surface - Light Ground Transport": "轻型地面运输",
            "Surface - Main Battle Tank": "主战坦克",
            "Surface - Infantry Fighting Vehicle": "步兵战车",
            "Surface - Mobile Anti-Air": "防空",
            "Surface - Transport": "运输",
            "Aircraft - Attack Helicopter": "武装直升机",
            "Aircraft - Attack Bomber": "攻击机",
            "Aircraft - Fighter Jet": "空优机",
            "Aircraft - Transport Helicopter": "运输机",

        }
        return category_map.get(category_name, category_name)

    @staticmethod
    def _get_vehicle_category(name):
        category_map = {
            # bf2042
            "LATV4 Recon ": "轻型侦察车",
            "M5C  ": "博尔特",
            "EBAA Wildcat ": "小野猫 ",
            "LCAA Hovercraft": "气垫船",
            "MAV ": "MAV",
            "F-35E Panther ": "F-35E",
            "SU-57 FELON": "SU-57",
            "MV38-Condor": "秃鹰",
            "MD540 Nightbird ": "夜莺",
            "AH-64GX Apache Warchief": "阿帕奇",
            "KA-52 Alligator": "KA-52",
            "Mi-240 Super Hind ": "超级雌鹿",
            "M10 Wolverine": "狼獾",
            "M4 Sherman": "谢尔曼",
            "9K22 Tunguska-M": "通古斯卡",
            "M1161 ITV": "咆哮者",
            "Mi-28 Havoc": "Mi-28",
            "Centurion C-RAM": "百夫长",
            "RAH-68 Huron": "肖肖尼",
            "YG-99 Hannibal": "汉尼拔",
            "SU-70": "德鲁格",
        }
        return category_map.get(name, name)

    def to_llm_text(self) -> str:
        """预处理 Vehicle 方便 llm 理解"""
        return f"""使用{self.category}{self.vehicle_name},{self.time_played}小时,总共击杀了{self.kills}名敌军,该载具平均每分钟击杀{self.kills_per_minute},摧毁了{self.destroyed}辆载具。"""

    def __repr__(self):
        return f"Vehicle(vehicle_name='{self.vehicle_name}', category='{self.category}', kills={self.kills})"


class Soldier:
    """士兵类"""

    def __init__(self,
                 soldier_name: str,  # 士兵名
                 category: str,  # 类型
                 image_url: str,  # 图标url
                 image: str,  # 图标base64s
                 kills: int,  # 击杀
                 kd_ratio: str,  # kd
                 kills_per_minute: str,  # kp
                 assists: str,  # 助攻
                 time_played: str,  # 使用时间
                 deployments: str,  # 部署
                 revives: str,  # 急救
                 deaths: str,  # 死亡
                 ):
        self.soldier_name = soldier_name
        self.category = category
        self.image_url = image_url
        self.image = image
        self.kills = kills
        self.kd_ratio = kd_ratio
        self.kills_per_minute = kills_per_minute
        self.assists = assists
        self.time_played = time_played
        self.deployments = deployments
        self.revives = revives
        self.deaths = deaths

    @classmethod
    def from_btr_dict(cls, data: Dict[str, Any]):
        """从btr字典创建 Soldier 实例"""
        return cls(
            soldier_name=Soldier._get_soldier_name(data.get("metadata").get("name", "--")),
            category=Soldier._get_category(data.get("metadata").get("category", "--")),
            image_url="",
            image="",
            kills=data.get("stats").get("kills").get("value", 0),
            kd_ratio=data.get("stats").get("kdRatio").get("displayValue", "--"),
            kills_per_minute=data.get("stats").get("killsPerMinute").get("displayValue", "--"),
            assists=data.get("stats").get("assists").get("displayValue", "--"),
            time_played=str(round(data.get("stats").get("timePlayed").get("value", 0) / 3600, 1)),
            deployments=data.get("stats").get("deployments").get("displayValue", "--"),
            revives=data.get("stats").get("revives").get("displayValue", "--"),
            deaths=data.get("stats").get("deaths").get("displayValue", "--"),
        )

    @classmethod
    async def from_bf6_dict(cls, data: Dict[str, Any]):
        image_url = data.get("metadata").get("imageUrl", "")
        image = ""
        if image_url:
            image = await get_image_base64(image_url)
        return cls(
            soldier_name=Soldier._get_category(data.get("metadata").get("name", "--")),
            category="",
            image_url=image_url,
            image=image,
            kills=data.get("stats").get("kills").get("value", 0),
            kd_ratio=data.get("stats").get("kdRatio").get("displayValue", "--"),
            kills_per_minute=data.get("stats").get("killsPerMinute").get("displayValue", "--"),
            assists=data.get("stats").get("assists").get("displayValue", "--"),
            time_played=str(round(data.get("stats").get("timePlayed").get("value", 0) / 3600, 1)),
            deployments=data.get("stats").get("deployments").get("displayValue", "--"),
            revives=data.get("stats").get("revives").get("displayValue", "--"),
            deaths=data.get("stats").get("deaths").get("displayValue", "--"),
        )

    @classmethod
    async def from_bf6_matches_dict(cls, data: Dict[str, Any]):
        image_url = data.get("metadata").get("imageUrl", "")
        image = ""
        if image_url:
            image = await get_image_base64(image_url)
        return cls(
            soldier_name=Soldier._get_category(data.get("metadata").get("name", "--")),
            category="",
            image_url=image_url,
            image=image,
            kills=data.get("stats").get("kills",0),
            kd_ratio=data.get("stats").get("kdRatio","--"),
            kills_per_minute=data.get("stats").get("killsPerMinute","--"),
            assists=data.get("stats").get("assists", "--"),
            time_played=str(round(data.get("stats").get("timePlayed", 0) / 60, 1)),
            deployments=data.get("stats").get("deployments", "--"),
            revives=data.get("stats").get("revives", "--"),
            deaths=data.get("stats").get("deaths","--"),
        )

    @staticmethod
    def _get_category(category_name):
        category_map = {
            "Assault": "突击",
            "Engineer": "工程",
            "Support": "支援",
            "Recon": "侦察",
        }
        return category_map.get(category_name, category_name)

    @staticmethod
    def _get_soldier_name(name):
        soldier_map = {
            "Mackay ": "麦凯",
            "Sundance ": "日舞",
            "Irish ": "爱尔兰佬",
            "Casper ": "卡斯帕",
            "Rao ": "拉奥",
            "Dozer ": "推土机",
            "Boris ": "鲍里斯",
            "Paik ": "智秀",
            "Lis": "莉斯",
            "Crawford": "克劳福德",
            "Zain": "扎因",
            "Blasco": "布拉斯科",
            "Falck ": "法尔克",
        }
        return soldier_map.get(name, name)

    def to_llm_text(self) -> str:
        """预处理 Soldier 方便 llm 理解"""
        return f"""最擅长使用{self.category}兵士兵{self.soldier_name},{self.time_played}小时中击杀了{self.kills}名敌军,平均每分钟击杀{self.kills_per_minute},击杀死亡比值{self.kd_ratio}。"""

    def to_llm_bf6_text(self) -> str:
        """预处理 Soldier 方便 llm 理解"""
        return f"""最擅长使用{self.soldier_name}兵,{self.time_played}小时中击杀了{self.kills}名敌军,平均每分钟击杀{self.kills_per_minute},击杀死亡比值{self.kd_ratio}。"""

    def __repr__(self):
        return f"Soldier(soldier_name='{self.soldier_name}', category='{self.category}', kills={self.kills})"


class Modes:
    """模式类"""

    def __init__(self,
                 mode_name: str,  # 模式名
                 image_url: str,  # 图标url
                 image: str,  # 图标base64s
                 time_played: str,  # 使用时间
                 kills: int,  # 击杀
                 assists: int,  # 助攻
                 deaths: int,  # 死亡
                 matches_won: int,  # 胜利
                 matches_lost: int,  # 失败
                 matches_played: int,  # 总场次
                 kills_per_minute: str,  # kp
                 ):
        self.mode_name = mode_name
        self.image_url = image_url
        self.image = image
        self.time_played = time_played
        self.kills = kills
        self.assists = assists
        self.deaths = deaths
        self.matches_won = matches_won
        self.matches_lost = matches_lost
        self.matches_played = matches_played
        self.kills_per_minute = kills_per_minute

    @classmethod
    async def from_bf6_matches_dict (cls, data: Dict[str, Any]):
        image_url = data.get("metadata").get("imageUrl", "")
        image = ""
        if image_url:
            image = await get_image_base64(image_url)

        return cls(
            mode_name=Modes._get_category(data.get("metadata").get("name", "--")),
            image_url=image_url,
            image=image,
            time_played=str(round(data.get("stats").get("timePlayed", 0)/ 60, 1)),
            kills=data.get("stats").get("kills", 0),
            assists=data.get("stats").get("assists", 0),
            deaths=data.get("stats").get("deaths", 0),
            matches_won=data.get("stats").get("matchesWon", 0),
            matches_lost=data.get("stats").get("matchesLost", 0),
            matches_played=data.get("stats").get("matchesPlayed", 0),
            kills_per_minute=data.get("stats").get("killsPerMinute", "--"),
        )

    @staticmethod
    def _get_category(category_name):
        category_map = {
            "Strikepoint": "打击点",
            "Conquest": "征服",
            "Breakthrough": "突破",
            "Rush": "突袭",
            "Escalation": "全面升级",
            "Domination": "抢攻",
            "Team Deathmatch": "团队死斗",
            "BR Duos": "双人大逃杀",
            "Gauntlet": "试炼场",
            "Squad Deathmatch": "小队死斗",
            "King of the Hill": "山丘之王",
            "Payload": "Payload",
            "BR Quads": "四人大逃杀",
        }
        return category_map.get(category_name, category_name)
    def __repr__(self):
        return f"Modes(mode_name='{self.mode_name}', matches_won='{self.matches_won}', matches_lost={self.matches_lost},matches_played={self.matches_played})"

class Maps:
    """地图类"""
    def __init__(self,
                 map_name: str,
                 image_url: str,
                 image: str,
                 time_played: str,
                 matches_played: str,
                 matches_won: str,
                 matches_lost: str,
                 wl_percentage: str,
                 ):
        self.map_name = map_name
        self.image_url = image_url
        self.image = image
        self.time_played = time_played
        self.matches_played = matches_played
        self.matches_won = matches_won
        self.matches_lost = matches_lost
        self.wl_percentage = wl_percentage

    @classmethod
    async def from_bf6_matches_dict (cls, data: Dict[str, Any]):
        image_url = data.get("metadata").get("imageUrl", "")
        image = ""
        if image_url:
            image = await get_image_base64(image_url)

        return cls(
            map_name=Maps._get_category(data.get("metadata").get("name", "--")),
            image_url=image_url,
            image=image,
            time_played=str(round(data.get("stats").get("timePlayed", 0)/ 60, 1)),
            matches_played=data.get("stats").get("matchesPlayed", 0),
            matches_won=data.get("stats").get("matchesWon", 0),
            matches_lost=data.get("stats").get("matchesLost", 0),
            wl_percentage=data.get("stats").get("wlPercentage", "--"),
        )

    @staticmethod
    def _get_category(map_name):
        category_map = {
            "Operation Firestorm": "火线风暴",
            "Mirak Valley": "米拉克山谷",
            "Iberian Offensive": "伊比利亚攻势",
            "Liberation Peak": "解放峰",
            "Saints Quarter": "圣徒区",
            "Empire State": "帝国之洲",
            "Siege of Cairo": "开罗围城",
            "Manhattan Bridge": "曼哈顿大桥",
            "New Sobek City": "新索贝克城",
            "Blackwell Fields": "布莱克威尔原野",
        }
        return category_map.get(map_name, map_name)

    def __repr__(self):
        return f"Maps(map_name='{self.map_name}', matches_won='{self.matches_won}', matches_lost={self.matches_lost})"
