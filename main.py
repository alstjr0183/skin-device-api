from config import settings
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from services.crawling import background_crawling_task, clear_cache
from services.scheduler import keep_alive
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    # 크롤링을 백그라운드 태스크로 실행하여 서버 부팅을 막지 않음
    task = asyncio.create_task(background_crawling_task())
    
    # 스케줄러 설정 및 시작
    scheduler = AsyncIOScheduler()
    scheduler.add_job(keep_alive, "interval", minutes=14)
    scheduler.start()
    
    yield
    
    # 종료 시 실행 (필요한 경우)
    task.cancel() # 혹은 await task
    scheduler.shutdown()
    clear_cache()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Hello, Skin API is running!"}
