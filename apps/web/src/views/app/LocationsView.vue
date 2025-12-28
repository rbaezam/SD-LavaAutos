<script setup lang="ts">
import { ref } from 'vue'
import { MapPin, Plus, Pencil } from 'lucide-vue-next'
import { z } from 'zod'
import {
  Alert,
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
import { useLocationStore, type Location } from '@/stores/location'

const authStore = useAuthStore()
const locationStore = useLocationStore()

// Modal state
const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingLocation = ref<Location | null>(null)

// Form state
const formName = ref('')
const formAddress = ref('')
const formError = ref('')
const formLoading = ref(false)

const locationSchema = z.object({
  name: z.string().min(2, 'El nombre debe tener al menos 2 caracteres').max(255),
  address: z.string().max(500).optional(),
})

function openCreateModal() {
  formName.value = ''
  formAddress.value = ''
  formError.value = ''
  showCreateModal.value = true
}

function openEditModal(location: Location) {
  editingLocation.value = location
  formName.value = location.name
  formAddress.value = location.address || ''
  formError.value = ''
  showEditModal.value = true
}

async function handleCreate() {
  formError.value = ''

  const validation = locationSchema.safeParse({
    name: formName.value,
    address: formAddress.value || undefined,
  })

  if (!validation.success) {
    formError.value = validation.error.errors[0].message
    return
  }

  formLoading.value = true
  try {
    await locationStore.createLocation(formName.value, formAddress.value || undefined)
    showCreateModal.value = false
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      formError.value = axiosErr.response?.data?.detail || 'Error al crear sucursal'
    } else {
      formError.value = 'Error al crear sucursal'
    }
  } finally {
    formLoading.value = false
  }
}

async function handleUpdate() {
  if (!editingLocation.value) return

  formError.value = ''

  const validation = locationSchema.safeParse({
    name: formName.value,
    address: formAddress.value || undefined,
  })

  if (!validation.success) {
    formError.value = validation.error.errors[0].message
    return
  }

  formLoading.value = true
  try {
    await locationStore.updateLocation(
      editingLocation.value.id,
      formName.value,
      formAddress.value || undefined
    )
    showEditModal.value = false
    editingLocation.value = null
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      formError.value = axiosErr.response?.data?.detail || 'Error al actualizar sucursal'
    } else {
      formError.value = 'Error al actualizar sucursal'
    }
  } finally {
    formLoading.value = false
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('es-MX', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <PageHeader
      title="Sucursales"
      subtitle="Administra las sucursales de tu negocio."
    >
      <template #actions>
        <Button v-if="authStore.isManager" @click="openCreateModal">
          <Plus class="mr-2 h-4 w-4" />
          Nueva sucursal
        </Button>
      </template>
    </PageHeader>

    <Card>
      <CardContent class="p-6">
        <!-- Loading state -->
        <TableSkeleton v-if="locationStore.loading" :rows="3" :columns="4" />

        <!-- Empty state -->
        <EmptyState
          v-else-if="!locationStore.hasLocations"
          :icon="MapPin"
          title="Aún no tienes sucursales"
          description="Crea tu primera sucursal para poder configurar servicios y estados."
        >
          <template #primary>
            <Button v-if="authStore.isManager" @click="openCreateModal">
              <Plus class="mr-2 h-4 w-4" />
              Crear sucursal
            </Button>
          </template>
        </EmptyState>

        <!-- Table -->
        <Table v-else>
          <thead>
            <tr class="border-b">
              <th class="py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Nombre
              </th>
              <th class="py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Dirección
              </th>
              <th class="hidden py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground sm:table-cell">
                Creada
              </th>
              <th class="py-3 text-right text-xs font-medium uppercase tracking-wide text-muted-foreground">
                <span class="sr-only">Acciones</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="location in locationStore.locations"
              :key="location.id"
              class="group border-b transition-colors last:border-0 hover:bg-muted/50"
            >
              <td class="py-4">
                <span class="text-sm font-medium">{{ location.name }}</span>
              </td>
              <td class="py-4">
                <span class="text-sm text-muted-foreground">
                  {{ location.address || '—' }}
                </span>
              </td>
              <td class="hidden py-4 sm:table-cell">
                <span class="text-sm text-muted-foreground">
                  {{ formatDate(location.created_at) }}
                </span>
              </td>
              <td class="py-4 text-right">
                <Button
                  v-if="authStore.isManager"
                  variant="ghost"
                  size="sm"
                  class="opacity-0 transition-opacity group-hover:opacity-100"
                  @click="openEditModal(location)"
                >
                  <Pencil class="mr-1.5 h-4 w-4" />
                  Editar
                </Button>
              </td>
            </tr>
          </tbody>
        </Table>
      </CardContent>
    </Card>

    <!-- Create Modal -->
    <Dialog v-model:open="showCreateModal" title="Nueva sucursal">
      <form class="space-y-4" @submit.prevent="handleCreate">
        <Alert v-if="formError" variant="destructive">
          {{ formError }}
        </Alert>
        <div class="space-y-2">
          <Label for="name">Nombre</Label>
          <Input
            id="name"
            v-model="formName"
            placeholder="Ej: Sucursal Centro"
            :disabled="formLoading"
          />
        </div>
        <div class="space-y-2">
          <Label for="address">Dirección</Label>
          <Input
            id="address"
            v-model="formAddress"
            placeholder="Ej: Av. Principal #123"
            :disabled="formLoading"
          />
          <p class="text-xs text-muted-foreground">Opcional</p>
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
            {{ formLoading ? 'Creando...' : 'Crear sucursal' }}
          </Button>
        </div>
      </form>
    </Dialog>

    <!-- Edit Modal -->
    <Dialog v-model:open="showEditModal" title="Editar sucursal">
      <form class="space-y-4" @submit.prevent="handleUpdate">
        <Alert v-if="formError" variant="destructive">
          {{ formError }}
        </Alert>
        <div class="space-y-2">
          <Label for="edit-name">Nombre</Label>
          <Input
            id="edit-name"
            v-model="formName"
            placeholder="Ej: Sucursal Centro"
            :disabled="formLoading"
          />
        </div>
        <div class="space-y-2">
          <Label for="edit-address">Dirección</Label>
          <Input
            id="edit-address"
            v-model="formAddress"
            placeholder="Ej: Av. Principal #123"
            :disabled="formLoading"
          />
          <p class="text-xs text-muted-foreground">Opcional</p>
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
  </div>
</template>
