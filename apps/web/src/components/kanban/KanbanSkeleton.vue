<script setup lang="ts">
interface Props {
  columns?: number
  cardsPerColumn?: number
}

withDefaults(defineProps<Props>(), {
  columns: 4,
  cardsPerColumn: 3,
})
</script>

<template>
  <div class="flex gap-4 overflow-x-auto pb-4">
    <!-- Skeleton columns -->
    <div
      v-for="col in columns"
      :key="`col-${col}`"
      class="flex h-[calc(100vh-280px)] min-h-[400px] w-72 flex-shrink-0 flex-col rounded-lg border-t-4 border-t-muted bg-muted/30"
    >
      <!-- Header skeleton -->
      <div class="flex items-center justify-between gap-2 p-3 border-b">
        <div class="h-4 w-24 animate-pulse rounded bg-muted" />
        <div class="h-5 w-8 animate-pulse rounded-full bg-muted" />
      </div>

      <!-- Cards skeleton -->
      <div class="flex-1 p-2 space-y-2">
        <div
          v-for="card in cardsPerColumn"
          :key="`card-${col}-${card}`"
          class="rounded-lg border bg-card p-3 space-y-2"
        >
          <!-- Folio + time -->
          <div class="flex items-center justify-between">
            <div class="h-4 w-16 animate-pulse rounded bg-muted" />
            <div class="h-3 w-12 animate-pulse rounded bg-muted" />
          </div>
          <!-- Vehicle -->
          <div class="h-4 w-32 animate-pulse rounded bg-muted" />
          <!-- Services -->
          <div class="h-3 w-24 animate-pulse rounded bg-muted" />
          <!-- Duration -->
          <div class="h-5 w-16 animate-pulse rounded bg-muted" />
        </div>
      </div>
    </div>
  </div>
</template>
