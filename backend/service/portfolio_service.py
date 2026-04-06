import sqlite3
from fastapi import HTTPException
from models import PortfolioItem
from repository import portfolio_repository as repo


def get_all() -> list:
    return repo.get_all()


def add(item: PortfolioItem) -> dict:
    try:
        repo.add(item.ticker.upper(), item.buy_price)
        return {"message": f"{item.ticker.upper()} 추가 완료"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="이미 존재하는 티커입니다.")


def delete(ticker: str) -> dict:
    rowcount = repo.delete(ticker.upper())
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="티커를 찾을 수 없습니다.")
    return {"message": f"{ticker.upper()} 삭제 완료"}
