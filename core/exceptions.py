"""
Battlefield 插件自定义异常类
提供统一的异常处理机制和用户友好的错误信息
"""


class BattlefieldPluginError(Exception):
    """插件基础异常类"""
    
    def __init__(self, message: str, user_message: str = None, error_code: str = None):
        """
        Args:
            message: 开发者调试信息
            user_message: 用户友好信息，如果为None则使用message
            error_code: 错误代码，用于错误分类
        """
        self.message = message
        self.user_message = user_message or message
        self.error_code = error_code
        super().__init__(self.message)


class NetworkError(BattlefieldPluginError):
    """网络相关异常"""
    
    def __init__(self, message: str, user_message: str = "网络连接异常，请稍后重试", error_code: str = "NETWORK_ERROR"):
        super().__init__(message, user_message, error_code)


class APIError(BattlefieldPluginError):
    """API调用异常"""
    
    def __init__(self, message: str, user_message: str = "数据获取失败，请检查输入或稍后重试", error_code: str = "API_ERROR"):
        super().__init__(message, user_message, error_code)


class DataParseError(BattlefieldPluginError):
    """数据解析异常"""
    
    def __init__(self, message: str, user_message: str = "数据解析异常，请联系开发者", error_code: str = "PARSE_ERROR"):
        super().__init__(message, user_message, error_code)


class UserInputError(BattlefieldPluginError):
    """用户输入异常"""
    
    def __init__(self, message: str, user_message: str = "输入格式错误，请检查命令格式", error_code: str = "INPUT_ERROR"):
        super().__init__(message, user_message, error_code)


class DatabaseError(BattlefieldPluginError):
    """数据库操作异常"""
    
    def __init__(self, message: str, user_message: str = "数据库操作失败，请稍后重试", error_code: str = "DATABASE_ERROR"):
        super().__init__(message, user_message, error_code)


class ImageGenerationError(BattlefieldPluginError):
    """图片生成异常"""
    
    def __init__(self, message: str, user_message: str = "图片生成失败，请稍后重试", error_code: str = "IMAGE_ERROR"):
        super().__init__(message, user_message, error_code)


class AuthenticationError(BattlefieldPluginError):
    """认证相关异常"""
    
    def __init__(self, message: str, user_message: str = "认证失败，请检查配置", error_code: str = "AUTH_ERROR"):
        super().__init__(message, user_message, error_code)


class PermissionError(BattlefieldPluginError):
    """权限相关异常"""
    
    def __init__(self, message: str, user_message: str = "权限不足，无法执行此操作", error_code: str = "PERMISSION_ERROR"):
        super().__init__(message, user_message, error_code)


class TimeoutError(BattlefieldPluginError):
    """超时异常"""
    
    def __init__(self, message: str, user_message: str = "请求超时，请稍后重试", error_code: str = "TIMEOUT_ERROR"):
        super().__init__(message, user_message, error_code)


class ConfigurationError(BattlefieldPluginError):
    """配置相关异常"""
    
    def __init__(self, message: str, user_message: str = "配置错误，请检查插件设置", error_code: str = "CONFIG_ERROR"):
        super().__init__(message, user_message, error_code)


class GameNotSupportedError(UserInputError):
    """游戏不支持异常"""
    
    def __init__(self, game: str, supported_games: list):
        user_message = f"不支持的游戏 '{game}'，支持的游戏: {', '.join(supported_games)}"
        super().__init__(f"游戏 {game} 不支持", user_message, "GAME_NOT_SUPPORTED")


class UserNotBoundError(UserInputError):
    """用户未绑定异常"""
    
    def __init__(self, user_id: str = None):
        if user_id:
            user_message = f"用户 {user_id} 未绑定EA账户，请先使用 bind [ea_name] 绑定"
        else:
            user_message = "请先使用 bind [ea_name] 绑定账户"
        super().__init__(f"用户未绑定: {user_id}", user_message, "USER_NOT_BOUND")


class ProviderNotConfiguredError(ConfigurationError):
    """Provider未配置异常"""
    
    def __init__(self):
        user_message = "锐评功能未配置，请在插件设置中指定 Provider ID"
        super().__init__("锐评功能未配置", user_message, "PROVIDER_NOT_CONFIGURED")


class PermissionDeniedError(PermissionError):
    """权限拒绝异常"""
    
    def __init__(self, operation: str = "此操作"):
        user_message = f"权限不足，只有管理员可以使用{operation}"
        super().__init__(f"操作 {operation} 权限不足", user_message, "PERMISSION_DENIED")


class InvalidParameterError(UserInputError):
    """无效参数异常"""
    
    def __init__(self, parameter: str, value: str = None, expected: str = None):
        if value and expected:
            user_message = f"参数 '{parameter}' 值 '{value}' 无效，期望: {expected}"
        elif value:
            user_message = f"参数 '{parameter}' 值 '{value}' 无效"
        else:
            user_message = f"缺少必要参数: {parameter}"
        super().__init__(f"无效参数: {parameter}", user_message, "INVALID_PARAMETER")


class PageLimitExceededError(UserInputError):
    """页码超出限制异常"""
    
    def __init__(self, max_page: int = 25):
        user_message = f"页码超出限制，最大支持{max_page}页"
        super().__init__(f"页码超出限制: {max_page}", user_message, "PAGE_LIMIT_EXCEEDED")


class GameNotSupportedForOperationError(UserInputError):
    """游戏不支持特定操作异常"""
    
    def __init__(self, game: str, operation: str, supported_games: list = None):
        if supported_games:
            user_message = f"{operation}仅支持 {', '.join(supported_games)}，不支持 {game}"
        else:
            user_message = f"{operation}不支持 {game}"
        super().__init__(f"游戏 {game} 不支持操作 {operation}", user_message, "GAME_NOT_SUPPORTED_FOR_OPERATION")


class PrivateDataError(UserInputError):
    """私有数据异常"""
    
    def __init__(self, message: str = "用户数据是私有的，请打开设置->系统->游戏数据分享"):
        super().__init__("私有数据访问被拒绝", message, "PRIVATE_DATA")


class MultipleUsersError(UserInputError):
    """多用户匹配异常"""
    
    def __init__(self, users: list,wake_prefix:list,name:str):
        user_info_list = []
        prefix = ""
        if len(wake_prefix) > 0:
            prefix = wake_prefix[0]
        for user in users:
            handle = user.get("platformUserHandle", "未知")
            identifier = user.get("platformUserIdentifier", "未知")
            user_info_list.append(f"用户名: {handle}, pider: {identifier}, 请尝试指令: \n{prefix}stat pider={identifier}\n{prefix}bind {name},pider={identifier}\n")
        
        user_message = (
            f"查询到多个用户：\n" + "\n".join(user_info_list) +
            "\n请先使用 stat 查询各个战绩确认哪个是您，然后使用 bind 绑定您的pid"
        )
        super().__init__("找到多个用户", user_message, "MULTIPLE_USERS")


class NoDataError(UserInputError):
    """无数据异常"""
    
    def __init__(self, data_type: str = "数据"):
        user_message = f"暂无{data_type}"
        super().__init__(f"无可用数据: {data_type}", user_message, "NO_DATA")
