<template>
  <div>
    <!-- 등록된 종목 -->
    <section class="section">
      <h2>등록된 종목 <span class="count">{{ portfolio.length }}</span></h2>
      <p v-if="!portfolio.length" class="empty">등록된 종목이 없습니다.</p>
      <div class="registered-list" v-else>
        <div class="reg-item" v-for="item in portfolio" :key="item.ticker">
          <div>
            <span class="ticker">{{ item.ticker }}</span>
            <span class="name">{{ nameMap[item.ticker] || '' }}</span>
          </div>
          <div class="reg-meta">
            <span v-if="item.buy_price !== null">{{ item.buy_price.toLocaleString() }}원</span>
            <button class="btn-delete" @click="remove(item.ticker)">삭제</button>
          </div>
        </div>
      </div>
    </section>

    <!-- 종목 추가 패널 -->
    <div class="panels">

      <!-- NASDAQ 200 -->
      <section class="section panel">
        <h2>NASDAQ 상위 200</h2>
        <input
          v-model="nasdaqSearch"
          class="search"
          placeholder="종목명 또는 티커 검색..."
        />
        <div class="stock-list">
          <div
            class="stock-item"
            v-for="s in filteredNasdaq"
            :key="s.ticker"
            :class="{ registered: isRegistered(s.ticker) }"
          >
            <div class="stock-info">
              <span class="ticker">{{ s.ticker }}</span>
              <span class="name">{{ s.name }}</span>
            </div>
            <button
              v-if="!isRegistered(s.ticker)"
              class="btn-add"
              @click="openAddModal(s)"
            >추가</button>
            <span v-else class="registered-label">등록됨</span>
          </div>
        </div>
      </section>

      <!-- KOSPI 100 -->
      <section class="section panel">
        <h2>KOSPI 100</h2>
        <input
          v-model="kospiSearch"
          class="search"
          placeholder="종목명 또는 티커 검색..."
        />
        <div class="stock-list">
          <div
            class="stock-item"
            v-for="s in filteredKospi"
            :key="s.ticker"
            :class="{ registered: isRegistered(s.ticker) }"
          >
            <div class="stock-info">
              <span class="ticker">{{ s.ticker }}</span>
              <span class="name">{{ s.name }}</span>
            </div>
            <button
              v-if="!isRegistered(s.ticker)"
              class="btn-add"
              @click="openAddModal(s)"
            >추가</button>
            <span v-else class="registered-label">등록됨</span>
          </div>
        </div>
      </section>

      <!-- 직접 입력 -->
      <section class="section panel">
        <h2>직접 입력</h2>
        <p class="direct-desc">목록에 없는 종목을 티커로 직접 추가합니다.</p>
        <form class="direct-form" @submit.prevent="confirmDirectAdd">
          <div class="direct-fields">
            <div class="field-group">
              <label>티커 <span class="required">*</span></label>
              <input v-model.trim="directForm.ticker" placeholder="예) PLTR, 035420.KS" />
            </div>
            <div class="field-group">
              <label>종목명 <span class="optional">(선택)</span></label>
              <input v-model.trim="directForm.name" placeholder="예) Palantir" />
            </div>
            <div class="field-group">
              <label>매수 평단 <span class="optional">(선택)</span></label>
              <input v-model.number="directForm.buy_price" type="number" step="0.01" min="0" placeholder="0.00" />
            </div>
          </div>
          <p v-if="directError" class="error">{{ directError }}</p>
          <button type="submit" class="btn-confirm direct-submit" :disabled="!directForm.ticker">추가</button>
        </form>
      </section>

    </div>

    <!-- 추가 모달 -->
    <div class="modal-overlay" v-if="addTarget" @click.self="addTarget = null">
      <div class="modal">
        <h3>{{ addTarget.ticker }} 추가</h3>
        <p class="modal-name">{{ addTarget.name }}</p>
        <form @submit.prevent="confirmAdd">
          <label>
            매수 평단 <span class="optional">(선택)</span>
            <input v-model.number="addForm.buy_price" type="number" step="0.01" min="0" placeholder="입력하지 않아도 됩니다" />
          </label>
          <p v-if="addError" class="error">{{ addError }}</p>
          <div class="modal-actions">
            <button type="button" @click="addTarget = null">취소</button>
            <button type="submit" class="btn-confirm">추가</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const API = import.meta.env.VITE_API_BASE

const portfolio = ref([])
const nasdaq200 = ref([])
const kospi100 = ref([])
const nasdaqSearch = ref('')
const kospiSearch = ref('')

const addTarget = ref(null)
const addForm = ref({ buy_price: null })
const addError = ref('')

const directForm = ref({ ticker: '', name: '', buy_price: null })
const directError = ref('')

const nameMap = computed(() => {
  const map = {}
  ;[...nasdaq200.value, ...kospi100.value].forEach(s => { map[s.ticker] = s.name })
  return map
})

const registeredTickers = computed(() => new Set(portfolio.value.map(p => p.ticker)))

function isRegistered(ticker) {
  return registeredTickers.value.has(ticker)
}

const filteredNasdaq = computed(() => {
  const q = nasdaqSearch.value.toLowerCase()
  if (!q) return nasdaq200.value
  return nasdaq200.value.filter(s =>
    s.ticker.toLowerCase().includes(q) || s.name.toLowerCase().includes(q)
  )
})

const filteredKospi = computed(() => {
  const q = kospiSearch.value.toLowerCase()
  if (!q) return kospi100.value
  return kospi100.value.filter(s =>
    s.ticker.toLowerCase().includes(q) || s.name.toLowerCase().includes(q)
  )
})

async function fetchAll() {
  const [p, n, k] = await Promise.all([
    fetch(`${API}/api/portfolio`).then(r => r.json()),
    fetch(`${API}/api/stocks/nasdaq200`).then(r => r.json()),
    fetch(`${API}/api/stocks/kospi100`).then(r => r.json()),
  ])
  portfolio.value = p
  nasdaq200.value = n
  kospi100.value = k
}

function openAddModal(stock) {
  addTarget.value = stock
  addForm.value = { buy_price: null }
  addError.value = ''
}

async function confirmAdd() {
  addError.value = ''
  const res = await fetch(`${API}/api/portfolio`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ticker: addTarget.value.ticker,
      buy_price: addForm.value.buy_price,
    }),
  })
  if (res.ok) {
    addTarget.value = null
    await fetchAll()
  } else {
    const data = await res.json()
    addError.value = data.detail
  }
}

async function confirmDirectAdd() {
  directError.value = ''
  const res = await fetch(`${API}/api/portfolio`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ticker: directForm.value.ticker.toUpperCase(),
      buy_price: directForm.value.buy_price,
    }),
  })
  if (res.ok) {
    directForm.value = { ticker: '', name: '', buy_price: null }
    await fetchAll()
  } else {
    const data = await res.json()
    directError.value = data.detail
  }
}

async function remove(ticker) {
  await fetch(`${API}/api/portfolio/${ticker}`, { method: 'DELETE' })
  await fetchAll()
}

onMounted(fetchAll)
</script>

<style scoped>
.section {
  background: var(--surface);
  border-radius: 10px;
  padding: 1.2rem;
  margin-bottom: 1.2rem;
  box-shadow: 0 1px 4px var(--shadow);
  transition: background 0.2s;
}

h2 { font-size: 1.1rem; margin-bottom: 0.9rem; }

.count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #1a1a2e;
  color: white;
  border-radius: 20px;
  font-size: 0.75rem;
  padding: 0.1rem 0.55rem;
  margin-left: 0.4rem;
  vertical-align: middle;
}

.registered-list { display: flex; flex-direction: column; gap: 0.5rem; }

.reg-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0.8rem;
  background: var(--surface-alt);
  border-radius: 6px;
}

.reg-meta { display: flex; gap: 0.8rem; align-items: center; font-size: 0.85rem; color: var(--text-secondary); }

.btn-delete {
  background: #ffebee;
  color: #c62828;
  border: none;
  border-radius: 4px;
  padding: 0.25rem 0.6rem;
  cursor: pointer;
  font-size: 0.8rem;
}

.panels {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.2rem;
}

@media (max-width: 900px) {
  .panels { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 600px) {
  .panels { grid-template-columns: 1fr; }
}

.panel { margin-bottom: 0; }

.search {
  width: 100%;
  padding: 0.4rem 0.7rem;
  border: 1px solid var(--input-border);
  border-radius: 6px;
  margin-bottom: 0.7rem;
  font-size: 0.9rem;
}

.stock-list {
  max-height: 420px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.45rem 0.6rem;
  border-radius: 6px;
  transition: background 0.1s;
}

.stock-item:hover { background: var(--hover); }
.stock-item.registered { opacity: 0.5; }

.stock-info { display: flex; flex-direction: column; gap: 0.05rem; }

.ticker { font-size: 0.9rem; font-weight: 600; }
.name { font-size: 0.78rem; color: var(--text-muted); }

.btn-add {
  background: #e8f5e9;
  color: #2e7d32;
  border: none;
  border-radius: 4px;
  padding: 0.25rem 0.6rem;
  cursor: pointer;
  font-size: 0.8rem;
  white-space: nowrap;
}

.registered-label { font-size: 0.78rem; color: var(--text-subtle); }

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
  width: 340px;
}

.modal h3 { font-size: 1.1rem; margin-bottom: 0.2rem; }
.modal-name { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem; }

form { display: flex; flex-direction: column; gap: 0.8rem; }

label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

label input {
  padding: 0.4rem 0.6rem;
  border: 1px solid var(--input-border);
  border-radius: 6px;
  font-size: 0.95rem;
}

.optional { font-size: 0.78rem; color: var(--text-subtle); font-weight: 400; }
.error { color: #c62828; font-size: 0.85rem; }

.modal-actions { display: flex; gap: 0.5rem; justify-content: flex-end; }

.modal-actions button {
  padding: 0.4rem 0.9rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  background: var(--btn-secondary);
  color: var(--text);
}

.btn-confirm { background: #4caf50; color: white; }

.direct-desc { font-size: 0.82rem; color: var(--text-subtle); margin-bottom: 1rem; }

.direct-form { display: flex; flex-direction: column; gap: 0.8rem; }

.direct-fields { display: flex; flex-direction: column; gap: 0.6rem; }

.field-group { display: flex; flex-direction: column; gap: 0.25rem; }

.field-group label { font-size: 0.82rem; color: var(--text-secondary); }

.field-group input {
  padding: 0.4rem 0.6rem;
  border: 1px solid var(--input-border);
  border-radius: 6px;
  font-size: 0.9rem;
  width: 100%;
  box-sizing: border-box;
}

.required { color: #e53935; font-size: 0.75rem; }

.direct-submit {
  align-self: flex-start;
  padding: 0.4rem 1.2rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.direct-submit:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
