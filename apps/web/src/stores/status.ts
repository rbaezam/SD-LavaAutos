import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import api from '@/lib/api'
import { useLocationStore } from './location'

export interface Status {
  id: string
  organization_id: string
  location_id: string
  name: string
  sort_order: number
  is_terminal: boolean
  created_at: string
  updated_at: string
}

export interface StatusListResponse {
  items: Status[]
  total: number
}

export interface StatusCreate {
  name: string
  is_terminal?: boolean
}

export interface StatusUpdate {
  name?: string
  is_terminal?: boolean
}

export const useStatusStore = defineStore('status', () => {
  const locationStore = useLocationStore()

  const statuses = ref<Status[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchStatuses() {
    if (!locationStore.selectedLocationId) {
      statuses.value = []
      return
    }

    loading.value = true
    error.value = null
    try {
      const response = await api.get<StatusListResponse>(
        `/api/v1/locations/${locationStore.selectedLocationId}/statuses`
      )
      statuses.value = response.data.items
    } catch (err) {
      error.value = 'Error al cargar estados'
      console.error('Failed to fetch statuses:', err)
    } finally {
      loading.value = false
    }
  }

  async function createStatus(data: StatusCreate) {
    if (!locationStore.selectedLocationId) {
      throw new Error('No hay sucursal seleccionada')
    }

    const response = await api.post<Status>(
      `/api/v1/locations/${locationStore.selectedLocationId}/statuses`,
      data
    )
    statuses.value.push(response.data)
    // Re-sort after adding
    statuses.value.sort((a, b) => a.sort_order - b.sort_order)
    return response.data
  }

  async function updateStatus(id: string, data: StatusUpdate) {
    const response = await api.patch<Status>(`/api/v1/statuses/${id}`, data)
    const index = statuses.value.findIndex((s) => s.id === id)
    if (index !== -1) {
      statuses.value[index] = response.data
    }
    return response.data
  }

  async function reorderStatuses(orderedIds: string[]) {
    if (!locationStore.selectedLocationId) {
      throw new Error('No hay sucursal seleccionada')
    }

    const response = await api.post<StatusListResponse>(
      `/api/v1/locations/${locationStore.selectedLocationId}/statuses/reorder`,
      { ordered_ids: orderedIds }
    )
    statuses.value = response.data.items
    return response.data.items
  }

  // Refetch when location changes
  watch(
    () => locationStore.selectedLocationId,
    () => {
      fetchStatuses()
    },
    { immediate: true }
  )

  return {
    statuses,
    loading,
    error,
    fetchStatuses,
    createStatus,
    updateStatus,
    reorderStatuses,
  }
})
