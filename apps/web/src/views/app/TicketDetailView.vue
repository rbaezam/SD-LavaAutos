<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft,
  Bell,
  Car,
  ChevronRight,
  Clock,
  ClipboardList,
  History,
  RefreshCw,
  Save,
  Share2,
  User,
  AlertCircle,
  Pencil,
  Plus,
} from 'lucide-vue-next'
import {
  Alert,
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Input,
  Label,
  MultiSelect,
  Select,
} from '@/components/ui'
import ActivityTimeline from '@/components/tickets/ActivityTimeline.vue'
import ShareTicketDialog from '@/components/tickets/ShareTicketDialog.vue'
import TicketDetailSkeleton from '@/components/tickets/TicketDetailSkeleton.vue'
import { SendNotificationDialog, NotificationHistory } from '@/components/notifications'
import { useNotificationStore } from '@/stores/notification'
import { useAuthStore } from '@/stores/auth'
import { useLocationStore } from '@/stores/location'
import { useStatusStore } from '@/stores/status'
import { useServiceStore } from '@/stores/service'
import { useTicketStore, type TicketUpdate } from '@/stores/ticket'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const locationStore = useLocationStore()
const statusStore = useStatusStore()
const serviceStore = useServiceStore()
const ticketStore = useTicketStore()
const notificationStore = useNotificationStore()

const ticketId = computed(() => route.params.id as string)

// Form state
const formPlate = ref('')
const formVehicleDesc = ref('')
const formManualTicketNo = ref('')
const formCustomerName = ref('')
const formCustomerWhatsapp = ref('')
const formServiceIds = ref<string[]>([])
const formStatusId = ref('')
const formEtaAt = ref('')

// UI state
const showEtaEditor = ref(false)

// Loading states
const initialLoading = ref(true)
const eventsLoading = ref(false)
const formLoading = ref(false)
const statusLoading = ref(false)
const etaLoading = ref(false)
const isRefreshing = ref(false)

// Toast state
const toast = ref<{ message: string; type: 'success' | 'error' } | null>(null)
const toastTimeout = ref<ReturnType<typeof setTimeout> | null>(null)

// Share dialog state
const shareDialogOpen = ref(false)

// Notification dialog state
const notificationDialogOpen = ref(false)

function showToast(message: string, type: 'success' | 'error' = 'success') {
  if (toastTimeout.value) clearTimeout(toastTimeout.value)
  toast.value = { message, type }
  toastTimeout.value = setTimeout(() => {
    toast.value = null
  }, 4000)
}

// Vehicle label for sharing
const vehicleLabel = computed(() => {
  if (!ticketStore.currentTicket) return ''
  return ticketStore.currentTicket.plate || ticketStore.currentTicket.vehicle_desc || 'Vehículo'
})

// Track if there are unsaved changes
const hasChanges = computed(() => {
  if (!ticketStore.currentTicket) return false
  const ticket = ticketStore.currentTicket
  return (
    formPlate.value !== (ticket.plate || '') ||
    formVehicleDesc.value !== (ticket.vehicle_desc || '') ||
    formManualTicketNo.value !== (ticket.manual_ticket_no || '') ||
    formCustomerName.value !== (ticket.customer_name || '') ||
    formCustomerWhatsapp.value !== (ticket.customer_whatsapp || '') ||
    hasServiceChanges.value
  )
})

const hasServiceChanges = computed(() => {
  if (!ticketStore.currentTicket) return false
  const currentIds = ticketStore.currentTicket.services
    .map((s) => s.service_id)
    .filter(Boolean) as string[]
  return (
    formServiceIds.value.length !== currentIds.length ||
    formServiceIds.value.some((id) => !currentIds.includes(id))
  )
})

const hasStatusChange = computed(() => {
  if (!ticketStore.currentTicket) return false
  return formStatusId.value !== ticketStore.currentTicket.current_status_id
})

const hasEtaChange = computed(() => {
  if (!ticketStore.currentTicket) return false
  const currentEta = ticketStore.currentTicket.eta_at
    ? formatDateTimeLocal(ticketStore.currentTicket.eta_at)
    : ''
  return formEtaAt.value !== currentEta
})

// Status options with permission check
const statusOptions = computed(() => {
  return statusStore.statuses.map((s) => {
    const isTerminal = s.is_terminal
    const isStaff = authStore.user?.role === 'staff'
    const disabled = isTerminal && isStaff

    return {
      value: s.id,
      label: s.name,
      disabled,
      description: disabled ? 'No tienes permisos para finalizar un ticket' : undefined,
    }
  })
})

// Check if all terminal statuses are disabled for staff
const hasTerminalRestriction = computed(() => {
  const isStaff = authStore.user?.role === 'staff'
  return isStaff && statusStore.statuses.some((s) => s.is_terminal)
})

const serviceOptions = computed(() =>
  serviceStore.services
    .filter((s) => s.active)
    .map((s) => ({
      value: s.id,
      label: s.name,
      description: `${s.duration_minutes} min${s.price_mxn ? ` · $${s.price_mxn}` : ''}`,
    }))
)

const totalDuration = computed(() => {
  if (!formServiceIds.value.length) return 0
  return serviceStore.services
    .filter((s) => formServiceIds.value.includes(s.id))
    .reduce((sum, s) => sum + s.duration_minutes, 0)
})

const totalPrice = computed(() => {
  if (!formServiceIds.value.length) return null
  const prices = serviceStore.services
    .filter((s) => formServiceIds.value.includes(s.id))
    .map((s) => s.price_mxn)

  if (prices.some((p) => p === null)) return null
  return prices.reduce((sum: number, p) => sum + (p || 0), 0)
})

// Location name for the ticket
const ticketLocationName = computed(() => {
  if (!ticketStore.currentTicket) return null
  const location = locationStore.locations.find(
    (l) => l.id === ticketStore.currentTicket?.location_id
  )
  return location?.name || null
})

// Current status info
const currentStatus = computed(() => {
  if (!ticketStore.currentTicket) return null
  return ticketStore.currentTicket.current_status
})

// Formatted ETA display
const formattedEta = computed(() => {
  if (!ticketStore.currentTicket?.eta_at) return null
  const eta = new Date(ticketStore.currentTicket.eta_at)
  const today = new Date()
  const isToday = eta.toDateString() === today.toDateString()

  if (isToday) {
    return `Hoy, ${eta.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })}`
  }

  return eta.toLocaleString('es-MX', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
})

function syncFormWithTicket() {
  if (!ticketStore.currentTicket) return
  const ticket = ticketStore.currentTicket

  formPlate.value = ticket.plate || ''
  formVehicleDesc.value = ticket.vehicle_desc || ''
  formManualTicketNo.value = ticket.manual_ticket_no || ''
  formCustomerName.value = ticket.customer_name || ''
  formCustomerWhatsapp.value = ticket.customer_whatsapp || ''
  formServiceIds.value = ticket.services.map((s) => s.service_id).filter(Boolean) as string[]
  formStatusId.value = ticket.current_status_id
  formEtaAt.value = ticket.eta_at ? formatDateTimeLocal(ticket.eta_at) : ''
  showEtaEditor.value = false
}

function formatDateTimeLocal(isoStr: string): string {
  const date = new Date(isoStr)
  return date.toISOString().slice(0, 16)
}

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('es-MX', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Ahora'
  if (diffMins < 60) return `Hace ${diffMins} min`

  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `Hace ${diffHours}h`

  const diffDays = Math.floor(diffHours / 24)
  return `Hace ${diffDays} día${diffDays > 1 ? 's' : ''}`
}

async function loadTicket() {
  initialLoading.value = true
  eventsLoading.value = true

  try {
    await ticketStore.getTicket(ticketId.value)
    syncFormWithTicket()

    // Load events and notification logs in parallel
    ticketStore.listEvents(ticketId.value).finally(() => {
      eventsLoading.value = false
    })
    notificationStore.fetchLogs(ticketId.value)
  } catch {
    showToast('Error al cargar el ticket', 'error')
    router.push({ name: 'tickets' })
  } finally {
    initialLoading.value = false
  }
}

function handleNotificationSent(result: { success: boolean; simulated: boolean }) {
  if (result.success) {
    showToast(result.simulated ? 'Notificación simulada' : 'Notificación enviada')
    // Refresh notification logs
    notificationStore.fetchLogs(ticketId.value)
  }
}

async function handleRefresh() {
  if (isRefreshing.value) return
  isRefreshing.value = true
  eventsLoading.value = true

  try {
    await ticketStore.getTicket(ticketId.value)
    syncFormWithTicket()
    await ticketStore.listEvents(ticketId.value)
  } catch {
    showToast('Error al actualizar', 'error')
  } finally {
    isRefreshing.value = false
    eventsLoading.value = false
  }
}

async function saveChanges() {
  if (!hasChanges.value || formLoading.value) return

  formLoading.value = true

  try {
    const data: TicketUpdate = {
      plate: formPlate.value || null,
      vehicle_desc: formVehicleDesc.value || null,
      manual_ticket_no: formManualTicketNo.value || null,
      customer_name: formCustomerName.value || null,
      customer_whatsapp: formCustomerWhatsapp.value || null,
      service_ids: formServiceIds.value,
    }
    await ticketStore.updateTicket(ticketId.value, data)
    await ticketStore.listEvents(ticketId.value)
    showToast('Ticket actualizado')
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      showToast(axiosErr.response?.data?.detail || 'No se pudo guardar. Intenta de nuevo.', 'error')
    } else {
      showToast('No se pudo guardar. Intenta de nuevo.', 'error')
    }
  } finally {
    formLoading.value = false
  }
}

async function changeStatus() {
  if (!hasStatusChange.value || statusLoading.value) return

  // Check permission for terminal status
  const toStatus = statusStore.statuses.find((s) => s.id === formStatusId.value)
  if (toStatus?.is_terminal && authStore.user?.role === 'staff') {
    showToast('No tienes permisos para finalizar un ticket', 'error')
    // Reset to current status
    if (ticketStore.currentTicket) {
      formStatusId.value = ticketStore.currentTicket.current_status_id
    }
    return
  }

  statusLoading.value = true
  const previousStatusId = ticketStore.currentTicket?.current_status_id

  try {
    await ticketStore.moveTicket(ticketId.value, formStatusId.value)
    await ticketStore.listEvents(ticketId.value)
    showToast('Estado actualizado')
  } catch (err: unknown) {
    // Rollback
    if (previousStatusId) {
      formStatusId.value = previousStatusId
    }
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      showToast(
        axiosErr.response?.data?.detail || 'No se pudo cambiar el estado. Intenta de nuevo.',
        'error'
      )
    } else {
      showToast('No se pudo cambiar el estado. Intenta de nuevo.', 'error')
    }
  } finally {
    statusLoading.value = false
  }
}

async function saveEta() {
  if (etaLoading.value) return

  etaLoading.value = true

  try {
    const etaAt = formEtaAt.value ? new Date(formEtaAt.value).toISOString() : null
    await ticketStore.updateEta(ticketId.value, etaAt)
    await ticketStore.listEvents(ticketId.value)
    showToast('ETA actualizada')
    showEtaEditor.value = false
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      showToast(axiosErr.response?.data?.detail || 'No se pudo guardar. Intenta de nuevo.', 'error')
    } else {
      showToast('No se pudo guardar. Intenta de nuevo.', 'error')
    }
  } finally {
    etaLoading.value = false
  }
}

function goBack() {
  router.push({ name: 'tickets' })
}

// Keyboard shortcut: Ctrl/Cmd + S to save
function handleKeyDown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 's') {
    e.preventDefault()
    if (hasChanges.value && !formLoading.value) {
      saveChanges()
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

// Load ticket on mount and watch for changes
watch(
  ticketId,
  () => {
    loadTicket()
  },
  { immediate: true }
)
</script>

<template>
  <div class="space-y-6">
    <!-- Toast notification -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="transform -translate-y-2 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform -translate-y-2 opacity-0"
    >
      <div v-if="toast" class="fixed left-1/2 top-20 z-50 -translate-x-1/2">
        <Alert
          :variant="toast.type === 'error' ? 'destructive' : 'default'"
          :class="[
            'flex items-center gap-2 shadow-lg',
            toast.type === 'success' && 'border-green-500 bg-green-50 text-green-800',
          ]"
        >
          {{ toast.message }}
        </Alert>
      </div>
    </Transition>

    <!-- Loading skeleton -->
    <TicketDetailSkeleton v-if="initialLoading" />

    <!-- Ticket content -->
    <template v-else-if="ticketStore.currentTicket">
      <!-- Header -->
      <div class="space-y-4">
        <!-- Breadcrumb -->
        <nav class="flex items-center gap-1 text-sm text-muted-foreground">
          <button class="transition-colors hover:text-foreground" @click="goBack">
            <ArrowLeft class="mr-1 inline-block h-4 w-4" />
            Tickets
          </button>
          <ChevronRight class="h-4 w-4" />
          <span class="font-medium text-foreground">
            {{ ticketStore.currentTicket.public_code }}
          </span>
        </nav>

        <!-- Title row with badge and actions -->
        <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div class="space-y-3">
            <!-- Folio + Status Badge -->
            <div class="flex flex-wrap items-center gap-3">
              <h1 class="font-mono text-2xl font-bold tracking-tight sm:text-3xl">
                {{ ticketStore.currentTicket.public_code }}
              </h1>
              <Badge
                :variant="currentStatus?.is_terminal ? 'success' : 'default'"
                class="px-3 py-1 text-sm font-semibold"
              >
                {{ currentStatus?.name }}
              </Badge>
            </div>

            <!-- Meta info line -->
            <p class="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-muted-foreground">
              <span>Creado: {{ formatDateTime(ticketStore.currentTicket.created_at) }}</span>
              <span>·</span>
              <span>{{ formatRelativeTime(ticketStore.currentTicket.created_at) }}</span>
              <template v-if="ticketLocationName">
                <span>·</span>
                <span>Sucursal: {{ ticketLocationName }}</span>
              </template>
            </p>
          </div>

          <!-- Action buttons -->
          <div class="flex items-center gap-2">
            <!-- Unsaved changes indicator -->
            <span
              v-if="hasChanges"
              class="flex items-center gap-1 text-sm text-amber-600"
            >
              <AlertCircle class="h-4 w-4" />
              <span class="hidden sm:inline">Cambios sin guardar</span>
            </span>

            <Button
              variant="outline"
              size="sm"
              title="Enviar notificación al cliente"
              @click="notificationDialogOpen = true"
            >
              <Bell class="mr-2 h-4 w-4" />
              <span class="hidden sm:inline">Notificar</span>
            </Button>

            <Button
              variant="outline"
              size="sm"
              title="Compartir con cliente"
              @click="shareDialogOpen = true"
            >
              <Share2 class="mr-2 h-4 w-4" />
              <span class="hidden sm:inline">Compartir</span>
            </Button>

            <Button
              variant="ghost"
              size="icon"
              :disabled="isRefreshing"
              title="Actualizar"
              @click="handleRefresh"
            >
              <RefreshCw :class="['h-4 w-4', isRefreshing && 'animate-spin']" />
            </Button>

            <Button
              :disabled="!hasChanges || formLoading"
              @click="saveChanges"
            >
              <Save class="mr-2 h-4 w-4" />
              {{ formLoading ? 'Guardando...' : 'Guardar cambios' }}
            </Button>
          </div>
        </div>
      </div>

      <!-- Two-column layout -->
      <div class="grid gap-6 lg:grid-cols-[1fr_380px]">
        <!-- Left column (main) -->
        <div class="space-y-6">
          <!-- Vehicle Card -->
          <Card>
            <CardHeader class="pb-4">
              <CardTitle class="flex items-center gap-2 text-base">
                <Car class="h-5 w-5 text-muted-foreground" />
                Vehículo
              </CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="grid gap-4 sm:grid-cols-2">
                <div class="space-y-2">
                  <Label for="plate">Placas</Label>
                  <Input
                    id="plate"
                    v-model="formPlate"
                    placeholder="ABC-123"
                    :disabled="formLoading"
                  />
                </div>
                <div class="space-y-2">
                  <Label for="manual-ticket">Folio físico</Label>
                  <Input
                    id="manual-ticket"
                    v-model="formManualTicketNo"
                    placeholder="001234"
                    :disabled="formLoading"
                  />
                </div>
              </div>
              <div class="space-y-2">
                <Label for="vehicle-desc">Descripción del vehículo</Label>
                <Input
                  id="vehicle-desc"
                  v-model="formVehicleDesc"
                  placeholder="Toyota Corolla Blanco"
                  :disabled="formLoading"
                />
              </div>
            </CardContent>
          </Card>

          <!-- Customer Card -->
          <Card>
            <CardHeader class="pb-4">
              <CardTitle class="flex items-center gap-2 text-base">
                <User class="h-5 w-5 text-muted-foreground" />
                Cliente
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid gap-4 sm:grid-cols-2">
                <div class="space-y-2">
                  <Label for="customer-name">Nombre</Label>
                  <Input
                    id="customer-name"
                    v-model="formCustomerName"
                    placeholder="Juan Pérez"
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
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Services Card -->
          <Card>
            <CardHeader class="pb-4">
              <CardTitle class="flex items-center gap-2 text-base">
                <ClipboardList class="h-5 w-5 text-muted-foreground" />
                Servicios
              </CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <!-- Empty state -->
              <div
                v-if="formServiceIds.length === 0 && serviceOptions.length > 0"
                class="rounded-lg border border-dashed p-4 text-center"
              >
                <Plus class="mx-auto mb-2 h-8 w-8 text-muted-foreground/50" />
                <p class="text-sm text-muted-foreground">
                  No hay servicios asignados. Agrega uno para estimar duración.
                </p>
              </div>

              <MultiSelect
                v-model="formServiceIds"
                :options="serviceOptions"
                placeholder="Selecciona los servicios"
                :disabled="formLoading"
              />

              <!-- Totals -->
              <div
                v-if="formServiceIds.length > 0"
                class="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted-foreground"
              >
                <span>
                  Duración estimada:
                  <strong class="text-foreground">{{ totalDuration }} min</strong>
                </span>
                <span v-if="totalPrice !== null">
                  Costo estimado:
                  <strong class="text-foreground"
                    >${{ totalPrice.toLocaleString('es-MX') }}</strong
                  >
                </span>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Right column (sidebar) - sticky -->
        <div class="space-y-6 lg:sticky lg:top-6 lg:self-start">
          <!-- Status Card -->
          <Card>
            <CardHeader class="pb-3">
              <CardTitle class="text-base">Estado</CardTitle>
              <p class="text-xs text-muted-foreground">
                Actualiza el estado del vehículo según el progreso.
              </p>
            </CardHeader>
            <CardContent class="space-y-4">
              <Select
                v-model="formStatusId"
                :options="statusOptions"
                :disabled="statusLoading"
              />

              <!-- Staff restriction notice -->
              <p
                v-if="hasTerminalRestriction"
                class="flex items-start gap-2 text-xs text-muted-foreground"
              >
                <AlertCircle class="mt-0.5 h-3 w-3 shrink-0" />
                Los estados finales requieren permisos de administrador.
              </p>

              <Button
                v-if="hasStatusChange"
                :disabled="statusLoading"
                class="w-full"
                @click="changeStatus"
              >
                {{ statusLoading ? 'Aplicando...' : 'Aplicar cambio' }}
              </Button>
            </CardContent>
          </Card>

          <!-- ETA Card -->
          <Card>
            <CardHeader class="pb-3">
              <CardTitle class="flex items-center gap-2 text-base">
                <Clock class="h-5 w-5 text-muted-foreground" />
                ETA
              </CardTitle>
            </CardHeader>
            <CardContent class="space-y-3">
              <!-- Current ETA display -->
              <div class="text-sm">
                <span class="text-muted-foreground">Hora estimada:</span>
                <span class="ml-2 font-medium">
                  {{ formattedEta || 'No definida' }}
                </span>
              </div>

              <!-- Only managers can edit -->
              <template v-if="authStore.isManager">
                <!-- Show editor or toggle button -->
                <template v-if="!showEtaEditor">
                  <Button
                    variant="outline"
                    size="sm"
                    class="w-full"
                    @click="showEtaEditor = true"
                  >
                    <Pencil class="mr-2 h-4 w-4" />
                    {{ ticketStore.currentTicket.eta_at ? 'Cambiar ETA' : 'Establecer ETA' }}
                  </Button>
                </template>

                <!-- ETA Editor -->
                <template v-else>
                  <div class="space-y-3 rounded-lg border bg-muted/30 p-3">
                    <div class="space-y-2">
                      <Label for="eta" class="text-xs">Nueva ETA</Label>
                      <Input
                        id="eta"
                        v-model="formEtaAt"
                        type="datetime-local"
                        :disabled="etaLoading"
                      />
                    </div>
                    <div class="flex gap-2">
                      <Button
                        size="sm"
                        :disabled="etaLoading || !hasEtaChange"
                        @click="saveEta"
                      >
                        {{ etaLoading ? 'Guardando...' : 'Guardar ETA' }}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        :disabled="etaLoading"
                        @click="
                          () => {
                            showEtaEditor = false
                            formEtaAt = ticketStore.currentTicket?.eta_at
                              ? formatDateTimeLocal(ticketStore.currentTicket.eta_at)
                              : ''
                          }
                        "
                      >
                        Cancelar
                      </Button>
                    </div>
                  </div>
                </template>
              </template>

              <!-- Staff restriction -->
              <p v-else class="text-xs text-muted-foreground">
                Solo un administrador puede ajustar la ETA.
              </p>
            </CardContent>
          </Card>

          <!-- Activity Card -->
          <Card>
            <CardHeader class="pb-3">
              <CardTitle class="flex items-center gap-2 text-base">
                <History class="h-5 w-5 text-muted-foreground" />
                Actividad
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="max-h-[350px] overflow-y-auto pr-2">
                <ActivityTimeline :events="ticketStore.events" :loading="eventsLoading" />
              </div>
            </CardContent>
          </Card>

          <!-- Notifications Card -->
          <Card>
            <CardHeader class="pb-3">
              <CardTitle class="flex items-center gap-2 text-base">
                <Bell class="h-5 w-5 text-muted-foreground" />
                Notificaciones
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="max-h-[250px] overflow-y-auto pr-2">
                <NotificationHistory :logs="notificationStore.logs" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </template>

    <!-- Error state -->
    <div v-else class="py-12 text-center">
      <p class="text-muted-foreground">No se encontró el ticket.</p>
      <Button variant="ghost" class="mt-4" @click="goBack">
        <ArrowLeft class="mr-2 h-4 w-4" />
        Volver a tickets
      </Button>
    </div>

    <!-- Share dialog -->
    <ShareTicketDialog
      v-if="ticketStore.currentTicket"
      v-model:open="shareDialogOpen"
      :public-code="ticketStore.currentTicket.public_code"
      :vehicle-label="vehicleLabel"
    />

    <!-- Notification dialog -->
    <SendNotificationDialog
      v-if="ticketStore.currentTicket"
      v-model:open="notificationDialogOpen"
      :ticket="ticketStore.currentTicket"
      @sent="handleNotificationSent"
    />
  </div>
</template>
