<script setup lang="ts">
// Skeleton loading component for public ticket view
</script>

<template>
  <div class="overflow-hidden rounded-2xl bg-white shadow-xl">
    <!-- Hero skeleton -->
    <div class="relative bg-gradient-to-br from-slate-200 to-slate-300 px-6 py-8">
      <div class="text-center">
        <!-- Icon skeleton -->
        <div class="mb-4 flex justify-center">
          <div class="h-20 w-20 animate-pulse rounded-full bg-white/30" />
        </div>

        <!-- Status skeleton -->
        <div class="mx-auto h-8 w-48 animate-pulse rounded-lg bg-white/30" />

        <!-- Message skeleton -->
        <div class="mx-auto mt-3 h-5 w-64 animate-pulse rounded bg-white/20" />
      </div>
    </div>

    <!-- Info skeletons -->
    <div class="divide-y divide-slate-100">
      <!-- Row 1 -->
      <div class="flex items-center justify-between px-6 py-4">
        <div class="h-4 w-12 animate-pulse rounded bg-slate-200" />
        <div class="h-6 w-24 animate-pulse rounded bg-slate-200" />
      </div>

      <!-- Row 2 -->
      <div class="flex items-center justify-between px-6 py-4">
        <div class="flex items-center gap-2">
          <div class="h-4 w-4 animate-pulse rounded bg-slate-200" />
          <div class="h-4 w-16 animate-pulse rounded bg-slate-200" />
        </div>
        <div class="h-5 w-32 animate-pulse rounded bg-slate-200" />
      </div>

      <!-- Row 3 -->
      <div class="flex items-center justify-between px-6 py-4">
        <div class="flex items-center gap-2">
          <div class="h-4 w-4 animate-pulse rounded bg-slate-200" />
          <div class="h-4 w-24 animate-pulse rounded bg-slate-200" />
        </div>
        <div class="h-5 w-20 animate-pulse rounded bg-slate-200" />
      </div>

      <!-- Row 4 -->
      <div class="flex items-center justify-between px-6 py-4">
        <div class="flex items-center gap-2">
          <div class="h-4 w-4 animate-pulse rounded bg-slate-200" />
          <div class="h-4 w-16 animate-pulse rounded bg-slate-200" />
        </div>
        <div class="h-5 w-28 animate-pulse rounded bg-slate-200" />
      </div>
    </div>

    <!-- Footer skeleton -->
    <div class="bg-slate-50 px-6 py-3">
      <div class="mx-auto h-3 w-40 animate-pulse rounded bg-slate-200" />
    </div>
  </div>
</template>
