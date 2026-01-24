import httpx
import logging
from config import settings

# 로깅 설정
logger = logging.getLogger(__name__)

async def keep_alive():
    """14분마다 자기 자신의 루트 경로를 호출하여 깨어있게 함"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.APP_BASE_URL}/")
            if response.status_code == 200:
                logger.info("Keep-alive ping successful")
            else:
                logger.warning(f"Keep-alive ping failed with status: {response.status_code}")
    except Exception as e:
        logger.error(f"Keep-alive ping error: {e}")
