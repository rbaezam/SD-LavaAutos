<script setup lang="ts">
import { ref, watch } from 'vue'
import { Search, X } from 'lucide-vue-next'
import { Button, Input, Select, Badge } from '@/components/ui'

interface StatusOption {
  value: string
  label: string
}

interface Props {
  statusOptions: StatusOption[]
  modelValue: {
    search: string
    statusId: string
    datePreset: 'today' | 'all'
  }
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: Props['modelValue']]
}>()

const dateOptions = [
  { value: 'today', label: 'Hoy' },
  { value: 'all', label: 'Todos' },
]

const localSearch = ref(props.modelValue.search)

// Debounce search input
let debounceTimer: ReturnType<typeof setTimeout> | null = null
watch(localSearch, (value) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    emit('update:modelValue', { ...props.modelValue, search: value })
  }, 300)
})

function updateStatus(value: string) {
  emit('update:modelValue', { ...props.modelValue, statusId: value })
}

function updateDate(value: string) {
  emit('update:modelValue', { ...props.modelValue, datePreset: value as 'today' | 'all' })
}

function clearSearch() {
  localSearch.value = ''
  emit('update:modelValue', { ...props.modelValue, search: '' })
}

function clearStatus() {
  emit('update:modelValue', { ...props.modelValue, statusId: 'all' })
}

const hasActiveFilters = () => {
  return props.modelValue.search || (props.modelValue.statusId && props.modelValue.statusId !== 'all')
}

const getActiveStatusLabel = () => {
  const option = props.statusOptions.find((o) => o.value === props.modelValue.statusId)
  return option?.label || ''
}
</script>

<template>
  <div class="space-y-3">
    <!-- Filter inputs -->
    <div class="flex flex-col gap-3 sm:flex-row">
      <div class="relative flex-1">
        <Search
          class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
        />
        <Input
          v-model="localSearch"
          placeholder="Buscar por folio, placas o descripción..."
          class="pl-9 pr-9"
        />
        <button
          v-if="localSearch"
          type="button"
          class="absolute right-3 top-1/2 -translate-y-1/2 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          @click="clearSearch"
        >
          <X class="h-4 w-4" />
          <span class="sr-only">Limpiar búsqueda</span>
        </button>
      </div>
      <Select
        :model-value="modelValue.statusId"
        :options="statusOptions"
        placeholder="Estado"
        class="w-full sm:w-48"
        @update:model-value="updateStatus"
      />
      <Select
        :model-value="modelValue.datePreset"
        :options="dateOptions"
        placeholder="Fecha"
        class="w-full sm:w-32"
        @update:model-value="updateDate"
      />
    </div>

    <!-- Active filters chips -->
    <div v-if="hasActiveFilters()" class="flex flex-wrap items-center gap-2">
      <span class="text-xs text-muted-foreground">Filtros activos:</span>
      <Badge
        v-if="modelValue.search"
        variant="secondary"
        class="gap-1 pr-1"
      >
        Búsqueda: "{{ modelValue.search }}"
        <button
          type="button"
          class="ml-1 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          @click="clearSearch"
        >
          <X class="h-3 w-3" />
        </button>
      </Badge>
      <Badge
        v-if="modelValue.statusId && modelValue.statusId !== 'all'"
        variant="secondary"
        class="gap-1 pr-1"
      >
        Estado: {{ getActiveStatusLabel() }}
        <button
          type="button"
          class="ml-1 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          @click="clearStatus"
        >
          <X class="h-3 w-3" />
        </button>
      </Badge>
      <Button
        variant="ghost"
        size="sm"
        class="h-6 px-2 text-xs"
        @click="() => { clearSearch(); clearStatus(); }"
      >
        Limpiar todo
      </Button>
    </div>
  </div>
</template>
