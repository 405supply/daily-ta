import os
from pathlib import Path
import yfinance as yf
import ta
from datetime import datetime
from google import genai
from repository import portfolio_repository, analysis_repository

_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
_PROMPT_TEMPLATE = (Path(__file__).parent / "prompt.txt").read_text(encoding="utf-8")


def _ma_alignment(sma20: float, sma50: float, sma120: float) -> str:
    if sma20 > sma50 > sma120:
        return "정배열"
    elif sma20 < sma50 < sma120:
        return "역배열"
    else:
        return "혼조"


def _hist_state(hist: float, hist_prev: float) -> str:
    if hist > 0 and hist_prev <= 0:
        return "양전환"
    if hist < 0 and hist_prev >= 0:
        return "음전환"
    return f"{'양' if hist > 0 else '음'}수 유지"


def _build_prompt(ticker: str, indicators: dict) -> str:
    d = indicators
    data_section = f"""당신은 월스트리트에서 20년 이상의 경력을 가진 수석 기술적 분석가(Chief Technical Analyst)이자 리스크 관리에 철저한 퀀트 트레이더입니다.

제가 아래에 제공하는 특정 종목의 기술적 지표(Technical Indicators) 데이터를 바탕으로,
현재 시장 국면을 심층적으로 진단하고 단기 및 중장기 관점에서의 매우 구체적이고 실행 가능한 트레이딩 전략을 수립해 주십시오.

분석 기준 일자: {d['date']}

종목명/티커: {ticker}

타임프레임 (Timeframe): 1일봉(Daily) 기준

현재가 및 거래량 (Price & Volume): 현재가 {d['price']:.2f}, 금일 거래량 {d['volume']:,} (전일 대비 {'증가' if d['volume'] > d['volume_prev'] else '감소'})

이동평균선 (Moving Averages): 20일선 {d['sma20']:.2f} / 50일선 {d['sma50']:.2f} / 120일선 {d['sma120']:.2f} ({d['alignment']})

RSI (14일 기준): {d['rsi']:.2f}

MACD: MACD 라인 {d['macd']:.4f} / 시그널 라인 {d['macd_signal']:.4f} / 히스토그램 {d['macd_hist']:.4f} ({d['hist_state']})

볼린저 밴드 (20일, 2σ): 상단 {d['bb_upper']:.2f} / 중단 {d['bb_mid']:.2f} / 하단 {d['bb_lower']:.2f}

"""
    return data_section + _PROMPT_TEMPLATE


def analyze_stock(ticker: str) -> dict:
    df = yf.download(ticker, period="6mo", auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"No data for {ticker}")

    close = df["Close"].squeeze()
    volume = df["Volume"].squeeze()

    macd_obj = ta.trend.MACD(close)
    macd_hist = macd_obj.macd_diff()
    bb = ta.volatility.BollingerBands(close)

    indicators = {
        "date": datetime.now().strftime("%Y년 %m월 %d일"),
        "price": float(close.iloc[-1]),
        "volume": int(volume.iloc[-1]),
        "volume_prev": int(volume.iloc[-2]),
        "sma20": float(ta.trend.SMAIndicator(close, window=20).sma_indicator().iloc[-1]),
        "sma50": float(ta.trend.SMAIndicator(close, window=50).sma_indicator().iloc[-1]),
        "sma120": float(ta.trend.SMAIndicator(close, window=120).sma_indicator().iloc[-1]),
        "rsi": float(ta.momentum.RSIIndicator(close).rsi().iloc[-1]),
        "macd": float(macd_obj.macd().iloc[-1]),
        "macd_signal": float(macd_obj.macd_signal().iloc[-1]),
        "macd_hist": float(macd_hist.iloc[-1]),
        "bb_upper": float(bb.bollinger_hband().iloc[-1]),
        "bb_mid": float(bb.bollinger_mavg().iloc[-1]),
        "bb_lower": float(bb.bollinger_lband().iloc[-1]),
    }
    indicators["alignment"] = _ma_alignment(indicators["sma20"], indicators["sma50"], indicators["sma120"])
    indicators["hist_state"] = _hist_state(indicators["macd_hist"], float(macd_hist.iloc[-2]))

    try:
        print(f"[Gemini] {ticker} 요청 시작")
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=_build_prompt(ticker, indicators),
        )
        signal = response.text.strip() if response.text else ""
        if not signal:
            raise ValueError("Gemini 응답이 비어 있습니다.")
        print(f"[Gemini] {ticker} 응답 완료: {signal[:80]}")
    except Exception as e:
        print(f"[Gemini] {ticker} 오류: {type(e).__name__}: {e}")
        raise RuntimeError(f"Gemini API 오류: {e}") from e

    result = {
        "ticker": ticker,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "rsi": round(indicators["rsi"], 2),
        "macd": round(indicators["macd"], 4),
        "signal": signal,
    }

    analysis_repository.save(result)
    return result


def analyze_all() -> dict:
    tickers = portfolio_repository.get_tickers()
    results, errors = [], []
    for ticker in tickers:
        try:
            results.append(analyze_stock(ticker))
        except Exception as e:
            errors.append({"ticker": ticker, "error": str(e)})
    return {"results": results, "errors": errors}


def scheduled_analysis():
    tickers = portfolio_repository.get_tickers()
    for ticker in tickers:
        try:
            analyze_stock(ticker)
        except Exception as e:
            print(f"[Scheduler] {ticker} 분석 실패: {e}")
