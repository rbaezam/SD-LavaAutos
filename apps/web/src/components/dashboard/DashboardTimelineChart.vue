<script setup lang="ts">
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  BarController,
  type TooltipItem,
} from 'chart.js'
import { Bar } from 'vue-chartjs'
import { Card } from '@/components/ui'
import type { DashboardTimeline } from '@/stores/dashboard'

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, BarController)

interface Props {
  timeline: DashboardTimeline | null
  loading?: boolean
  range?: string // 'hoy' | 'ayer' | 'ultimos_7_dias' | 'personalizado'
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  range: 'hoy',
})

// Get the current bucket label for highlighting
const currentBucketLabel = computed(() => {
  if (!props.timeline) return null

  const now = new Date()

  if (props.timeline.bucket === 'hour' && props.range === 'hoy') {
    // Format: "HH:00"
    const hour = now.getHours()
    return `${hour.toString().padStart(2, '0')}:00`
  }

  if (props.timeline.bucket === 'day') {
    // Format: "dd/mm"
    const day = now.getDate().toString().padStart(2, '0')
    const month = (now.getMonth() + 1).toString().padStart(2, '0')
    return `${day}/${month}`
  }

  return null
})

// Check if empty
const isEmpty = computed(() => {
  if (!props.timeline?.points) return true
  return props.timeline.points.every((p) => p.count === 0)
})

// Chart data with current bucket highlighting
const chartData = computed(() => {
  if (!props.timeline?.points) {
    return {
      labels: [] as string[],
      datasets: [] as {
        label: string
        data: number[]
        backgroundColor: string | string[]
        borderColor: string | string[]
        borderWidth: number
        borderRadius: number
        maxBarThickness: number
      }[],
    }
  }

  const labels = props.timeline.points.map((p) => p.label)
  const currentLabel = currentBucketLabel.value

  // Generate colors array with highlight for current bucket
  const backgroundColors = labels.map((label) =>
    label === currentLabel ? 'rgba(16, 185, 129, 0.8)' : 'rgba(37, 99, 235, 0.7)'
  )
  const borderColors = labels.map((label) =>
    label === currentLabel ? 'rgba(16, 185, 129, 1)' : 'rgba(37, 99, 235, 1)'
  )

  return {
    labels,
    datasets: [
      {
        label: 'Vehículos',
        data: props.timeline.points.map((p) => p.count),
        backgroundColor: backgroundColors,
        borderColor: borderColors,
        borderWidth: 1,
        borderRadius: 4,
        maxBarThickness: 40,
      },
    ],
  }
})

// Chart options
const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      callbacks: {
        label: (context: TooltipItem<'bar'>) => {
          const value = context.raw as number
          return `${value} vehículo${value !== 1 ? 's' : ''}`
        },
      },
    },
  },
  scales: {
    x: {
      grid: {
        display: false,
      },
      ticks: {
        maxRotation: 0,
        autoSkip: true,
        maxTicksLimit: props.timeline?.bucket === 'hour' ? 12 : 7,
        font: {
          size: 11,
        },
      },
    },
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 1,
        precision: 0,
        font: {
          size: 11,
        },
      },
      grid: {
        color: 'rgba(0, 0, 0, 0.05)',
      },
    },
  },
}))

// Title based on bucket type
const chartTitle = computed(() => {
  if (!props.timeline) return 'Actividad'
  return props.timeline.bucket === 'hour' ? 'Actividad por hora' : 'Actividad por día'
})
</script>

<template>
  <Card class="p-4">
    <div class="mb-3">
      <h3 class="text-sm font-semibold text-foreground">{{ chartTitle }}</h3>
    </div>

    <!-- Loading skeleton -->
    <div
      v-if="loading"
      class="flex h-[200px] items-end justify-center gap-1 rounded-lg bg-slate-50 p-4"
    >
      <div
        v-for="i in 12"
        :key="i"
        class="w-6 animate-pulse rounded-t bg-slate-200"
        :style="{ height: `${20 + Math.random() * 100}px` }"
      />
    </div>

    <!-- Empty state -->
    <div
      v-else-if="isEmpty"
      class="flex h-[200px] items-center justify-center rounded-lg bg-slate-50"
    >
      <p class="text-sm text-muted-foreground">Aún no hay vehículos en este periodo</p>
    </div>

    <!-- Chart -->
    <div v-else class="h-[200px]">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </Card>
</template>
