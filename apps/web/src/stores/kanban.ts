import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/lib/api'
import type { Status } from './status'
import type { TicketListItem, TicketListResponse } from './ticket'

export interface KanbanTicket extends TicketListItem {
  // Additional computed properties for kanban display
}

export const useKanbanStore = defineStore('kanban', () => {
  const statuses = ref<Status[]>([])
  const tickets = ref<KanbanTicket[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Group tickets by status
  const ticketsByStatus = computed(() => {
    const grouped: Record<string, KanbanTicket[]> = {}
    for (const status of statuses.value) {
      grouped[status.id] = []
    }
    for (const ticket of tickets.value) {
      if (grouped[ticket.current_status_id]) {
        grouped[ticket.current_status_id].push(ticket)
      }
    }
    return grouped
  })

  // Count tickets per status
  const statusCounts = computed(() => {
    const counts: Record<string, number> = {}
    for (const status of statuses.value) {
      counts[status.id] = ticketsByStatus.value[status.id]?.length || 0
    }
    return counts
  })

  // Total active tickets (non-terminal)
  const totalActiveTickets = computed(() => {
    return tickets.value.filter((t) => !t.current_status.is_terminal).length
  })

  // Sorted statuses by sort_order
  const sortedStatuses = computed(() => {
    return [...statuses.value].sort((a, b) => a.sort_order - b.sort_order)
  })

  async function fetchBoard(locationId: string) {
    loading.value = true
    error.value = null

    try {
      // Fetch statuses and tickets in parallel
      const [statusesRes, ticketsRes] = await Promise.all([
        api.get<{ items: Status[]; total: number }>(
          `/api/v1/locations/${locationId}/statuses`
        ),
        api.get<TicketListResponse>(`/api/v1/locations/${locationId}/tickets`),
      ])

      statuses.value = statusesRes.data.items
      tickets.value = ticketsRes.data.items
    } catch (err) {
      error.value = 'Error al cargar el tablero'
      console.error('Failed to fetch kanban board:', err)
    } finally {
      loading.value = false
    }
  }

  async function moveTicket(
    ticketId: string,
    _fromStatusId: string,
    toStatusId: string
  ): Promise<boolean> {
    // Find the ticket
    const ticketIndex = tickets.value.findIndex((t) => t.id === ticketId)
    if (ticketIndex === -1) return false

    const ticket = tickets.value[ticketIndex]
    const toStatus = statuses.value.find((s) => s.id === toStatusId)
    if (!toStatus) return false

    // Optimistic update
    const previousStatusId = ticket.current_status_id
    const previousStatus = ticket.current_status

    ticket.current_status_id = toStatusId
    ticket.current_status = toStatus

    try {
      await api.post(`/api/v1/tickets/${ticketId}/move`, {
        to_status_id: toStatusId,
      })
      return true
    } catch (err) {
      // Rollback on error
      ticket.current_status_id = previousStatusId
      ticket.current_status = previousStatus
      error.value = 'Error al mover el ticket'
      console.error('Failed to move ticket:', err)
      return false
    }
  }

  async function refresh(locationId: string) {
    await fetchBoard(locationId)
  }

  function clearBoard() {
    statuses.value = []
    tickets.value = []
    error.value = null
  }

  return {
    statuses,
    tickets,
    loading,
    error,
    ticketsByStatus,
    statusCounts,
    totalActiveTickets,
    sortedStatuses,
    fetchBoard,
    moveTicket,
    refresh,
    clearBoard,
  }
})
