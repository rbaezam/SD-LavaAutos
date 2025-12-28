<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Ticket, Plus, Eye, Car, Package2, ArrowLeft, Clock, Users, Check } from 'lucide-vue-next'
import {
  Alert,
  Badge,
  Button,
  Card,
  CardContent,
  Dialog,
  Input,
  Label,
  MultiSelect,
  Table,
} from '@/components/ui'
import PageHeader from '@/components/layout/PageHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import TicketStats from '@/components/tickets/TicketStats.vue'
import TicketFilters from '@/components/tickets/TicketFilters.vue'
import TableSkeleton from '@/components/table/TableSkeleton.vue'
import { useLocationStore } from '@/stores/location'
import { useStatusStore } from '@/stores/status'
import { useServiceStore } from '@/stores/service'
import { useTicketStore, type TicketCreate } from '@/stores/ticket'
import { useVehicleTypeStore } from '@/stores/vehicleType'
import { usePackageStore } from '@/stores/package'

const router = useRouter()
const locationStore = useLocationStore()
const statusStore = useStatusStore()
const serviceStore = useServiceStore()
const ticketStore = useTicketStore()
const vehicleTypeStore = useVehicleTypeStore()
const packageStore = usePackageStore()

// Filters
const filters = ref({
  search: '',
  statusId: 'all',
  datePreset: 'today' as 'today' | 'all',
})

// Modal state
const showCreateModal = ref(false)
const formLoading = ref(false)
const formError = ref('')

// Multi-step form state
const createStep = ref<'vehicle-type' | 'package' | 'details'>('vehicle-type')
const selectedVehicleTypeId = ref<string | null>(null)
const selectedPackageId = ref<string | null>(null)
const useLegacyMode = ref(false)

// Form state
const formPlate = ref('')
const formVehicleDesc = ref('')
const formManualTicketNo = ref('')
const formCustomerName = ref('')
const formCustomerWhatsapp = ref('')
const formServiceIds = ref<string[]>([])

const statusOptions = computed(() => [
  { value: 'all', label: 'Todos los estados' },
  ...statusStore.statuses.map((s) => ({ value: s.id, label: s.name })),
])

const serviceOptions = computed(() =>
  serviceStore.services
    .filter((s) => s.active)
    .map((s) => ({
      value: s.id,
      label: s.name,
      description: `${s.duration_minutes} min${s.price_mxn ? ` - $${s.price_mxn}` : ''}`,
    }))
)

// Get packages filtered by selected vehicle type
const packagesForVehicleType = computed(() => {
  if (!selectedVehicleTypeId.value) return []
  return packageStore.getPackagesByVehicleTypeId(selectedVehicleTypeId.value)
})

// Get selected package details
const selectedPackage = computed(() => {
  if (!selectedPackageId.value) return null
  return packageStore.getPackageById(selectedPackageId.value)
})

// Get selected vehicle type details
const selectedVehicleType = computed(() => {
  if (!selectedVehicleTypeId.value) return null
  return vehicleTypeStore.getVehicleTypeById(selectedVehicleTypeId.value)
})

// Check if packages are available
const hasPackages = computed(() => packageStore.activePackages.length > 0)

onMounted(() => {
  vehicleTypeStore.fetchVehicleTypes()
  packageStore.fetchPackages()
})

async function loadTickets() {
  if (!locationStore.selectedLocationId) return

  await ticketStore.listTickets(locationStore.selectedLocationId, {
    status_id: filters.value.statusId !== 'all' ? filters.value.statusId : undefined,
    q: filters.value.search || undefined,
    date: filters.value.datePreset !== 'all' ? filters.value.datePreset : undefined,
  })
}

function resetForm() {
  createStep.value = 'vehicle-type'
  selectedVehicleTypeId.value = null
  selectedPackageId.value = null
  useLegacyMode.value = false
  formPlate.value = ''
  formVehicleDesc.value = ''
  formManualTicketNo.value = ''
  formCustomerName.value = ''
  formCustomerWhatsapp.value = ''
  formServiceIds.value = []
  formError.value = ''
}

function openCreateModal() {
  resetForm()
  // If no packages exist, go directly to legacy mode
  if (!hasPackages.value) {
    useLegacyMode.value = true
    createStep.value = 'details'
  }
  showCreateModal.value = true
}

function selectVehicleType(vehicleTypeId: string) {
  selectedVehicleTypeId.value = vehicleTypeId
  createStep.value = 'package'
}

function selectPackage(packageId: string) {
  selectedPackageId.value = packageId
  createStep.value = 'details'
}

function goBackToVehicleType() {
  createStep.value = 'vehicle-type'
  selectedVehicleTypeId.value = null
  selectedPackageId.value = null
}

function goBackToPackage() {
  createStep.value = 'package'
  selectedPackageId.value = null
}

function switchToLegacyMode() {
  useLegacyMode.value = true
  createStep.value = 'details'
  selectedVehicleTypeId.value = null
  selectedPackageId.value = null
}

async function handleCreate() {
  if (!locationStore.selectedLocationId) return

  formError.value = ''
  formLoading.value = true

  try {
    const data: TicketCreate = {
      plate: formPlate.value || null,
      vehicle_desc: formVehicleDesc.value || null,
      manual_ticket_no: formManualTicketNo.value || null,
      customer_name: formCustomerName.value || null,
      customer_whatsapp: formCustomerWhatsapp.value || null,
    }

    // If using package mode
    if (selectedPackageId.value && selectedVehicleTypeId.value) {
      data.package_id = selectedPackageId.value
      data.vehicle_type_id = selectedVehicleTypeId.value
    } else {
      // Legacy mode - use service_ids
      data.service_ids = formServiceIds.value
    }

    const ticket = await ticketStore.createTicket(locationStore.selectedLocationId, data)
    showCreateModal.value = false
    router.push({ name: 'ticket-detail', params: { id: ticket.id } })
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      formError.value = axiosErr.response?.data?.detail || 'Error al crear ticket'
    } else {
      formError.value = 'Error al crear ticket'
    }
  } finally {
    formLoading.value = false
  }
}

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('es-MX', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatEta(etaStr: string | null): string {
  if (!etaStr) return '—'
  const eta = new Date(etaStr)
  return eta.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })
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

function goToDetail(ticketId: string) {
  router.push({ name: 'ticket-detail', params: { id: ticketId } })
}

function showAllDates() {
  filters.value.datePreset = 'all'
}

// Modal title based on step
const modalTitle = computed(() => {
  if (useLegacyMode.value) return 'Nuevo ticket'
  switch (createStep.value) {
    case 'vehicle-type':
      return 'Tipo de vehiculo'
    case 'package':
      return 'Seleccionar paquete'
    case 'details':
      return 'Datos del ticket'
    default:
      return 'Nuevo ticket'
  }
})

// Watch for filter changes
watch(
  filters,
  () => {
    loadTickets()
  },
  { deep: true }
)

// Watch for location changes - immediate ensures it runs on mount too
watch(
  () => locationStore.selectedLocationId,
  (locationId) => {
    if (locationId) {
      loadTickets()
    }
  },
  { immediate: true }
)
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <PageHeader
      title="Tickets"
      subtitle="Registra vehiculos y controla su progreso."
    >
      <template #actions>
        <Button v-if="locationStore.selectedLocationId" @click="openCreateModal">
          <Plus class="mr-2 h-4 w-4" />
          Nuevo ticket
        </Button>
      </template>
    </PageHeader>

    <!-- No location selected -->
    <Alert v-if="!locationStore.selectedLocationId">
      Selecciona una sucursal para ver y crear tickets.
    </Alert>

    <template v-else>
      <!-- Stats -->
      <TicketStats :tickets="ticketStore.tickets" :loading="ticketStore.loading" />

      <!-- Main Content Card -->
      <Card>
        <CardContent class="p-6">
          <!-- Filters -->
          <TicketFilters
            v-model="filters"
            :status-options="statusOptions"
            class="mb-6"
          />

          <!-- Loading state -->
          <TableSkeleton v-if="ticketStore.loading" :rows="5" :columns="7" />

          <!-- Empty state -->
          <EmptyState
            v-else-if="ticketStore.tickets.length === 0"
            :icon="Ticket"
            title="No hay tickets"
            :description="
              filters.datePreset === 'today'
                ? 'Aun no has registrado vehiculos hoy.'
                : 'No se encontraron tickets con los filtros seleccionados.'
            "
            tip="Usa placas o una descripcion rapida como 'Auto rojo' para encontrarlo mas facil."
          >
            <template #primary>
              <Button @click="openCreateModal">
                <Plus class="mr-2 h-4 w-4" />
                Crear ticket
              </Button>
            </template>
            <template v-if="filters.datePreset === 'today'" #secondary>
              <Button variant="ghost" @click="showAllDates">
                Ver todos
              </Button>
            </template>
          </EmptyState>

          <!-- Table -->
          <Table v-else>
            <thead>
              <tr class="border-b">
                <th class="py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Folio
                </th>
                <th class="py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Vehiculo
                </th>
                <th class="hidden py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground md:table-cell">
                  Servicios
                </th>
                <th class="py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Estado
                </th>
                <th class="hidden py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground sm:table-cell">
                  ETA
                </th>
                <th class="hidden py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground lg:table-cell">
                  Creado
                </th>
                <th class="py-3 text-right text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  <span class="sr-only">Acciones</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="ticket in ticketStore.tickets"
                :key="ticket.id"
                class="group border-b transition-colors last:border-0 hover:bg-muted/50"
              >
                <td class="py-4">
                  <span class="font-mono text-sm font-semibold">{{ ticket.public_code }}</span>
                </td>
                <td class="py-4">
                  <div v-if="ticket.plate || ticket.vehicle_desc" class="space-y-0.5">
                    <span v-if="ticket.plate" class="block text-sm font-medium">{{ ticket.plate }}</span>
                    <span v-if="ticket.vehicle_desc" class="block text-xs text-muted-foreground">
                      {{ ticket.vehicle_desc }}
                    </span>
                  </div>
                  <span v-else class="text-sm text-muted-foreground">—</span>
                </td>
                <td class="hidden py-4 md:table-cell">
                  <span v-if="ticket.services_summary" class="text-sm text-muted-foreground">
                    {{ ticket.services_summary }}
                  </span>
                  <span v-else class="text-sm text-muted-foreground">—</span>
                </td>
                <td class="py-4">
                  <Badge
                    :variant="ticket.current_status.is_terminal ? 'success' : 'default'"
                  >
                    {{ ticket.current_status.name }}
                  </Badge>
                </td>
                <td class="hidden py-4 sm:table-cell">
                  <span class="text-sm text-muted-foreground">{{ formatEta(ticket.eta_at) }}</span>
                </td>
                <td class="hidden py-4 lg:table-cell">
                  <span class="text-sm text-muted-foreground">{{ formatDateTime(ticket.created_at) }}</span>
                </td>
                <td class="py-4 text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    class="opacity-0 transition-opacity group-hover:opacity-100"
                    @click="goToDetail(ticket.id)"
                  >
                    <Eye class="mr-1.5 h-4 w-4" />
                    Ver
                  </Button>
                </td>
              </tr>
            </tbody>
          </Table>
        </CardContent>
      </Card>
    </template>

    <!-- Create Modal -->
    <Dialog v-model:open="showCreateModal" :title="modalTitle">
      <!-- Step 1: Vehicle Type Selection -->
      <div v-if="createStep === 'vehicle-type' && !useLegacyMode" class="space-y-4">
        <p class="text-sm text-muted-foreground">
          Selecciona el tipo de vehiculo para ver los paquetes disponibles.
        </p>

        <!-- Vehicle Type Grid -->
        <div class="grid gap-3 sm:grid-cols-2">
          <button
            v-for="vt in vehicleTypeStore.activeVehicleTypes"
            :key="vt.id"
            type="button"
            class="flex flex-col items-center gap-2 rounded-lg border-2 border-muted bg-card p-4 text-center transition-all hover:border-primary hover:bg-primary/5"
            @click="selectVehicleType(vt.id)"
          >
            <div class="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <Car class="h-6 w-6 text-primary" />
            </div>
            <span class="font-medium">{{ vt.name }}</span>
            <span v-if="vt.description" class="text-xs text-muted-foreground">
              {{ vt.description }}
            </span>
          </button>
        </div>

        <!-- Legacy mode link -->
        <div class="border-t pt-4 text-center">
          <button
            type="button"
            class="text-sm text-muted-foreground hover:text-foreground hover:underline"
            @click="switchToLegacyMode"
          >
            Crear ticket sin paquete (modo manual)
          </button>
        </div>
      </div>

      <!-- Step 2: Package Selection -->
      <div v-else-if="createStep === 'package' && !useLegacyMode" class="space-y-4">
        <!-- Back button -->
        <button
          type="button"
          class="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
          @click="goBackToVehicleType"
        >
          <ArrowLeft class="h-4 w-4" />
          <span>Cambiar tipo de vehiculo</span>
        </button>

        <!-- Selected vehicle type -->
        <div v-if="selectedVehicleType" class="flex items-center gap-2 rounded-lg bg-muted/50 px-3 py-2">
          <Car class="h-4 w-4 text-muted-foreground" />
          <span class="text-sm font-medium">{{ selectedVehicleType.name }}</span>
        </div>

        <!-- Package Grid -->
        <div v-if="packagesForVehicleType.length > 0" class="grid gap-3">
          <button
            v-for="pkg in packagesForVehicleType"
            :key="pkg.id"
            type="button"
            class="flex flex-col gap-2 rounded-lg border-2 border-muted bg-card p-4 text-left transition-all hover:border-primary hover:bg-primary/5"
            @click="selectPackage(pkg.id)"
          >
            <div class="flex items-start justify-between">
              <div>
                <span class="font-semibold">{{ pkg.name }}</span>
                <p v-if="pkg.description" class="mt-0.5 text-sm text-muted-foreground">
                  {{ pkg.description }}
                </p>
              </div>
              <span class="text-lg font-bold text-primary">
                {{ formatPrice(pkg.base_price_mxn) }}
              </span>
            </div>
            <div class="flex flex-wrap gap-3 text-xs text-muted-foreground">
              <span class="flex items-center gap-1">
                <Clock class="h-3.5 w-3.5" />
                {{ formatDuration(pkg.estimated_duration_minutes) }}
              </span>
              <span class="flex items-center gap-1">
                <Users class="h-3.5 w-3.5" />
                {{ pkg.workers_required }} {{ pkg.workers_required === 1 ? 'trabajador' : 'trabajadores' }}
              </span>
            </div>
            <!-- Services included -->
            <div v-if="pkg.services.length > 0" class="flex flex-wrap gap-1">
              <Badge v-for="ps in pkg.services" :key="ps.id" variant="secondary" class="text-xs">
                {{ ps.service.name }}
              </Badge>
            </div>
          </button>
        </div>

        <!-- No packages -->
        <div v-else class="py-8 text-center">
          <Package2 class="mx-auto mb-3 h-10 w-10 text-muted-foreground/50" />
          <p class="text-sm text-muted-foreground">
            No hay paquetes para este tipo de vehiculo.
          </p>
          <Button variant="link" class="mt-2" @click="switchToLegacyMode">
            Crear ticket sin paquete
          </Button>
        </div>
      </div>

      <!-- Step 3: Details Form -->
      <form v-else class="space-y-6" @submit.prevent="handleCreate">
        <Alert v-if="formError" variant="destructive">
          {{ formError }}
        </Alert>

        <!-- Package Summary (if using package mode) -->
        <div v-if="selectedPackage && !useLegacyMode" class="space-y-3">
          <button
            type="button"
            class="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
            @click="goBackToPackage"
          >
            <ArrowLeft class="h-4 w-4" />
            <span>Cambiar paquete</span>
          </button>

          <div class="rounded-lg border bg-primary/5 p-4">
            <div class="flex items-start justify-between">
              <div>
                <div class="flex items-center gap-2">
                  <Package2 class="h-5 w-5 text-primary" />
                  <span class="font-semibold">{{ selectedPackage.name }}</span>
                </div>
                <div v-if="selectedVehicleType" class="mt-1 flex items-center gap-1 text-sm text-muted-foreground">
                  <Car class="h-3.5 w-3.5" />
                  {{ selectedVehicleType.name }}
                </div>
              </div>
              <span class="text-xl font-bold text-primary">
                {{ formatPrice(selectedPackage.base_price_mxn) }}
              </span>
            </div>
            <div class="mt-3 flex flex-wrap gap-4 text-sm text-muted-foreground">
              <span class="flex items-center gap-1">
                <Clock class="h-4 w-4" />
                {{ formatDuration(selectedPackage.estimated_duration_minutes) }}
              </span>
              <span class="flex items-center gap-1">
                <Users class="h-4 w-4" />
                {{ selectedPackage.workers_required }} {{ selectedPackage.workers_required === 1 ? 'trabajador' : 'trabajadores' }}
              </span>
            </div>
            <!-- Services -->
            <div v-if="selectedPackage.services.length > 0" class="mt-3 flex flex-wrap gap-1">
              <Badge v-for="ps in selectedPackage.services" :key="ps.id" variant="secondary" class="text-xs">
                <Check class="mr-1 h-3 w-3" />
                {{ ps.service.name }}
              </Badge>
            </div>
          </div>
        </div>

        <!-- Legacy mode header -->
        <div v-if="useLegacyMode && hasPackages" class="mb-4">
          <button
            type="button"
            class="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
            @click="resetForm"
          >
            <ArrowLeft class="h-4 w-4" />
            <span>Usar paquetes</span>
          </button>
        </div>

        <!-- Vehicle Section -->
        <div class="space-y-4">
          <h3 class="text-sm font-medium text-muted-foreground">Vehiculo</h3>
          <div class="grid gap-4 sm:grid-cols-2">
            <div class="space-y-2">
              <Label for="plate">Placas</Label>
              <Input
                id="plate"
                v-model="formPlate"
                placeholder="ABC-123"
                :disabled="formLoading"
              />
              <p class="text-xs text-muted-foreground">Opcional</p>
            </div>
            <div class="space-y-2">
              <Label for="manual-ticket">Folio fisico</Label>
              <Input
                id="manual-ticket"
                v-model="formManualTicketNo"
                placeholder="001234"
                :disabled="formLoading"
              />
              <p class="text-xs text-muted-foreground">Si usas boletos impresos</p>
            </div>
          </div>
          <div class="space-y-2">
            <Label for="vehicle-desc">Descripcion del vehiculo</Label>
            <Input
              id="vehicle-desc"
              v-model="formVehicleDesc"
              placeholder="Toyota Corolla Blanco"
              :disabled="formLoading"
            />
            <p class="text-xs text-muted-foreground">Ayuda a identificar el vehiculo rapidamente</p>
          </div>
        </div>

        <!-- Customer Section -->
        <div class="space-y-4">
          <h3 class="text-sm font-medium text-muted-foreground">Cliente</h3>
          <div class="grid gap-4 sm:grid-cols-2">
            <div class="space-y-2">
              <Label for="customer-name">Nombre</Label>
              <Input
                id="customer-name"
                v-model="formCustomerName"
                placeholder="Juan Perez"
                :disabled="formLoading"
              />
            </div>
            <div class="space-y-2">
              <Label for="customer-whatsapp">WhatsApp</Label>
              <Input
                id="customer-whatsapp"
                v-model="formCustomerWhatsapp"
                placeholder="9991234567"
                :disabled="formLoading"
              />
              <p class="text-xs text-muted-foreground">Ej: 9991234567 o +52...</p>
            </div>
          </div>
        </div>

        <!-- Services Section (Legacy mode only) -->
        <div v-if="useLegacyMode" class="space-y-4">
          <h3 class="text-sm font-medium text-muted-foreground">Servicios</h3>
          <MultiSelect
            v-model="formServiceIds"
            :options="serviceOptions"
            placeholder="Selecciona los servicios a realizar"
            :disabled="formLoading"
          />
        </div>

        <!-- Actions -->
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
            {{ formLoading ? 'Creando...' : 'Crear ticket' }}
          </Button>
        </div>
      </form>
    </Dialog>
  </div>
</template>
