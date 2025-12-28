<script setup lang="ts">
import { type Component } from 'vue'
import { Button } from '@/components/ui'

interface Props {
  icon?: Component
  title: string
  description?: string
  tip?: string
}

defineProps<Props>()

const emit = defineEmits<{
  primary: []
  secondary: []
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 px-4">
    <div
      v-if="icon"
      class="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted"
    >
      <component :is="icon" class="h-8 w-8 text-muted-foreground" />
    </div>
    <h3 class="text-lg font-medium text-foreground">{{ title }}</h3>
    <p v-if="description" class="mt-1 max-w-sm text-center text-sm text-muted-foreground">
      {{ description }}
    </p>
    <div v-if="$slots.primary || $slots.secondary" class="mt-6 flex items-center gap-3">
      <slot name="primary">
        <Button v-if="$slots.primaryLabel" @click="emit('primary')">
          <slot name="primaryLabel" />
        </Button>
      </slot>
      <slot name="secondary">
        <Button v-if="$slots.secondaryLabel" variant="ghost" @click="emit('secondary')">
          <slot name="secondaryLabel" />
        </Button>
      </slot>
    </div>
    <div
      v-if="tip"
      class="mt-6 max-w-md rounded-lg border border-dashed bg-muted/50 p-4"
    >
      <p class="text-center text-sm text-muted-foreground">
        <span class="font-medium text-foreground">Tip:</span> {{ tip }}
      </p>
    </div>
  </div>
</template>
