import sqlite3

DB_PATH = "ta.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT UNIQUE NOT NULL,
            buy_price REAL
        )
    """)

    # 기존 DB에 quantity 컬럼이 있으면 새 스키마로 마이그레이션
    cols = [row[1] for row in cur.execute("PRAGMA table_info(portfolio)").fetchall()]
    if 'quantity' in cols:
        cur.execute("ALTER TABLE portfolio RENAME TO portfolio_old")
        cur.execute("""
            CREATE TABLE portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT UNIQUE NOT NULL,
                buy_price REAL
            )
        """)
        cur.execute("INSERT INTO portfolio (id, ticker, buy_price) SELECT id, ticker, buy_price FROM portfolio_old")
        cur.execute("DROP TABLE portfolio_old")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            rsi REAL,
            macd REAL,
            signal TEXT
        )
    """)

    con.commit()
    con.close()
