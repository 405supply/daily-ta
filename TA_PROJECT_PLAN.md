# 📈 TA 분석 웹사이트 프로젝트 계획서

## 프로젝트 개요

**목표**: 보유 종목의 기술적 분석(TA)을 자동으로 수행하고, 일일 매매 신호를 제공하는 웹 애플리케이션 개발

**목적**:
- 개발 공부 (풀스택: FastAPI + Vue.js)
- 시장 관찰 및 투자 감각 향상
- 객관적인 TA 신호로 감정적 거래 제어
- **투자 수익 기대는 NO** (TA는 정확도 50-60% 수준)

---

## 기술 스택

### 백엔드
- **프레임워크**: FastAPI (Python)
- **이유**: 비동기 처리, 자동 문서화, 타입 안정성

### 프론트엔드
- **프레임워크**: Vue.js 3
- **기능**: 포트폴리오 관리, TA 결과 시각화

### 데이터 소스
- **주가 데이터**: yfinance (무료, 무제한)
- **기술적 지표**: ta 라이브러리 (RSI, MACD, 이동평균선 등)
- **LLM**: Gemini API 무료 플랜
  - 월 60개 요청 한도
  - 한국어 지원 우수
  - 역할: 지표 해석 및 매매 신호 생성

### 데이터베이스
- **SQLite** (로컬 개발용)
- 테이블:
  - `portfolio`: 보유 종목 정보
  - `analysis`: 분석 결과 및 기록

### 자동화
- **APScheduler**: 매일 정해진 시간(9시)에 분석 자동 실행

### 호스팅
- **현재**: 로컬 PC (24/7 실행 필요)
- **추후**: Railway ($5/월 크레딧) 또는 Render (무료)

---

## 시스템 아키텍처

```
┌─ 로컬 PC (항상 켜져있음)
│
├─ FastAPI 백엔드 (포트 8000)
│  ├─ /api/portfolio (GET/POST) → 포트폴리오 관리
│  ├─ /api/analyze/{ticker} (GET) → 단일 종목 분석
│  ├─ /api/analyze-all (GET) → 전체 포트폴리오 분석
│  ├─ /api/history/{ticker} (GET) → 분석 기록 조회
│  └─ SQLite DB (ta_analysis.db)
│
├─ Vue.js 프론트엔드 (포트 5173)
│  ├─ 포트폴리오 입력 폼
│  ├─ TA 분석 결과 카드
│  └─ 분석 기록 그래프
│
└─ 자동 스케줄러
   └─ 매일 9시 분석 실행 (APScheduler)

요청 흐름:
yfinance (주가) → FastAPI (지표 계산) → Gemini (해석) → Vue (표시)
```

---

## 주요 기능 (MVP)

### 1단계: 기본 기능
- [x] 포트폴리오 종목 추가/조회
- [x] 각 종목 TA 분석 (RSI, MACD, 이동평균선)
- [x] Gemini API로 매매 신호 생성
- [x] 분석 결과 웹페이지 표시
- [x] 분석 기록 DB 저장

### 2단계: 고도화 (선택)
- [ ] 일일 자동 분석 및 이메일 알림
- [ ] 분석 기록 차트 시각화
- [ ] 백테스팅 (과거 신호 정확도 검증)
- [ ] 여러 TA 전략 조합

---

## 기술적 지표 정보

### 계산 방식
- **RSI(14)**: 과매수(70 초과)/과매도(30 미만) 판단
- **MACD**: 추세 변화 신호
- **이동평균선(20/50)**: 지지/저항선, 추세 방향

### LLM 역할
- 지표 수치를 받아서 "해석만" 수행
- 예: "RSI 72 → 과매수, 손절 고려"
- 미래 예측은 하지 않음 (정확도 없음)

### 기대 정확도
- Gemini 무료: 55-60%
- 사람 트레이더: 65-70%
- **결론**: TA는 주술사 수준 (정확도 낮음)

---

## 데이터 흐름 (상세)

### 단일 종목 분석 프로세스
```
1. 사용자: 종목코드 입력 (예: 005930.KS)
2. FastAPI:
   - yfinance로 3개월 주가 데이터 다운로드
   - ta 라이브러리로 지표 계산 (RSI, MACD, SMA 등)
3. Gemini API:
   - 지표 수치 + 현재가 → 프롬프트 생성
   - "매수/중립/매도" + 이유 반환
4. SQLite:
   - 분석 결과 저장 (ticker, date, rsi, macd, signal)
5. Vue:
   - 결과를 카드 형식으로 표시

응답 시간: ~3-5초 (Gemini API 호출 포함)
```

### 자동 스케줄 프로세스
```
매일 09:00 (APScheduler)
  ↓
포트폴리오의 모든 종목 조회
  ↓
각 종목마다 위의 "단일 분석" 프로세스 반복
  ↓
모든 결과를 DB에 저장
  ↓
(선택) 이메일 발송 또는 알림
```

---

## Gemini API 설정

### 무료 플랜 한도
- 월 60개 요청
- 분당 15개 요청 (RPM)
- 평가 계산: 22 영업일 ÷ 60 = **일일 2-3종목 분석 가능**

### 종목이 많으면?
**옵션 1**: Ollama 로컬 LLM 추가 (무제한, 응답 느림)
**옵션 2**: Gemini Pro 유료 전환 ($5-10/월)
**옵션 3**: 로컬 PC에서만 사용 (현재 계획)

---

## 프로젝트 구조 (계획)

```
ta-analyzer/
├── backend/
│   ├── main.py              # FastAPI 앱 시작점
│   ├── api/
│   │   ├── portfolio.py      # 포트폴리오 엔드포인트
│   │   ├── analysis.py       # 분석 엔드포인트
│   │   └── history.py        # 기록 엔드포인트
│   ├── services/
│   │   ├── stock_analyzer.py # TA 분석 로직
│   │   ├── gemini_service.py # Gemini API 호출
│   │   └── scheduler.py      # 자동 스케줄
│   ├── models/
│   │   └── database.py       # SQLite 모델
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Portfolio.vue
│   │   │   ├── AnalysisCard.vue
│   │   │   └── History.vue
│   │   └── App.vue
│   └── package.json
│
└── ta_analysis.db            # SQLite DB (자동 생성)
```

---

## 환경 설정 (사전 요구사항)

### Python
- Python 3.8+
- pip 패키지 매니저

### Node.js
- Node.js 14+
- npm 또는 yarn

### API 키
- **Gemini API 키** (무료 가입 필요)
  - https://ai.google.dev/

---

## 설치 및 실행 (예상 흐름)

### 1. 저장소 생성
```bash
mkdir ta-analyzer
cd ta-analyzer
git init
```

### 2. 백엔드 설정
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn yfinance ta requests apscheduler google-generativeai
```

### 3. 프론트엔드 설정
```bash
cd frontend
npm create vite@latest . -- --template vue
npm install
```

### 4. 환경 변수 설정
```bash
# backend/.env
GEMINI_API_KEY=your_api_key_here
```

### 5. 실행 (2개 터미널)
```bash
# 터미널 1: 백엔드
cd backend
python main.py

# 터미널 2: 프론트엔드
cd frontend
npm run dev
```

### 6. 접속
- 프론트엔드: http://localhost:5173
- API 문서: http://localhost:8000/docs

---

## 현재 상태

- ✅ 기술 스택 결정
- ✅ 아키텍처 설계
- ✅ 기능 정의
- ❌ 코드 작성 (다음 단계)
- ❌ 배포 (추후)

---

## 주의사항

### 투자 관련
1. **이 시스템은 자동 매매 도구가 아닙니다**
   - 참고 정보일 뿐, 최종 판단은 본인이
2. **TA 정확도는 50-60% 수준**
   - 무작위 매매와 비슷한 수준
   - 큰 수익을 기대하면 안 됨
3. **투자는 본인 책임**
   - 손실 가능성 항상 있음

### 기술 관련
1. **Gemini 월 60개 요청 제한**
   - 종목 많으면 Ollama 추가 고려
2. **로컬 PC 24/7 켜야 함**
   - 자동 스케줄 실행을 위해
3. **인터넷 연결 필수**
   - yfinance, Gemini API 호출용

---

## 참고자료

### 라이브러리 공식 문서
- FastAPI: https://fastapi.tiangolo.com/
- Vue.js: https://vuejs.org/
- yfinance: https://github.com/ranaroussi/yfinance
- ta: https://github.com/bukosabino/ta
- Gemini API: https://ai.google.dev/

### TA 개념 학습
- RSI: https://ko.wikipedia.org/wiki/상대강도지수
- MACD: https://ko.wikipedia.org/wiki/MACD
- 이동평균선: https://ko.wikipedia.org/wiki/이동평균

---

## 연락 및 피드백

- 개발 중 막히는 부분 있으면 물어보기
- 기능 추가/변경 필요하면 말하기
- 버그 발생하면 보고하기

---

**마지막 확인:**
- [x] 기술 스택 동의 (FastAPI, Vue.js, Gemini, yfinance)
- [x] 호스팅은 로컬 (추후 Railway)
- [x] 투자 수익 기대 NO (개발 + 공부 목표)
- [x] 계획 완성

**다음: 터미널에서 코드 작성 시작!** 🚀
