<script setup lang="ts">
import { computed } from 'vue'
import { Check, X } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

interface Option {
  value: string
  label: string
  description?: string
}

interface Props {
  modelValue: string[]
  options: Option[]
  placeholder?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Seleccionar...',
})

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const selectedValues = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const selectedOptions = computed(() =>
  props.options.filter((opt) => selectedValues.value.includes(opt.value))
)

const availableOptions = computed(() =>
  props.options.filter((opt) => !selectedValues.value.includes(opt.value))
)

function toggleOption(value: string) {
  if (props.disabled) return
  if (selectedValues.value.includes(value)) {
    selectedValues.value = selectedValues.value.filter((v) => v !== value)
  } else {
    selectedValues.value = [...selectedValues.value, value]
  }
}

function removeOption(value: string) {
  if (props.disabled) return
  selectedValues.value = selectedValues.value.filter((v) => v !== value)
}
</script>

<template>
  <div class="space-y-2">
    <!-- Selected items -->
    <div v-if="selectedOptions.length > 0" class="flex flex-wrap gap-2">
      <span
        v-for="option in selectedOptions"
        :key="option.value"
        :class="
          cn(
            'inline-flex items-center gap-1 rounded-md bg-primary/10 px-2 py-1 text-sm text-primary',
            disabled && 'opacity-50'
          )
        "
      >
        {{ option.label }}
        <button
          type="button"
          class="rounded-full p-0.5 hover:bg-primary/20"
          :disabled="disabled"
          @click="removeOption(option.value)"
        >
          <X class="h-3 w-3" />
        </button>
      </span>
    </div>

    <!-- Options list -->
    <div
      :class="
        cn(
          'max-h-48 space-y-1 overflow-y-auto rounded-md border p-2',
          disabled && 'cursor-not-allowed opacity-50'
        )
      "
    >
      <div
        v-if="availableOptions.length === 0 && selectedOptions.length === 0"
        class="py-2 text-center text-sm text-muted-foreground"
      >
        No hay opciones disponibles
      </div>
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        :disabled="disabled"
        :class="
          cn(
            'flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm transition-colors hover:bg-accent',
            selectedValues.includes(option.value) && 'bg-accent'
          )
        "
        @click="toggleOption(option.value)"
      >
        <div
          :class="
            cn(
              'flex h-4 w-4 shrink-0 items-center justify-center rounded border',
              selectedValues.includes(option.value)
                ? 'border-primary bg-primary text-primary-foreground'
                : 'border-input'
            )
          "
        >
          <Check v-if="selectedValues.includes(option.value)" class="h-3 w-3" />
        </div>
        <div class="flex-1">
          <div>{{ option.label }}</div>
          <div v-if="option.description" class="text-xs text-muted-foreground">
            {{ option.description }}
          </div>
        </div>
      </button>
    </div>
  </div>
</template>
