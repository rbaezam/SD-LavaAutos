<script setup lang="ts">
import { computed } from 'vue'
import { Plus, ArrowRightLeft, Pencil, Clock } from 'lucide-vue-next'
import type { TicketEvent } from '@/stores/ticket'

interface Props {
  events: TicketEvent[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

// Field key to Spanish label mapping
const fieldLabels: Record<string, string> = {
  plate: 'Placas',
  vehicle_desc: 'Descripción',
  manual_ticket_no: 'Folio físico',
  customer_name: 'Cliente',
  customer_whatsapp: 'WhatsApp',
  service_ids: 'Servicios',
  eta_at: 'ETA',
}

// Event type configurations
const eventConfig: Record<string, { icon: typeof Plus; title: string; color: string }> = {
  created: { icon: Plus, title: 'Ticket creado', color: 'bg-green-500' },
  moved: { icon: ArrowRightLeft, title: 'Cambio de estado', color: 'bg-blue-500' },
  edited: { icon: Pencil, title: 'Información actualizada', color: 'bg-amber-500' },
  eta_changed: { icon: Clock, title: 'ETA ajustada', color: 'bg-purple-500' },
}

// Reverse chronological order
const sortedEvents = computed(() => {
  return [...props.events].sort(
    (a, b) => new Date(b.happened_at).getTime() - new Date(a.happened_at).getTime()
  )
})

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'ahora'
  if (diffMins < 60) return `hace ${diffMins} min`

  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `hace ${diffHours}h`

  const diffDays = Math.floor(diffHours / 24)
  if (diffDays === 1) return 'ayer'
  if (diffDays < 7) return `hace ${diffDays} días`

  return date.toLocaleDateString('es-MX', { day: '2-digit', month: 'short' })
}

function formatEtaTime(etaStr: string): string {
  const eta = new Date(etaStr)
  return eta.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })
}

function getEventDetail(event: TicketEvent): string | null {
  if (event.event_type === 'moved') {
    const from = event.from_status_name || '?'
    const to = event.to_status_name || '?'
    return `De "${from}" a "${to}"`
  }

  if (event.event_type === 'created') {
    return event.to_status_name ? `Estado inicial: ${event.to_status_name}` : null
  }

  if (event.event_type === 'eta_changed' && event.payload_json) {
    const payload = event.payload_json as { from?: string | null; to?: string | null }
    if (payload.to) {
      return `Nueva ETA: ${formatEtaTime(payload.to)}`
    }
    return 'ETA eliminada'
  }

  if (event.event_type === 'edited' && event.payload_json) {
    // payload_json is a dict with field names as keys: { "plate": { "from": "...", "to": "..." }, ... }
    const payload = event.payload_json as Record<string, unknown>
    const fields = Object.keys(payload)
    if (fields.length === 0) return null

    const labels = fields.slice(0, 3).map((f) => fieldLabels[f] || f)
    const remaining = fields.length - 3

    if (remaining > 0) {
      return `${labels.join(', ')} y ${remaining} más`
    }
    return labels.join(', ')
  }

  return null
}

function getConfig(eventType: string) {
  return eventConfig[eventType] || eventConfig.edited
}
</script>

<template>
  <div class="relative">
    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="flex gap-3">
        <div class="flex flex-col items-center">
          <div class="h-8 w-8 animate-pulse rounded-full bg-muted" />
          <div v-if="i < 3" class="mt-2 h-12 w-0.5 bg-muted" />
        </div>
        <div class="flex-1 space-y-2 pt-1">
          <div class="h-4 w-32 animate-pulse rounded bg-muted" />
          <div class="h-3 w-24 animate-pulse rounded bg-muted" />
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="events.length === 0"
      class="flex flex-col items-center justify-center py-8 text-center"
    >
      <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-muted">
        <Clock class="h-6 w-6 text-muted-foreground" />
      </div>
      <p class="text-sm text-muted-foreground">Aún no hay actividad registrada.</p>
    </div>

    <!-- Timeline -->
    <div v-else class="space-y-0">
      <div
        v-for="(event, index) in sortedEvents"
        :key="event.id"
        class="relative flex gap-3"
      >
        <!-- Timeline line and dot -->
        <div class="flex flex-col items-center">
          <!-- Dot with icon -->
          <div
            :class="[
              'flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-white',
              getConfig(event.event_type).color,
            ]"
          >
            <component :is="getConfig(event.event_type).icon" class="h-4 w-4" />
          </div>
          <!-- Connecting line -->
          <div
            v-if="index < sortedEvents.length - 1"
            class="mt-1 h-full w-0.5 bg-border"
          />
        </div>

        <!-- Content -->
        <div class="flex-1 pb-6">
          <!-- Title -->
          <p class="text-sm font-medium leading-tight">
            {{ getConfig(event.event_type).title }}
          </p>

          <!-- Detail line -->
          <p v-if="getEventDetail(event)" class="mt-0.5 text-sm text-muted-foreground">
            {{ getEventDetail(event) }}
          </p>

          <!-- Meta line -->
          <p class="mt-1 text-xs text-muted-foreground/70">
            {{ formatRelativeTime(event.happened_at) }}
            <template v-if="event.actor_name">
              · por {{ event.actor_name }}
            </template>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
