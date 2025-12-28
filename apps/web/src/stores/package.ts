import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/lib/api'

export interface ServiceSimple {
  id: string
  name: string
}

export interface VehicleTypeSimple {
  id: string
  name: string
}

export interface PackageServiceItem {
  id: string
  service_id: string
  service: ServiceSimple
  sort_order: number
}

export interface Package {
  id: string
  organization_id: string
  name: string
  description: string | null
  base_price_mxn: number
  vehicle_type_id: string
  vehicle_type: VehicleTypeSimple
  workers_required: number
  estimated_duration_minutes: number
  commission_per_worker_mxn: number | null
  is_active: boolean
  sort_order: number
  services: PackageServiceItem[]
  created_at: string
  updated_at: string
}

export interface PackageSimple {
  id: string
  name: string
  description: string | null
  base_price_mxn: number
  vehicle_type_id: string
  workers_required: number
  estimated_duration_minutes: number
}

export interface PackageListResponse {
  items: Package[]
  total: number
}

export interface PackageSimpleListResponse {
  items: PackageSimple[]
  total: number
}

export interface PackageCreate {
  name: string
  description?: string | null
  base_price_mxn: number
  vehicle_type_id: string
  workers_required?: number
  estimated_duration_minutes?: number
  commission_per_worker_mxn?: number | null
  service_ids?: string[]
  sort_order?: number
}

export interface PackageUpdate {
  name?: string
  description?: string | null
  base_price_mxn?: number
  vehicle_type_id?: string
  workers_required?: number
  estimated_duration_minutes?: number
  commission_per_worker_mxn?: number | null
  is_active?: boolean
  service_ids?: string[]
  sort_order?: number
}

export const usePackageStore = defineStore('package', () => {
  const packages = ref<Package[]>([])
  const packagesSimple = ref<PackageSimple[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const activePackages = computed(() =>
    packages.value.filter((p) => p.is_active).sort((a, b) => a.sort_order - b.sort_order)
  )

  // Get packages grouped by vehicle type
  const packagesByVehicleType = computed(() => {
    const grouped: Record<string, Package[]> = {}
    for (const pkg of activePackages.value) {
      const vtId = pkg.vehicle_type_id
      if (!grouped[vtId]) {
        grouped[vtId] = []
      }
      grouped[vtId].push(pkg)
    }
    return grouped
  })

  async function fetchPackages() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get<PackageListResponse>('/api/v1/packages', {
        params: { include_inactive: true },
      })
      packages.value = response.data.items
    } catch (err) {
      error.value = 'Error al cargar paquetes'
      console.error('Failed to fetch packages:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchPackagesSimple() {
    try {
      const response = await api.get<PackageSimple[]>('/api/v1/packages/simple')
      packagesSimple.value = response.data
    } catch (err) {
      console.error('Failed to fetch simple packages:', err)
    }
  }

  async function createPackage(data: PackageCreate) {
    const response = await api.post<Package>('/api/v1/packages', data)
    packages.value.push(response.data)
    return response.data
  }

  async function updatePackage(id: string, data: PackageUpdate) {
    const response = await api.patch<Package>(`/api/v1/packages/${id}`, data)
    const index = packages.value.findIndex((p) => p.id === id)
    if (index !== -1) {
      packages.value[index] = response.data
    }
    return response.data
  }

  async function deletePackage(id: string) {
    await api.delete(`/api/v1/packages/${id}`)
    packages.value = packages.value.filter((p) => p.id !== id)
  }

  function getPackageById(id: string) {
    return packages.value.find((p) => p.id === id)
  }

  function getPackagesByVehicleTypeId(vehicleTypeId: string) {
    return activePackages.value.filter((p) => p.vehicle_type_id === vehicleTypeId)
  }

  return {
    packages,
    packagesSimple,
    activePackages,
    packagesByVehicleType,
    loading,
    error,
    fetchPackages,
    fetchPackagesSimple,
    createPackage,
    updatePackage,
    deletePackage,
    getPackageById,
    getPackagesByVehicleTypeId,
  }
})
