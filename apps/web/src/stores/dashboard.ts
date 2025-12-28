import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import api from '@/lib/api'
import { useLocationStore } from './location'

export type DateRange = 'hoy' | 'ayer' | 'ultimos_7_dias' | 'personalizado'

export interface DashboardSummary {
  range: string
  from_date: string
  to_date: string
  total_tickets: number
  in_progress: number
  completed: number
  avg_total_minutes: number | null
  avg_sample_size: number
  throughput_per_hour: number | null
}

export interface StatusFlowItem {
  status_id: string
  name: string
  count: number
  sort_order: number
}

export interface DashboardFlow {
  statuses: StatusFlowItem[]
}

export interface TimelinePoint {
  label: string
  count: number
}

export interface DashboardTimeline {
  bucket: 'hour' | 'day'
  points: TimelinePoint[]
}

export const useDashboardStore = defineStore('dashboard', () => {
  const locationStore = useLocationStore()

  // State
  const range = ref<DateRange>('hoy')
  const fromDate = ref<string | null>(null)
  const toDate = ref<string | null>(null)

  const summary = ref<DashboardSummary | null>(null)
  const flow = ref<DashboardFlow | null>(null)
  const timeline = ref<DashboardTimeline | null>(null)

  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  async function fetchSummary() {
    if (!locationStore.selectedLocationId) return

    const params: Record<string, string> = { range: range.value }
    if (range.value === 'personalizado' && fromDate.value && toDate.value) {
      params.from = fromDate.value
      params.to = toDate.value
    }

    const response = await api.get<DashboardSummary>('/api/v1/dashboard/summary', {
      params,
    })
    summary.value = response.data
  }

  async function fetchFlow() {
    if (!locationStore.selectedLocationId) return

    const params: Record<string, string> = { range: range.value }
    if (range.value === 'personalizado' && fromDate.value && toDate.value) {
      params.from = fromDate.value
      params.to = toDate.value
    }

    const response = await api.get<DashboardFlow>('/api/v1/dashboard/flow', {
      params,
    })
    flow.value = response.data
  }

  async function fetchTimeline() {
    if (!locationStore.selectedLocationId) return

    const params: Record<string, string> = { range: range.value }
    if (range.value === 'personalizado' && fromDate.value && toDate.value) {
      params.from = fromDate.value
      params.to = toDate.value
    }

    const response = await api.get<DashboardTimeline>('/api/v1/dashboard/timeline', {
      params,
    })
    timeline.value = response.data
  }

  async function fetchAll() {
    if (!locationStore.selectedLocationId) {
      summary.value = null
      flow.value = null
      timeline.value = null
      return
    }

    loading.value = true
    error.value = null

    try {
      await Promise.all([fetchSummary(), fetchFlow(), fetchTimeline()])
    } catch (err) {
      error.value = 'Error al cargar el dashboard'
      console.error('Dashboard fetch error:', err)
    } finally {
      loading.value = false
    }
  }

  async function refresh() {
    await fetchAll()
  }

  function setRange(newRange: DateRange, from?: string, to?: string) {
    range.value = newRange
    if (newRange === 'personalizado') {
      fromDate.value = from || null
      toDate.value = to || null
    } else {
      fromDate.value = null
      toDate.value = null
    }
    fetchAll()
  }

  // Watch for location changes
  watch(
    () => locationStore.selectedLocationId,
    () => {
      fetchAll()
    },
    { immediate: true }
  )

  return {
    // State
    range,
    fromDate,
    toDate,
    summary,
    flow,
    timeline,
    loading,
    error,

    // Actions
    fetchAll,
    refresh,
    setRange,
  }
})
