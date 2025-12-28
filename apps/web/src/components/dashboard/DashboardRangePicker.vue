<script setup lang="ts">
import { ref, computed } from 'vue'
import { RefreshCw, ChevronDown } from 'lucide-vue-next'
import { Button, Input, Label } from '@/components/ui'
import type { DateRange } from '@/stores/dashboard'

interface Props {
  currentRange: DateRange
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

const emit = defineEmits<{
  (e: 'change', range: DateRange, from?: string, to?: string): void
  (e: 'refresh'): void
}>()

const showCustom = ref(false)
const customFrom = ref('')
const customTo = ref('')

const rangeOptions: { value: DateRange; label: string }[] = [
  { value: 'hoy', label: 'Hoy' },
  { value: 'ayer', label: 'Ayer' },
  { value: 'ultimos_7_dias', label: 'Últimos 7 días' },
  { value: 'personalizado', label: 'Personalizado' },
]

const currentLabel = computed(() => {
  const option = rangeOptions.find((o) => o.value === props.currentRange)
  return option?.label || 'Hoy'
})

function selectRange(range: DateRange) {
  if (range === 'personalizado') {
    showCustom.value = true
  } else {
    showCustom.value = false
    emit('change', range)
  }
}

function applyCustom() {
  if (customFrom.value && customTo.value) {
    emit('change', 'personalizado', customFrom.value, customTo.value)
    showCustom.value = false
  }
}

function handleRefresh() {
  emit('refresh')
}
</script>

<template>
  <div class="flex flex-wrap items-center gap-2">
    <!-- Range buttons (desktop) -->
    <div class="hidden gap-1 sm:flex">
      <Button
        v-for="option in rangeOptions"
        :key="option.value"
        :variant="currentRange === option.value ? 'default' : 'outline'"
        size="sm"
        @click="selectRange(option.value)"
      >
        {{ option.label }}
      </Button>
    </div>

    <!-- Range dropdown (mobile) -->
    <div class="relative sm:hidden">
      <Button variant="outline" size="sm" class="gap-2">
        {{ currentLabel }}
        <ChevronDown class="h-4 w-4" />
      </Button>
      <!-- Simple dropdown could be added here -->
    </div>

    <!-- Custom date inputs -->
    <div v-if="showCustom" class="flex items-end gap-2">
      <div class="space-y-1">
        <Label class="text-xs">Desde</Label>
        <Input v-model="customFrom" type="date" class="h-8 w-32 text-sm" />
      </div>
      <div class="space-y-1">
        <Label class="text-xs">Hasta</Label>
        <Input v-model="customTo" type="date" class="h-8 w-32 text-sm" />
      </div>
      <Button
        size="sm"
        :disabled="!customFrom || !customTo"
        @click="applyCustom"
      >
        Aplicar
      </Button>
    </div>

    <!-- Refresh button -->
    <Button
      variant="ghost"
      size="sm"
      :disabled="loading"
      @click="handleRefresh"
    >
      <RefreshCw :class="['h-4 w-4', loading && 'animate-spin']" />
    </Button>
  </div>
</template>
