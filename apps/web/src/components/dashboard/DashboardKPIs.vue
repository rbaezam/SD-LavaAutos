<script setup lang="ts">
import { computed } from 'vue'
import { Car, Loader2, CheckCircle2, Clock, TrendingUp } from 'lucide-vue-next'
import KpiCard from './KpiCard.vue'
import { Badge } from '@/components/ui'
import type { DashboardSummary } from '@/stores/dashboard'

interface Props {
  summary: DashboardSummary | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

// Format average time
const avgTimeDisplay = computed(() => {
  const minutes = props.summary?.avg_total_minutes
  if (minutes === null || minutes === undefined) return null

  if (minutes < 60) {
    return `${minutes} min`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (mins === 0) {
    return `${hours} h`
  }
  return `${hours} h ${mins} min`
})

// Average sample size subtitle
const avgSampleSubtitle = computed(() => {
  const size = props.summary?.avg_sample_size ?? 0
  if (size === 0) return 'Sin datos'
  return `Basado en ${size} vehículo${size !== 1 ? 's' : ''}`
})

// Is sample size small (preliminary)?
const isAvgPreliminary = computed(() => {
  return (props.summary?.avg_sample_size ?? 0) < 3 && (props.summary?.avg_sample_size ?? 0) > 0
})

// Format throughput - show "—" if completed < 2
const throughputDisplay = computed(() => {
  const completed = props.summary?.completed ?? 0
  if (completed < 2) return null
  const value = props.summary?.throughput_per_hour
  if (value === null || value === undefined) return null
  return value.toFixed(1)
})

// Throughput subtitle
const throughputSubtitle = computed(() => {
  const completed = props.summary?.completed ?? 0
  if (completed < 2) return 'Insuficiente información'
  return 'Rendimiento'
})
</script>

<template>
  <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
    <KpiCard
      title="Vehículos"
      :value="summary?.total_tickets ?? null"
      subtitle="Total en el periodo"
      :icon="Car"
      :loading="loading"
    />

    <KpiCard
      title="En proceso"
      :value="summary?.in_progress ?? null"
      subtitle="Activos ahora"
      :icon="Loader2"
      icon-color="text-amber-600"
      :loading="loading"
    />

    <KpiCard
      title="Completados"
      :value="summary?.completed ?? null"
      subtitle="Entregados"
      :icon="CheckCircle2"
      icon-color="text-emerald-600"
      :loading="loading"
    />

    <!-- Tiempo promedio with sample size info -->
    <KpiCard
      title="Tiempo promedio"
      :value="avgTimeDisplay"
      :subtitle="avgSampleSubtitle"
      :icon="Clock"
      icon-color="text-blue-600"
      :loading="loading"
    >
      <template v-if="isAvgPreliminary && !loading" #badge>
        <Badge variant="secondary" class="mt-1 text-[10px]">
          Promedio preliminar
        </Badge>
      </template>
    </KpiCard>

    <!-- Vehículos/hora with insufficient data handling -->
    <KpiCard
      title="Vehículos/hora"
      :value="throughputDisplay"
      :subtitle="throughputSubtitle"
      :icon="TrendingUp"
      icon-color="text-purple-600"
      :loading="loading"
    />
  </div>
</template>
