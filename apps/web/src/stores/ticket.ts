import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/lib/api'
import type { Status } from './status'

export interface TicketServiceSnapshot {
  id: string
  service_id: string | null
  captured_name: string
  captured_price_mxn: number | null
  captured_duration_minutes: number
  sort_order: number
}

export interface Ticket {
  id: string
  organization_id: string
  location_id: string
  public_code: string
  plate: string | null
  vehicle_desc: string | null
  manual_ticket_no: string | null
  customer_name: string | null
  customer_whatsapp: string | null
  current_status_id: string
  current_status: Status
  eta_at: string | null
  created_at: string
  updated_at: string
  completed_at: string | null
  services: TicketServiceSnapshot[]
  total_duration_minutes: number
  total_price_mxn: number | null
  package_snapshot: PackageSnapshot | null
}

export interface TicketListItem {
  id: string
  public_code: string
  plate: string | null
  vehicle_desc: string | null
  current_status_id: string
  current_status: Status
  eta_at: string | null
  created_at: string
  services_summary: string
  total_duration_minutes: number
}

export interface TicketListResponse {
  items: TicketListItem[]
  total: number
}

export interface PackageSnapshot {
  package_id: string
  name: string
  price_mxn: number
  workers_required: number
  estimated_duration_minutes: number
}

export interface TicketCreate {
  plate?: string | null
  vehicle_desc?: string | null
  manual_ticket_no?: string | null
  customer_name?: string | null
  customer_whatsapp?: string | null
  service_ids?: string[]
  package_id?: string | null
  vehicle_type_id?: string | null
}

export interface TicketUpdate {
  plate?: string | null
  vehicle_desc?: string | null
  manual_ticket_no?: string | null
  customer_name?: string | null
  customer_whatsapp?: string | null
  service_ids?: string[]
}

export interface TicketEvent {
  id: string
  ticket_id: string
  actor_user_id: string
  actor_name: string | null
  event_type: string
  from_status_id: string | null
  from_status_name: string | null
  to_status_id: string | null
  to_status_name: string | null
  payload_json: Record<string, unknown> | null
  happened_at: string
}

export interface TicketEventListResponse {
  items: TicketEvent[]
  total: number
}

export interface TicketFilters {
  status_id?: string
  q?: string
  date?: 'today' | null
}

export const useTicketStore = defineStore('ticket', () => {
  const tickets = ref<TicketListItem[]>([])
  const currentTicket = ref<Ticket | null>(null)
  const events = ref<TicketEvent[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)

  async function listTickets(locationId: string, filters: TicketFilters = {}) {
    loading.value = true
    error.value = null
    try {
      const params: Record<string, string> = {}
      if (filters.status_id) params.status_id = filters.status_id
      if (filters.q) params.q = filters.q
      if (filters.date) params.date = filters.date

      const response = await api.get<TicketListResponse>(
        `/api/v1/locations/${locationId}/tickets`,
        { params }
      )
      tickets.value = response.data.items
      total.value = response.data.total
    } catch (err) {
      error.value = 'Error al cargar tickets'
      console.error('Failed to fetch tickets:', err)
    } finally {
      loading.value = false
    }
  }

  async function getTicket(id: string) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get<Ticket>(`/api/v1/tickets/${id}`)
      currentTicket.value = response.data
      return response.data
    } catch (err) {
      error.value = 'Error al cargar ticket'
      console.error('Failed to fetch ticket:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createTicket(locationId: string, data: TicketCreate) {
    const response = await api.post<Ticket>(
      `/api/v1/locations/${locationId}/tickets`,
      data
    )
    return response.data
  }

  async function updateTicket(id: string, data: TicketUpdate) {
    const response = await api.patch<Ticket>(`/api/v1/tickets/${id}`, data)
    currentTicket.value = response.data
    return response.data
  }

  async function moveTicket(id: string, toStatusId: string) {
    const response = await api.post<Ticket>(`/api/v1/tickets/${id}/move`, {
      to_status_id: toStatusId,
    })
    currentTicket.value = response.data
    return response.data
  }

  async function updateEta(id: string, etaAt: string | null) {
    const response = await api.patch<Ticket>(`/api/v1/tickets/${id}/eta`, {
      eta_at: etaAt,
    })
    currentTicket.value = response.data
    return response.data
  }

  async function listEvents(ticketId: string) {
    const response = await api.get<TicketEventListResponse>(
      `/api/v1/tickets/${ticketId}/events`
    )
    events.value = response.data.items
    return response.data.items
  }

  function clearCurrentTicket() {
    currentTicket.value = null
    events.value = []
  }

  return {
    tickets,
    currentTicket,
    events,
    loading,
    error,
    total,
    listTickets,
    getTicket,
    createTicket,
    updateTicket,
    moveTicket,
    updateEta,
    listEvents,
    clearCurrentTicket,
  }
})
