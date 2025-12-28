<script setup lang="ts">
import { computed } from 'vue'
import { Clock, CheckCircle, Truck, Timer } from 'lucide-vue-next'
import { Card } from '@/components/ui'

interface Props {
  tickets: Array<{
    current_status: { is_terminal: boolean; name: string }
    eta_at: string | null
    created_at: string
  }>
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

const stats = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const inProgress = props.tickets.filter((t) => !t.current_status.is_terminal).length
  const ready = props.tickets.filter(
    (t) => t.current_status.name.toLowerCase().includes('listo') && !t.current_status.is_terminal
  ).length
  const delivered = props.tickets.filter((t) => {
    const createdAt = new Date(t.created_at)
    return t.current_status.is_terminal && createdAt >= today
  }).length

  return { inProgress, ready, delivered }
})

const statItems = computed(() => [
  {
    label: 'En progreso',
    value: props.loading ? '—' : stats.value.inProgress,
    icon: Clock,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100 dark:bg-blue-900/30',
  },
  {
    label: 'Listos',
    value: props.loading ? '—' : stats.value.ready,
    icon: CheckCircle,
    color: 'text-green-600',
    bgColor: 'bg-green-100 dark:bg-green-900/30',
  },
  {
    label: 'Entregados hoy',
    value: props.loading ? '—' : stats.value.delivered,
    icon: Truck,
    color: 'text-purple-600',
    bgColor: 'bg-purple-100 dark:bg-purple-900/30',
  },
  {
    label: 'Tiempo promedio',
    value: '—',
    icon: Timer,
    color: 'text-orange-600',
    bgColor: 'bg-orange-100 dark:bg-orange-900/30',
  },
])
</script>

<template>
  <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
    <Card v-for="stat in statItems" :key="stat.label" class="p-4">
      <div class="flex items-center gap-3">
        <div :class="['flex h-10 w-10 items-center justify-center rounded-lg', stat.bgColor]">
          <component :is="stat.icon" :class="['h-5 w-5', stat.color]" />
        </div>
        <div>
          <p class="text-2xl font-semibold tabular-nums">{{ stat.value }}</p>
          <p class="text-xs text-muted-foreground">{{ stat.label }}</p>
        </div>
      </div>
    </Card>
  </div>
</template>
