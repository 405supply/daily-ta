from typing import Optional
from pydantic import BaseModel


class PortfolioItem(BaseModel):
    ticker: str
    buy_price: Optional[float] = None
