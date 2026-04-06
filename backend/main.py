from dotenv import load_dotenv
load_dotenv()

import certifi
import os
os.environ["CURL_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from database import init_db
from service.analysis_service import scheduled_analysis
from controller import portfolio_controller, analysis_controller, stock_controller

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio_controller.router)
app.include_router(analysis_controller.router)
app.include_router(stock_controller.router)

init_db()

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_analysis, "cron", hour=9, minute=0)
scheduler.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
