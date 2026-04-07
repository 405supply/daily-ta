from fastapi import APIRouter
from service import price_service

router = APIRouter(prefix="/api")


@router.get("/prices")
def get_prices():
    return price_service.get_prices()
