<script setup lang="ts">
import { ref } from 'vue'
import { Layers, Plus, Pencil } from 'lucide-vue-next'
import { z } from 'zod'
import {
  Alert,
  Badge,
  Button,
  Card,
  CardContent,
  Dialog,
  Input,
  Label,
  Table,
} from '@/components/ui'
import PageHeader from '@/components/layout/PageHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import TableSkeleton from '@/components/table/TableSkeleton.vue'
import { useAuthStore } from '@/stores/auth'
import { useLocationStore } from '@/stores/location'
import { useServiceStore, type Service } from '@/stores/service'

const authStore = useAuthStore()
const locationStore = useLocationStore()
const serviceStore = useServiceStore()

// Modal state
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeactivateConfirm = ref(false)
const editingService = ref<Service | null>(null)
const deactivatingService = ref<Service | null>(null)

// Form state
const formName = ref('')
const formDuration = ref(20)
const formPrice = ref<number | null>(null)
const formSortOrder = ref(0)
const formError = ref('')
const formLoading = ref(false)

const serviceSchema = z.object({
  name: z.string().min(2, 'El nombre debe tener al menos 2 caracteres').max(60),
  duration_minutes: z.number().min(1, 'Mínimo 1 minuto').max(600, 'Máximo 600 minutos'),
  price_mxn: z.number().min(0, 'El precio no puede ser negativo').optional().nullable(),
  sort_order: z.number().min(0).optional(),
})

function openCreateModal() {
  formName.value = ''
  formDuration.value = 20
  formPrice.value = null
  formSortOrder.value = 0
  formError.value = ''
  showCreateModal.value = true
}

function openEditModal(service: Service) {
  editingService.value = service
  formName.value = service.name
  formDuration.value = service.duration_minutes
  formPrice.value = service.price_mxn
  formSortOrder.value = service.sort_order
  formError.value = ''
  showEditModal.value = true
}

function confirmDeactivate(service: Service) {
  deactivatingService.value = service
  showDeactivateConfirm.value = true
}

async function handleCreate() {
  formError.value = ''

  const validation = serviceSchema.safeParse({
    name: formName.value,
    duration_minutes: formDuration.value,
    price_mxn: formPrice.value,
    sort_order: formSortOrder.value,
  })

  if (!validation.success) {
    formError.value = validation.error.errors[0].message
    return
  }

  formLoading.value = true
  try {
    await serviceStore.createService({
      name: formName.value,
      duration_minutes: formDuration.value,
      price_mxn: formPrice.value,
      sort_order: formSortOrder.value,
    })
    showCreateModal.value = false
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      formError.value = axiosErr.response?.data?.detail || 'Error al crear servicio'
    } else {
      formError.value = 'Error al crear servicio'
    }
  } finally {
    formLoading.value = false
  }
}

async function handleUpdate() {
  if (!editingService.value) return

  formError.value = ''

  const validation = serviceSchema.safeParse({
    name: formName.value,
    duration_minutes: formDuration.value,
    price_mxn: formPrice.value,
    sort_order: formSortOrder.value,
  })

  if (!validation.success) {
    formError.value = validation.error.errors[0].message
    return
  }

  formLoading.value = true
  try {
    await serviceStore.updateService(editingService.value.id, {
      name: formName.value,
      duration_minutes: formDuration.value,
      price_mxn: formPrice.value,
      sort_order: formSortOrder.value,
    })
    showEditModal.value = false
    editingService.value = null
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      formError.value = axiosErr.response?.data?.detail || 'Error al actualizar servicio'
    } else {
      formError.value = 'Error al actualizar servicio'
    }
  } finally {
    formLoading.value = false
  }
}

async function handleDeactivate() {
  if (!deactivatingService.value) return

  formLoading.value = true
  try {
    await serviceStore.deactivateService(deactivatingService.value.id)
    showDeactivateConfirm.value = false
    deactivatingService.value = null
  } catch (err: unknown) {
    console.error('Error deactivating service:', err)
  } finally {
    formLoading.value = false
  }
}

async function handleActivate(service: Service) {
  try {
    await serviceStore.activateService(service.id)
  } catch (err: unknown) {
    console.error('Error activating service:', err)
  }
}

function formatPrice(price: number | null): string {
  if (price === null) return '—'
  return `$${price.toLocaleString('es-MX')}`
}
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <PageHeader
      title="Servicios"
      subtitle="Configura los servicios disponibles por sucursal."
    >
      <template #actions>
        <Button v-if="authStore.isManager && locationStore.selectedLocationId" @click="openCreateModal">
          <Plus class="mr-2 h-4 w-4" />
          Nuevo servicio
        </Button>
      </template>
    </PageHeader>

    <!-- No location selected -->
    <Alert v-if="!locationStore.selectedLocationId">
      Selecciona una sucursal para ver sus servicios.
    </Alert>

    <Card v-else>
      <CardContent class="p-6">
        <!-- Loading state -->
        <TableSkeleton v-if="serviceStore.loading" :rows="4" :columns="6" />

        <!-- Empty state -->
        <EmptyState
          v-else-if="serviceStore.services.length === 0"
          :icon="Layers"
          title="No hay servicios registrados"
          description="Crea tu primer servicio para esta sucursal."
        >
          <template #primary>
            <Button v-if="authStore.isManager" @click="openCreateModal">
              <Plus class="mr-2 h-4 w-4" />
              Crear servicio
            </Button>
          </template>
        </EmptyState>

        <!-- Table -->
        <Table v-else>
          <thead>
            <tr class="border-b">
              <th class="py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Servicio
              </th>
              <th class="py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Duración
              </th>
              <th class="hidden py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground sm:table-cell">
                Precio
              </th>
              <th class="py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Estado
              </th>
              <th class="hidden py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground md:table-cell">
                Orden
              </th>
              <th class="py-3 text-right text-xs font-medium uppercase tracking-wide text-muted-foreground">
                <span class="sr-only">Acciones</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="service in serviceStore.services"
              :key="service.id"
              class="group border-b transition-colors last:border-0 hover:bg-muted/50"
            >
              <td class="py-4">
                <span class="text-sm font-medium">{{ service.name }}</span>
              </td>
              <td class="py-4">
                <span class="text-sm text-muted-foreground">{{ service.duration_minutes }} min</span>
              </td>
              <td class="hidden py-4 sm:table-cell">
                <span class="text-sm text-muted-foreground">{{ formatPrice(service.price_mxn) }}</span>
              </td>
              <td class="py-4">
                <Badge :variant="service.active ? 'success' : 'secondary'">
                  {{ service.active ? 'Activo' : 'Inactivo' }}
                </Badge>
              </td>
              <td class="hidden py-4 md:table-cell">
                <span class="text-sm text-muted-foreground">{{ service.sort_order }}</span>
              </td>
              <td class="py-4 text-right">
                <div v-if="authStore.isManager" class="flex justify-end gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                  <Button variant="ghost" size="sm" @click="openEditModal(service)">
                    <Pencil class="mr-1.5 h-4 w-4" />
                    Editar
                  </Button>
                  <Button
                    v-if="service.active"
                    variant="ghost"
                    size="sm"
                    @click="confirmDeactivate(service)"
                  >
                    Desactivar
                  </Button>
                  <Button
                    v-else
                    variant="ghost"
                    size="sm"
                    @click="handleActivate(service)"
                  >
                    Activar
                  </Button>
                </div>
              </td>
            </tr>
          </tbody>
        </Table>
      </CardContent>
    </Card>

    <!-- Create Modal -->
    <Dialog v-model:open="showCreateModal" title="Nuevo servicio">
      <form class="space-y-4" @submit.prevent="handleCreate">
        <Alert v-if="formError" variant="destructive">
          {{ formError }}
        </Alert>
        <div class="space-y-2">
          <Label for="name">Nombre</Label>
          <Input
            id="name"
            v-model="formName"
            placeholder="Ej: Lavado completo"
            :disabled="formLoading"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="duration">Duración (min)</Label>
            <Input
              id="duration"
              v-model.number="formDuration"
              type="number"
              min="1"
              max="600"
              :disabled="formLoading"
            />
          </div>
          <div class="space-y-2">
            <Label for="price">Precio (MXN)</Label>
            <Input
              id="price"
              v-model.number="formPrice"
              type="number"
              min="0"
              placeholder="Opcional"
              :disabled="formLoading"
            />
          </div>
        </div>
        <div class="space-y-2">
          <Label for="sort">Orden</Label>
          <Input
            id="sort"
            v-model.number="formSortOrder"
            type="number"
            min="0"
            :disabled="formLoading"
          />
          <p class="text-xs text-muted-foreground">Posición en la lista de servicios</p>
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
            {{ formLoading ? 'Creando...' : 'Crear servicio' }}
          </Button>
        </div>
      </form>
    </Dialog>

    <!-- Edit Modal -->
    <Dialog v-model:open="showEditModal" title="Editar servicio">
      <form class="space-y-4" @submit.prevent="handleUpdate">
        <Alert v-if="formError" variant="destructive">
          {{ formError }}
        </Alert>
        <div class="space-y-2">
          <Label for="edit-name">Nombre</Label>
          <Input
            id="edit-name"
            v-model="formName"
            placeholder="Ej: Lavado completo"
            :disabled="formLoading"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="edit-duration">Duración (min)</Label>
            <Input
              id="edit-duration"
              v-model.number="formDuration"
              type="number"
              min="1"
              max="600"
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
              placeholder="Opcional"
              :disabled="formLoading"
            />
          </div>
        </div>
        <div class="space-y-2">
          <Label for="edit-sort">Orden</Label>
          <Input
            id="edit-sort"
            v-model.number="formSortOrder"
            type="number"
            min="0"
            :disabled="formLoading"
          />
          <p class="text-xs text-muted-foreground">Posición en la lista de servicios</p>
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

    <!-- Deactivate Confirmation Modal -->
    <Dialog v-model:open="showDeactivateConfirm" title="Desactivar servicio">
      <div class="space-y-4">
        <p class="text-muted-foreground">
          Este servicio ya no aparecerá para nuevos tickets. Puedes reactivarlo después.
        </p>
        <div class="flex justify-end gap-3 border-t pt-4">
          <Button
            variant="outline"
            :disabled="formLoading"
            @click="showDeactivateConfirm = false"
          >
            Cancelar
          </Button>
          <Button
            variant="destructive"
            :disabled="formLoading"
            @click="handleDeactivate"
          >
            {{ formLoading ? 'Desactivando...' : 'Desactivar' }}
          </Button>
        </div>
      </div>
    </Dialog>
  </div>
</template>
