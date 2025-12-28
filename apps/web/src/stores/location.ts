import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import api from '@/lib/api'
import { useAuthStore } from './auth'

export interface Location {
  id: string
  organization_id: string
  name: string
  address: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LocationListResponse {
  items: Location[]
  total: number
}

export const useLocationStore = defineStore('location', () => {
  const authStore = useAuthStore()

  const locations = ref<Location[]>([])
  const selectedLocationId = ref<string | null>(
    localStorage.getItem('selected_location_id')
  )
  const loading = ref(false)
  const error = ref<string | null>(null)

  const selectedLocation = computed(() =>
    locations.value.find((loc) => loc.id === selectedLocationId.value) || null
  )

  const hasLocations = computed(() => locations.value.length > 0)

  // Check if user can change location (owner/admin with multiple locations, or staff without assigned location)
  const canChangeLocation = computed(() => {
    if (!authStore.user) return false
    if (authStore.user.role === 'staff' && authStore.user.location_id) {
      return false // Staff with assigned location cannot change
    }
    return locations.value.length > 1 || authStore.isManager
  })

  function setSelectedLocation(locationId: string | null) {
    selectedLocationId.value = locationId
    if (locationId) {
      localStorage.setItem('selected_location_id', locationId)
    } else {
      localStorage.removeItem('selected_location_id')
    }
  }

  async function fetchLocations() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get<LocationListResponse>('/api/v1/locations')
      locations.value = response.data.items

      // Auto-select location if needed
      if (locations.value.length > 0) {
        // If user has an assigned location, use that
        if (authStore.user?.location_id) {
          const userLocation = locations.value.find(
            (loc) => loc.id === authStore.user?.location_id
          )
          if (userLocation) {
            setSelectedLocation(userLocation.id)
            return
          }
        }

        // If no location selected or selected location no longer exists
        if (
          !selectedLocationId.value ||
          !locations.value.find((loc) => loc.id === selectedLocationId.value)
        ) {
          setSelectedLocation(locations.value[0].id)
        }
      } else {
        setSelectedLocation(null)
      }
    } catch (err) {
      error.value = 'Error al cargar sucursales'
      console.error('Failed to fetch locations:', err)
    } finally {
      loading.value = false
    }
  }

  async function createLocation(name: string, address?: string) {
    const response = await api.post<Location>('/api/v1/locations', {
      name,
      address: address || null,
    })
    locations.value.push(response.data)
    setSelectedLocation(response.data.id)
    return response.data
  }

  async function updateLocation(id: string, name: string, address?: string) {
    const response = await api.patch<Location>(`/api/v1/locations/${id}`, {
      name,
      address: address || null,
    })
    const index = locations.value.findIndex((loc) => loc.id === id)
    if (index !== -1) {
      locations.value[index] = response.data
    }
    return response.data
  }

  async function deleteLocation(id: string) {
    await api.delete(`/api/v1/locations/${id}`)
    locations.value = locations.value.filter((loc) => loc.id !== id)
    if (selectedLocationId.value === id) {
      setSelectedLocation(locations.value[0]?.id || null)
    }
  }

  // Watch for auth changes to refetch locations
  watch(
    () => authStore.user,
    (newUser) => {
      if (newUser) {
        fetchLocations()
      } else {
        locations.value = []
        setSelectedLocation(null)
      }
    },
    { immediate: true }
  )

  return {
    locations,
    selectedLocationId,
    selectedLocation,
    loading,
    error,
    hasLocations,
    canChangeLocation,
    setSelectedLocation,
    fetchLocations,
    createLocation,
    updateLocation,
    deleteLocation,
  }
})
