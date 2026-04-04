# TA Analyzer Project

## Project Summary
TA (기술적 분석) 자동화 웹 애플리케이션
- 보유 종목 기술적 분석
- 일일 매매 신호 제공
- 분석 기록 저장

## Tech Stack
- Backend: FastAPI (Python)
- Frontend: Vue.js 3
- Data: yfinance (주가), ta (지표), Gemini API (LLM)
- Database: SQLite
- Scheduling: APScheduler (매일 9시 자동 실행)
- Hosting: Local PC (추후 Railway)

## System Architecture
```
FastAPI (8000) ← yfinance, ta, Gemini API → SQLite
         ↑
     Vue.js (5173)
```

## Database Schema
### portfolio
- id: INTEGER PRIMARY KEY
- ticker: TEXT
- quantity: INTEGER
- buy_price: REAL

### analysis
- id: INTEGER PRIMARY KEY
- ticker: TEXT
- date: TEXT (ISO format)
- rsi: REAL
- macd: REAL
- signal: TEXT

## API Endpoints
GET /api/portfolio - 포트폴리오 조회
POST /api/portfolio - 종목 추가
GET /api/analyze/{ticker} - 단일 종목 분석
GET /api/analyze-all - 전체 포트폴리오 분석
GET /api/history/{ticker} - 분석 기록 조회

## Key Functions
1. analyze_stock(ticker)
   - yfinance로 3개월 주가 데이터 조회
   - ta로 RSI, MACD, SMA 계산
   - Gemini API로 매매 신호 생성
   - SQLite에 결과 저장

2. scheduled_analysis()
   - APScheduler로 매일 9시 실행
   - portfolio의 모든 종목 자동 분석

## Requirements
- Python 3.8+
- Node.js 14+
- GEMINI_API_KEY environment variable

## Install Commands
Backend:
pip install fastapi uvicorn yfinance ta requests apscheduler google-generativeai

Frontend:
npm create vite@latest . -- --template vue
npm install

## Run Commands
Backend: python main.py (localhost:8000)
Frontend: npm run dev (localhost:5173)
API Docs: http://localhost:8000/docs

## Important Notes
- TA 정확도: 50-60% (참고 정보일 뿐)
- Gemini 무료: 월 60개 요청 한도
- 로컬 PC 24/7 켜야 자동 스케줄 실행
- 투자 손실 책임은 본인
