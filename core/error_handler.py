"""
全局异常处理器
提供统一的异常处理、日志记录和用户友好的错误消息
"""

from astrbot.api import logger
from .exceptions import BattlefieldPluginError


class ErrorHandler:
    """全局异常处理器"""
    
    def __init__(self):
        # 用户友好的错误消息模板
        self.error_messages = {
            "network_error": "网络连接异常，请稍后重试",
            "api_error": "数据获取失败，请检查输入或稍后重试",
            "parse_error": "数据解析异常，请联系开发者",
            "input_error": "输入格式错误，请检查命令格式",
            "database_error": "数据库操作失败，请稍后重试",
            "image_error": "图片生成失败，请稍后重试",
            "auth_error": "认证失败，请检查配置",
            "permission_error": "权限不足，无法执行此操作",
            "timeout_error": "请求超时，请稍后重试",
            "config_error": "配置错误，请检查插件设置",
            "unknown_error": "系统异常，请稍后重试或联系开发者",
            "player_not_found": "未找到玩家 '{player_name}'，请确认用户名是否正确",
            "game_not_supported": "不支持的游戏 '{game}'，支持的游戏: {supported_games}",
            "network_timeout": "网络请求超时，请检查网络连接后重试",
            "api_limit": "API调用频率过高，请稍后重试",
            "private_profile": "该玩家数据设置为私有，无法查看",
            "server_not_found": "未找到服务器 '{server_name}'",
            "bind_required": "请先使用 bind [用户名] 绑定账户",
            "permission_denied": "权限不足，只有管理员可以使用此命令",
            "invalid_command": "命令格式错误，请使用 {prefix}bf_help 查看帮助",
            "missing_parameter": "缺少必要参数: {parameter}",
            "invalid_game": "游戏代号错误，支持的游戏: {supported_games}",
            "page_limit": "页码超出限制，最大支持25页",
            "no_data": "暂无数据",
            "multiple_users": "查询到多个用户，请使用 pider 参数指定具体用户",
            "private_data": "用户数据是私有的，请打开设置->系统->游戏数据分享"
        }
    
    def format_user_message(self, error: BattlefieldPluginError) -> str:
        """
        格式化用户友好的错误信息
        
        Args:
            error: 插件异常实例
            
        Returns:
            用户友好的错误消息
        """
        # 如果异常已经包含用户友好的消息，直接使用
        if error.user_message and error.user_message != error.message:
            return error.user_message
        
        # 根据异常类型返回默认消息
        error_type = type(error).__name__.lower().replace("error", "")
        return self.error_messages.get(error_type, self.error_messages["unknown_error"])
    
    def handle_unknown_error(self, error: Exception) -> str:
        """
        处理未知异常
        
        Args:
            error: 未知异常实例
            
        Returns:
            用户友好的错误消息
        """
        # 减少日志冗余，只在 log_error 中统一记录
        return self.error_messages["unknown_error"]
    
    def log_error(self, error: Exception, context: dict = None):
        """
        记录错误日志
        
        Args:
            error: 异常实例
            context: 错误上下文信息
        """
        # 简化日志记录，只记录关键信息
        error_type = type(error).__name__
        error_msg = str(error)
        
        # 对于已知的插件异常，使用更简洁的日志
        if isinstance(error, BattlefieldPluginError):
            logger.error(f"battlefield-插件异常: {error_type} - {error_msg}")
        else:
            # 对于未知异常，记录详细信息但减少冗余
            logger.error(f"battlefield-未知异常: {error_type} - {error_msg}")
    
    def get_error_message(self, error_key: str, **kwargs) -> str:
        """
        获取格式化的错误消息
        
        Args:
            error_key: 错误消息键
            **kwargs: 格式化参数
            
        Returns:
            格式化后的错误消息
        """
        template = self.error_messages.get(error_key, self.error_messages["unknown_error"])
        try:
            return template.format(**kwargs)
        except KeyError:
            # 如果格式化失败，返回原始模板
            logger.warning(f"错误消息模板格式化失败: {error_key}, 参数: {kwargs}")
            return template
    
    def create_error_response(self, error: Exception, event=None) -> str:
        """
        创建统一的错误响应
        
        Args:
            error: 异常实例
            event: 事件对象（可选）
            
        Returns:
            错误响应消息
        """
        if isinstance(error, BattlefieldPluginError):
            user_message = self.format_user_message(error)
        else:
            user_message = self.handle_unknown_error(error)
        
        # 记录错误
        context = {}
        if event:
            context["user_id"] = event.get_sender_id() if hasattr(event, 'get_sender_id') else None
            context["message"] = event.message_str if hasattr(event, 'message_str') else None
        
        self.log_error(error, context)
        
        return user_message
