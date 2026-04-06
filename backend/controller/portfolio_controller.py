from fastapi import APIRouter
from models import PortfolioItem
from service import portfolio_service as service

router = APIRouter(prefix="/api/portfolio")


@router.get("")
def get_portfolio():
    return service.get_all()


@router.post("", status_code=201)
def add_portfolio(item: PortfolioItem):
    return service.add(item)


@router.delete("/{ticker}")
def delete_portfolio(ticker: str):
    return service.delete(ticker)
