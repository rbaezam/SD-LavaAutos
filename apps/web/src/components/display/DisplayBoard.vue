<script setup lang="ts">
import { computed } from 'vue'
import type { Status } from '@/stores/status'
import type { TicketListItem } from '@/stores/ticket'
import DisplayColumn from './DisplayColumn.vue'

interface Props {
  statuses: Status[]
  tickets: TicketListItem[]
  showEta?: boolean
  showElapsed?: boolean
  darkMode?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showEta: true,
  showElapsed: true,
  darkMode: false,
})

// Group tickets by status, ordered by creation date (oldest first for FIFO)
const ticketsByStatus = computed(() => {
  const grouped: Record<string, TicketListItem[]> = {}

  // Initialize all status groups
  for (const status of props.statuses) {
    grouped[status.id] = []
  }

  // Group tickets
  for (const ticket of props.tickets) {
    if (grouped[ticket.current_status_id]) {
      grouped[ticket.current_status_id].push(ticket)
    }
  }

  // Sort each group by created_at (oldest first - FIFO for visibility)
  for (const statusId of Object.keys(grouped)) {
    grouped[statusId].sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    )
  }

  return grouped
})

// Sorted statuses by sort_order
const sortedStatuses = computed(() => {
  return [...props.statuses].sort((a, b) => a.sort_order - b.sort_order)
})

// Total tickets count
const totalTickets = computed(() => props.tickets.length)

// Determine which column should be "in focus"
// Priority: 1) "En lavado" if it has tickets, 2) first non-empty column from left
const focusedStatusId = computed(() => {
  if (totalTickets.value === 0) return null

  // Check for "En lavado" pattern first
  const lavadoStatus = sortedStatuses.value.find((s) => {
    const normalized = s.name.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    return normalized.includes('lavado') || normalized.includes('lavando')
  })

  if (lavadoStatus && (ticketsByStatus.value[lavadoStatus.id]?.length || 0) > 0) {
    return lavadoStatus.id
  }

  // Otherwise, first non-empty column
  for (const status of sortedStatuses.value) {
    if ((ticketsByStatus.value[status.id]?.length || 0) > 0) {
      return status.id
    }
  }

  return null
})
</script>

<template>
  <div class="h-full">
    <!-- Empty state for no tickets -->
    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      leave-active-class="transition-opacity duration-200"
      leave-to-class="opacity-0"
    >
      <div
        v-if="totalTickets === 0"
        :class="[
          'flex h-full items-center justify-center',
          darkMode ? 'text-gray-400' : 'text-gray-500',
        ]"
      >
        <div class="text-center">
          <p class="text-2xl font-medium">No hay vehículos en operación hoy.</p>
          <p class="mt-2 text-lg opacity-75">Los tickets aparecerán aquí automáticamente.</p>
        </div>
      </div>
    </Transition>

    <!-- Columns grid -->
    <Transition
      enter-active-class="transition-opacity duration-500"
      enter-from-class="opacity-0"
    >
      <div
        v-if="totalTickets > 0 || sortedStatuses.length > 0"
        class="grid h-full gap-4 overflow-x-auto"
        :style="{
          gridTemplateColumns: `repeat(${sortedStatuses.length}, minmax(300px, 1fr))`,
        }"
      >
        <DisplayColumn
          v-for="status in sortedStatuses"
          :key="status.id"
          :status="status"
          :tickets="ticketsByStatus[status.id] || []"
          :show-eta="showEta"
          :show-elapsed="showElapsed"
          :dark-mode="darkMode"
          :is-focused="status.id === focusedStatusId"
        />
      </div>
    </Transition>
  </div>
</template>
