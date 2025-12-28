<script setup lang="ts">
import { computed } from 'vue'
import { Clock, Timer } from 'lucide-vue-next'
import type { TicketListItem } from '@/stores/ticket'

interface Props {
  ticket: TicketListItem
  showEta?: boolean
  showElapsed?: boolean
  darkMode?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showEta: true,
  showElapsed: true,
  darkMode: false,
})

// Vehicle display: prefer plate, fallback to description
const vehicleDisplay = computed(() => {
  if (props.ticket.plate) {
    return props.ticket.plate
  }
  return props.ticket.vehicle_desc || 'Sin identificar'
})

// Format ETA
const formattedEta = computed(() => {
  if (!props.ticket.eta_at) return null
  const eta = new Date(props.ticket.eta_at)
  return eta.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })
})

// Elapsed time since creation
const elapsedTime = computed(() => {
  const created = new Date(props.ticket.created_at)
  const now = new Date()
  const diffMs = now.getTime() - created.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Ahora'
  if (diffMins < 60) return `${diffMins} min`

  const diffHours = Math.floor(diffMins / 60)
  const remainingMins = diffMins % 60
  if (diffHours < 24) {
    return remainingMins > 0 ? `${diffHours}h ${remainingMins}m` : `${diffHours}h`
  }

  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}d`
})

// Check if ticket is taking long (over 2 hours)
const isLongWait = computed(() => {
  const created = new Date(props.ticket.created_at)
  const now = new Date()
  const diffMs = now.getTime() - created.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  return diffMins > 120
})
</script>

<template>
  <div
    :class="[
      'rounded-xl p-4 shadow-sm transition-all duration-300',
      darkMode
        ? 'bg-gray-800 border border-gray-700'
        : 'bg-white border border-gray-100',
      isLongWait && !darkMode && 'border-l-4 border-l-amber-400',
      isLongWait && darkMode && 'border-l-4 border-l-amber-500',
    ]"
  >
    <!-- Folio -->
    <p
      :class="[
        'font-mono text-xl font-bold tracking-tight',
        darkMode ? 'text-white' : 'text-gray-900',
      ]"
    >
      {{ ticket.public_code }}
    </p>

    <!-- Vehicle -->
    <p
      :class="[
        'mt-1.5 truncate text-base',
        darkMode ? 'text-gray-300' : 'text-gray-600',
      ]"
      :title="vehicleDisplay"
    >
      {{ vehicleDisplay }}
    </p>

    <!-- Meta info -->
    <div
      v-if="(showEta && formattedEta) || showElapsed"
      :class="[
        'mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-sm',
        darkMode ? 'text-gray-400' : 'text-gray-500',
      ]"
    >
      <!-- ETA -->
      <span
        v-if="showEta && formattedEta"
        :class="[
          'inline-flex items-center gap-1.5 rounded-md px-2 py-0.5',
          darkMode ? 'bg-gray-700/50' : 'bg-gray-100',
        ]"
      >
        <Clock class="h-3.5 w-3.5" />
        <span>ETA {{ formattedEta }}</span>
      </span>

      <!-- Elapsed -->
      <span
        v-if="showElapsed"
        :class="[
          'inline-flex items-center gap-1.5',
          isLongWait && 'text-amber-500',
        ]"
      >
        <Timer class="h-3.5 w-3.5" />
        <span>{{ elapsedTime }}</span>
      </span>
    </div>
  </div>
</template>
