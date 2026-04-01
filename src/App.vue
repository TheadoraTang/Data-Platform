<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">Traffic 中台</div>
      <nav class="nav">
        <RouterLink class="nav-item" to="/trip">轨迹分析</RouterLink>
        <RouterLink class="nav-item" to="/car">车辆画像</RouterLink>
      </nav>
<!--      <div class="hint">-->
<!--        后端：<code>localhost:8000</code><br />-->
<!--        前端：<code>localhost:8081</code>-->
<!--      </div>-->
    </aside>

    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: 240px 1fr;
  height: 100vh;
  background: #0b1220;
  color: #e6edf3;
}
.sidebar {
  padding: 16px;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0));
}
.brand {
  font-weight: 700;
  letter-spacing: 0.2px;
  margin-bottom: 16px;
}
.nav {
  display: grid;
  gap: 8px;
}
.nav-item {
  display: block;
  padding: 10px 12px;
  border-radius: 10px;
  color: #e6edf3;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.nav-item.router-link-active {
  background: rgba(79, 70, 229, 0.24);
  border-color: rgba(79, 70, 229, 0.42);
}
.hint {
  margin-top: 16px;
  opacity: 0.8;
  font-size: 12px;
  line-height: 1.6;
}
.main {
  background: #0b1220;
  padding: 16px;
  overflow: auto;
}
</style>