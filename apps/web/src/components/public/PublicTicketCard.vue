<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import {
  Car,
  Clock,
  MapPin,
  CheckCircle2,
  BadgeCheck,
  Hourglass,
  Loader2,
  Wind,
  Sparkles,
  Tag,
} from 'lucide-vue-next'

interface PublicTicket {
  public_code: string
  vehicle_label: string
  service_name: string | null
  status_name: string
  status_is_terminal: boolean
  eta_at: string | null
  updated_at: string
  location_name: string
  organization_name: string
  brand_name: string
  brand_logo_url: string | null
  brand_primary_color: string | null
}

interface Props {
  ticket: PublicTicket
  lastUpdate: Date | null
  brandColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  brandColor: '#2563eb',
})

// Live clock for relative time
const now = ref(new Date())
let clockInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  clockInterval = setInterval(() => {
    now.value = new Date()
  }, 10000) // Update every 10 seconds
})

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval)
})

// Normalize status name for icon matching
function normalizeStatus(name: string): string {
  return name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}

// Get contextual icon based on status name
const statusIcon = computed(() => {
  const normalized = normalizeStatus(props.ticket.status_name)

  // Terminal states
  if (props.ticket.status_is_terminal) {
    if (normalized.includes('entregado') || normalized.includes('entrega')) {
      return BadgeCheck
    }
    return CheckCircle2
  }

  // In-progress states
  if (normalized.includes('espera') || normalized.includes('recepcion')) {
    return Hourglass
  }
  if (normalized.includes('lavado') || normalized.includes('lavando')) {
    return Loader2
  }
  if (normalized.includes('secado') || normalized.includes('secando')) {
    return Wind
  }
  if (normalized.includes('detallado') || normalized.includes('detalle')) {
    return Sparkles
  }

  // Default: spinning loader
  return Loader2
})

// Should the icon spin?
const iconShouldSpin = computed(() => {
  const normalized = normalizeStatus(props.ticket.status_name)
  return (
    !props.ticket.status_is_terminal &&
    (normalized.includes('lavado') || normalized.includes('lavando'))
  )
})

// Hero title for terminal states
const heroTitle = computed(() => {
  const normalized = normalizeStatus(props.ticket.status_name)

  if (props.ticket.status_is_terminal) {
    if (normalized.includes('entregado') || normalized.includes('entrega')) {
      return 'ENTREGADO'
    }
    return 'LISTO'
  }

  return props.ticket.status_name.toUpperCase()
})

// Hero subtitle for terminal states
const heroSubtitle = computed(() => {
  const normalized = normalizeStatus(props.ticket.status_name)

  if (props.ticket.status_is_terminal) {
    if (normalized.includes('entregado') || normalized.includes('entrega')) {
      return 'Gracias por tu preferencia.'
    }
    return 'Tu vehículo está listo para entrega'
  }

  return 'Tu vehículo está siendo atendido'
})

// Hero gradient colors
const heroGradient = computed(() => {
  if (props.ticket.status_is_terminal) {
    return 'from-emerald-500 to-emerald-600'
  }
  // Use brand color for non-terminal
  return ''
})

const heroStyle = computed(() => {
  if (!props.ticket.status_is_terminal) {
    return {
      background: `linear-gradient(135deg, ${props.brandColor}, ${adjustColor(props.brandColor, -20)})`,
    }
  }
  return {}
})

// Adjust color brightness
function adjustColor(hex: string, percent: number): string {
  const num = parseInt(hex.replace('#', ''), 16)
  const r = Math.min(255, Math.max(0, (num >> 16) + percent))
  const g = Math.min(255, Math.max(0, ((num >> 8) & 0x00ff) + percent))
  const b = Math.min(255, Math.max(0, (num & 0x0000ff) + percent))
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`
}

// Format ETA
const formattedEta = computed(() => {
  if (!props.ticket.eta_at) return null
  const eta = new Date(props.ticket.eta_at)
  return eta.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })
})

// Time until ETA
const etaRelative = computed(() => {
  if (!props.ticket.eta_at) return null
  const eta = new Date(props.ticket.eta_at)
  const diffMs = eta.getTime() - now.value.getTime()

  if (diffMs < 0) return 'Pasado'

  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return 'Menos de 1 min'
  if (diffMins < 60) return `~${diffMins} min`

  const hours = Math.floor(diffMins / 60)
  const mins = diffMins % 60
  return mins > 0 ? `~${hours}h ${mins}m` : `~${hours}h`
})

// Last update relative time
const lastUpdateRelative = computed(() => {
  if (!props.lastUpdate) return null
  const diffMs = now.value.getTime() - props.lastUpdate.getTime()
  const diffSecs = Math.floor(diffMs / 1000)

  if (diffSecs < 10) return 'ahora'
  if (diffSecs < 60) return `hace ${diffSecs}s`

  const diffMins = Math.floor(diffSecs / 60)
  if (diffMins < 60) return `hace ${diffMins} min`

  return 'hace más de 1h'
})
</script>

<template>
  <div class="overflow-hidden rounded-2xl bg-white shadow-xl">
    <!-- Hero section with status -->
    <div
      :class="[
        'relative px-6 py-8',
        heroGradient,
      ]"
      :style="heroStyle"
    >
      <!-- Success animation for terminal -->
      <Transition
        enter-active-class="transition-opacity duration-500"
        enter-from-class="opacity-0"
      >
        <div
          v-if="ticket.status_is_terminal"
          class="absolute inset-0 flex items-center justify-center"
        >
          <div class="h-32 w-32 animate-ping rounded-full bg-white/10" />
        </div>
      </Transition>

      <div class="relative text-center text-white">
        <!-- Status icon -->
        <div class="mb-4 flex justify-center">
          <div
            class="flex h-20 w-20 items-center justify-center rounded-full bg-white/20 backdrop-blur-sm"
          >
            <component
              :is="statusIcon"
              :class="['h-10 w-10', iconShouldSpin && 'animate-spin']"
            />
          </div>
        </div>

        <!-- Status name -->
        <h2 class="text-2xl font-bold uppercase tracking-wide">
          {{ heroTitle }}
        </h2>

        <!-- Status message -->
        <p class="mt-2 text-lg text-white/80">
          {{ heroSubtitle }}
        </p>
      </div>
    </div>

    <!-- Ticket info -->
    <div class="divide-y divide-slate-100">
      <!-- Public code -->
      <div class="flex items-center justify-between px-6 py-4">
        <span class="text-sm font-medium text-slate-500">Folio</span>
        <span class="font-mono text-xl font-bold text-slate-900">
          {{ ticket.public_code }}
        </span>
      </div>

      <!-- Vehicle -->
      <div class="flex items-center justify-between px-6 py-4">
        <div class="flex items-center gap-2 text-slate-500">
          <Car class="h-4 w-4" />
          <span class="text-sm font-medium">Vehículo</span>
        </div>
        <span class="font-medium text-slate-900">
          {{ ticket.vehicle_label }}
        </span>
      </div>

      <!-- Service -->
      <div v-if="ticket.service_name" class="flex items-center justify-between px-6 py-4">
        <div class="flex items-center gap-2 text-slate-500">
          <Tag class="h-4 w-4" />
          <span class="text-sm font-medium">Servicio</span>
        </div>
        <span class="font-medium text-slate-900">
          {{ ticket.service_name }}
        </span>
      </div>

      <!-- ETA (only show if not terminal) -->
      <div class="flex items-center justify-between px-6 py-4">
        <div class="flex items-center gap-2 text-slate-500">
          <Clock class="h-4 w-4" />
          <span class="text-sm font-medium">Hora estimada</span>
        </div>
        <div v-if="!ticket.status_is_terminal && formattedEta" class="text-right">
          <span class="font-medium text-slate-900">{{ formattedEta }}</span>
          <span class="ml-2 text-sm text-slate-500">({{ etaRelative }})</span>
        </div>
        <span v-else class="text-sm text-slate-400">
          {{ ticket.status_is_terminal ? '—' : 'No disponible' }}
        </span>
      </div>

      <!-- Location -->
      <div class="flex items-center justify-between px-6 py-4">
        <div class="flex items-center gap-2 text-slate-500">
          <MapPin class="h-4 w-4" />
          <span class="text-sm font-medium">Sucursal</span>
        </div>
        <span class="font-medium text-slate-900">
          {{ ticket.location_name }}
        </span>
      </div>
    </div>

    <!-- Footer -->
    <div class="bg-slate-50 px-6 py-3">
      <p class="text-center text-xs text-slate-400">
        Última actualización: {{ lastUpdateRelative }}
      </p>
    </div>
  </div>
</template>
