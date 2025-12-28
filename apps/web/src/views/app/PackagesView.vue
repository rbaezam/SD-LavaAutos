<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Package2, Plus, Pencil, Trash2, Car, Clock, Users, DollarSign } from 'lucide-vue-next'
import { z } from 'zod'
import {
  Alert,
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Dialog,
  Input,
  Label,
  MultiSelect,
  Select,
} from '@/components/ui'
import PageHeader from '@/components/layout/PageHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import TableSkeleton from '@/components/table/TableSkeleton.vue'
import { useAuthStore } from '@/stores/auth'
import { useLocationStore } from '@/stores/location'
import { useVehicleTypeStore, type VehicleType } from '@/stores/vehicleType'
import { usePackageStore, type Package } from '@/stores/package'
import { useServiceStore } from '@/stores/service'

const authStore = useAuthStore()
const locationStore = useLocationStore()
const vehicleTypeStore = useVehicleTypeStore()
const packageStore = usePackageStore()
const serviceStore = useServiceStore()

// Modal state
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteConfirm = ref(false)
const showVehicleTypeModal = ref(false)
const editingPackage = ref<Package | null>(null)
const deletingPackage = ref<Package | null>(null)

// Package form state
const formName = ref('')
const formDescription = ref('')
const formPrice = ref<number>(0)
const formVehicleTypeId = ref('')
const formWorkers = ref(1)
const formDuration = ref(30)
const formCommission = ref<number | null>(null)
const formServiceIds = ref<string[]>([])
const formSortOrder = ref(0)
const formError = ref('')
const formLoading = ref(false)

// Vehicle type form state
const vtFormName = ref('')
const vtFormDescription = ref('')
const vtFormWorkers = ref(1)
const vtFormDuration = ref(30)
const vtFormError = ref('')
const vtFormLoading = ref(false)

const packageSchema = z.object({
  name: z.string().min(2, 'El nombre debe tener al menos 2 caracteres').max(80),
  description: z.string().max(500).optional().nullable(),
  base_price_mxn: z.number().min(0, 'El precio no puede ser negativo'),
  vehicle_type_id: z.string().min(1, 'Selecciona un tipo de vehículo'),
  workers_required: z.number().min(1, 'Mínimo 1 trabajador').max(20),
  estimated_duration_minutes: z.number().min(1, 'Mínimo 1 minuto').max(600),
  commission_per_worker_mxn: z.number().min(0).optional().nullable(),
  service_ids: z.array(z.string()).optional(),
  sort_order: z.number().min(0).optional(),
})

const vehicleTypeSchema = z.object({
  name: z.string().min(2, 'El nombre debe tener al menos 2 caracteres').max(60),
  description: z.string().max(500).optional().nullable(),
  default_workers: z.number().min(1).max(20),
  default_duration_minutes: z.number().min(1).max(600),
})

const vehicleTypeOptions = computed(() =>
  vehicleTypeStore.activeVehicleTypes.map((vt) => ({
    value: vt.id,
    label: vt.name,
  }))
)

const serviceOptions = computed(() =>
  serviceStore.services
    .filter((s) => s.active)
    .map((s) => ({
      value: s.id,
      label: s.name,
    }))
)

// Group packages by vehicle type
const groupedPackages = computed(() => {
  const groups: { vehicleType: VehicleType; packages: Package[] }[] = []
  for (const vt of vehicleTypeStore.activeVehicleTypes) {
    const pkgs = packageStore.getPackagesByVehicleTypeId(vt.id)
    groups.push({ vehicleType: vt, packages: pkgs })
  }
  return groups
})

onMounted(() => {
  vehicleTypeStore.fetchVehicleTypes()
  packageStore.fetchPackages()
})

function resetPackageForm() {
  formName.value = ''
  formDescription.value = ''
  formPrice.value = 0
  formVehicleTypeId.value = ''
  formWorkers.value = 1
  formDuration.value = 30
  formCommission.value = null
  formServiceIds.value = []
  formSortOrder.value = 0
  formError.value = ''
}

function openCreateModal(vehicleTypeId?: string) {
  resetPackageForm()
  if (vehicleTypeId) {
    formVehicleTypeId.value = vehicleTypeId
    const vt = vehicleTypeStore.getVehicleTypeById(vehicleTypeId)
    if (vt) {
      formWorkers.value = vt.default_workers
      formDuration.value = vt.default_duration_minutes
    }
  }
  showCreateModal.value = true
}

function openEditModal(pkg: Package) {
  editingPackage.value = pkg
  formName.value = pkg.name
  formDescription.value = pkg.description || ''
  formPrice.value = pkg.base_price_mxn
  formVehicleTypeId.value = pkg.vehicle_type_id
  formWorkers.value = pkg.workers_required
  formDuration.value = pkg.estimated_duration_minutes
  formCommission.value = pkg.commission_per_worker_mxn
  formServiceIds.value = pkg.services.map((s) => s.service_id)
  formSortOrder.value = pkg.sort_order
  formError.value = ''
  showEditModal.value = true
}

function confirmDelete(pkg: Package) {
  deletingPackage.value = pkg
  showDeleteConfirm.value = true
}

function openVehicleTypeModal() {
  vtFormName.value = ''
  vtFormDescription.value = ''
  vtFormWorkers.value = 1
  vtFormDuration.value = 30
  vtFormError.value = ''
  showVehicleTypeModal.value = true
}

// Update defaults when vehicle type changes
function onVehicleTypeChange(vtId: string) {
  const vt = vehicleTypeStore.getVehicleTypeById(vtId)
  if (vt && !editingPackage.value) {
    formWorkers.value = vt.default_workers
    formDuration.value = vt.default_duration_minutes
  }
}

async function handleCreate() {
  formError.value = ''

  const validation = packageSchema.safeParse({
    name: formName.value,
    description: formDescription.value || null,
    base_price_mxn: formPrice.value,
    vehicle_type_id: formVehicleTypeId.value,
    workers_required: formWorkers.value,
    estimated_duration_minutes: formDuration.value,
    commission_per_worker_mxn: formCommission.value,
    service_ids: formServiceIds.value,
    sort_order: formSortOrder.value,
  })

  if (!validation.success) {
    formError.value = validation.error.errors[0].message
    return
  }

  formLoading.value = true
  try {
    await packageStore.createPackage({
      name: formName.value,
      description: formDescription.value || null,
      base_price_mxn: formPrice.value,
      vehicle_type_id: formVehicleTypeId.value,
      workers_required: formWorkers.value,
      estimated_duration_minutes: formDuration.value,
      commission_per_worker_mxn: formCommission.value,
      service_ids: formServiceIds.value,
      sort_order: formSortOrder.value,
    })
    showCreateModal.value = false
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      formError.value = axiosErr.response?.data?.detail || 'Error al crear paquete'
    } else {
      formError.value = 'Error al crear paquete'
    }
  } finally {
    formLoading.value = false
  }
}

async function handleUpdate() {
  if (!editingPackage.value) return

  formError.value = ''

  const validation = packageSchema.safeParse({
    name: formName.value,
    description: formDescription.value || null,
    base_price_mxn: formPrice.value,
    vehicle_type_id: formVehicleTypeId.value,
    workers_required: formWorkers.value,
    estimated_duration_minutes: formDuration.value,
    commission_per_worker_mxn: formCommission.value,
    service_ids: formServiceIds.value,
    sort_order: formSortOrder.value,
  })

  if (!validation.success) {
    formError.value = validation.error.errors[0].message
    return
  }

  formLoading.value = true
  try {
    await packageStore.updatePackage(editingPackage.value.id, {
      name: formName.value,
      description: formDescription.value || null,
      base_price_mxn: formPrice.value,
      vehicle_type_id: formVehicleTypeId.value,
      workers_required: formWorkers.value,
      estimated_duration_minutes: formDuration.value,
      commission_per_worker_mxn: formCommission.value,
      service_ids: formServiceIds.value,
      sort_order: formSortOrder.value,
    })
    showEditModal.value = false
    editingPackage.value = null
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      formError.value = axiosErr.response?.data?.detail || 'Error al actualizar paquete'
    } else {
      formError.value = 'Error al actualizar paquete'
    }
  } finally {
    formLoading.value = false
  }
}

async function handleDelete() {
  if (!deletingPackage.value) return

  formLoading.value = true
  try {
    await packageStore.deletePackage(deletingPackage.value.id)
    showDeleteConfirm.value = false
    deletingPackage.value = null
  } catch (err: unknown) {
    console.error('Error deleting package:', err)
  } finally {
    formLoading.value = false
  }
}

async function handleCreateVehicleType() {
  vtFormError.value = ''

  const validation = vehicleTypeSchema.safeParse({
    name: vtFormName.value,
    description: vtFormDescription.value || null,
    default_workers: vtFormWorkers.value,
    default_duration_minutes: vtFormDuration.value,
  })

  if (!validation.success) {
    vtFormError.value = validation.error.errors[0].message
    return
  }

  vtFormLoading.value = true
  try {
    await vehicleTypeStore.createVehicleType({
      name: vtFormName.value,
      description: vtFormDescription.value || null,
      default_workers: vtFormWorkers.value,
      default_duration_minutes: vtFormDuration.value,
    })
    showVehicleTypeModal.value = false
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      vtFormError.value = axiosErr.response?.data?.detail || 'Error al crear tipo de vehículo'
    } else {
      vtFormError.value = 'Error al crear tipo de vehículo'
    }
  } finally {
    vtFormLoading.value = false
  }
}

function formatPrice(price: number): string {
  return `$${price.toLocaleString('es-MX')}`
}

function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes} min`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return mins > 0 ? `${hours}h ${mins}min` : `${hours}h`
}
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <PageHeader title="Paquetes" subtitle="Configura los paquetes de servicios por tipo de vehículo.">
      <template #actions>
        <div v-if="authStore.isManager && locationStore.selectedLocationId" class="flex gap-2">
          <Button variant="outline" @click="openVehicleTypeModal">
            <Car class="mr-2 h-4 w-4" />
            Nuevo tipo de vehículo
          </Button>
          <Button @click="openCreateModal()">
            <Plus class="mr-2 h-4 w-4" />
            Nuevo paquete
          </Button>
        </div>
      </template>
    </PageHeader>

    <!-- No location selected -->
    <Alert v-if="!locationStore.selectedLocationId">
      Selecciona una sucursal para ver sus paquetes.
    </Alert>

    <!-- Loading state -->
    <Card v-else-if="packageStore.loading || vehicleTypeStore.loading">
      <CardContent class="p-6">
        <TableSkeleton :rows="4" :columns="4" />
      </CardContent>
    </Card>

    <!-- Empty state - no vehicle types -->
    <Card v-else-if="vehicleTypeStore.activeVehicleTypes.length === 0">
      <CardContent class="p-6">
        <EmptyState
          :icon="Car"
          title="No hay tipos de vehículo"
          description="Primero crea tipos de vehículo (Sedán, SUV, Camioneta, etc.) para organizar tus paquetes."
        >
          <template #primary>
            <Button v-if="authStore.isManager" @click="openVehicleTypeModal">
              <Plus class="mr-2 h-4 w-4" />
              Crear tipo de vehículo
            </Button>
          </template>
        </EmptyState>
      </CardContent>
    </Card>

    <!-- Packages grouped by vehicle type -->
    <template v-else>
      <div v-for="group in groupedPackages" :key="group.vehicleType.id" class="space-y-4">
        <Card>
          <CardHeader class="flex flex-row items-center justify-between pb-2">
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                <Car class="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle class="text-lg">{{ group.vehicleType.name }}</CardTitle>
                <p v-if="group.vehicleType.description" class="text-sm text-muted-foreground">
                  {{ group.vehicleType.description }}
                </p>
              </div>
            </div>
            <Button
              v-if="authStore.isManager"
              variant="ghost"
              size="sm"
              @click="openCreateModal(group.vehicleType.id)"
            >
              <Plus class="mr-1.5 h-4 w-4" />
              Agregar paquete
            </Button>
          </CardHeader>
          <CardContent>
            <!-- No packages for this vehicle type -->
            <div
              v-if="group.packages.length === 0"
              class="flex flex-col items-center justify-center py-8 text-center"
            >
              <Package2 class="mb-3 h-10 w-10 text-muted-foreground/50" />
              <p class="text-sm text-muted-foreground">
                No hay paquetes para {{ group.vehicleType.name }}
              </p>
            </div>

            <!-- Package cards grid -->
            <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <div
                v-for="pkg in group.packages"
                :key="pkg.id"
                class="group relative rounded-lg border bg-card p-4 transition-shadow hover:shadow-md"
              >
                <!-- Actions -->
                <div
                  v-if="authStore.isManager"
                  class="absolute right-2 top-2 flex gap-1 opacity-0 transition-opacity group-hover:opacity-100"
                >
                  <Button variant="ghost" size="icon" class="h-8 w-8" @click="openEditModal(pkg)">
                    <Pencil class="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    class="h-8 w-8 text-destructive"
                    @click="confirmDelete(pkg)"
                  >
                    <Trash2 class="h-4 w-4" />
                  </Button>
                </div>

                <!-- Package info -->
                <div class="mb-3">
                  <h4 class="font-semibold">{{ pkg.name }}</h4>
                  <p v-if="pkg.description" class="mt-1 text-sm text-muted-foreground line-clamp-2">
                    {{ pkg.description }}
                  </p>
                </div>

                <!-- Price -->
                <div class="mb-3 text-2xl font-bold text-primary">
                  {{ formatPrice(pkg.base_price_mxn) }}
                  <span class="text-sm font-normal text-muted-foreground">MXN</span>
                </div>

                <!-- Meta info -->
                <div class="flex flex-wrap gap-3 text-sm text-muted-foreground">
                  <div class="flex items-center gap-1">
                    <Users class="h-4 w-4" />
                    <span>{{ pkg.workers_required }} {{ pkg.workers_required === 1 ? 'trabajador' : 'trabajadores' }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <Clock class="h-4 w-4" />
                    <span>{{ formatDuration(pkg.estimated_duration_minutes) }}</span>
                  </div>
                  <div v-if="pkg.commission_per_worker_mxn" class="flex items-center gap-1">
                    <DollarSign class="h-4 w-4" />
                    <span>{{ formatPrice(pkg.commission_per_worker_mxn) }}/trabajador</span>
                  </div>
                </div>

                <!-- Services -->
                <div v-if="pkg.services.length > 0" class="mt-3 flex flex-wrap gap-1">
                  <Badge v-for="ps in pkg.services" :key="ps.id" variant="secondary" class="text-xs">
                    {{ ps.service.name }}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </template>

    <!-- Create Package Modal -->
    <Dialog v-model:open="showCreateModal" title="Nuevo paquete">
      <form class="space-y-4" @submit.prevent="handleCreate">
        <Alert v-if="formError" variant="destructive">
          {{ formError }}
        </Alert>
        <div class="space-y-2">
          <Label for="name">Nombre</Label>
          <Input
            id="name"
            v-model="formName"
            placeholder="Ej: Lavado Express"
            :disabled="formLoading"
          />
        </div>
        <div class="space-y-2">
          <Label for="description">Descripcion (opcional)</Label>
          <Input
            id="description"
            v-model="formDescription"
            placeholder="Breve descripcion del paquete"
            :disabled="formLoading"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="vehicle-type">Tipo de vehiculo</Label>
            <Select
              id="vehicle-type"
              v-model="formVehicleTypeId"
              :options="vehicleTypeOptions"
              placeholder="Seleccionar..."
              :disabled="formLoading"
              @update:model-value="onVehicleTypeChange"
            />
          </div>
          <div class="space-y-2">
            <Label for="price">Precio (MXN)</Label>
            <Input
              id="price"
              v-model.number="formPrice"
              type="number"
              min="0"
              :disabled="formLoading"
            />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="workers">Trabajadores</Label>
            <Input
              id="workers"
              v-model.number="formWorkers"
              type="number"
              min="1"
              max="20"
              :disabled="formLoading"
            />
          </div>
          <div class="space-y-2">
            <Label for="duration">Duracion (min)</Label>
            <Input
              id="duration"
              v-model.number="formDuration"
              type="number"
              min="1"
              max="600"
              :disabled="formLoading"
            />
          </div>
        </div>
        <div class="space-y-2">
          <Label for="commission">Comision por trabajador (MXN, opcional)</Label>
          <Input
            id="commission"
            v-model.number="formCommission"
            type="number"
            min="0"
            placeholder="Opcional"
            :disabled="formLoading"
          />
        </div>
        <div class="space-y-2">
          <Label>Servicios incluidos</Label>
          <MultiSelect
            v-model="formServiceIds"
            :options="serviceOptions"
            placeholder="Seleccionar servicios..."
            :disabled="formLoading"
          />
        </div>
        <div class="flex justify-end gap-3 border-t pt-4">
          <Button
            type="button"
            variant="outline"
            :disabled="formLoading"
            @click="showCreateModal = false"
          >
            Cancelar
          </Button>
          <Button type="submit" :disabled="formLoading">
            {{ formLoading ? 'Creando...' : 'Crear paquete' }}
          </Button>
        </div>
      </form>
    </Dialog>

    <!-- Edit Package Modal -->
    <Dialog v-model:open="showEditModal" title="Editar paquete">
      <form class="space-y-4" @submit.prevent="handleUpdate">
        <Alert v-if="formError" variant="destructive">
          {{ formError }}
        </Alert>
        <div class="space-y-2">
          <Label for="edit-name">Nombre</Label>
          <Input
            id="edit-name"
            v-model="formName"
            placeholder="Ej: Lavado Express"
            :disabled="formLoading"
          />
        </div>
        <div class="space-y-2">
          <Label for="edit-description">Descripcion (opcional)</Label>
          <Input
            id="edit-description"
            v-model="formDescription"
            placeholder="Breve descripcion del paquete"
            :disabled="formLoading"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="edit-vehicle-type">Tipo de vehiculo</Label>
            <Select
              id="edit-vehicle-type"
              v-model="formVehicleTypeId"
              :options="vehicleTypeOptions"
              placeholder="Seleccionar..."
              :disabled="formLoading"
            />
          </div>
          <div class="space-y-2">
            <Label for="edit-price">Precio (MXN)</Label>
            <Input
              id="edit-price"
              v-model.number="formPrice"
              type="number"
              min="0"
              :disabled="formLoading"
            />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="edit-workers">Trabajadores</Label>
            <Input
              id="edit-workers"
              v-model.number="formWorkers"
              type="number"
              min="1"
              max="20"
              :disabled="formLoading"
            />
          </div>
          <div class="space-y-2">
            <Label for="edit-duration">Duracion (min)</Label>
            <Input
              id="edit-duration"
              v-model.number="formDuration"
              type="number"
              min="1"
              max="600"
              :disabled="formLoading"
            />
          </div>
        </div>
        <div class="space-y-2">
          <Label for="edit-commission">Comision por trabajador (MXN, opcional)</Label>
          <Input
            id="edit-commission"
            v-model.number="formCommission"
            type="number"
            min="0"
            placeholder="Opcional"
            :disabled="formLoading"
          />
        </div>
        <div class="space-y-2">
          <Label>Servicios incluidos</Label>
          <MultiSelect
            v-model="formServiceIds"
            :options="serviceOptions"
            placeholder="Seleccionar servicios..."
            :disabled="formLoading"
          />
        </div>
        <div class="flex justify-end gap-3 border-t pt-4">
          <Button
            type="button"
            variant="outline"
            :disabled="formLoading"
            @click="showEditModal = false"
          >
            Cancelar
          </Button>
          <Button type="submit" :disabled="formLoading">
            {{ formLoading ? 'Guardando...' : 'Guardar cambios' }}
          </Button>
        </div>
      </form>
    </Dialog>

    <!-- Delete Confirmation Modal -->
    <Dialog v-model:open="showDeleteConfirm" title="Eliminar paquete">
      <div class="space-y-4">
        <p class="text-muted-foreground">
          Esta accion no se puede deshacer. El paquete sera eliminado permanentemente.
        </p>
        <div class="flex justify-end gap-3 border-t pt-4">
          <Button
            variant="outline"
            :disabled="formLoading"
            @click="showDeleteConfirm = false"
          >
            Cancelar
          </Button>
          <Button
            variant="destructive"
            :disabled="formLoading"
            @click="handleDelete"
          >
            {{ formLoading ? 'Eliminando...' : 'Eliminar' }}
          </Button>
        </div>
      </div>
    </Dialog>

    <!-- Vehicle Type Modal -->
    <Dialog v-model:open="showVehicleTypeModal" title="Nuevo tipo de vehiculo">
      <form class="space-y-4" @submit.prevent="handleCreateVehicleType">
        <Alert v-if="vtFormError" variant="destructive">
          {{ vtFormError }}
        </Alert>
        <div class="space-y-2">
          <Label for="vt-name">Nombre</Label>
          <Input
            id="vt-name"
            v-model="vtFormName"
            placeholder="Ej: Sedan, SUV, Camioneta"
            :disabled="vtFormLoading"
          />
        </div>
        <div class="space-y-2">
          <Label for="vt-description">Descripcion (opcional)</Label>
          <Input
            id="vt-description"
            v-model="vtFormDescription"
            placeholder="Breve descripcion"
            :disabled="vtFormLoading"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="vt-workers">Trabajadores por defecto</Label>
            <Input
              id="vt-workers"
              v-model.number="vtFormWorkers"
              type="number"
              min="1"
              max="20"
              :disabled="vtFormLoading"
            />
          </div>
          <div class="space-y-2">
            <Label for="vt-duration">Duracion por defecto (min)</Label>
            <Input
              id="vt-duration"
              v-model.number="vtFormDuration"
              type="number"
              min="1"
              max="600"
              :disabled="vtFormLoading"
            />
          </div>
        </div>
        <p class="text-xs text-muted-foreground">
          Estos valores se usaran como predeterminados al crear paquetes para este tipo de vehiculo.
        </p>
        <div class="flex justify-end gap-3 border-t pt-4">
          <Button
            type="button"
            variant="outline"
            :disabled="vtFormLoading"
            @click="showVehicleTypeModal = false"
          >
            Cancelar
          </Button>
          <Button type="submit" :disabled="vtFormLoading">
            {{ vtFormLoading ? 'Creando...' : 'Crear tipo' }}
          </Button>
        </div>
      </form>
    </Dialog>
  </div>
</template>
