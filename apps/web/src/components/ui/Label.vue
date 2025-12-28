<script setup lang="ts">
import { type HTMLAttributes, computed } from 'vue'
import { cn } from '@/lib/utils'

interface Props extends /* @vue-ignore */ HTMLAttributes {
  for?: string
}

const props = defineProps<Props>()

const classes = computed(() =>
  cn(
    'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
    props.class as string
  )
)
</script>

<template>
  <label :for="props.for" :class="classes">
    <slot />
  </label>
</template>
