<script setup lang="ts">
import { computed } from 'vue'
import { Badge } from '@/components/ui'
import { cn } from '@/lib/utils'
import type { Status } from '@/stores/status'
import type { KanbanTicket } from '@/stores/kanban'
import KanbanCard from './KanbanCard.vue'

interface Props {
  status: Status
  tickets: KanbanTicket[]
  columnIndex: number
  isDropTarget?: boolean
  draggingTicketId?: string | null
  highlighted?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isDropTarget: false,
  draggingTicketId: null,
  highlighted: false,
})

const emit = defineEmits<{
  dragStart: [ticketId: string, statusId: string]
  dragEnd: []
  drop: [ticketId: string, toStatusId: string]
}>()

// Column colors based on index
const columnColors = [
  'border-t-blue-500',
  'border-t-amber-500',
  'border-t-purple-500',
  'border-t-emerald-500',
  'border-t-rose-500',
  'border-t-cyan-500',
  'border-t-orange-500',
  'border-t-indigo-500',
]

const columnColor = computed(() => {
  if (props.status.is_terminal) return 'border-t-green-500'
  return columnColors[props.columnIndex % columnColors.length]
})

const ticketCount = computed(() => props.tickets.length)

function handleDragStart(e: DragEvent, ticketId: string) {
  if (!e.dataTransfer) return
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('ticketId', ticketId)
  e.dataTransfer.setData('fromStatusId', props.status.id)
  emit('dragStart', ticketId, props.status.id)
}

function handleDragEnd() {
  emit('dragEnd')
}

function handleDragOver(e: DragEvent) {
  e.preventDefault()
  if (e.dataTransfer) {
    e.dataTransfer.dropEffect = 'move'
  }
}

function handleDrop(e: DragEvent) {
  e.preventDefault()
  const ticketId = e.dataTransfer?.getData('ticketId')
  if (ticketId) {
    emit('drop', ticketId, props.status.id)
  }
}
</script>

<template>
  <div
    :class="
      cn(
        'flex h-full w-72 flex-shrink-0 flex-col rounded-lg border-t-4 bg-muted/30 transition-all duration-300',
        columnColor,
        isDropTarget && 'ring-2 ring-primary ring-offset-2 bg-primary/5',
        highlighted && 'ring-2 ring-blue-500 ring-offset-2 bg-blue-50/50 dark:bg-blue-900/20'
      )
    "
    @dragover="handleDragOver"
    @drop="handleDrop"
  >
    <!-- Column Header -->
    <div class="sticky top-0 z-10 flex items-center justify-between gap-2 bg-background/95 backdrop-blur-sm p-3 border-b">
      <div class="flex items-center gap-2 min-w-0">
        <h3 class="font-medium text-sm truncate">{{ status.name }}</h3>
        <Badge v-if="status.is_terminal" variant="success" class="text-xs">
          Final
        </Badge>
      </div>
      <Badge variant="secondary" class="text-xs tabular-nums shrink-0">
        {{ ticketCount }}
      </Badge>
    </div>

    <!-- Column Body -->
    <div class="flex-1 overflow-y-auto p-2 space-y-2">
      <!-- Empty state -->
      <div
        v-if="tickets.length === 0"
        class="flex h-24 items-center justify-center rounded-lg border-2 border-dashed text-center"
      >
        <p class="text-xs text-muted-foreground px-4">
          Sin vehículos en este estado
        </p>
      </div>

      <!-- Ticket cards -->
      <div
        v-for="ticket in tickets"
        :key="ticket.id"
        draggable="true"
        @dragstart="(e) => handleDragStart(e, ticket.id)"
        @dragend="handleDragEnd"
      >
        <KanbanCard
          :ticket="ticket"
          :is-dragging="draggingTicketId === ticket.id"
        />
      </div>
    </div>
  </div>
</template>
