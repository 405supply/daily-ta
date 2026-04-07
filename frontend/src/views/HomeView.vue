<template>
  <div>
    <ConfirmDialog ref="confirmRef" />
    <div v-if="errorMsg" class="error-toast" @click="errorMsg = ''">{{ errorMsg }} ✕</div>
    <div class="toolbar">
      <h2>내 포트폴리오</h2>
      <div class="toolbar-actions">
        <button class="btn-refresh" @click="load" :disabled="loading">새로고침</button>
        <button class="btn-analyze-all" @click="analyzeAll" :disabled="analyzing">
          {{ analyzing ? '분석 중...' : '전체 분석' }}
        </button>
      </div>
    </div>

    <p v-if="loading" class="status">불러오는 중...</p>
    <p v-else-if="!items.length" class="status empty">
      등록된 종목이 없습니다.
      <RouterLink to="/manage">종목 관리</RouterLink>에서 추가해주세요.
    </p>

    <div class="cards" v-else>
      <div
        v-for="item in items"
        :key="item.ticker"
        class="card"
        :class="[signalClass(item.signal), { 'card-loading': analyzingTicker === item.ticker }]"
      >
        <div class="card-top">
          <div>
            <span class="ticker">{{ item.ticker }}</span>
            <span class="name" v-if="stockName(item.ticker)">{{ stockName(item.ticker) }}</span>
          </div>
          <span class="badge" :class="badgeClass(item.signal)">{{ badgeLabel(item.signal) }}</span>
        </div>

        <!-- 현재가 -->
        <div class="price-block" v-if="prices[item.ticker]">
          <div class="current-price-row">
            <span class="current-price">${{ prices[item.ticker].price?.toLocaleString() }}</span>
            <span
              class="change-pct"
              :class="prices[item.ticker].change_pct >= 0 ? 'pos' : 'neg'"
            >
              {{ prices[item.ticker].change_pct >= 0 ? '+' : '' }}{{ prices[item.ticker].change_pct }}%
            </span>
          </div>
          <div class="pl-row" v-if="item.buy_price !== null">
            <span class="label">매수가 ${{ item.buy_price.toLocaleString() }}</span>
            <span
              class="pl-pct"
              :class="plPct(item) >= 0 ? 'pos' : 'neg'"
            >
              {{ plPct(item) >= 0 ? '+' : '' }}{{ plPct(item) }}%
            </span>
          </div>
          <span class="price-time">{{ prices[item.ticker].updated_at }} 기준</span>
        </div>
        <div class="price-row" v-else-if="item.buy_price !== null">
          <span class="label">매수 평단</span>
          <span class="price">{{ item.buy_price.toLocaleString() }}</span>
        </div>

        <!-- 로딩 상태 -->
        <div v-if="analyzingTicker === item.ticker" class="analyzing-overlay">
          <div class="spinner"></div>
          <span>분석 중...</span>
        </div>

        <template v-else>
          <div class="indicators" v-if="item.rsi !== null">
            <div class="ind">
              <span class="label">RSI(14)</span>
              <span :class="rsiClass(item.rsi)">{{ item.rsi }}</span>
            </div>
            <div class="ind">
              <span class="label">MACD</span>
              <span :class="item.macd >= 0 ? 'pos' : 'neg'">{{ item.macd }}</span>
            </div>
            <div class="ind">
              <span class="label">분석일</span>
              <span>{{ item.analysis_date }}</span>
            </div>
          </div>
          <p v-else class="no-analysis">분석 기록 없음</p>

          <div v-if="item.signal" class="signal-preview" @click="openSignalModal(item)">
            <span class="signal-summary">{{ signalSummary(item.signal) }}</span>
            <span class="signal-more">전체 보기 →</span>
          </div>
        </template>

        <div class="card-actions">
          <button class="btn-analyze" @click="analyzeSingle(item.ticker)" :disabled="analyzingTicker === item.ticker">
            분석
          </button>
          <button class="btn-history" @click="openHistory(item.ticker)" :disabled="analyzingTicker === item.ticker">기록</button>
        </div>
      </div>
    </div>

    <!-- 분석 보고서 모달 -->
    <div class="modal-overlay" v-if="signalModal.open" @click.self="signalModal.open = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ signalModal.ticker }} 분석 보고서 <span class="modal-date">{{ signalModal.date }}</span></h3>
          <button @click="signalModal.open = false">✕</button>
        </div>
        <div class="signal-full">{{ signalModal.text }}</div>
      </div>
    </div>

    <!-- 분석 기록 모달 -->
    <div class="modal-overlay" v-if="historyTicker" @click.self="historyTicker = null">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ historyTicker }} 분석 기록</h3>
          <button @click="historyTicker = null">✕</button>
        </div>
        <p v-if="historyLoading" class="status">불러오는 중...</p>
        <p v-else-if="!historyRows.length" class="status">기록이 없습니다.</p>
        <table v-else class="history-table">
          <thead>
            <tr><th>날짜</th><th>RSI</th><th>MACD</th><th>의견</th></tr>
          </thead>
          <tbody>
            <tr v-for="row in historyRows" :key="row.id" class="history-row" @click="openSignalFromHistory(row)">
              <td>{{ row.date }}</td>
              <td :class="rsiClass(row.rsi)">{{ row.rsi }}</td>
              <td :class="row.macd >= 0 ? 'pos' : 'neg'">{{ row.macd }}</td>
              <td class="signal-cell">{{ signalOpinion(row.signal) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const API = import.meta.env.VITE_API_BASE

const confirmRef = ref(null)
const items = ref([])
const loading = ref(false)
const analyzing = ref(false)
const analyzingTicker = ref(null)

const errorMsg = ref('')

const historyTicker = ref(null)
const historyRows = ref([])
const historyLoading = ref(false)

const signalModal = reactive({ open: false, ticker: '', date: '', text: '' })

const prices = ref({})
let priceTimer = null

const nameMap = ref({})

async function fetchPrices() {
  const res = await fetch(`${API}/api/prices`)
  prices.value = await res.json()
}

function plPct(item) {
  const p = prices.value[item.ticker]
  if (!p?.price || !item.buy_price) return null
  return ((p.price - item.buy_price) / item.buy_price * 100).toFixed(2)
}

async function loadNameMap() {
  const [n, k] = await Promise.all([
    fetch(`${API}/api/stocks/nasdaq200`).then(r => r.json()),
    fetch(`${API}/api/stocks/kospi100`).then(r => r.json()),
  ])
  const map = {}
  ;[...n, ...k].forEach(s => { map[s.ticker] = s.name })
  nameMap.value = map
}

function stockName(ticker) {
  return nameMap.value[ticker] || ''
}

async function load() {
  loading.value = true
  const res = await fetch(`${API}/api/dashboard`)
  items.value = await res.json()
  loading.value = false
}

async function analyzeSingle(ticker) {
  const item = items.value.find(i => i.ticker === ticker)
  const today = new Date().toISOString().slice(0, 10)
  if (item?.analysis_date === today) {
    const ok = await confirmRef.value.open({
      icon: '📊',
      title: '이미 분석 완료',
      message: '오늘 이미 분석 완료한 종목입니다.\n다시 분석하시겠습니까?',
      confirmLabel: '다시 분석',
      cancelLabel: '취소',
      variant: 'warning',
    })
    if (!ok) return
  }
  analyzingTicker.value = ticker
  try {
    const res = await fetch(`${API}/api/analyze/${ticker}`)
    if (res.ok) await load()
    else errorMsg.value = `${ticker} 분석 실패 (${res.status})`
  } catch {
    errorMsg.value = `${ticker} 분석 중 오류가 발생했습니다`
  } finally {
    analyzingTicker.value = null
  }
}

async function analyzeAll() {
  analyzing.value = true
  try {
    await fetch(`${API}/api/analyze-all`)
    await load()
  } catch {
    errorMsg.value = '전체 분석 중 오류가 발생했습니다'
  } finally {
    analyzing.value = false
  }
}

async function openHistory(ticker) {
  historyTicker.value = ticker
  historyRows.value = []
  historyLoading.value = true
  const res = await fetch(`${API}/api/history/${ticker}`)
  historyRows.value = await res.json()
  historyLoading.value = false
}

function openSignalModal(item) {
  signalModal.ticker = item.ticker
  signalModal.date = item.analysis_date || ''
  signalModal.text = item.signal
  signalModal.open = true
}

function openSignalFromHistory(row) {
  signalModal.ticker = row.ticker
  signalModal.date = row.date
  signalModal.text = row.signal
  signalModal.open = true
}

// 첫 번째 비어있지 않은 줄 (투자 의견)
function signalOpinion(signal) {
  if (!signal) return '-'
  return signal.split('\n').find(l => l.trim()) || '-'
}

// 카드에 표시할 요약: 첫 줄 + 두 번째 줄
function signalSummary(signal) {
  if (!signal) return ''
  const lines = signal.split('\n').filter(l => l.trim())
  return lines.slice(0, 2).join(' · ')
}

function rsiClass(rsi) {
  if (rsi === null) return ''
  if (rsi >= 70) return 'neg'
  if (rsi <= 30) return 'pos'
  return ''
}

function signalClass(signal) {
  const opinion = signalOpinion(signal)
  if (opinion.includes('매수')) return 'card-buy'
  if (opinion.includes('매도')) return 'card-sell'
  if (opinion.includes('중립')) return 'card-hold'
  return ''
}

function badgeClass(signal) {
  const opinion = signalOpinion(signal)
  if (opinion.includes('매수')) return 'badge-buy'
  if (opinion.includes('매도')) return 'badge-sell'
  if (opinion.includes('중립')) return 'badge-hold'
  return 'badge-none'
}

function badgeLabel(signal) {
  if (!signal) return '-'
  const opinion = signalOpinion(signal)
  for (const label of ['강력 매수', '강력 매도', '매수', '매도', '중립']) {
    if (opinion.includes(label)) return label
  }
  return opinion.slice(0, 6)
}

onMounted(() => {
  loadNameMap()
  load()
  fetchPrices()
  priceTimer = setInterval(fetchPrices, 60_000)
})

onUnmounted(() => {
  clearInterval(priceTimer)
})
</script>

<style scoped>
.error-toast {
  background: #ffebee;
  color: #c62828;
  border-radius: 8px;
  padding: 0.6rem 1rem;
  margin-bottom: 1rem;
  font-size: 0.85rem;
  cursor: pointer;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2rem;
}

.toolbar h2 { font-size: 1.2rem; }

.toolbar-actions { display: flex; gap: 0.5rem; }

button {
  padding: 0.4rem 0.9rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
}

.btn-refresh { background: var(--btn-secondary); color: var(--text); }
.btn-analyze-all { background: #ff9800; color: white; }
.btn-analyze { background: #2196f3; color: white; }
.btn-history { background: var(--btn-secondary); color: var(--text); }
button:disabled { opacity: 0.5; cursor: not-allowed; }

.card-loading { opacity: 0.75; }

.analyzing-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
  padding: 1.6rem 0;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--btn-secondary);
  border-top-color: #2196f3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.status { color: var(--text-muted); padding: 2rem 0; }
.empty a { color: #2196f3; }

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.card {
  background: var(--surface);
  border-radius: 10px;
  padding: 1rem;
  border: 2px solid transparent;
  box-shadow: 0 1px 4px var(--shadow);
  transition: background 0.2s, box-shadow 0.2s;
}

.card-buy { border-color: #bbdefb; }
.card-sell { border-color: #ffcdd2; }
.card-hold { border-color: #fff9c4; }

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.7rem;
}

.ticker { font-size: 1rem; font-weight: 700; }
.name { font-size: 0.8rem; color: var(--text-muted); margin-left: 0.4rem; }

.badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  white-space: nowrap;
}
.badge-buy { background: #e3f2fd; color: #1565c0; }
.badge-sell { background: #ffebee; color: #c62828; }
.badge-hold { background: #fffde7; color: #f57f17; }
.badge-none { background: var(--surface-alt2); color: var(--text-subtle); }

.price-row {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  font-size: 0.85rem;
  margin-bottom: 0.8rem;
  color: var(--text-secondary);
}

.price-block { margin-bottom: 0.8rem; }

.current-price-row {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.2rem;
}

.current-price {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text);
}

.change-pct { font-size: 0.85rem; font-weight: 600; }

.pl-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.15rem;
}

.pl-pct { font-size: 0.8rem; font-weight: 600; }

.price-time { font-size: 0.7rem; color: var(--text-subtle); }

.label { color: var(--text-subtle); font-size: 0.75rem; }

.indicators {
  display: flex;
  gap: 1.2rem;
  margin-bottom: 0.7rem;
}

.ind { display: flex; flex-direction: column; }
.ind .label { font-size: 0.7rem; margin-bottom: 0.1rem; }

.pos { color: #2e7d32; font-weight: 600; }
.neg { color: #c62828; font-weight: 600; }

.no-analysis { font-size: 0.8rem; color: var(--text-subtle); margin-bottom: 0.7rem; }

.signal-preview {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  background: var(--surface-alt);
  border-radius: 6px;
  padding: 0.5rem 0.7rem;
  margin-bottom: 0.8rem;
  cursor: pointer;
  transition: background 0.15s;
}
.signal-preview:hover { background: var(--hover); }

.signal-summary {
  font-size: 0.82rem;
  color: var(--text-secondary);
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.signal-more {
  font-size: 0.75rem;
  color: #2196f3;
  white-space: nowrap;
  flex-shrink: 0;
}

.card-actions { display: flex; gap: 0.5rem; }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: var(--surface);
  border-radius: 10px;
  padding: 1.5rem;
  width: 90%;
  max-width: 680px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.modal-header h3 { font-size: 1rem; }
.modal-date { font-size: 0.8rem; color: var(--text-subtle); font-weight: 400; margin-left: 0.5rem; }

.modal-header button {
  background: none;
  font-size: 1.1rem;
  color: var(--text-muted);
}

.signal-full {
  font-size: 0.88rem;
  color: var(--text);
  line-height: 1.8;
  white-space: pre-wrap;
}

.history-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.history-table th, .history-table td {
  padding: 0.5rem 0.7rem;
  border-bottom: 1px solid var(--border);
  text-align: left;
}
.history-table th { background: var(--surface-alt2); color: var(--text); }
.history-row { cursor: pointer; }
.history-row:hover td { background: var(--hover); }
.signal-cell { font-size: 0.82rem; }
</style>
