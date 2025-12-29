<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { config } from '@/lib/config'
import PublicTicketCard from '@/components/public/PublicTicketCard.vue'
import PublicTicketSkeleton from '@/components/public/PublicTicketSkeleton.vue'
import PublicTicketNotFound from '@/components/public/PublicTicketNotFound.vue'

// Types
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

const route = useRoute()

// State
const ticket = ref<PublicTicket | null>(null)
const loading = ref(true)
const notFound = ref(false)
const error = ref(false)
const lastUpdate = ref<Date | null>(null)

// Polling
const POLL_INTERVAL = 15000 // 15 seconds
let pollTimer: ReturnType<typeof setTimeout> | null = null

// Get public code from route
const publicCode = computed(() => {
  return (route.params.code as string)?.toUpperCase() || ''
})

// API base URL (from runtime config)
const apiBaseUrl = config.API_BASE_URL

// Branding computed values
const brandColor = computed(() => ticket.value?.brand_primary_color || '#2563eb')
const brandName = computed(() => ticket.value?.brand_name || 'WashFlow')
const brandLogoUrl = computed(() => ticket.value?.brand_logo_url || null)

// Fetch ticket data
async function fetchTicket() {
  if (!publicCode.value) {
    notFound.value = true
    loading.value = false
    return
  }

  try {
    const response = await axios.get<PublicTicket>(
      `${apiBaseUrl}/api/v1/public/tickets/${publicCode.value}`
    )
    ticket.value = response.data
    lastUpdate.value = new Date()
    notFound.value = false
    error.value = false

    // Stop polling if terminal
    if (response.data.status_is_terminal && pollTimer) {
      clearTimeout(pollTimer)
      pollTimer = null
    }
  } catch (err: unknown) {
    if (axios.isAxiosError(err) && err.response?.status === 404) {
      notFound.value = true
    } else {
      error.value = true
    }
  } finally {
    loading.value = false
  }
}

// Schedule polling
function schedulePoll() {
  if (ticket.value?.status_is_terminal) return

  pollTimer = setTimeout(async () => {
    await fetchTicket()
    if (!ticket.value?.status_is_terminal) {
      schedulePoll()
    }
  }, POLL_INTERVAL)
}

// Lifecycle
onMounted(async () => {
  await fetchTicket()
  if (ticket.value && !ticket.value.status_is_terminal) {
    schedulePoll()
  }
})

onUnmounted(() => {
  if (pollTimer) {
    clearTimeout(pollTimer)
  }
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
    <!-- Header with branding -->
    <header class="bg-white border-b border-slate-200 px-4 py-4 shadow-sm">
      <div class="mx-auto max-w-lg">
        <div class="flex items-center gap-3">
          <!-- Logo -->
          <div v-if="brandLogoUrl" class="h-10 w-10 overflow-hidden rounded-lg">
            <img
              :src="brandLogoUrl"
              :alt="brandName"
              class="h-full w-full object-contain"
            />
          </div>
          <div
            v-else
            class="flex h-10 w-10 items-center justify-center rounded-lg font-bold text-white shadow-sm"
            :style="{ backgroundColor: brandColor }"
          >
            {{ brandName.charAt(0).toUpperCase() }}
          </div>

          <div>
            <h1 class="text-lg font-semibold text-slate-900">{{ brandName }}</h1>
            <p class="text-sm text-slate-500">Seguimiento de tu vehículo</p>
          </div>
        </div>
      </div>
    </header>

    <!-- Main content -->
    <main class="px-4 py-8 pb-20">
      <div class="mx-auto max-w-lg">
        <!-- Loading -->
        <PublicTicketSkeleton v-if="loading" />

        <!-- Not found -->
        <PublicTicketNotFound
          v-else-if="notFound"
          :public-code="publicCode"
        />

        <!-- Error -->
        <div
          v-else-if="error"
          class="rounded-2xl bg-white p-8 text-center shadow-lg"
        >
          <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-amber-100">
            <svg
              class="h-8 w-8 text-amber-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-slate-900">Error de conexión</h2>
          <p class="mt-2 text-slate-600">
            No pudimos cargar la información. Por favor, intenta de nuevo.
          </p>
          <button
            class="mt-6 rounded-lg px-6 py-2 font-medium text-white transition-colors"
            :style="{ backgroundColor: brandColor }"
            @click="fetchTicket"
          >
            Reintentar
          </button>
        </div>

        <!-- Ticket card -->
        <PublicTicketCard
          v-else-if="ticket"
          :ticket="ticket"
          :last-update="lastUpdate"
          :brand-color="brandColor"
        />
      </div>
    </main>

    <!-- Footer -->
    <footer class="fixed bottom-0 left-0 right-0 bg-white/80 backdrop-blur-sm border-t border-slate-200 px-4 py-3">
      <div class="mx-auto max-w-lg text-center">
        <p class="text-xs text-slate-400">
          Esta página se actualiza automáticamente
        </p>
        <p class="mt-1 text-xs text-slate-400">
          Si tienes dudas, pregunta en recepción.
        </p>
      </div>
    </footer>
  </div>
</template>
