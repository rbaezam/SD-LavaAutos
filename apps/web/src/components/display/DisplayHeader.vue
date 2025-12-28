<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  locationName: string | null
  lastUpdate: Date | null
  darkMode?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  darkMode: false,
})

// Live clock
const currentTime = ref(new Date())
let clockInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  clockInterval = setInterval(() => {
    currentTime.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval)
})

// Current time formatted
const formattedTime = computed(() => {
  return currentTime.value.toLocaleTimeString('es-MX', {
    hour: '2-digit',
    minute: '2-digit',
  })
})

// Current date formatted
const formattedDate = computed(() => {
  return currentTime.value.toLocaleDateString('es-MX', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  })
})

// Last update relative time
const lastUpdateText = computed(() => {
  if (!props.lastUpdate) return null

  const diffMs = currentTime.value.getTime() - props.lastUpdate.getTime()
  const diffSecs = Math.floor(diffMs / 1000)

  if (diffSecs < 5) return 'ahora'
  if (diffSecs < 60) return `hace ${diffSecs} s`

  const diffMins = Math.floor(diffSecs / 60)
  return `hace ${diffMins} min`
})
</script>

<template>
  <header
    :class="[
      'flex items-center justify-between px-6 py-4 transition-colors duration-300',
      darkMode
        ? 'bg-gray-900 border-b border-gray-800'
        : 'bg-white border-b border-gray-200',
    ]"
  >
    <!-- Left: Branding -->
    <div class="flex items-center gap-4">
      <div
        class="flex h-11 w-11 items-center justify-center rounded-xl bg-primary font-bold text-lg text-primary-foreground shadow-sm"
      >
        W
      </div>
      <div>
        <h1
          :class="[
            'text-xl font-semibold tracking-tight',
            darkMode ? 'text-white' : 'text-gray-900',
          ]"
        >
          WashFlow
          <span
            :class="[
              'ml-2 text-base font-normal',
              darkMode ? 'text-gray-500' : 'text-gray-400',
            ]"
          >
            ·
          </span>
          <span
            :class="[
              'ml-2 text-base font-normal',
              darkMode ? 'text-gray-400' : 'text-gray-500',
            ]"
          >
            Pantalla de sala
          </span>
        </h1>
        <p
          v-if="locationName"
          :class="[
            'text-sm',
            darkMode ? 'text-gray-400' : 'text-gray-500',
          ]"
        >
          Sucursal: {{ locationName }}
        </p>
      </div>
    </div>

    <!-- Right: Time and update info -->
    <div class="text-right">
      <!-- Clock -->
      <div class="flex items-baseline justify-end gap-2">
        <p
          :class="[
            'font-mono text-3xl font-bold tabular-nums tracking-tight',
            darkMode ? 'text-white' : 'text-gray-900',
          ]"
        >
          {{ formattedTime }}
        </p>
        <p
          :class="[
            'text-sm capitalize',
            darkMode ? 'text-gray-500' : 'text-gray-400',
          ]"
        >
          {{ formattedDate }}
        </p>
      </div>

      <!-- Last update -->
      <p
        v-if="lastUpdateText"
        :class="[
          'mt-1 text-sm',
          darkMode ? 'text-gray-500' : 'text-gray-400',
        ]"
      >
        Última actualización: {{ lastUpdateText }}
      </p>
    </div>
  </header>
</template>
