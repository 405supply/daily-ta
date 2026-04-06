from fastapi import APIRouter
from static_data import NASDAQ_100, KOSPI_100
from repository import analysis_repository

router = APIRouter(prefix="/api")


@router.get("/stocks/nasdaq100")
def get_nasdaq100():
    return NASDAQ_100


@router.get("/stocks/kospi100")
def get_kospi100():
    return KOSPI_100


@router.get("/dashboard")
def get_dashboard():
    return analysis_repository.get_dashboard_data()
