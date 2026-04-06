import sqlite3
from database import get_connection


def get_all() -> list:
    con = get_connection()
    rows = con.execute("SELECT id, ticker, buy_price FROM portfolio").fetchall()
    con.close()
    return [{"id": r[0], "ticker": r[1], "buy_price": r[2]} for r in rows]


def add(ticker: str, buy_price: float | None):
    con = get_connection()
    con.execute(
        "INSERT INTO portfolio (ticker, buy_price) VALUES (?, ?)",
        (ticker, buy_price),
    )
    con.commit()
    con.close()


def delete(ticker: str) -> int:
    con = get_connection()
    cur = con.execute("DELETE FROM portfolio WHERE ticker = ?", (ticker,))
    con.commit()
    con.close()
    return cur.rowcount


def get_tickers() -> list:
    con = get_connection()
    tickers = [row[0] for row in con.execute("SELECT ticker FROM portfolio").fetchall()]
    con.close()
    return tickers
