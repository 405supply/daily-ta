from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import yfinance as yf
import ta
import pandas as pd
import google.generativeai as genai
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL 설치 시 CURL_CA_BUNDLE이 잘못 설정되는 문제 수정
import certifi
os.environ["CURL_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

DB_PATH = "ta.db"

# --- Static stock lists ---

NASDAQ_100 = [
    {"ticker": "AAPL",  "name": "Apple"},
    {"ticker": "MSFT",  "name": "Microsoft"},
    {"ticker": "NVDA",  "name": "NVIDIA"},
    {"ticker": "AMZN",  "name": "Amazon"},
    {"ticker": "META",  "name": "Meta Platforms"},
    {"ticker": "GOOGL", "name": "Alphabet A"},
    {"ticker": "GOOG",  "name": "Alphabet C"},
    {"ticker": "TSLA",  "name": "Tesla"},
    {"ticker": "AVGO",  "name": "Broadcom"},
    {"ticker": "COST",  "name": "Costco"},
    {"ticker": "NFLX",  "name": "Netflix"},
    {"ticker": "ASML",  "name": "ASML"},
    {"ticker": "AMD",   "name": "Advanced Micro Devices"},
    {"ticker": "QCOM",  "name": "Qualcomm"},
    {"ticker": "INTU",  "name": "Intuit"},
    {"ticker": "TXN",   "name": "Texas Instruments"},
    {"ticker": "CMCSA", "name": "Comcast"},
    {"ticker": "AMGN",  "name": "Amgen"},
    {"ticker": "ISRG",  "name": "Intuitive Surgical"},
    {"ticker": "HON",   "name": "Honeywell"},
    {"ticker": "BKNG",  "name": "Booking Holdings"},
    {"ticker": "VRTX",  "name": "Vertex Pharmaceuticals"},
    {"ticker": "REGN",  "name": "Regeneron"},
    {"ticker": "MU",    "name": "Micron Technology"},
    {"ticker": "ADI",   "name": "Analog Devices"},
    {"ticker": "PANW",  "name": "Palo Alto Networks"},
    {"ticker": "GILD",  "name": "Gilead Sciences"},
    {"ticker": "LRCX",  "name": "Lam Research"},
    {"ticker": "KLAC",  "name": "KLA Corporation"},
    {"ticker": "MELI",  "name": "MercadoLibre"},
    {"ticker": "CTAS",  "name": "Cintas"},
    {"ticker": "CRWD",  "name": "CrowdStrike"},
    {"ticker": "MDLZ",  "name": "Mondelez"},
    {"ticker": "SNPS",  "name": "Synopsys"},
    {"ticker": "CDNS",  "name": "Cadence Design"},
    {"ticker": "CSX",   "name": "CSX Corporation"},
    {"ticker": "ORLY",  "name": "O'Reilly Automotive"},
    {"ticker": "ADSK",  "name": "Autodesk"},
    {"ticker": "FTNT",  "name": "Fortinet"},
    {"ticker": "PCAR",  "name": "PACCAR"},
    {"ticker": "ABNB",  "name": "Airbnb"},
    {"ticker": "TEAM",  "name": "Atlassian"},
    {"ticker": "MCHP",  "name": "Microchip Technology"},
    {"ticker": "AEP",   "name": "American Electric Power"},
    {"ticker": "WDAY",  "name": "Workday"},
    {"ticker": "ROP",   "name": "Roper Technologies"},
    {"ticker": "NXPI",  "name": "NXP Semiconductors"},
    {"ticker": "IDXX",  "name": "IDEXX Laboratories"},
    {"ticker": "CPRT",  "name": "Copart"},
    {"ticker": "ROST",  "name": "Ross Stores"},
    {"ticker": "MNST",  "name": "Monster Beverage"},
    {"ticker": "KHC",   "name": "Kraft Heinz"},
    {"ticker": "PAYX",  "name": "Paychex"},
    {"ticker": "ODFL",  "name": "Old Dominion Freight"},
    {"ticker": "FAST",  "name": "Fastenal"},
    {"ticker": "VRSK",  "name": "Verisk Analytics"},
    {"ticker": "CTSH",  "name": "Cognizant"},
    {"ticker": "ON",    "name": "ON Semiconductor"},
    {"ticker": "EA",    "name": "Electronic Arts"},
    {"ticker": "DDOG",  "name": "Datadog"},
    {"ticker": "ZS",    "name": "Zscaler"},
    {"ticker": "ANSS",  "name": "Ansys"},
    {"ticker": "BIIB",  "name": "Biogen"},
    {"ticker": "ILMN",  "name": "Illumina"},
    {"ticker": "DXCM",  "name": "DexCom"},
    {"ticker": "EBAY",  "name": "eBay"},
    {"ticker": "TTD",   "name": "The Trade Desk"},
    {"ticker": "CEG",   "name": "Constellation Energy"},
    {"ticker": "EXC",   "name": "Exelon"},
    {"ticker": "XEL",   "name": "Xcel Energy"},
    {"ticker": "GEHC",  "name": "GE HealthCare"},
    {"ticker": "FANG",  "name": "Diamondback Energy"},
    {"ticker": "BKR",   "name": "Baker Hughes"},
    {"ticker": "DLTR",  "name": "Dollar Tree"},
    {"ticker": "ZM",    "name": "Zoom"},
    {"ticker": "MTCH",  "name": "Match Group"},
    {"ticker": "RIVN",  "name": "Rivian"},
    {"ticker": "LCID",  "name": "Lucid Group"},
    {"ticker": "WBD",   "name": "Warner Bros. Discovery"},
    {"ticker": "SIRI",  "name": "Sirius XM"},
]

KOSPI_100 = [
    {"ticker": "005930.KS", "name": "삼성전자"},
    {"ticker": "000660.KS", "name": "SK하이닉스"},
    {"ticker": "207940.KS", "name": "삼성바이오로직스"},
    {"ticker": "005380.KS", "name": "현대차"},
    {"ticker": "000270.KS", "name": "기아"},
    {"ticker": "068270.KS", "name": "셀트리온"},
    {"ticker": "035420.KS", "name": "NAVER"},
    {"ticker": "051910.KS", "name": "LG화학"},
    {"ticker": "006400.KS", "name": "삼성SDI"},
    {"ticker": "028260.KS", "name": "삼성물산"},
    {"ticker": "012330.KS", "name": "현대모비스"},
    {"ticker": "066570.KS", "name": "LG전자"},
    {"ticker": "003550.KS", "name": "LG"},
    {"ticker": "032830.KS", "name": "삼성생명"},
    {"ticker": "017670.KS", "name": "SK텔레콤"},
    {"ticker": "030200.KS", "name": "KT"},
    {"ticker": "086790.KS", "name": "하나금융지주"},
    {"ticker": "105560.KS", "name": "KB금융"},
    {"ticker": "055550.KS", "name": "신한지주"},
    {"ticker": "034730.KS", "name": "SK"},
    {"ticker": "005490.KS", "name": "POSCO홀딩스"},
    {"ticker": "003670.KS", "name": "포스코퓨처엠"},
    {"ticker": "009150.KS", "name": "삼성전기"},
    {"ticker": "018260.KS", "name": "삼성에스디에스"},
    {"ticker": "096770.KS", "name": "SK이노베이션"},
    {"ticker": "011200.KS", "name": "HMM"},
    {"ticker": "010130.KS", "name": "고려아연"},
    {"ticker": "000810.KS", "name": "삼성화재"},
    {"ticker": "047050.KS", "name": "포스코인터내셔널"},
    {"ticker": "009830.KS", "name": "한화솔루션"},
    {"ticker": "010950.KS", "name": "S-Oil"},
    {"ticker": "024110.KS", "name": "기업은행"},
    {"ticker": "000100.KS", "name": "유한양행"},
    {"ticker": "035720.KS", "name": "카카오"},
    {"ticker": "352820.KS", "name": "하이브"},
    {"ticker": "036570.KS", "name": "엔씨소프트"},
    {"ticker": "251270.KS", "name": "넷마블"},
    {"ticker": "006800.KS", "name": "미래에셋증권"},
    {"ticker": "032640.KS", "name": "LG유플러스"},
    {"ticker": "011070.KS", "name": "LG이노텍"},
    {"ticker": "161390.KS", "name": "한국타이어앤테크놀로지"},
    {"ticker": "051900.KS", "name": "LG생활건강"},
    {"ticker": "090430.KS", "name": "아모레퍼시픽"},
    {"ticker": "011170.KS", "name": "롯데케미칼"},
    {"ticker": "004020.KS", "name": "현대제철"},
    {"ticker": "000720.KS", "name": "현대건설"},
    {"ticker": "010140.KS", "name": "삼성중공업"},
    {"ticker": "042660.KS", "name": "한화오션"},
    {"ticker": "329180.KS", "name": "HD현대중공업"},
    {"ticker": "267250.KS", "name": "HD현대"},
    {"ticker": "078930.KS", "name": "GS"},
    {"ticker": "071050.KS", "name": "한국금융지주"},
    {"ticker": "015760.KS", "name": "한국전력"},
    {"ticker": "000830.KS", "name": "삼성C&T"},
    {"ticker": "316140.KS", "name": "우리금융지주"},
    {"ticker": "003490.KS", "name": "대한항공"},
    {"ticker": "020150.KS", "name": "롯데에너지머티리얼즈"},
    {"ticker": "034020.KS", "name": "두산에너빌리티"},
    {"ticker": "064350.KS", "name": "현대로템"},
    {"ticker": "012450.KS", "name": "한화에어로스페이스"},
]


# --- DB ---

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT UNIQUE NOT NULL,
            quantity INTEGER NOT NULL,
            buy_price REAL NOT NULL
        )
    """)
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


class PortfolioItem(BaseModel):
    ticker: str
    quantity: int
    buy_price: float


def analyze_stock(ticker: str) -> dict:
    df = yf.download(ticker, period="3mo", auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"No data for {ticker}")

    close = df["Close"].squeeze()

    rsi_val = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    macd_obj = ta.trend.MACD(close)
    macd_val = macd_obj.macd().iloc[-1]
    macd_signal_val = macd_obj.macd_signal().iloc[-1]
    sma20 = ta.trend.SMAIndicator(close, window=20).sma_indicator().iloc[-1]
    current_price = close.iloc[-1]

    prompt = (
        f"종목: {ticker}\n"
        f"현재가: {current_price:.2f}\n"
        f"RSI(14): {rsi_val:.2f}\n"
        f"MACD: {macd_val:.4f}, Signal: {macd_signal_val:.4f}\n"
        f"SMA20: {sma20:.2f}\n\n"
        "위 기술적 지표를 바탕으로 매수/매도/관망 중 하나의 신호와 간단한 이유를 한국어로 답해줘. "
        "형식: [신호] 이유"
    )

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        print(f"[Gemini] {ticker} 요청 시작")
        response = model.generate_content(prompt)
        signal = response.text.strip()
        print(f"[Gemini] {ticker} 응답 완료: {signal[:80]}")
    except Exception as e:
        print(f"[Gemini] {ticker} 오류: {type(e).__name__}: {e}")
        signal = "API 오류 - 지표만 참고"

    result = {
        "ticker": ticker,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "rsi": round(float(rsi_val), 2),
        "macd": round(float(macd_val), 4),
        "signal": signal,
    }

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO analysis (ticker, date, rsi, macd, signal) VALUES (?, ?, ?, ?, ?)",
        (result["ticker"], result["date"], result["rsi"], result["macd"], result["signal"]),
    )
    con.commit()
    con.close()

    return result


def scheduled_analysis():
    con = sqlite3.connect(DB_PATH)
    tickers = [row[0] for row in con.execute("SELECT ticker FROM portfolio").fetchall()]
    con.close()
    for ticker in tickers:
        try:
            analyze_stock(ticker)
        except Exception as e:
            print(f"[Scheduler] {ticker} 분석 실패: {e}")


# --- Stock list endpoints ---

@app.get("/api/stocks/nasdaq100")
def get_nasdaq100():
    return NASDAQ_100

@app.get("/api/stocks/kospi100")
def get_kospi100():
    return KOSPI_100


# --- Dashboard endpoint ---

@app.get("/api/dashboard")
def get_dashboard():
    con = sqlite3.connect(DB_PATH)
    rows = con.execute("""
        SELECT p.id, p.ticker, p.quantity, p.buy_price,
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
            "id": r[0], "ticker": r[1], "quantity": r[2], "buy_price": r[3],
            "rsi": r[4], "macd": r[5], "signal": r[6], "analysis_date": r[7],
        }
        for r in rows
    ]


# --- Portfolio endpoints ---

@app.get("/api/portfolio")
def get_portfolio():
    con = sqlite3.connect(DB_PATH)
    rows = con.execute("SELECT id, ticker, quantity, buy_price FROM portfolio").fetchall()
    con.close()
    return [{"id": r[0], "ticker": r[1], "quantity": r[2], "buy_price": r[3]} for r in rows]


@app.post("/api/portfolio", status_code=201)
def add_portfolio(item: PortfolioItem):
    try:
        con = sqlite3.connect(DB_PATH)
        con.execute(
            "INSERT INTO portfolio (ticker, quantity, buy_price) VALUES (?, ?, ?)",
            (item.ticker.upper(), item.quantity, item.buy_price),
        )
        con.commit()
        con.close()
        return {"message": f"{item.ticker.upper()} 추가 완료"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="이미 존재하는 티커입니다.")


@app.delete("/api/portfolio/{ticker}")
def delete_portfolio(ticker: str):
    con = sqlite3.connect(DB_PATH)
    cur = con.execute("DELETE FROM portfolio WHERE ticker = ?", (ticker.upper(),))
    con.commit()
    con.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="티커를 찾을 수 없습니다.")
    return {"message": f"{ticker.upper()} 삭제 완료"}


# --- Analysis endpoints ---

@app.get("/api/analyze/{ticker}")
def analyze_single(ticker: str):
    try:
        return analyze_stock(ticker.upper())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analyze-all")
def analyze_all():
    con = sqlite3.connect(DB_PATH)
    tickers = [row[0] for row in con.execute("SELECT ticker FROM portfolio").fetchall()]
    con.close()
    results, errors = [], []
    for ticker in tickers:
        try:
            results.append(analyze_stock(ticker))
        except Exception as e:
            errors.append({"ticker": ticker, "error": str(e)})
    return {"results": results, "errors": errors}


@app.get("/api/history/{ticker}")
def get_history(ticker: str):
    con = sqlite3.connect(DB_PATH)
    rows = con.execute(
        "SELECT id, ticker, date, rsi, macd, signal FROM analysis WHERE ticker = ? ORDER BY date DESC LIMIT 30",
        (ticker.upper(),),
    ).fetchall()
    con.close()
    return [{"id": r[0], "ticker": r[1], "date": r[2], "rsi": r[3], "macd": r[4], "signal": r[5]} for r in rows]


# --- Startup ---

init_db()

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_analysis, "cron", hour=9, minute=0)
scheduler.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
