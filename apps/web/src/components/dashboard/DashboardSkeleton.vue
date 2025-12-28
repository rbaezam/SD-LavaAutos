<script setup lang="ts">
import { Card } from '@/components/ui'
</script>

<template>
  <div class="space-y-6">
    <!-- Header skeleton -->
    <div class="flex items-center justify-between">
      <div class="h-7 w-32 animate-pulse rounded bg-slate-200" />
      <div class="flex gap-2">
        <div class="h-8 w-16 animate-pulse rounded bg-slate-200" />
        <div class="h-8 w-16 animate-pulse rounded bg-slate-200" />
        <div class="h-8 w-24 animate-pulse rounded bg-slate-200" />
      </div>
    </div>

    <!-- KPIs skeleton -->
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
      <Card v-for="i in 5" :key="i" class="p-4">
        <div class="space-y-2">
          <div class="h-4 w-20 animate-pulse rounded bg-slate-200" />
          <div class="h-8 w-16 animate-pulse rounded bg-slate-200" />
          <div class="h-3 w-24 animate-pulse rounded bg-slate-200" />
        </div>
      </Card>
    </div>

    <!-- Flow skeleton -->
    <Card class="p-4">
      <div class="mb-3 h-4 w-24 animate-pulse rounded bg-slate-200" />
      <div class="flex gap-3">
        <div
          v-for="i in 5"
          :key="i"
          class="flex h-16 w-24 shrink-0 animate-pulse flex-col items-center justify-center rounded-lg bg-slate-100"
        >
          <div class="mb-1 h-6 w-8 rounded bg-slate-200" />
          <div class="h-3 w-14 rounded bg-slate-200" />
        </div>
      </div>
    </Card>

    <!-- Chart skeleton -->
    <Card class="p-4">
      <div class="mb-3 h-4 w-32 animate-pulse rounded bg-slate-200" />
      <div class="flex h-[200px] items-end justify-center gap-1 rounded-lg bg-slate-50 p-4">
        <div
          v-for="i in 12"
          :key="i"
          class="w-6 animate-pulse rounded-t bg-slate-200"
          :style="{ height: `${20 + Math.random() * 100}px` }"
        />
      </div>
    </Card>
  </div>
</template>
