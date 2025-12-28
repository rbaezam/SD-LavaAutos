<script setup lang="ts">
interface Props {
  columns?: number
  rows?: number
}

withDefaults(defineProps<Props>(), {
  columns: 7,
  rows: 5,
})
</script>

<template>
  <div class="w-full">
    <!-- Header skeleton -->
    <div class="flex border-b py-3">
      <div
        v-for="col in columns"
        :key="`header-${col}`"
        class="flex-1 px-2"
        :class="col === columns ? 'text-right' : ''"
      >
        <div
          class="h-4 animate-pulse rounded bg-muted"
          :class="col === columns ? 'ml-auto w-16' : col === 1 ? 'w-16' : 'w-24'"
        />
      </div>
    </div>
    <!-- Row skeletons -->
    <div v-for="row in rows" :key="`row-${row}`" class="flex border-b py-4 last:border-0">
      <div
        v-for="col in columns"
        :key="`cell-${row}-${col}`"
        class="flex-1 px-2"
        :class="col === columns ? 'text-right' : ''"
      >
        <div
          class="h-4 animate-pulse rounded bg-muted"
          :class="[
            col === columns ? 'ml-auto w-12' : '',
            col === 1 ? 'w-20' : '',
            col === 2 ? 'w-32' : '',
            col === 3 ? 'w-24' : '',
            col === 4 ? 'w-16' : '',
            col === 5 ? 'w-12' : '',
            col === 6 ? 'w-20' : '',
          ]"
        />
      </div>
    </div>
  </div>
</template>
