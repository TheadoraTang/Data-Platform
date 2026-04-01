<template>
  <div class="page">
    <div class="header">
      <div>
        <div class="title">车辆画像</div>
        <div class="subtitle">输入车辆 ID，查看订单(轨迹)列表，以及按 2 小时统计的轨迹数/里程。</div>
      </div>
      <div class="controls">
        <input
          v-model.trim="deviceId"
          class="input"
          list="device-id-options"
          placeholder="选择或输入 device_id，例如 100032066"
          @focus="loadDeviceOptions()"
          @input="loadDeviceOptions(deviceId)"
        />
        <datalist id="device-id-options">
          <option v-for="id in deviceOptions" :key="id" :value="id">{{ id }}</option>
        </datalist>
        <button class="btn" :disabled="!deviceId || loading" @click="loadCar">查询</button>
      </div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <div class="grid">
      <div class="card">
        <div class="card-title">统计图（每 2 小时）</div>
        <div class="charts">
          <div ref="chartTripsEl" class="chart"></div>
          <div ref="chartDistEl" class="chart"></div>
        </div>
      </div>

      <div class="card info">
        <div class="card-title">车辆信息</div>
        <div v-if="car">
          <div class="kv"><span>车辆ID</span><b>{{ car.device_id }}</b></div>
          <div class="kv"><span>总轨迹数</span><b>{{ car.trips_total }}</b></div>
          <div class="kv"><span>累计里程(km)</span><b>{{ fmt(car.total_distance) }}</b></div>
<!--          <div class="kv"><span>行程数量</span><b>{{ car.trip_ids?.length ?? 0 }}</b></div>-->
        </div>
        <div v-else class="muted">暂无数据。请先查询一个 device_id。</div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">该车轨迹列表（最近 {{ trips.length }} 条）</div>
      <div class="table">
        <div class="tr head">
          <div>行程ID</div>
          <div>行程日期</div>
          <div>行程公里数</div>
          <div>行程时长</div>
          <div>开始时间</div>
          <div>结束时间</div>
        </div>
        <div v-for="t in trips" :key="`${t.trip_id}-${t.log_date}`" class="tr">
          <div><code class="click" @click="goTrip(t.trip_id)">{{ t.trip_id }}</code></div>
          <div>{{ t.log_date }}</div>
          <div>{{ fmt(t.distance_km) }}</div>
          <div>{{ fmtDuration(t.duration_seconds) }}</div>
          <div>{{ t.start_time ?? '-' }}</div>
          <div>{{ t.end_time ?? '-' }}</div>
        </div>
        <div v-if="!trips.length" class="muted" style="padding: 10px 0">无列表数据（该 device_id 可能非纯数字，或行程表的 `devid` 不匹配）。</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { api } from '@/lib/api'

const router = useRouter()

const deviceId = ref('100032066')
const loading = ref(false)
const error = ref('')

const car = ref(null)
const trips = ref([])
const deviceOptions = ref([])

const chartTripsEl = ref(null)
const chartDistEl = ref(null)
let chartTrips = null
let chartDist = null

function fmt(n) {
  if (n === null || n === undefined || Number.isNaN(n)) return '-'
  return Number(n).toFixed(2)
}

function fmtDuration(sec) {
  if (!sec && sec !== 0) return '-'
  const s = Math.max(0, Math.floor(sec))
  const hh = String(Math.floor(s / 3600)).padStart(2, '0')
  const mm = String(Math.floor((s % 3600) / 60)).padStart(2, '0')
  const ss = String(s % 60).padStart(2, '0')
  return `${hh}:${mm}:${ss}`
}

function goTrip(tripId) {
  router.push({ path: '/trip', query: { id: String(tripId) } })
}

function renderCharts() {
  const c = car.value
  if (!c) return
  const labels = Object.keys(c.trips_total_by_2h || {})
  const tripCounts = labels.map(k => c.trips_total_by_2h[k] ?? 0)
  const dists = labels.map(k => c.total_distance_by_2h[k] ?? 0)

  chartTrips?.dispose()
  chartDist?.dispose()
  chartTrips = echarts.init(chartTripsEl.value)
  chartDist = echarts.init(chartDistEl.value)

  const baseGrid = {
    left: 45,
    right: 18,
    top: 24,
    bottom: 34,
    containLabel: false,
  }

  chartTrips.setOption({
    backgroundColor: 'transparent',
    title: { text: '轨迹数', textStyle: { color: '#e6edf3', fontSize: 12 } },
    grid: baseGrid,
    xAxis: { type: 'category', data: labels, axisLabel: { color: 'rgba(230,237,243,0.7)' } },
    yAxis: { type: 'value', axisLabel: { color: 'rgba(230,237,243,0.7)' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } } },
    series: [{ type: 'bar', data: tripCounts, itemStyle: { color: 'rgba(79,70,229,0.75)' }, barMaxWidth: 26 }],
    tooltip: { trigger: 'axis' },
  })

  chartDist.setOption({
    backgroundColor: 'transparent',
    title: { text: '里程(km)', textStyle: { color: '#e6edf3', fontSize: 12 } },
    grid: baseGrid,
    xAxis: { type: 'category', data: labels, axisLabel: { color: 'rgba(230,237,243,0.7)' } },
    yAxis: { type: 'value', axisLabel: { color: 'rgba(230,237,243,0.7)' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } } },
    series: [{ type: 'line', data: dists, smooth: true, symbolSize: 6, lineStyle: { width: 3, color: 'rgba(34,197,94,0.9)' }, itemStyle: { color: 'rgba(34,197,94,0.9)' } }],
    tooltip: { trigger: 'axis' },
  })

  window.addEventListener('resize', handleResize)
}

function handleResize() {
  chartTrips?.resize()
  chartDist?.resize()
}

async function loadCar() {
  error.value = ''
  loading.value = true
  try {
    const [carResp, tripsResp] = await Promise.all([
      api.get(`/api/cars/${encodeURIComponent(deviceId.value)}`),
      api.get(`/api/cars/${encodeURIComponent(deviceId.value)}/trips`, { params: { limit: 200 } }),
    ])
    car.value = carResp.data
    trips.value = tripsResp.data || []
    await nextTick()
    renderCharts()
  } catch (e) {
    car.value = null
    trips.value = []
    error.value = e?.response?.data?.detail || e?.message || String(e)
  } finally {
    loading.value = false
  }
}

async function loadDeviceOptions(keyword = '') {
  try {
    const resp = await api.get('/api/meta/device-ids', {
      params: { q: keyword || '', limit: 200 },
    })
    deviceOptions.value = resp.data || []
  } catch {
    deviceOptions.value = []
  }
}

onMounted(() => {
  loadDeviceOptions(deviceId.value)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartTrips?.dispose()
  chartDist?.dispose()
})
</script>

<style scoped>
.page {
  display: grid;
  gap: 12px;
}
.header {
  display: flex;
  gap: 12px;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
}
.title {
  font-size: 18px;
  font-weight: 700;
}
.subtitle {
  margin-top: 4px;
  opacity: 0.7;
  font-size: 12px;
}
.controls {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.input {
  height: 36px;
  padding: 0 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.06);
  color: #e6edf3;
  outline: none;
}
.btn {
  height: 36px;
  padding: 0 14px;
  border-radius: 10px;
  border: 1px solid rgba(79, 70, 229, 0.42);
  background: rgba(79, 70, 229, 0.24);
  color: #e6edf3;
  cursor: pointer;
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.grid {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 12px;
}
.card {
  border-radius: 14px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
}
.card-title {
  font-weight: 700;
  margin-bottom: 10px;
}
.charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.chart {
  height: 300px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.02);
}
.info .kv {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.info .kv span {
  opacity: 0.75;
}
.muted {
  opacity: 0.7;
}
.error {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.12);
  color: #fecaca;
}
.table {
  width: 100%;
  overflow: auto;
}
.tr {
  display: grid;
  grid-template-columns: 110px 110px 110px 110px 1fr 1fr;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  min-width: 860px;
}
.tr.head {
  opacity: 0.75;
  font-size: 12px;
}
.click {
  cursor: pointer;
  color: #93c5fd;
}
@media (max-width: 1100px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .charts {
    grid-template-columns: 1fr;
  }
}
</style>

