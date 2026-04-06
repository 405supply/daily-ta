<template>
  <div class="app">
    <header>
      <div class="header-inner">
        <div class="brand">
          <h1>TA 분석기</h1>
          <span class="subtitle">기술적 분석 매매 신호 (참고용)</span>
        </div>
        <nav>
          <RouterLink to="/" class="nav-link">홈</RouterLink>
          <RouterLink to="/manage" class="nav-link">종목 관리</RouterLink>
        </nav>
      </div>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #f4f6f8;
  color: #222;
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

main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.5rem;
}
</style>
