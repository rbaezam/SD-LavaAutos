<script setup lang="ts">
import { Maximize, Moon, Sun, Clock, Timer, MapPin, Settings2 } from 'lucide-vue-next'
import type { Location } from '@/stores/location'

interface Props {
  locations: Location[]
  selectedLocationId: string | null
  showEta: boolean
  showElapsed: boolean
  darkMode: boolean
  isFullscreen: boolean
  canFullscreen: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  'update:selectedLocationId': [value: string]
  'update:showEta': [value: boolean]
  'update:showElapsed': [value: boolean]
  'update:darkMode': [value: boolean]
  toggleFullscreen: []
}>()
</script>

<template>
  <div
    :class="[
      'flex flex-wrap items-center justify-between gap-4 px-6 py-3',
      darkMode
        ? 'bg-gray-900/50 border-b border-gray-800'
        : 'bg-gray-50 border-b border-gray-200',
    ]"
  >
    <!-- Left: Location selector -->
    <div class="flex items-center gap-3">
      <MapPin
        :class="['h-4 w-4', darkMode ? 'text-gray-400' : 'text-gray-500']"
      />
      <select
        :value="selectedLocationId || ''"
        :class="[
          'rounded-lg border px-3 py-1.5 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary',
          darkMode
            ? 'border-gray-700 bg-gray-800 text-white'
            : 'border-gray-300 bg-white text-gray-900',
        ]"
        @change="emit('update:selectedLocationId', ($event.target as HTMLSelectElement).value)"
      >
        <option
          v-for="location in locations"
          :key="location.id"
          :value="location.id"
        >
          {{ location.name }}
        </option>
      </select>
    </div>

    <!-- Right: Controls -->
    <div class="flex items-center gap-2">
      <!-- Show ETA toggle -->
      <button
        type="button"
        :class="[
          'flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors',
          showEta
            ? darkMode
              ? 'bg-primary/20 text-primary'
              : 'bg-primary/10 text-primary'
            : darkMode
              ? 'text-gray-400 hover:bg-gray-800'
              : 'text-gray-600 hover:bg-gray-200',
        ]"
        title="Mostrar ETA"
        @click="emit('update:showEta', !showEta)"
      >
        <Clock class="h-4 w-4" />
        <span class="hidden sm:inline">Mostrar ETA</span>
      </button>

      <!-- Show elapsed toggle -->
      <button
        type="button"
        :class="[
          'flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors',
          showElapsed
            ? darkMode
              ? 'bg-primary/20 text-primary'
              : 'bg-primary/10 text-primary'
            : darkMode
              ? 'text-gray-400 hover:bg-gray-800'
              : 'text-gray-600 hover:bg-gray-200',
        ]"
        title="Mostrar tiempo transcurrido"
        @click="emit('update:showElapsed', !showElapsed)"
      >
        <Timer class="h-4 w-4" />
        <span class="hidden sm:inline">Tiempo transcurrido</span>
      </button>

      <!-- Dark mode toggle -->
      <button
        type="button"
        :class="[
          'flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors',
          darkMode
            ? 'bg-gray-700 text-yellow-400'
            : 'text-gray-600 hover:bg-gray-200',
        ]"
        title="Modo oscuro"
        @click="emit('update:darkMode', !darkMode)"
      >
        <Moon v-if="!darkMode" class="h-4 w-4" />
        <Sun v-else class="h-4 w-4" />
        <span class="hidden sm:inline">{{ darkMode ? 'Modo claro' : 'Modo oscuro' }}</span>
      </button>

      <!-- Fullscreen button -->
      <button
        v-if="canFullscreen"
        type="button"
        :class="[
          'flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors',
          isFullscreen
            ? 'bg-primary text-primary-foreground'
            : darkMode
              ? 'bg-gray-800 text-white hover:bg-gray-700'
              : 'bg-gray-900 text-white hover:bg-gray-800',
        ]"
        title="Pantalla completa"
        @click="emit('toggleFullscreen')"
      >
        <Maximize class="h-4 w-4" />
        <span class="hidden sm:inline">Pantalla completa</span>
      </button>

      <span
        v-else
        :class="[
          'text-xs',
          darkMode ? 'text-gray-500' : 'text-gray-400',
        ]"
        title="Tu navegador no permite pantalla completa."
      >
        <Settings2 class="h-4 w-4" />
      </span>
    </div>
  </div>
</template>
