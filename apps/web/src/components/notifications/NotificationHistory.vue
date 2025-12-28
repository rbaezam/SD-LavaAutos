<script setup lang="ts">
import { computed } from 'vue'
import { MessageCircle, Smartphone, Bell } from 'lucide-vue-next'
import NotificationStatusBadge from './NotificationStatusBadge.vue'
import type { NotificationLog } from '@/stores/notification'
import { useNotificationStore } from '@/stores/notification'

interface Props {
  logs: NotificationLog[]
  showTicketId?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showTicketId: false,
})

const notificationStore = useNotificationStore()

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Ahora'
  if (diffMins < 60) return `Hace ${diffMins} min`
  if (diffHours < 24) return `Hace ${diffHours}h`
  if (diffDays < 7) return `Hace ${diffDays}d`

  return date.toLocaleDateString('es-MX', {
    day: 'numeric',
    month: 'short',
  })
}

const sortedLogs = computed(() => {
  return [...props.logs].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )
})
</script>

<template>
  <div class="space-y-3">
    <!-- Empty state -->
    <div
      v-if="logs.length === 0"
      class="flex flex-col items-center justify-center py-8 text-center"
    >
      <Bell class="h-8 w-8 text-muted-foreground/50" />
      <p class="mt-2 text-sm text-muted-foreground">
        Sin notificaciones enviadas
      </p>
    </div>

    <!-- Log list -->
    <div
      v-for="log in sortedLogs"
      :key="log.id"
      class="flex items-start gap-3 rounded-lg border p-3"
    >
      <!-- Channel icon -->
      <div
        :class="[
          'flex h-8 w-8 items-center justify-center rounded-full',
          log.channel === 'whatsapp'
            ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
            : 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
        ]"
      >
        <component
          :is="log.channel === 'whatsapp' ? MessageCircle : Smartphone"
          class="h-4 w-4"
        />
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <span class="font-medium text-sm">
            {{ notificationStore.getChannelLabel(log.channel) }}
          </span>
          <NotificationStatusBadge :status="log.status" />
        </div>

        <p class="text-xs text-muted-foreground mt-0.5">
          {{ notificationStore.getEventLabel(log.event) }}
        </p>

        <p class="text-xs text-muted-foreground font-mono mt-1 truncate">
          {{ log.recipient }}
        </p>

        <p v-if="showTicketId && log.ticket_id" class="text-xs text-muted-foreground mt-1">
          Ticket: {{ log.ticket_id.slice(0, 8) }}...
        </p>
      </div>

      <!-- Timestamp -->
      <span class="text-xs text-muted-foreground whitespace-nowrap">
        {{ formatDate(log.created_at) }}
      </span>
    </div>
  </div>
</template>
