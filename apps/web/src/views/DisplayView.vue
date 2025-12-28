<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { WifiOff } from 'lucide-vue-next'
import api from '@/lib/api'
import { useLocationStore, type Location } from '@/stores/location'
import type { Status } from '@/stores/status'
import type { TicketListItem } from '@/stores/ticket'
import DisplayHeader from '@/components/display/DisplayHeader.vue'
import DisplayToolbar from '@/components/display/DisplayToolbar.vue'
import DisplayBoard from '@/components/display/DisplayBoard.vue'
import DisplaySkeleton from '@/components/display/DisplaySkeleton.vue'

// LocalStorage keys
const STORAGE_KEYS = {
  showEta: 'display_show_eta',
  showElapsed: 'display_show_elapsed',
  darkMode: 'display_dark_mode',
  locationId: 'display_location_id',
}

// Load preference from localStorage
function loadPref<T>(key: string, defaultValue: T): T {
  const stored = localStorage.getItem(key)
  if (stored === null) return defaultValue
  try {
    return JSON.parse(stored) as T
  } catch {
    return defaultValue
  }
}

// Save preference to localStorage
function savePref<T>(key: string, value: T) {
  localStorage.setItem(key, JSON.stringify(value))
}

const locationStore = useLocationStore()

// UI Preferences (persisted)
const showEta = ref(loadPref(STORAGE_KEYS.showEta, true))
const showElapsed = ref(loadPref(STORAGE_KEYS.showElapsed, true))
const darkMode = ref(loadPref(STORAGE_KEYS.darkMode, false))
const selectedLocationId = ref<string | null>(
  loadPref(STORAGE_KEYS.locationId, null) || locationStore.selectedLocationId
)

// Watch and persist preferences
watch(showEta, (val) => savePref(STORAGE_KEYS.showEta, val))
watch(showElapsed, (val) => savePref(STORAGE_KEYS.showElapsed, val))
watch(darkMode, (val) => savePref(STORAGE_KEYS.darkMode, val))
watch(selectedLocationId, (val) => savePref(STORAGE_KEYS.locationId, val))

// Data state
const statuses = ref<Status[]>([])
const tickets = ref<TicketListItem[]>([])
const lastUpdate = ref<Date | null>(null)
const initialLoading = ref(true)
const connectionError = ref(false)

// Polling state
const POLL_INTERVAL_DEFAULT = 10000 // 10 seconds
const POLL_INTERVAL_ERROR_MAX = 30000 // 30 seconds max backoff
let pollInterval = POLL_INTERVAL_DEFAULT
let pollTimer: ReturnType<typeof setTimeout> | null = null

// Fullscreen state
const isFullscreen = ref(false)
const canFullscreen = ref(!!document.documentElement.requestFullscreen)

// Selected location info
const selectedLocation = computed<Location | null>(() => {
  if (!selectedLocationId.value) return null
  return locationStore.locations.find((l) => l.id === selectedLocationId.value) || null
})

// Fetch data from API
async function fetchData() {
  if (!selectedLocationId.value) return

  try {
    // Fetch statuses and tickets in parallel
    const [statusesRes, ticketsRes] = await Promise.all([
      api.get<{ items: Status[] }>(`/api/v1/locations/${selectedLocationId.value}/statuses`),
      api.get<{ items: TicketListItem[] }>(
        `/api/v1/locations/${selectedLocationId.value}/tickets`,
        { params: { date: 'today' } }
      ),
    ])

    statuses.value = statusesRes.data.items
    tickets.value = ticketsRes.data.items
    lastUpdate.value = new Date()
    connectionError.value = false
    pollInterval = POLL_INTERVAL_DEFAULT // Reset on success
  } catch (err) {
    console.error('Display fetch error:', err)
    connectionError.value = true
    // Increase backoff on error
    pollInterval = Math.min(pollInterval * 1.5, POLL_INTERVAL_ERROR_MAX)
  } finally {
    initialLoading.value = false
  }
}

// Schedule next poll
function schedulePoll() {
  if (pollTimer) clearTimeout(pollTimer)
  pollTimer = setTimeout(async () => {
    await fetchData()
    schedulePoll()
  }, pollInterval)
}

// Fullscreen handling
async function toggleFullscreen() {
  if (!canFullscreen.value) return

  try {
    if (!document.fullscreenElement) {
      await document.documentElement.requestFullscreen()
      isFullscreen.value = true
    } else {
      await document.exitFullscreen()
      isFullscreen.value = false
    }
  } catch (err) {
    console.error('Fullscreen error:', err)
  }
}

function handleFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement
}

// Lifecycle
onMounted(async () => {
  // Ensure locations are loaded
  if (locationStore.locations.length === 0) {
    await locationStore.fetchLocations()
  }

  // Auto-select first location if none selected
  if (!selectedLocationId.value && locationStore.locations.length > 0) {
    selectedLocationId.value = locationStore.locations[0].id
  }

  // Initial fetch
  await fetchData()

  // Start polling
  schedulePoll()

  // Listen for fullscreen changes
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  if (pollTimer) clearTimeout(pollTimer)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
})

// Refetch when location changes
watch(selectedLocationId, async (newId) => {
  if (newId) {
    initialLoading.value = true
    await fetchData()
  }
})
</script>

<template>
  <div
    :class="[
      'flex h-screen flex-col overflow-hidden transition-colors duration-300',
      darkMode ? 'bg-gray-950' : 'bg-gray-100',
    ]"
  >
    <!-- Loading skeleton -->
    <DisplaySkeleton
      v-if="initialLoading"
      :dark-mode="darkMode"
      :column-count="4"
    />

    <template v-else>
      <!-- Header -->
      <DisplayHeader
        :location-name="selectedLocation?.name || null"
        :last-update="lastUpdate"
        :dark-mode="darkMode"
      />

      <!-- Toolbar -->
      <DisplayToolbar
        :locations="locationStore.locations"
        :selected-location-id="selectedLocationId"
        :show-eta="showEta"
        :show-elapsed="showElapsed"
        :dark-mode="darkMode"
        :is-fullscreen="isFullscreen"
        :can-fullscreen="canFullscreen"
        @update:selected-location-id="selectedLocationId = $event"
        @update:show-eta="showEta = $event"
        @update:show-elapsed="showElapsed = $event"
        @update:dark-mode="darkMode = $event"
        @toggle-fullscreen="toggleFullscreen"
      />

      <!-- Connection error banner -->
      <div
        v-if="connectionError"
        :class="[
          'flex items-center justify-center gap-2 py-2 text-sm font-medium',
          darkMode ? 'bg-red-900/50 text-red-300' : 'bg-red-100 text-red-700',
        ]"
      >
        <WifiOff class="h-4 w-4" />
        Sin conexión. Reintentando…
      </div>

      <!-- Board -->
      <main class="flex-1 overflow-hidden p-6">
        <DisplayBoard
          :statuses="statuses"
          :tickets="tickets"
          :show-eta="showEta"
          :show-elapsed="showElapsed"
          :dark-mode="darkMode"
        />
      </main>
    </template>
  </div>
</template>
