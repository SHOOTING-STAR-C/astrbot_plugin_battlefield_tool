import json
import asyncio
import aiohttp

from astrbot.api import logger
from typing import Optional



GAMETOOLS_API_SITE = "https://api.gametools.network/"
BTR_API_SITE = "https://battlefield.shooting-star-c.top/api"
# BTR_API_SITE = "http://localhost:8766/api"
SUPPORTED_GAMES = ["bf4","bf1", "bfv"]


async def gt_request_api(game, prop="stats", params=None, timeout=15, session=None):
    """
    异步请求API
        Args:
        game: 游戏代号(bfv/bf1/bf4)
        prop: 请求属性(stats/servers等)
        params: 查询参数
        timeout: 超时时间(秒)
        session: 可选的aiohttp.ClientSession实例
    Returns:
        JSON响应数据
    Raises:
        aiohttp.ClientError: 网络或HTTP错误
        json.JSONDecodeError: 响应不是合法JSON
    """
    if params is None:
        params = {}
    url = GAMETOOLS_API_SITE + f"{game}/{prop}"
    logger.info(f"Battlefield Tool Request Gametools API: {url}，请求参数: {params}")

    should_close = session is None
    if should_close:
        session = aiohttp.ClientSession()

    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with session.get(url, params=params, timeout=timeout_obj) as response:
            if response.status == 200:
                result = await response.json()
                result["code"] = response.status
                return result
            else:
                # 携带状态码和错误信息抛出
                error_dict = await response.json()
                error_dict["code"] = response.status
                error_msg = (
                    f"玩家 '{params['player_name']}' 未找到或游戏代号错误\n"
                    f"• 确认ID: {params['player_name']}\n"
                    f"• 游戏代号: {game}\n"
                    f"• 可用代号: {', '.join(SUPPORTED_GAMES)}"
                    f"• 原始错误: {error_dict}"
                )
                logger.error(f"Battlefield Tool 调用接口失败，错误信息{error_dict}")
                return error_msg
    except aiohttp.ClientError as e:
        error_msg = f"网络请求异常: {str(e)}"
        logger.error(error_msg)
        raise ConnectionError(error_msg) from e
    except json.JSONDecodeError as e:
        error_msg = f"JSON解析失败: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except asyncio.TimeoutError as e:
        error_msg = f"请求超时: {timeout}秒内未收到响应"
        logger.error(error_msg)
        raise TimeoutError(error_msg) from e
    finally:
        if should_close and session is not None:
            await session.close()


async def fetch_image(url: str, timeout: int = 15, session: Optional[aiohttp.ClientSession] = None) -> Optional[bytes]:
    """
    异步获取图片
    Args:
        url: 图片的URL
        timeout: 超时时间(秒)
        session: 可选的aiohttp.ClientSession实例
    Returns:
        图片的二进制内容，如果失败则返回None
    Raises:
        aiohttp.ClientError: 网络或HTTP错误
        asyncio.TimeoutError: 请求超时
    """
    should_close = session is None
    if should_close:
        session = aiohttp.ClientSession()

    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with session.get(url, timeout=timeout_obj) as response:
            if response.status == 200:
                return await response.read()
            else:
                logger.error(f"Battlefield Tool Failed to fetch image from {url}, status: {response.status}")
                return None
    except aiohttp.ClientError as e:
        logger.error(f"Battlefield Tool Network request error while fetching image from {url}: {str(e)}")
        return None
    except asyncio.TimeoutError:
        logger.error(f"Battlefield Tool Request timeout while fetching image from {url} after {timeout} seconds")
        return None
    finally:
        if should_close and session is not None:
            await session.close()



async def btr_request_api(prop: str, params: Optional[dict] = None, timeout: int = 15,ssc_token= "", session: Optional[aiohttp.ClientSession] = None):
    """
    异步请求BTR API
        Args:
        prop: 请求属性
        params: 查询参数
        timeout: 超时时间(秒)
        session: 可选的aiohttp.ClientSession实例
        headers: 可选的请求头字典
    Returns:
        JSON响应数据
    Raises:
        aiohttp.ClientError: 网络或HTTP错误
        json.JSONDecodeError: 响应不是合法JSON
    """
    if params is None:
        params = {}
    if ssc_token == "":
        headers={}
    else:
        headers = {"X-API-Key":ssc_token}
    url = BTR_API_SITE + prop
    has_token = "是" if ssc_token else "否"

    #下面几行是shi山
    if params.get("player_name") is None and params.get("pider") is None:
        raise ValueError("ea_name，或pider必填")
    if params.get("player_name") is None:
        params["player_name"] = ""
    if params.get("pider") is None:
        params["pider"] = ""

    logger.info(f"Battlefield Tool Request API: {url}，请求参数: {params}, 是否有ssc_token: {has_token}")

    should_close = session is None
    if should_close:
        session = aiohttp.ClientSession()

    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with session.get(url, params=params, timeout=timeout_obj, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return result
            else:
                error_dict = await response.json()
                error_msg = (
                    f"Battlefield Tool 调用接口失败，状态码: {response.status}, 错误信息: {error_dict}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
    except aiohttp.ClientError as e:
        error_msg = f"API网络请求异常: {str(e)}"
        logger.error(error_msg)
        raise ConnectionError(error_msg) from e
    except json.JSONDecodeError as e:
        error_msg = f"API JSON解析失败: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except asyncio.TimeoutError as e:
        error_msg = f"API请求超时: {timeout}秒内未收到响应"
        logger.error(error_msg)
        raise TimeoutError(error_msg) from e
    finally:
        if should_close and session is not None:
            await session.close()
