<template>
  <div class="page">
    <div class="header">
      <div>
        <div class="title">轨迹分析</div>
        <div class="subtitle">输入轨迹 ID，还原真实行驶路径并标注拥堵（红）/畅通（绿）。</div>
      </div>
      <div class="controls">
        <input
          v-model.trim="tripId"
          class="input"
          list="trip-id-options"
          placeholder="选择或输入 trip_id，例如 286254"
          @focus="loadTripOptions()"
          @input="loadTripOptions(tripId)"
        />
        <datalist id="trip-id-options">
          <option v-for="id in tripOptions" :key="id" :value="String(id)">{{ id }}</option>
        </datalist>
        <label class="label">
          拥堵阈值(km/h)
          <input v-model.number="congestionKph" type="number" class="input small" min="0" max="200" />
        </label>
        <button class="btn" :disabled="!tripId || loading" @click="loadTrip">查询</button>
      </div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <div class="grid">
      <div class="card">
        <AmapTripMap :segments="segments" :trip="trip" />
      </div>
      <div class="card info">
        <div class="card-title">行程信息</div>
        <div v-if="trip">
          <div class="kv"><span>行程ID</span><b>{{ trip.trip_id }}</b></div>
          <div class="kv"><span>行程日期</span><b>{{ trip.log_date }}</b></div>
          <div class="kv"><span>车辆ID</span><b>{{ trip.devid ?? '-' }}</b></div>
          <div class="kv"><span>距离(km)</span><b>{{ fmt(trip.distance_km) }}</b></div>
          <div class="kv"><span>时长</span><b>{{ fmtDuration(trip.duration_seconds) }}</b></div>
          <div class="kv"><span>均速(km/h)</span><b>{{ fmt(trip.avg_speed_kph) }}</b></div>
          <div class="kv"><span>起点时间</span><b>{{ trip.start_time ?? '-' }}</b></div>
          <div class="kv"><span>终点时间</span><b>{{ trip.end_time ?? '-' }}</b></div>
          <div class="kv"><span>点数量</span><b>{{ trip.points?.length ?? 0 }}</b></div>
        </div>
        <div v-else class="muted">暂无数据。请先查询一个 trip_id。</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/lib/api'
import AmapTripMap from '@/components/AmapTripMap.vue'

const route = useRoute()

const tripId = ref('286254')
const congestionKph = ref(20)
const loading = ref(false)
const error = ref('')
const tripOptions = ref([])

const trip = ref(null)
const segments = ref([])

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

async function loadTrip() {
  error.value = ''
  loading.value = true
  try {
    const id = Number(tripId.value)
    if (!Number.isFinite(id)) throw new Error('trip_id 必须是数字')

    const [tripResp, segResp] = await Promise.all([
      api.get(`/api/trips/${id}`),
      api.get(`/api/trips/${id}/segments`, { params: { congestion_kph: congestionKph.value } }),
    ])
    trip.value = tripResp.data
    segments.value = segResp.data.segments || []
  } catch (e) {
    trip.value = null
    segments.value = []
    error.value = e?.response?.data?.detail || e?.message || String(e)
  } finally {
    loading.value = false
  }
}

async function loadTripOptions(keyword = '') {
  try {
    const resp = await api.get('/api/meta/trip-ids', {
      params: { q: keyword || '', limit: 200 },
    })
    tripOptions.value = resp.data || []
  } catch {
    tripOptions.value = []
  }
}

onMounted(() => {
  const qid = route.query?.id
  if (qid) tripId.value = String(qid)
  loadTripOptions(tripId.value)
  if (tripId.value) loadTrip()
})

watch(
  () => route.query?.id,
  (qid) => {
    if (!qid) return
    tripId.value = String(qid)
    loadTrip()
  }
)
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
.input.small {
  width: 110px;
}
.select {
  height: 10px;
  width: 140px;
  padding: 0 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.06);
  color: #e6edf3;
  outline: none;
}
.label {
  display: flex;
  gap: 8px;
  align-items: center;
  opacity: 0.9;
  font-size: 12px;
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
  grid-template-columns: 1.7fr 1fr;
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
@media (max-width: 1100px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>

