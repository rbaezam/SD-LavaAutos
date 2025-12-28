<script setup lang="ts">
import { computed } from 'vue'
import type { LucideIcon } from 'lucide-vue-next'
import { Card } from '@/components/ui'

interface Props {
  title: string
  value: string | number | null
  subtitle?: string
  icon: LucideIcon
  iconColor?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  subtitle: undefined,
  iconColor: 'text-primary',
  loading: false,
})

const displayValue = computed(() => {
  if (props.value === null || props.value === undefined) return '—'
  return props.value
})
</script>

<template>
  <Card class="relative overflow-hidden p-4">
    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-2">
      <div class="h-4 w-20 animate-pulse rounded bg-slate-200" />
      <div class="h-8 w-16 animate-pulse rounded bg-slate-200" />
      <div class="h-3 w-24 animate-pulse rounded bg-slate-200" />
    </div>

    <!-- Content -->
    <template v-else>
      <div class="flex items-start justify-between">
        <div class="min-w-0 flex-1">
          <p class="text-sm font-medium text-muted-foreground">
            {{ title }}
          </p>
          <p class="mt-1 text-2xl font-bold tracking-tight text-foreground">
            {{ displayValue }}
          </p>
          <p v-if="subtitle" class="mt-1 text-xs text-muted-foreground">
            {{ subtitle }}
          </p>
          <slot name="badge" />
        </div>
        <div
          :class="[
            'flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10',
            iconColor,
          ]"
        >
          <component :is="icon" class="h-5 w-5" />
        </div>
      </div>
    </template>
  </Card>
</template>
