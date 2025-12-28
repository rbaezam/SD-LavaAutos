import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/lib/api'

export interface VehicleType {
  id: string
  organization_id: string
  name: string
  description: string | null
  default_workers: number
  default_duration_minutes: number
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface VehicleTypeListResponse {
  items: VehicleType[]
  total: number
}

export interface VehicleTypeCreate {
  name: string
  description?: string | null
  default_workers?: number
  default_duration_minutes?: number
  sort_order?: number
}

export interface VehicleTypeUpdate {
  name?: string
  description?: string | null
  default_workers?: number
  default_duration_minutes?: number
  is_active?: boolean
  sort_order?: number
}

export const useVehicleTypeStore = defineStore('vehicleType', () => {
  const vehicleTypes = ref<VehicleType[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const activeVehicleTypes = computed(() =>
    vehicleTypes.value.filter((vt) => vt.is_active).sort((a, b) => a.sort_order - b.sort_order)
  )

  async function fetchVehicleTypes() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get<VehicleTypeListResponse>('/api/v1/vehicle-types', {
        params: { include_inactive: true },
      })
      vehicleTypes.value = response.data.items
    } catch (err) {
      error.value = 'Error al cargar tipos de vehículo'
      console.error('Failed to fetch vehicle types:', err)
    } finally {
      loading.value = false
    }
  }

  async function createVehicleType(data: VehicleTypeCreate) {
    const response = await api.post<VehicleType>('/api/v1/vehicle-types', data)
    vehicleTypes.value.push(response.data)
    return response.data
  }

  async function updateVehicleType(id: string, data: VehicleTypeUpdate) {
    const response = await api.patch<VehicleType>(`/api/v1/vehicle-types/${id}`, data)
    const index = vehicleTypes.value.findIndex((vt) => vt.id === id)
    if (index !== -1) {
      vehicleTypes.value[index] = response.data
    }
    return response.data
  }

  async function deleteVehicleType(id: string) {
    await api.delete(`/api/v1/vehicle-types/${id}`)
    vehicleTypes.value = vehicleTypes.value.filter((vt) => vt.id !== id)
  }

  function getVehicleTypeById(id: string) {
    return vehicleTypes.value.find((vt) => vt.id === id)
  }

  return {
    vehicleTypes,
    activeVehicleTypes,
    loading,
    error,
    fetchVehicleTypes,
    createVehicleType,
    updateVehicleType,
    deleteVehicleType,
    getVehicleTypeById,
  }
})
