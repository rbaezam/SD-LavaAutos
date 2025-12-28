<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Car, Plus, RefreshCw, AlertCircle } from 'lucide-vue-next'
import { Button, Alert } from '@/components/ui'
import EmptyState from '@/components/EmptyState.vue'
import { useKanbanStore } from '@/stores/kanban'
import { useLocationStore } from '@/stores/location'
import { useAuthStore } from '@/stores/auth'
import KanbanColumn from './KanbanColumn.vue'
import KanbanSkeleton from './KanbanSkeleton.vue'

const router = useRouter()
const route = useRoute()
const kanbanStore = useKanbanStore()
const locationStore = useLocationStore()
const authStore = useAuthStore()

// Drag state
const draggingTicketId = ref<string | null>(null)
const draggingFromStatusId = ref<string | null>(null)
const dropTargetStatusId = ref<string | null>(null)

// Error state for move operations
const moveError = ref<string | null>(null)
const moveErrorTimeout = ref<ReturnType<typeof setTimeout> | null>(null)

// Auto-refresh
const refreshInterval = ref<ReturnType<typeof setInterval> | null>(null)
const isRefreshing = ref(false)

// Highlighted column from query param (for navigation from dashboard)
const highlightedStatusId = ref<string | null>(null)
const columnRefs = ref<Map<string, HTMLElement>>(new Map())

const hasNoStatuses = computed(() => kanbanStore.sortedStatuses.length === 0)
const hasNoTickets = computed(() => kanbanStore.tickets.length === 0)

async function loadBoard() {
  if (!locationStore.selectedLocationId) return
  await kanbanStore.fetchBoard(locationStore.selectedLocationId)

  // Check for status query param after board loads
  await nextTick()
  handleStatusQueryParam()
}

// Handle status query param (from dashboard navigation)
function handleStatusQueryParam() {
  const statusParam = route.query.status as string | undefined
  if (statusParam && kanbanStore.statuses.some((s) => s.id === statusParam)) {
    highlightedStatusId.value = statusParam

    // Scroll to the column
    const columnElement = columnRefs.value.get(statusParam)
    if (columnElement) {
      columnElement.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
    }

    // Clear highlight after 2 seconds
    setTimeout(() => {
      highlightedStatusId.value = null
    }, 2000)

    // Clear the query param from URL without navigation
    router.replace({ query: {} })
  }
}

// Register column ref
function setColumnRef(statusId: string, el: HTMLElement | null) {
  if (el) {
    columnRefs.value.set(statusId, el)
  } else {
    columnRefs.value.delete(statusId)
  }
}

async function handleRefresh() {
  if (!locationStore.selectedLocationId || isRefreshing.value) return
  isRefreshing.value = true
  await kanbanStore.refresh(locationStore.selectedLocationId)
  isRefreshing.value = false
}

function handleDragStart(ticketId: string, statusId: string) {
  draggingTicketId.value = ticketId
  draggingFromStatusId.value = statusId
  moveError.value = null
}

function handleDragEnd() {
  draggingTicketId.value = null
  draggingFromStatusId.value = null
  dropTargetStatusId.value = null
}

async function handleDrop(ticketId: string, toStatusId: string) {
  const fromStatusId = draggingFromStatusId.value
  handleDragEnd()

  if (!fromStatusId || fromStatusId === toStatusId) return

  // Check if moving to terminal status and user is staff
  const toStatus = kanbanStore.statuses.find((s) => s.id === toStatusId)
  if (toStatus?.is_terminal && authStore.user?.role === 'staff') {
    showMoveError('No tienes permisos para finalizar un ticket')
    return
  }

  const success = await kanbanStore.moveTicket(ticketId, fromStatusId, toStatusId)
  if (!success) {
    showMoveError('Error al mover el ticket')
  }
}

function showMoveError(message: string) {
  moveError.value = message
  if (moveErrorTimeout.value) {
    clearTimeout(moveErrorTimeout.value)
  }
  moveErrorTimeout.value = setTimeout(() => {
    moveError.value = null
  }, 4000)
}

function goToCreateTicket() {
  router.push({ name: 'tickets' })
}

// Watch for location changes
watch(
  () => locationStore.selectedLocationId,
  () => {
    loadBoard()
  }
)

onMounted(() => {
  loadBoard()
  // Auto-refresh every 30 seconds
  refreshInterval.value = setInterval(() => {
    if (locationStore.selectedLocationId && !draggingTicketId.value) {
      kanbanStore.refresh(locationStore.selectedLocationId)
    }
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  if (moveErrorTimeout.value) {
    clearTimeout(moveErrorTimeout.value)
  }
  kanbanStore.clearBoard()
})
</script>

<template>
  <div class="flex h-full flex-col">
    <!-- Error toast -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="transform -translate-y-2 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform -translate-y-2 opacity-0"
    >
      <div
        v-if="moveError"
        class="fixed top-20 left-1/2 z-50 -translate-x-1/2"
      >
        <Alert variant="destructive" class="flex items-center gap-2 shadow-lg">
          <AlertCircle class="h-4 w-4" />
          {{ moveError }}
        </Alert>
      </div>
    </Transition>

    <!-- Toolbar -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <span class="text-sm text-muted-foreground">
          {{ kanbanStore.totalActiveTickets }} vehículos en operación
        </span>
      </div>
      <Button
        variant="ghost"
        size="sm"
        :disabled="isRefreshing"
        @click="handleRefresh"
      >
        <RefreshCw :class="['h-4 w-4 mr-2', isRefreshing && 'animate-spin']" />
        Actualizar
      </Button>
    </div>

    <!-- Loading state -->
    <KanbanSkeleton v-if="kanbanStore.loading" />

    <!-- No location selected -->
    <Alert v-else-if="!locationStore.selectedLocationId" class="mb-4">
      Selecciona una sucursal para ver la operación.
    </Alert>

    <!-- No statuses -->
    <EmptyState
      v-else-if="hasNoStatuses"
      :icon="Car"
      title="Sin estados configurados"
      description="Configura los estados del flujo de trabajo para comenzar a usar el tablero."
    >
      <template #primary>
        <Button @click="router.push({ name: 'statuses' })">
          Configurar estados
        </Button>
      </template>
    </EmptyState>

    <!-- No tickets (but has statuses) -->
    <div v-else-if="hasNoTickets" class="flex-1 flex flex-col">
      <!-- Still show columns -->
      <div class="flex gap-4 overflow-x-auto pb-4 flex-1">
        <KanbanColumn
          v-for="(status, index) in kanbanStore.sortedStatuses"
          :ref="(el) => setColumnRef(status.id, el as HTMLElement | null)"
          :key="status.id"
          :status="status"
          :tickets="[]"
          :column-index="index"
          :highlighted="highlightedStatusId === status.id"
        />
      </div>
      <!-- Centered empty message -->
      <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div class="bg-background/95 backdrop-blur-sm rounded-lg p-8 shadow-lg pointer-events-auto">
          <EmptyState
            :icon="Car"
            title="No hay vehículos en operación"
            description="Cuando registres un ticket aparecerá aquí."
          >
            <template #primary>
              <Button @click="goToCreateTicket">
                <Plus class="mr-2 h-4 w-4" />
                Crear ticket
              </Button>
            </template>
          </EmptyState>
        </div>
      </div>
    </div>

    <!-- Kanban board -->
    <div v-else class="flex gap-4 overflow-x-auto pb-4 flex-1">
      <KanbanColumn
        v-for="(status, index) in kanbanStore.sortedStatuses"
        :ref="(el) => setColumnRef(status.id, el as HTMLElement | null)"
        :key="status.id"
        :status="status"
        :tickets="kanbanStore.ticketsByStatus[status.id] || []"
        :column-index="index"
        :dragging-ticket-id="draggingTicketId"
        :is-drop-target="dropTargetStatusId === status.id"
        :highlighted="highlightedStatusId === status.id"
        @drag-start="handleDragStart"
        @drag-end="handleDragEnd"
        @drop="handleDrop"
      />
    </div>
  </div>
</template>
