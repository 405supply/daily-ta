import yfinance as yf
from datetime import datetime
from repository import portfolio_repository

_cache: dict = {}  # {ticker: {price, change_pct, pl_pct, updated_at}}


def get_prices() -> dict:
    return _cache


def refresh_prices():
    tickers = portfolio_repository.get_tickers()
    if not tickers:
        _cache.clear()
        return

    for ticker in tickers:
        try:
            hist = yf.Ticker(ticker).history(period="2d", interval="1m")
            if hist.empty:
                continue

            dates = hist.index.date
            today = dates[-1]
            today_df = hist[dates == today]
            prev_df = hist[dates < today]

            current = float(today_df["Close"].iloc[-1]) if not today_df.empty else None
            prev_close = float(prev_df["Close"].iloc[-1]) if not prev_df.empty else None

            change_pct = (
                round((current - prev_close) / prev_close * 100, 2)
                if current and prev_close
                else None
            )

            _cache[ticker] = {
                "price": round(current, 2) if current else None,
                "change_pct": change_pct,
                "updated_at": datetime.now().strftime("%H:%M"),
            }
        except Exception:
            pass
