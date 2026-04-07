from dotenv import load_dotenv
load_dotenv()

import certifi
import os
os.environ["CURL_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from database import init_db
from service.analysis_service import scheduled_analysis
from service.price_service import refresh_prices
from controller import portfolio_controller, analysis_controller, stock_controller, price_controller


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_analysis, "cron", hour=9, minute=0)
    scheduler.add_job(refresh_prices, "interval", minutes=1)
    scheduler.start()
    asyncio.get_running_loop().run_in_executor(None, refresh_prices)  # non-blocking 초기 가격 로드
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio_controller.router)
app.include_router(analysis_controller.router)
app.include_router(stock_controller.router)
app.include_router(price_controller.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
