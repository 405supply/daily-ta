<template>
  <div class="app">
    <header>
      <div class="header-inner">
        <div class="brand">
          <h1>Daily TA</h1>
          <span class="subtitle">손절하지 못하는 우리들을 위하여</span>
        </div>
        <div class="header-right">
          <nav>
            <RouterLink to="/" class="nav-link">홈</RouterLink>
            <RouterLink to="/manage" class="nav-link">종목 관리</RouterLink>
          </nav>
          <button class="theme-toggle" @click="toggleTheme" :title="isDark ? '라이트 모드' : '다크 모드'">
            {{ isDark ? '☀️' : '🌙' }}
          </button>
        </div>
      </div>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isDark = ref(false)

function applyTheme(dark) {
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
  isDark.value = dark
}

function toggleTheme() {
  const next = !isDark.value
  localStorage.setItem('theme', next ? 'dark' : 'light')
  applyTheme(next)
}

onMounted(() => {
  const saved = localStorage.getItem('theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  applyTheme(saved ? saved === 'dark' : prefersDark)
})
</script>

<style>
:root {
  --bg: #f4f6f8;
  --surface: #ffffff;
  --surface-alt: #f9f9f9;
  --surface-alt2: #f5f5f5;
  --text: #222;
  --text-secondary: #555;
  --text-muted: #888;
  --text-subtle: #999;
  --border: #eee;
  --input-border: #ddd;
  --hover: #f0f0f0;
  --btn-secondary: #e0e0e0;
  --shadow: rgba(0,0,0,0.07);
}

[data-theme="dark"] {
  --bg: #0f0f1a;
  --surface: #1c1c2e;
  --surface-alt: #252538;
  --surface-alt2: #2a2a40;
  --text: #e8e8f0;
  --text-secondary: #b0b0c8;
  --text-muted: #7a7a9a;
  --text-subtle: #66668a;
  --border: #2e2e48;
  --input-border: #3a3a58;
  --hover: #2e2e48;
  --btn-secondary: #2a2a42;
  --shadow: rgba(0,0,0,0.35);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg);
  color: var(--text);
  transition: background 0.2s, color 0.2s;
}

input, textarea, select {
  background: var(--surface);
  color: var(--text);
}

.app { min-height: 100vh; }

header {
  background: #1a1a2e;
  color: white;
  padding: 0 1.5rem;
}

.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.header-right { display: flex; align-items: center; gap: 0.5rem; }

.brand h1 { font-size: 1.2rem; font-weight: 700; }
.subtitle { font-size: 0.75rem; color: #aaa; }

nav { display: flex; gap: 0.5rem; }

.nav-link {
  color: #ccc;
  text-decoration: none;
  padding: 0.4rem 0.9rem;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: background 0.15s;
}

.nav-link:hover { background: rgba(255,255,255,0.1); color: white; }
.nav-link.router-link-exact-active { background: rgba(255,255,255,0.15); color: white; }

.theme-toggle {
  background: rgba(255,255,255,0.1);
  border: none;
  border-radius: 6px;
  padding: 0.3rem 0.6rem;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  transition: background 0.15s;
}
.theme-toggle:hover { background: rgba(255,255,255,0.2); }

main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.5rem;
}
</style>
