import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import api from '@/lib/api'
import { useLocationStore } from './location'

export interface Service {
  id: string
  organization_id: string
  location_id: string
  name: string
  active: boolean
  price_mxn: number | null
  duration_minutes: number
  sort_order: number
  created_at: string
  updated_at: string
}

export interface ServiceListResponse {
  items: Service[]
  total: number
}

export interface ServiceCreate {
  name: string
  price_mxn?: number | null
  duration_minutes?: number
  sort_order?: number
}

export interface ServiceUpdate {
  name?: string
  price_mxn?: number | null
  duration_minutes?: number
  sort_order?: number
}

export const useServiceStore = defineStore('service', () => {
  const locationStore = useLocationStore()

  const services = ref<Service[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchServices() {
    if (!locationStore.selectedLocationId) {
      services.value = []
      return
    }

    loading.value = true
    error.value = null
    try {
      const response = await api.get<ServiceListResponse>(
        `/api/v1/locations/${locationStore.selectedLocationId}/services`,
        { params: { include_inactive: true } }
      )
      services.value = response.data.items
    } catch (err) {
      error.value = 'Error al cargar servicios'
      console.error('Failed to fetch services:', err)
    } finally {
      loading.value = false
    }
  }

  async function createService(data: ServiceCreate) {
    if (!locationStore.selectedLocationId) {
      throw new Error('No hay sucursal seleccionada')
    }

    const response = await api.post<Service>(
      `/api/v1/locations/${locationStore.selectedLocationId}/services`,
      data
    )
    services.value.push(response.data)
    return response.data
  }

  async function updateService(id: string, data: ServiceUpdate) {
    const response = await api.patch<Service>(`/api/v1/services/${id}`, data)
    const index = services.value.findIndex((s) => s.id === id)
    if (index !== -1) {
      services.value[index] = response.data
    }
    return response.data
  }

  async function activateService(id: string) {
    const response = await api.post<Service>(`/api/v1/services/${id}/activate`)
    const index = services.value.findIndex((s) => s.id === id)
    if (index !== -1) {
      services.value[index] = response.data
    }
    return response.data
  }

  async function deactivateService(id: string) {
    const response = await api.post<Service>(`/api/v1/services/${id}/deactivate`)
    const index = services.value.findIndex((s) => s.id === id)
    if (index !== -1) {
      services.value[index] = response.data
    }
    return response.data
  }

  // Refetch when location changes
  watch(
    () => locationStore.selectedLocationId,
    () => {
      fetchServices()
    },
    { immediate: true }
  )

  return {
    services,
    loading,
    error,
    fetchServices,
    createService,
    updateService,
    activateService,
    deactivateService,
  }
})
