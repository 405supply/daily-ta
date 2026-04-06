from database import get_connection


def save(result: dict):
    con = get_connection()
    con.execute(
        "DELETE FROM analysis WHERE ticker = ? AND date = ?",
        (result["ticker"], result["date"]),
    )
    con.execute(
        "INSERT INTO analysis (ticker, date, rsi, macd, signal) VALUES (?, ?, ?, ?, ?)",
        (result["ticker"], result["date"], result["rsi"], result["macd"], result["signal"]),
    )
    con.commit()
    con.close()


def get_history(ticker: str, limit: int = 30) -> list:
    con = get_connection()
    rows = con.execute(
        "SELECT id, ticker, date, rsi, macd, signal FROM analysis WHERE ticker = ? ORDER BY date DESC LIMIT ?",
        (ticker, limit),
    ).fetchall()
    con.close()
    return [{"id": r[0], "ticker": r[1], "date": r[2], "rsi": r[3], "macd": r[4], "signal": r[5]} for r in rows]


def get_dashboard_data() -> list:
    con = get_connection()
    rows = con.execute("""
        SELECT p.id, p.ticker, p.buy_price,
               a.rsi, a.macd, a.signal, a.date
        FROM portfolio p
        LEFT JOIN (
            SELECT ticker, rsi, macd, signal, date,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY date DESC, id DESC) as rn
            FROM analysis
        ) a ON p.ticker = a.ticker AND a.rn = 1
    """).fetchall()
    con.close()
    return [
        {
            "id": r[0], "ticker": r[1], "buy_price": r[2],
            "rsi": r[3], "macd": r[4], "signal": r[5], "analysis_date": r[6],
        }
        for r in rows
    ]
