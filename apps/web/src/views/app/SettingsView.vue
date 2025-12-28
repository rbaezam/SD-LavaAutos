<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ListOrdered, Plus, Pencil, ChevronUp, ChevronDown, Info, User, Workflow, Monitor, ExternalLink, Palette, Loader2, Bell, Trash2, MessageCircle, Smartphone } from 'lucide-vue-next'
import { z } from 'zod'
import {
  Alert,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Dialog,
  Input,
  Label,
  Switch,
} from '@/components/ui'
import PageHeader from '@/components/layout/PageHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import { useAuthStore } from '@/stores/auth'
import { useLocationStore } from '@/stores/location'
import { useStatusStore, type Status } from '@/stores/status'
import { useNotificationStore, type NotificationTemplate, type NotificationChannel, type NotificationEvent } from '@/stores/notification'
import { NotificationPreview } from '@/components/notifications'
import api from '@/lib/api'

const router = useRouter()
const authStore = useAuthStore()
const locationStore = useLocationStore()
const statusStore = useStatusStore()
const notificationStore = useNotificationStore()

// ====== Branding State ======
interface Branding {
  brand_name: string | null
  brand_logo_url: string | null
  brand_primary_color: string | null
}

const branding = ref<Branding>({
  brand_name: null,
  brand_logo_url: null,
  brand_primary_color: null,
})
const brandingLoading = ref(false)
const brandingSaving = ref(false)
const brandingError = ref('')
const brandingSuccess = ref(false)

// Branding form state
const brandForm = ref({
  brand_name: '',
  brand_logo_url: '',
  brand_primary_color: '#2563eb',
})

// Fetch branding
async function fetchBranding() {
  if (!authStore.isManager) return
  brandingLoading.value = true
  brandingError.value = ''
  try {
    const response = await api.get<Branding>('/api/v1/org/branding')
    branding.value = response.data
    // Populate form
    brandForm.value.brand_name = response.data.brand_name || ''
    brandForm.value.brand_logo_url = response.data.brand_logo_url || ''
    brandForm.value.brand_primary_color = response.data.brand_primary_color || '#2563eb'
  } catch (err) {
    brandingError.value = 'Error al cargar la configuración de branding'
    console.error('Failed to fetch branding:', err)
  } finally {
    brandingLoading.value = false
  }
}

// Save branding
async function saveBranding() {
  brandingSaving.value = true
  brandingError.value = ''
  brandingSuccess.value = false
  try {
    const response = await api.patch<Branding>('/api/v1/org/branding', {
      brand_name: brandForm.value.brand_name.trim() || null,
      brand_logo_url: brandForm.value.brand_logo_url.trim() || null,
      brand_primary_color: brandForm.value.brand_primary_color.trim() || null,
    })
    branding.value = response.data
    brandingSuccess.value = true
    setTimeout(() => {
      brandingSuccess.value = false
    }, 3000)
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      brandingError.value = axiosErr.response?.data?.detail || 'Error al guardar'
    } else {
      brandingError.value = 'Error al guardar'
    }
  } finally {
    brandingSaving.value = false
  }
}

// Computed for preview
const previewColor = computed(() => brandForm.value.brand_primary_color || '#2563eb')
const previewName = computed(() => brandForm.value.brand_name || 'WashFlow')

onMounted(() => {
  if (authStore.isManager) {
    fetchBranding()
  }
})

// Open display in new tab
function openDisplay() {
  const url = router.resolve({ name: 'display' }).href
  window.open(url, '_blank')
}

// Tab state
const activeTab = ref<'profile' | 'statuses' | 'branding' | 'notifications'>('profile')

// Modal state for statuses
const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingStatus = ref<Status | null>(null)

// Form state for statuses
const formName = ref('')
const formIsTerminal = ref(false)
const formError = ref('')
const formLoading = ref(false)

// Reorder state
const localStatuses = ref<Status[]>([])
const hasUnsavedChanges = ref(false)
const reorderLoading = ref(false)

// Keep local copy in sync with store
const syncLocalStatuses = () => {
  localStatuses.value = [...statusStore.statuses]
  hasUnsavedChanges.value = false
}

// Watch for store changes and sync
statusStore.$subscribe(() => {
  if (!hasUnsavedChanges.value) {
    syncLocalStatuses()
  }
})

// Initialize local statuses
syncLocalStatuses()

const sortedLocalStatuses = computed(() => {
  return [...localStatuses.value].sort((a, b) => a.sort_order - b.sort_order)
})

const statusSchema = z.object({
  name: z.string().min(2, 'El nombre debe tener al menos 2 caracteres').max(40),
  is_terminal: z.boolean().optional(),
})

function openCreateModal() {
  formName.value = ''
  formIsTerminal.value = false
  formError.value = ''
  showCreateModal.value = true
}

function openEditModal(status: Status) {
  editingStatus.value = status
  formName.value = status.name
  formIsTerminal.value = status.is_terminal
  formError.value = ''
  showEditModal.value = true
}

async function handleCreate() {
  formError.value = ''

  const validation = statusSchema.safeParse({
    name: formName.value,
    is_terminal: formIsTerminal.value,
  })

  if (!validation.success) {
    formError.value = validation.error.errors[0].message
    return
  }

  formLoading.value = true
  try {
    await statusStore.createStatus({
      name: formName.value,
      is_terminal: formIsTerminal.value,
    })
    showCreateModal.value = false
    syncLocalStatuses()
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      formError.value = axiosErr.response?.data?.detail || 'Error al crear estado'
    } else {
      formError.value = 'Error al crear estado'
    }
  } finally {
    formLoading.value = false
  }
}

async function handleUpdate() {
  if (!editingStatus.value) return

  formError.value = ''

  const validation = statusSchema.safeParse({
    name: formName.value,
    is_terminal: formIsTerminal.value,
  })

  if (!validation.success) {
    formError.value = validation.error.errors[0].message
    return
  }

  formLoading.value = true
  try {
    await statusStore.updateStatus(editingStatus.value.id, {
      name: formName.value,
      is_terminal: formIsTerminal.value,
    })
    showEditModal.value = false
    editingStatus.value = null
    syncLocalStatuses()
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      formError.value = axiosErr.response?.data?.detail || 'Error al actualizar estado'
    } else {
      formError.value = 'Error al actualizar estado'
    }
  } finally {
    formLoading.value = false
  }
}

function moveUp(index: number) {
  if (index <= 0) return
  const sorted = sortedLocalStatuses.value
  const currentId = sorted[index].id
  const prevId = sorted[index - 1].id

  const currentItem = localStatuses.value.find((s) => s.id === currentId)
  const prevItem = localStatuses.value.find((s) => s.id === prevId)

  if (currentItem && prevItem) {
    const temp = currentItem.sort_order
    currentItem.sort_order = prevItem.sort_order
    prevItem.sort_order = temp
    hasUnsavedChanges.value = true
  }
}

function moveDown(index: number) {
  const sorted = sortedLocalStatuses.value
  if (index >= sorted.length - 1) return

  const currentId = sorted[index].id
  const nextId = sorted[index + 1].id

  const currentItem = localStatuses.value.find((s) => s.id === currentId)
  const nextItem = localStatuses.value.find((s) => s.id === nextId)

  if (currentItem && nextItem) {
    const temp = currentItem.sort_order
    currentItem.sort_order = nextItem.sort_order
    nextItem.sort_order = temp
    hasUnsavedChanges.value = true
  }
}

async function saveReorder() {
  reorderLoading.value = true
  try {
    const orderedIds = sortedLocalStatuses.value.map((s) => s.id)
    await statusStore.reorderStatuses(orderedIds)
    hasUnsavedChanges.value = false
  } catch (err: unknown) {
    console.error('Error saving reorder:', err)
  } finally {
    reorderLoading.value = false
  }
}

function cancelReorder() {
  syncLocalStatuses()
}

// ====== Notification Templates State ======
const showTemplateModal = ref(false)
const editingTemplate = ref<NotificationTemplate | null>(null)
const templateFormLoading = ref(false)
const templateFormError = ref('')
const templateFormSuccess = ref(false)
const deleteConfirmId = ref<string | null>(null)

// Template form state
const templateForm = ref({
  channel: 'whatsapp' as NotificationChannel,
  event: 'ticket_created' as NotificationEvent,
  title: '',
  message_template: '',
  is_active: true,
})

// Channel options
const channelOptions = [
  { value: 'whatsapp', label: 'WhatsApp', icon: MessageCircle },
  { value: 'sms', label: 'SMS', icon: Smartphone },
]

// Event options
const eventOptions = computed(() => [
  { value: 'ticket_created', label: notificationStore.getEventLabel('ticket_created') },
  { value: 'status_changed', label: notificationStore.getEventLabel('status_changed') },
  { value: 'ready', label: notificationStore.getEventLabel('ready') },
  { value: 'delivered', label: notificationStore.getEventLabel('delivered') },
  { value: 'manual', label: notificationStore.getEventLabel('manual') },
])

// Preview message with example variables
const previewMessage = computed(() => {
  let message = templateForm.value.message_template
  const examples: Record<string, string> = {
    '{{customer_name}}': 'Juan Pérez',
    '{{vehicle_label}}': 'ABC-123',
    '{{status}}': 'En lavado',
    '{{location_name}}': 'Sucursal Centro',
    '{{public_code}}': 'WF-A1B2',
    '{{eta}}': '2:30 PM',
    '{{tracking_url}}': 'https://example.com/t/WF-A1B2',
  }
  for (const [variable, example] of Object.entries(examples)) {
    message = message.replace(new RegExp(variable.replace(/[{}]/g, '\\$&'), 'g'), example)
  }
  return message
})

function openTemplateCreateModal() {
  editingTemplate.value = null
  templateForm.value = {
    channel: 'whatsapp',
    event: 'ticket_created',
    title: '',
    message_template: '',
    is_active: true,
  }
  templateFormError.value = ''
  showTemplateModal.value = true
}

function openTemplateEditModal(template: NotificationTemplate) {
  editingTemplate.value = template
  templateForm.value = {
    channel: template.channel,
    event: template.event,
    title: template.title,
    message_template: template.message_template,
    is_active: template.is_active,
  }
  templateFormError.value = ''
  showTemplateModal.value = true
}

async function handleTemplateSave() {
  if (!templateForm.value.title.trim()) {
    templateFormError.value = 'El título es requerido'
    return
  }
  if (!templateForm.value.message_template.trim()) {
    templateFormError.value = 'El mensaje es requerido'
    return
  }

  templateFormLoading.value = true
  templateFormError.value = ''

  try {
    if (editingTemplate.value) {
      await notificationStore.updateTemplate(editingTemplate.value.id, {
        title: templateForm.value.title,
        message_template: templateForm.value.message_template,
        is_active: templateForm.value.is_active,
      })
    } else {
      await notificationStore.createTemplate({
        channel: templateForm.value.channel,
        event: templateForm.value.event,
        title: templateForm.value.title,
        message_template: templateForm.value.message_template,
        is_active: templateForm.value.is_active,
      })
    }
    showTemplateModal.value = false
    templateFormSuccess.value = true
    setTimeout(() => {
      templateFormSuccess.value = false
    }, 3000)
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      templateFormError.value = axiosErr.response?.data?.detail || 'Error al guardar plantilla'
    } else {
      templateFormError.value = 'Error al guardar plantilla'
    }
  } finally {
    templateFormLoading.value = false
  }
}

async function handleTemplateDelete(id: string) {
  try {
    await notificationStore.deleteTemplate(id)
    deleteConfirmId.value = null
  } catch (err) {
    console.error('Error deleting template:', err)
  }
}

async function handleTemplateToggle(template: NotificationTemplate) {
  await notificationStore.updateTemplate(template.id, {
    is_active: !template.is_active,
  })
}

// Load templates when tab is selected
function loadNotificationTemplates() {
  if (authStore.isManager) {
    notificationStore.fetchTemplates()
    notificationStore.fetchVariables()
  }
}

// Format variable name with braces
function formatVariableName(name: string): string {
  return `{{${name}}}`
}
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <PageHeader
      title="Configuración"
      subtitle="Administra tu cuenta y la configuración del sistema."
    />

    <!-- Tabs -->
    <div class="border-b">
      <nav class="-mb-px flex gap-4">
        <button
          type="button"
          :class="[
            'flex items-center gap-2 border-b-2 px-1 py-3 text-sm font-medium transition-colors',
            activeTab === 'profile'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:border-muted-foreground/30 hover:text-foreground',
          ]"
          @click="activeTab = 'profile'"
        >
          <User class="h-4 w-4" />
          Perfil
        </button>
        <button
          type="button"
          :class="[
            'flex items-center gap-2 border-b-2 px-1 py-3 text-sm font-medium transition-colors',
            activeTab === 'statuses'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:border-muted-foreground/30 hover:text-foreground',
          ]"
          @click="activeTab = 'statuses'"
        >
          <Workflow class="h-4 w-4" />
          Estados del flujo
        </button>
        <button
          v-if="authStore.isManager"
          type="button"
          :class="[
            'flex items-center gap-2 border-b-2 px-1 py-3 text-sm font-medium transition-colors',
            activeTab === 'branding'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:border-muted-foreground/30 hover:text-foreground',
          ]"
          @click="activeTab = 'branding'"
        >
          <Palette class="h-4 w-4" />
          Branding
        </button>
        <button
          v-if="authStore.isManager"
          type="button"
          :class="[
            'flex items-center gap-2 border-b-2 px-1 py-3 text-sm font-medium transition-colors',
            activeTab === 'notifications'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:border-muted-foreground/30 hover:text-foreground',
          ]"
          @click="activeTab = 'notifications'; loadNotificationTemplates()"
        >
          <Bell class="h-4 w-4" />
          Notificaciones
        </button>
      </nav>
    </div>

    <!-- Profile Tab -->
    <div v-if="activeTab === 'profile'" class="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Perfil</CardTitle>
          <CardDescription>Tu información de cuenta.</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-2">
            <Label for="email">Correo electrónico</Label>
            <Input
              id="email"
              :model-value="authStore.user?.email"
              disabled
            />
          </div>
          <div class="space-y-2">
            <Label for="fullName">Nombre completo</Label>
            <Input
              id="fullName"
              :model-value="authStore.user?.full_name || ''"
              placeholder="Tu nombre completo"
              disabled
            />
          </div>
          <div class="pt-4">
            <Button disabled>
              Guardar cambios (próximamente)
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Cuenta</CardTitle>
          <CardDescription>Información de tu cuenta.</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-2">
            <Label>ID de cuenta</Label>
            <p class="text-sm font-mono text-muted-foreground">
              {{ authStore.user?.id }}
            </p>
          </div>
          <div class="space-y-2">
            <Label>Miembro desde</Label>
            <p class="text-sm text-muted-foreground">
              {{ authStore.user?.created_at ? new Date(authStore.user.created_at).toLocaleDateString('es-MX') : '-' }}
            </p>
          </div>
        </CardContent>
      </Card>

      <!-- Display Screen Card (only for managers) -->
      <Card v-if="authStore.isManager">
        <CardHeader>
          <CardTitle class="flex items-center gap-2">
            <Monitor class="h-5 w-5" />
            Pantalla de sala
          </CardTitle>
          <CardDescription>
            Muestra el estado de los vehículos en tiempo real en una pantalla o TV.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p class="mb-4 text-sm text-muted-foreground">
            Ideal para mostrar a los clientes el avance de su servicio sin necesidad de preguntar.
            La pantalla se actualiza automáticamente cada 10 segundos.
          </p>
          <Button @click="openDisplay">
            <ExternalLink class="mr-2 h-4 w-4" />
            Abrir pantalla de sala
          </Button>
        </CardContent>
      </Card>
    </div>

    <!-- Statuses Tab -->
    <div v-if="activeTab === 'statuses'" class="space-y-6">
      <!-- Header with actions -->
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-semibold">Estados del flujo</h2>
          <p class="text-sm text-muted-foreground">
            Define el flujo de trabajo de los vehículos en cada sucursal.
          </p>
        </div>
        <div class="flex items-center gap-2">
          <template v-if="hasUnsavedChanges">
            <Badge variant="warning" class="mr-2">Cambios sin guardar</Badge>
            <Button
              variant="outline"
              size="sm"
              :disabled="reorderLoading"
              @click="cancelReorder"
            >
              Cancelar
            </Button>
            <Button
              size="sm"
              :disabled="reorderLoading"
              @click="saveReorder"
            >
              {{ reorderLoading ? 'Guardando...' : 'Guardar orden' }}
            </Button>
          </template>
          <Button v-else-if="authStore.isManager && locationStore.selectedLocationId" @click="openCreateModal">
            <Plus class="mr-2 h-4 w-4" />
            Nuevo estado
          </Button>
        </div>
      </div>

      <!-- No location selected -->
      <Alert v-if="!locationStore.selectedLocationId">
        Selecciona una sucursal para ver sus estados.
      </Alert>

      <template v-else>
        <!-- Info tip -->
        <div class="rounded-lg border border-dashed bg-muted/50 p-4">
          <div class="flex items-start gap-3">
            <Info class="mt-0.5 h-4 w-4 text-muted-foreground" />
            <p class="text-sm text-muted-foreground">
              <span class="font-medium text-foreground">Tip:</span> Ordena los estados según el flujo real. El estado marcado como
              "Terminal" indica que el vehículo ha sido entregado.
            </p>
          </div>
        </div>

        <Card>
          <CardContent class="p-6">
            <!-- Loading state -->
            <div v-if="statusStore.loading" class="py-8 text-center text-muted-foreground">
              Cargando estados...
            </div>

            <!-- Empty state -->
            <EmptyState
              v-else-if="localStatuses.length === 0"
              :icon="ListOrdered"
              title="No hay estados registrados"
              description="Crea tu primer estado para definir el flujo de trabajo."
            >
              <template #primary>
                <Button v-if="authStore.isManager" @click="openCreateModal">
                  <Plus class="mr-2 h-4 w-4" />
                  Crear estado
                </Button>
              </template>
            </EmptyState>

            <!-- Status list -->
            <div v-else class="space-y-2">
              <div
                v-for="(status, index) in sortedLocalStatuses"
                :key="status.id"
                class="group flex items-center justify-between rounded-lg border bg-card p-4 transition-colors hover:bg-muted/50"
              >
                <div class="flex items-center gap-4">
                  <!-- Reorder buttons -->
                  <div v-if="authStore.isManager" class="flex flex-col gap-0.5">
                    <button
                      type="button"
                      class="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground disabled:cursor-not-allowed disabled:opacity-30"
                      :disabled="index === 0"
                      @click="moveUp(index)"
                    >
                      <ChevronUp class="h-4 w-4" />
                    </button>
                    <button
                      type="button"
                      class="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground disabled:cursor-not-allowed disabled:opacity-30"
                      :disabled="index === sortedLocalStatuses.length - 1"
                      @click="moveDown(index)"
                    >
                      <ChevronDown class="h-4 w-4" />
                    </button>
                  </div>

                  <!-- Order number -->
                  <span class="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
                    {{ index + 1 }}
                  </span>

                  <!-- Status info -->
                  <div>
                    <span class="font-medium">{{ status.name }}</span>
                    <div v-if="status.is_terminal" class="mt-1">
                      <Badge variant="success">Terminal</Badge>
                    </div>
                  </div>
                </div>

                <!-- Actions -->
                <div v-if="authStore.isManager">
                  <Button
                    variant="ghost"
                    size="sm"
                    class="opacity-0 transition-opacity group-hover:opacity-100"
                    @click="openEditModal(status)"
                  >
                    <Pencil class="mr-1.5 h-4 w-4" />
                    Editar
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </template>
    </div>

    <!-- Branding Tab (managers only) -->
    <div v-if="activeTab === 'branding' && authStore.isManager" class="space-y-6">
      <!-- Loading state -->
      <div v-if="brandingLoading" class="flex items-center justify-center py-12">
        <Loader2 class="h-8 w-8 animate-spin text-muted-foreground" />
      </div>

      <template v-else>
        <!-- Info tip -->
        <div class="rounded-lg border border-dashed bg-muted/50 p-4">
          <div class="flex items-start gap-3">
            <Info class="mt-0.5 h-4 w-4 text-muted-foreground" />
            <p class="text-sm text-muted-foreground">
              <span class="font-medium text-foreground">Personaliza tu marca:</span> Esta configuración se muestra en la página pública de seguimiento de tickets y en los recibos impresos.
            </p>
          </div>
        </div>

        <!-- Success message -->
        <Alert v-if="brandingSuccess" variant="success">
          Configuración guardada correctamente.
        </Alert>

        <!-- Error message -->
        <Alert v-if="brandingError" variant="destructive">
          {{ brandingError }}
        </Alert>

        <div class="grid gap-6 lg:grid-cols-2">
          <!-- Form -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Palette class="h-5 w-5" />
                Configuración de marca
              </CardTitle>
              <CardDescription>
                Personaliza cómo se muestra tu negocio a los clientes.
              </CardDescription>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="space-y-2">
                <Label for="brand_name">Nombre para mostrar</Label>
                <Input
                  id="brand_name"
                  v-model="brandForm.brand_name"
                  placeholder="Ej: Mi Autolavado"
                  :disabled="brandingSaving"
                />
                <p class="text-xs text-muted-foreground">
                  Si está vacío, se usará "WashFlow"
                </p>
              </div>

              <div class="space-y-2">
                <Label for="brand_logo_url">URL del logo</Label>
                <Input
                  id="brand_logo_url"
                  v-model="brandForm.brand_logo_url"
                  placeholder="https://ejemplo.com/logo.png"
                  type="url"
                  :disabled="brandingSaving"
                />
                <p class="text-xs text-muted-foreground">
                  URL directa a la imagen (PNG, JPG, SVG)
                </p>
              </div>

              <div class="space-y-2">
                <Label for="brand_primary_color">Color principal</Label>
                <div class="flex items-center gap-3">
                  <input
                    id="brand_primary_color_picker"
                    v-model="brandForm.brand_primary_color"
                    type="color"
                    class="h-10 w-14 cursor-pointer rounded border"
                    :disabled="brandingSaving"
                  />
                  <Input
                    id="brand_primary_color"
                    v-model="brandForm.brand_primary_color"
                    placeholder="#2563eb"
                    class="flex-1 font-mono"
                    :disabled="brandingSaving"
                  />
                </div>
                <p class="text-xs text-muted-foreground">
                  Formato HEX (#RRGGBB)
                </p>
              </div>

              <div class="pt-4">
                <Button
                  :disabled="brandingSaving"
                  @click="saveBranding"
                >
                  <Loader2 v-if="brandingSaving" class="mr-2 h-4 w-4 animate-spin" />
                  {{ brandingSaving ? 'Guardando...' : 'Guardar cambios' }}
                </Button>
              </div>
            </CardContent>
          </Card>

          <!-- Preview -->
          <Card>
            <CardHeader>
              <CardTitle>Vista previa</CardTitle>
              <CardDescription>
                Así se verá la página pública de seguimiento.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div class="overflow-hidden rounded-lg border bg-slate-50 p-4">
                <!-- Preview header -->
                <div class="mb-4 flex items-center gap-3 rounded-lg bg-white p-3 shadow-sm">
                  <div
                    v-if="!brandForm.brand_logo_url"
                    class="flex h-10 w-10 items-center justify-center rounded-lg text-lg font-bold text-white"
                    :style="{ backgroundColor: previewColor }"
                  >
                    {{ previewName.charAt(0).toUpperCase() }}
                  </div>
                  <img
                    v-else
                    :src="brandForm.brand_logo_url"
                    :alt="previewName"
                    class="h-10 w-10 rounded-lg object-contain"
                    @error="($event.target as HTMLImageElement).style.display = 'none'"
                  />
                  <div>
                    <p class="font-semibold">{{ previewName }}</p>
                    <p class="text-xs text-slate-500">Seguimiento de tu vehículo</p>
                  </div>
                </div>

                <!-- Preview card -->
                <div class="rounded-lg bg-white shadow-sm">
                  <div
                    class="rounded-t-lg p-4 text-center text-white"
                    :style="{ background: `linear-gradient(135deg, ${previewColor}, ${previewColor}dd)` }"
                  >
                    <div
                      class="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-white/20"
                    >
                      <Loader2 class="h-6 w-6 animate-spin" />
                    </div>
                    <p class="text-sm font-semibold uppercase">En lavado</p>
                    <p class="text-xs opacity-80">Tu vehículo está siendo atendido</p>
                  </div>
                  <div class="space-y-2 p-3 text-sm">
                    <div class="flex justify-between">
                      <span class="text-slate-500">Folio</span>
                      <span class="font-mono font-bold">ABC-1234</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-slate-500">Vehículo</span>
                      <span class="font-medium">Toyota Camry (ABC-123)</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </template>
    </div>

    <!-- Notifications Tab (managers only) -->
    <div v-if="activeTab === 'notifications' && authStore.isManager" class="space-y-6">
      <!-- Loading state -->
      <div v-if="notificationStore.loading" class="flex items-center justify-center py-12">
        <Loader2 class="h-8 w-8 animate-spin text-muted-foreground" />
      </div>

      <template v-else>
        <!-- Info tip -->
        <div class="rounded-lg border border-dashed bg-muted/50 p-4">
          <div class="flex items-start gap-3">
            <Info class="mt-0.5 h-4 w-4 text-muted-foreground" />
            <div class="text-sm text-muted-foreground">
              <span class="font-medium text-foreground">Plantillas de notificación:</span>
              Configura los mensajes que se enviarán a los clientes por WhatsApp o SMS cuando ocurran eventos en sus tickets.
            </div>
          </div>
        </div>

        <!-- Success message -->
        <Alert v-if="templateFormSuccess" variant="success">
          Plantilla guardada correctamente.
        </Alert>

        <!-- Header with actions -->
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold">Plantillas de notificación</h2>
            <p class="text-sm text-muted-foreground">
              Define los mensajes automáticos para cada evento.
            </p>
          </div>
          <Button @click="openTemplateCreateModal">
            <Plus class="mr-2 h-4 w-4" />
            Nueva plantilla
          </Button>
        </div>

        <!-- Templates list -->
        <Card>
          <CardContent class="p-6">
            <!-- Empty state -->
            <EmptyState
              v-if="notificationStore.templates.length === 0"
              :icon="Bell"
              title="No hay plantillas configuradas"
              description="Crea tu primera plantilla para empezar a enviar notificaciones."
            >
              <template #primary>
                <Button @click="openTemplateCreateModal">
                  <Plus class="mr-2 h-4 w-4" />
                  Crear plantilla
                </Button>
              </template>
            </EmptyState>

            <!-- Template list -->
            <div v-else class="space-y-3">
              <div
                v-for="template in notificationStore.templates"
                :key="template.id"
                class="group flex items-start justify-between rounded-lg border bg-card p-4 transition-colors hover:bg-muted/50"
              >
                <div class="flex items-start gap-4">
                  <!-- Channel icon -->
                  <div
                    :class="[
                      'flex h-10 w-10 items-center justify-center rounded-full',
                      template.channel === 'whatsapp'
                        ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
                        : 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
                    ]"
                  >
                    <component
                      :is="template.channel === 'whatsapp' ? MessageCircle : Smartphone"
                      class="h-5 w-5"
                    />
                  </div>

                  <!-- Template info -->
                  <div class="space-y-1">
                    <div class="flex items-center gap-2">
                      <span class="font-medium">{{ template.title }}</span>
                      <Badge v-if="!template.is_active" variant="secondary">
                        Inactiva
                      </Badge>
                    </div>
                    <p class="text-sm text-muted-foreground">
                      {{ notificationStore.getChannelLabel(template.channel) }} ·
                      {{ notificationStore.getEventLabel(template.event) }}
                    </p>
                    <p class="text-xs text-muted-foreground line-clamp-2">
                      {{ template.message_template }}
                    </p>
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex items-center gap-2">
                  <Switch
                    :model-value="template.is_active"
                    @update:model-value="handleTemplateToggle(template)"
                  />
                  <Button
                    variant="ghost"
                    size="sm"
                    class="opacity-0 transition-opacity group-hover:opacity-100"
                    @click="openTemplateEditModal(template)"
                  >
                    <Pencil class="h-4 w-4" />
                  </Button>
                  <Button
                    v-if="deleteConfirmId !== template.id"
                    variant="ghost"
                    size="sm"
                    class="text-destructive opacity-0 transition-opacity group-hover:opacity-100"
                    @click="deleteConfirmId = template.id"
                  >
                    <Trash2 class="h-4 w-4" />
                  </Button>
                  <div v-else class="flex items-center gap-1">
                    <Button
                      variant="destructive"
                      size="sm"
                      @click="handleTemplateDelete(template.id)"
                    >
                      Eliminar
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="deleteConfirmId = null"
                    >
                      Cancelar
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Variables reference -->
        <Card>
          <CardHeader>
            <CardTitle class="text-base">Variables disponibles</CardTitle>
            <CardDescription>
              Usa estas variables en tus plantillas para personalizar los mensajes.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              <div
                v-for="variable in notificationStore.variables"
                :key="variable.name"
                class="rounded-lg border bg-muted/30 p-3"
              >
                <code class="text-sm font-mono text-primary">{{ formatVariableName(variable.name) }}</code>
                <p class="mt-1 text-xs text-muted-foreground">{{ variable.description }}</p>
                <p class="mt-0.5 text-xs text-muted-foreground/70">Ej: {{ variable.example }}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </template>
    </div>

    <!-- Create Modal -->
    <Dialog v-model:open="showCreateModal" title="Nuevo estado">
      <form class="space-y-4" @submit.prevent="handleCreate">
        <Alert v-if="formError" variant="destructive">
          {{ formError }}
        </Alert>
        <div class="space-y-2">
          <Label for="name">Nombre</Label>
          <Input
            id="name"
            v-model="formName"
            placeholder="Ej: En lavado"
            :disabled="formLoading"
          />
        </div>
        <div class="flex items-center justify-between rounded-lg border p-4">
          <div>
            <Label for="terminal" class="cursor-pointer">Estado terminal</Label>
            <p class="text-sm text-muted-foreground">
              Marca este estado como el punto final del flujo (ej: Entregado)
            </p>
          </div>
          <Switch id="terminal" v-model="formIsTerminal" :disabled="formLoading" />
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
            {{ formLoading ? 'Creando...' : 'Crear estado' }}
          </Button>
        </div>
      </form>
    </Dialog>

    <!-- Edit Modal -->
    <Dialog v-model:open="showEditModal" title="Editar estado">
      <form class="space-y-4" @submit.prevent="handleUpdate">
        <Alert v-if="formError" variant="destructive">
          {{ formError }}
        </Alert>
        <div class="space-y-2">
          <Label for="edit-name">Nombre</Label>
          <Input
            id="edit-name"
            v-model="formName"
            placeholder="Ej: En lavado"
            :disabled="formLoading"
          />
        </div>
        <div class="flex items-center justify-between rounded-lg border p-4">
          <div>
            <Label for="edit-terminal" class="cursor-pointer">Estado terminal</Label>
            <p class="text-sm text-muted-foreground">
              Marca este estado como el punto final del flujo (ej: Entregado)
            </p>
          </div>
          <Switch id="edit-terminal" v-model="formIsTerminal" :disabled="formLoading" />
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

    <!-- Template Modal (Create/Edit) -->
    <Dialog v-model:open="showTemplateModal" :title="editingTemplate ? 'Editar plantilla' : 'Nueva plantilla'">
      <form class="space-y-4" @submit.prevent="handleTemplateSave">
        <Alert v-if="templateFormError" variant="destructive">
          {{ templateFormError }}
        </Alert>

        <!-- Channel selector (only for create) -->
        <div v-if="!editingTemplate" class="space-y-2">
          <Label>Canal</Label>
          <div class="flex gap-2">
            <button
              v-for="channel in channelOptions"
              :key="channel.value"
              type="button"
              :class="[
                'flex flex-1 items-center justify-center gap-2 rounded-lg border-2 p-3 transition-colors',
                templateForm.channel === channel.value
                  ? 'border-primary bg-primary/5'
                  : 'border-transparent bg-muted hover:bg-muted/80',
              ]"
              @click="templateForm.channel = channel.value as NotificationChannel"
            >
              <component :is="channel.icon" class="h-5 w-5" />
              <span class="font-medium">{{ channel.label }}</span>
            </button>
          </div>
        </div>

        <!-- Event selector (only for create) -->
        <div v-if="!editingTemplate" class="space-y-2">
          <Label for="template-event">Evento</Label>
          <select
            id="template-event"
            v-model="templateForm.event"
            class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          >
            <option v-for="event in eventOptions" :key="event.value" :value="event.value">
              {{ event.label }}
            </option>
          </select>
        </div>

        <!-- Title -->
        <div class="space-y-2">
          <Label for="template-title">Título</Label>
          <Input
            id="template-title"
            v-model="templateForm.title"
            placeholder="Ej: Bienvenida al cliente"
            :disabled="templateFormLoading"
          />
        </div>

        <!-- Message template -->
        <div class="space-y-2">
          <Label for="template-message">Mensaje</Label>
          <textarea
            id="template-message"
            v-model="templateForm.message_template"
            placeholder="Ej: Hola {{customer_name}}, tu vehículo {{vehicle_label}} está siendo atendido."
            rows="4"
            class="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            :disabled="templateFormLoading"
          />
          <p class="text-xs text-muted-foreground">
            Usa variables como <code class="text-primary">{{ formatVariableName('customer_name') }}</code> para personalizar el mensaje.
          </p>
        </div>

        <!-- Preview -->
        <div v-if="templateForm.message_template" class="space-y-2">
          <Label>Vista previa</Label>
          <NotificationPreview
            :message="previewMessage"
            :channel="templateForm.channel"
          />
        </div>

        <!-- Active toggle -->
        <div class="flex items-center justify-between rounded-lg border p-4">
          <div>
            <Label for="template-active" class="cursor-pointer">Activa</Label>
            <p class="text-sm text-muted-foreground">
              Las plantillas inactivas no se usarán para envío automático.
            </p>
          </div>
          <Switch id="template-active" v-model="templateForm.is_active" :disabled="templateFormLoading" />
        </div>

        <div class="flex justify-end gap-3 border-t pt-4">
          <Button
            type="button"
            variant="outline"
            :disabled="templateFormLoading"
            @click="showTemplateModal = false"
          >
            Cancelar
          </Button>
          <Button type="submit" :disabled="templateFormLoading">
            <Loader2 v-if="templateFormLoading" class="mr-2 h-4 w-4 animate-spin" />
            {{ templateFormLoading ? 'Guardando...' : (editingTemplate ? 'Guardar cambios' : 'Crear plantilla') }}
          </Button>
        </div>
      </form>
    </Dialog>
  </div>
</template>
