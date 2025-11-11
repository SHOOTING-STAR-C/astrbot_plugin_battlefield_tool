"""
异常处理装饰器
提供统一的异常处理机制，自动捕获、记录和格式化异常
"""

import functools
from astrbot.api import logger
from .exceptions import BattlefieldPluginError
from .error_handler import ErrorHandler


def handle_exceptions(reraise: bool = False):
    """
    异常处理装饰器 - 智能处理返回类型
    
    该装饰器会自动捕获异常并返回用户友好的错误消息。
    当发生异常时，统一返回 plain_result，让原函数自己决定正常情况下的返回类型。
    
    Args:
        reraise: 是否重新抛出异常（用于测试）
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, event, *args, **kwargs):
            error_handler = ErrorHandler()
            
            try:
                # 执行原函数，让原函数自己决定返回类型
                async for result in func(self, event, *args, **kwargs):
                    yield result
            except BattlefieldPluginError as e:
                # 处理已知的插件异常
                user_msg = error_handler.create_error_response(e, event)
                # 减少日志打印，只在 ErrorHandler 中统一记录
                
                if reraise:
                    raise
                    
                # 异常时统一返回 plain_result
                yield event.plain_result(user_msg)
            except Exception as e:
                # 处理未知异常
                user_msg = error_handler.create_error_response(e, event)
                # 减少日志打印，只在 ErrorHandler 中统一记录
                
                if reraise:
                    raise
                    
                # 异常时统一返回 plain_result
                yield event.plain_result(user_msg)
        return wrapper
    return decorator


def handle_sync_exceptions(reraise: bool = False):
    """
    同步函数的异常处理装饰器
    
    Args:
        reraise: 是否重新抛出异常（用于测试）
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, event, *args, **kwargs):
            error_handler = ErrorHandler()
            
            try:
                result = await func(self, event, *args, **kwargs)
                return result
            except BattlefieldPluginError as e:
                # 处理已知的插件异常
                user_msg = error_handler.create_error_response(e, event)

                if reraise:
                    raise
                    
                # 异常时统一返回 plain_result
                return event.plain_result(user_msg)
            except Exception as e:
                # 处理未知异常
                user_msg = error_handler.create_error_response(e, event)

                if reraise:
                    raise
                    
                # 异常时统一返回 plain_result
                return event.plain_result(user_msg)
        return wrapper
    return decorator


def safe_execute(default_return=None, log_error: bool = True):
    """
    安全执行装饰器，异常时返回默认值
    
    Args:
        default_return: 异常时的默认返回值
        log_error: 是否记录错误日志
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"安全执行异常 - 函数: {func.__name__}, 错误: {str(e)}", exc_info=True)
                return default_return
        return wrapper
    return decorator
