<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Card } from '@/components/ui'
import type { DashboardFlow } from '@/stores/dashboard'

interface Props {
  flow: DashboardFlow | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

const router = useRouter()

// Get status tone based on name (for coloring)
function getStatusTone(name: string): string {
  const normalized = name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')

  if (normalized.includes('espera') || normalized.includes('recepcion')) {
    return 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
  }
  if (normalized.includes('lavado') || normalized.includes('lavando')) {
    return 'bg-blue-100 text-blue-700 border-blue-200 hover:bg-blue-200'
  }
  if (normalized.includes('secado') || normalized.includes('secando')) {
    return 'bg-cyan-100 text-cyan-700 border-cyan-200 hover:bg-cyan-200'
  }
  if (normalized.includes('detallado') || normalized.includes('detalle')) {
    return 'bg-purple-100 text-purple-700 border-purple-200 hover:bg-purple-200'
  }
  if (normalized.includes('listo') || normalized.includes('terminado')) {
    return 'bg-emerald-100 text-emerald-700 border-emerald-200 hover:bg-emerald-200'
  }
  if (normalized.includes('entregado') || normalized.includes('entrega')) {
    return 'bg-green-100 text-green-700 border-green-200 hover:bg-green-200'
  }
  return 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
}

// Calculate total tickets in flow
const totalInFlow = computed(() => {
  if (!props.flow?.statuses) return 0
  return props.flow.statuses.reduce((sum, s) => sum + s.count, 0)
})

// Check if empty
const isEmpty = computed(() => totalInFlow.value === 0)

// Navigate to kanban with status filter
function navigateToKanban(statusId: string) {
  router.push({
    path: '/app/kanban',
    query: { status: statusId },
  })
}
</script>

<template>
  <Card class="p-4">
    <div class="mb-3 flex items-center justify-between">
      <h3 class="text-sm font-semibold text-foreground">Flujo actual</h3>
      <span v-if="!loading && !isEmpty" class="text-xs text-muted-foreground">
        {{ totalInFlow }} vehículo{{ totalInFlow !== 1 ? 's' : '' }}
      </span>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="flex gap-3 overflow-x-auto pb-2">
      <div
        v-for="i in 5"
        :key="i"
        class="flex h-16 w-24 shrink-0 animate-pulse flex-col items-center justify-center rounded-lg bg-slate-100"
      >
        <div class="mb-1 h-6 w-8 rounded bg-slate-200" />
        <div class="h-3 w-14 rounded bg-slate-200" />
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="isEmpty"
      class="flex h-16 items-center justify-center rounded-lg bg-slate-50"
    >
      <p class="text-sm text-muted-foreground">
        Sin actividad registrada en este periodo
      </p>
    </div>

    <!-- Flow strip (clickeable) -->
    <div v-else class="flex gap-3 overflow-x-auto pb-2">
      <button
        v-for="status in flow?.statuses"
        :key="status.status_id"
        type="button"
        :class="[
          'flex min-w-[90px] shrink-0 cursor-pointer flex-col items-center justify-center rounded-lg border px-3 py-2 transition-colors',
          getStatusTone(status.name),
        ]"
        :title="`Ver ${status.name} en Kanban`"
        @click="navigateToKanban(status.status_id)"
      >
        <span class="text-xl font-bold">{{ status.count }}</span>
        <span class="mt-0.5 text-center text-xs font-medium leading-tight">
          {{ status.name }}
        </span>
      </button>
    </div>
  </Card>
</template>
