from datetime import datetime, timezone, timedelta

def format_large_number(number: int) -> str:
    """
    格式化大数字，例如将 1234567 格式化为 1.2M。
    """
    if number > 1_000_000_000:
        return f"{round(number / 1_000_000_000, 1)}G"
    elif number > 1_000_000:
        return f"{round(number / 1_000_000, 1)}M"
    elif number > 1_000:
        return f"{round(number / 1_000, 1)}K"
    else:
        return str(number)

def format_datetime_string(dt_string: str) -> str:
    """
    格式化日期时间字符串为 "年/月/日 上午/下午时:分" 格式。
    例如：将 "2025-11-02T15:06:47.892897+00:00" 格式化为 "2025/11/02 下午11:06" (上海时间)。
    """
    try:
        # 解析 ISO 8601 格式的日期时间字符串，包括毫秒和时区信息
        dt_object = datetime.fromisoformat(dt_string.replace("Z", "+00:00"))

        # 定义上海时区 (UTC+8)
        shanghai_tz = timezone(timedelta(hours=8))

        # 将日期时间对象转换为上海时区
        dt_object_shanghai = dt_object.astimezone(shanghai_tz)

        # 获取小时数，用于判断上午/下午
        hour = dt_object_shanghai.hour

        # 根据小时数判断时间段
        if 0 <= hour < 5:
            time_period = "凌晨"
        elif 5 <= hour < 9:
            time_period = "早上"
        elif 9 <= hour < 12:
            time_period = "上午"
        elif hour == 12:
            time_period = "中午"
        elif 13 <= hour < 18:
            time_period = "下午"
        else: # 18 <= hour < 24
            time_period = "晚上"

        # 格式化日期和时间部分
        formatted_date = dt_object_shanghai.strftime("%Y/%m/%d")
        formatted_time = dt_object_shanghai.strftime("%I:%M") # %I 是12小时制，%M 是分钟

        # 调整12小时制的小时显示，如果小时是0，显示为12
        if hour % 12 == 0:
            formatted_time = f"12:{dt_object_shanghai.strftime('%M')}"
        else:
            formatted_time = dt_object_shanghai.strftime("%I:%M")

        return f"{formatted_date} {time_period}{formatted_time}"
    except ValueError:
        return f"无效日期时间字符串: {dt_string}"
