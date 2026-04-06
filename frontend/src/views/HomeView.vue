<template>
  <div>
    <ConfirmDialog ref="confirmRef" />
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

        <div class="price-row">
          <span class="label">매수가</span>
          <span class="price">{{ item.buy_price.toLocaleString() }}</span>
          <span class="label">수량</span>
          <span>{{ item.quantity }}주</span>
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

          <div class="signal-text" v-if="item.signal">{{ item.signal }}</div>
        </template>

        <div class="card-actions">
          <button class="btn-analyze" @click="analyzeSingle(item.ticker)" :disabled="analyzingTicker === item.ticker">
            분석
          </button>
          <button class="btn-history" @click="openHistory(item.ticker)" :disabled="analyzingTicker === item.ticker">기록</button>
        </div>
      </div>
    </div>

    <!-- History modal -->
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
            <tr><th>날짜</th><th>RSI</th><th>MACD</th><th>신호</th></tr>
          </thead>
          <tbody>
            <tr v-for="row in historyRows" :key="row.id">
              <td>{{ row.date }}</td>
              <td :class="rsiClass(row.rsi)">{{ row.rsi }}</td>
              <td :class="row.macd >= 0 ? 'pos' : 'neg'">{{ row.macd }}</td>
              <td class="signal-cell">{{ row.signal }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const confirmRef = ref(null)
const items = ref([])
const loading = ref(false)
const analyzing = ref(false)
const analyzingTicker = ref(null)

const historyTicker = ref(null)
const historyRows = ref([])
const historyLoading = ref(false)

// name lookup from both lists (fetched once)
const nameMap = ref({})

async function loadNameMap() {
  const [n, k] = await Promise.all([
    fetch('http://localhost:8000/api/stocks/nasdaq100').then(r => r.json()),
    fetch('http://localhost:8000/api/stocks/kospi100').then(r => r.json()),
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
  const res = await fetch('http://localhost:8000/api/dashboard')
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
  const res = await fetch(`http://localhost:8000/api/analyze/${ticker}`)
  if (res.ok) await load()
  analyzingTicker.value = null
}

async function analyzeAll() {
  analyzing.value = true
  await fetch('http://localhost:8000/api/analyze-all')
  await load()
  analyzing.value = false
}

async function openHistory(ticker) {
  historyTicker.value = ticker
  historyRows.value = []
  historyLoading.value = true
  const res = await fetch(`http://localhost:8000/api/history/${ticker}`)
  historyRows.value = await res.json()
  historyLoading.value = false
}

function rsiClass(rsi) {
  if (rsi === null) return ''
  if (rsi >= 70) return 'neg'
  if (rsi <= 30) return 'pos'
  return ''
}

function signalClass(signal) {
  if (!signal) return ''
  if (signal.includes('매수')) return 'card-buy'
  if (signal.includes('매도')) return 'card-sell'
  return 'card-hold'
}

function badgeClass(signal) {
  if (!signal) return 'badge-none'
  if (signal.includes('매수')) return 'badge-buy'
  if (signal.includes('매도')) return 'badge-sell'
  return 'badge-hold'
}

function badgeLabel(signal) {
  if (!signal) return '-'
  if (signal.includes('매수')) return '매수'
  if (signal.includes('매도')) return '매도'
  return '관망'
}

onMounted(() => {
  loadNameMap()
  load()
})
</script>

<style scoped>
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

.btn-refresh { background: #e0e0e0; }
.btn-analyze-all { background: #ff9800; color: white; }
.btn-analyze { background: #2196f3; color: white; }
.btn-history { background: #eeeeee; }
button:disabled { opacity: 0.5; cursor: not-allowed; }

.card-loading {
  opacity: 0.75;
}

.analyzing-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
  padding: 1.6rem 0;
  color: #888;
  font-size: 0.85rem;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #e0e0e0;
  border-top-color: #2196f3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.status { color: #888; padding: 2rem 0; }
.empty a { color: #2196f3; }

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.card {
  background: white;
  border-radius: 10px;
  padding: 1rem;
  border: 2px solid transparent;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
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
.name { font-size: 0.8rem; color: #666; margin-left: 0.4rem; }

.badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
}
.badge-buy { background: #e3f2fd; color: #1565c0; }
.badge-sell { background: #ffebee; color: #c62828; }
.badge-hold { background: #fffde7; color: #f57f17; }
.badge-none { background: #f5f5f5; color: #999; }

.price-row {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  font-size: 0.85rem;
  margin-bottom: 0.8rem;
  color: #444;
}

.label { color: #999; font-size: 0.75rem; }

.indicators {
  display: flex;
  gap: 1.2rem;
  margin-bottom: 0.7rem;
}

.ind { display: flex; flex-direction: column; }
.ind .label { font-size: 0.7rem; margin-bottom: 0.1rem; }

.pos { color: #2e7d32; font-weight: 600; }
.neg { color: #c62828; font-weight: 600; }

.no-analysis { font-size: 0.8rem; color: #bbb; margin-bottom: 0.7rem; }

.signal-text {
  font-size: 0.82rem;
  color: #555;
  background: #f9f9f9;
  padding: 0.5rem 0.7rem;
  border-radius: 6px;
  margin-bottom: 0.8rem;
  line-height: 1.5;
}

.card-actions { display: flex; gap: 0.5rem; }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: white;
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

.modal-header button {
  background: none;
  font-size: 1.1rem;
  color: #666;
}

.history-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.history-table th, .history-table td {
  padding: 0.5rem 0.7rem;
  border-bottom: 1px solid #eee;
  text-align: left;
}
.history-table th { background: #f5f5f5; }
.signal-cell { font-size: 0.78rem; max-width: 280px; }
</style>
