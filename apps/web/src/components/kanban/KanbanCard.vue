<script setup lang="ts">
import { computed } from 'vue'
import { Clock, GripVertical } from 'lucide-vue-next'
import { cn } from '@/lib/utils'
import type { KanbanTicket } from '@/stores/kanban'

interface Props {
  ticket: KanbanTicket
  isDragging?: boolean
  isDropTarget?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isDragging: false,
  isDropTarget: false,
})

// Format relative time
function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'ahora'
  if (diffMins < 60) return `hace ${diffMins} min`

  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `hace ${diffHours}h`

  const diffDays = Math.floor(diffHours / 24)
  return `hace ${diffDays}d`
}

// Format ETA time
function formatEta(etaStr: string | null): string | null {
  if (!etaStr) return null
  const eta = new Date(etaStr)
  return eta.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })
}

// Truncate services summary
const servicesDisplay = computed(() => {
  const summary = props.ticket.services_summary || ''
  if (summary.length > 30) {
    return summary.substring(0, 27) + '...'
  }
  return summary || 'Sin servicios'
})

// Vehicle display
const vehicleDisplay = computed(() => {
  if (props.ticket.plate && props.ticket.vehicle_desc) {
    return `${props.ticket.plate} · ${props.ticket.vehicle_desc}`
  }
  return props.ticket.plate || props.ticket.vehicle_desc || 'Sin identificar'
})

const relativeTime = computed(() => formatRelativeTime(props.ticket.created_at))
const etaTime = computed(() => formatEta(props.ticket.eta_at))
</script>

<template>
  <div
    :class="
      cn(
        'group relative cursor-grab rounded-lg border bg-card p-3 shadow-sm transition-all',
        'hover:shadow-md hover:border-primary/30',
        isDragging && 'opacity-50 rotate-2 scale-105 shadow-lg cursor-grabbing',
        isDropTarget && 'ring-2 ring-primary ring-offset-2'
      )
    "
  >
    <!-- Drag handle indicator -->
    <div class="absolute -left-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
      <GripVertical class="h-4 w-4 text-muted-foreground" />
    </div>

    <!-- Card content -->
    <div class="space-y-2">
      <!-- Header: Folio -->
      <div class="flex items-center justify-between">
        <span class="font-mono text-sm font-bold text-primary">
          {{ ticket.public_code }}
        </span>
        <span class="text-xs text-muted-foreground">
          {{ relativeTime }}
        </span>
      </div>

      <!-- Vehicle -->
      <p class="text-sm font-medium truncate" :title="vehicleDisplay">
        {{ vehicleDisplay }}
      </p>

      <!-- Services -->
      <p class="text-xs text-muted-foreground truncate" :title="ticket.services_summary">
        {{ servicesDisplay }}
      </p>

      <!-- Footer: ETA / Duration -->
      <div v-if="etaTime || ticket.total_duration_minutes" class="flex items-center gap-2 pt-1">
        <div
          v-if="etaTime"
          class="flex items-center gap-1 rounded-md bg-muted px-2 py-0.5"
        >
          <Clock class="h-3 w-3 text-muted-foreground" />
          <span class="text-xs font-medium">{{ etaTime }}</span>
        </div>
        <span v-if="ticket.total_duration_minutes" class="text-xs text-muted-foreground">
          {{ ticket.total_duration_minutes }} min
        </span>
      </div>
    </div>
  </div>
</template>
