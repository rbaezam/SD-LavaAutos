<script setup lang="ts">
// Skeleton component for ticket detail page loading state
</script>

<template>
  <div class="space-y-6">
    <!-- Header skeleton -->
    <div class="space-y-4">
      <!-- Breadcrumb -->
      <div class="flex items-center gap-2">
        <div class="h-4 w-16 animate-pulse rounded bg-muted" />
        <div class="h-4 w-4 animate-pulse rounded bg-muted" />
        <div class="h-4 w-24 animate-pulse rounded bg-muted" />
      </div>

      <!-- Title row -->
      <div class="flex items-start justify-between">
        <div class="space-y-3">
          <div class="h-8 w-48 animate-pulse rounded bg-muted" />
          <div class="flex items-center gap-3">
            <div class="h-6 w-20 animate-pulse rounded-full bg-muted" />
            <div class="h-4 w-40 animate-pulse rounded bg-muted" />
          </div>
        </div>
        <div class="flex gap-2">
          <div class="h-9 w-24 animate-pulse rounded bg-muted" />
          <div class="h-9 w-32 animate-pulse rounded bg-muted" />
        </div>
      </div>
    </div>

    <!-- Two column layout -->
    <div class="grid gap-6 lg:grid-cols-[1fr_380px]">
      <!-- Left column -->
      <div class="space-y-6">
        <!-- Vehicle card -->
        <div class="rounded-lg border bg-card p-6 space-y-4">
          <div class="flex items-center gap-2">
            <div class="h-5 w-5 animate-pulse rounded bg-muted" />
            <div class="h-5 w-20 animate-pulse rounded bg-muted" />
          </div>
          <div class="grid gap-4 sm:grid-cols-2">
            <div class="space-y-2">
              <div class="h-4 w-12 animate-pulse rounded bg-muted" />
              <div class="h-10 w-full animate-pulse rounded bg-muted" />
            </div>
            <div class="space-y-2">
              <div class="h-4 w-20 animate-pulse rounded bg-muted" />
              <div class="h-10 w-full animate-pulse rounded bg-muted" />
            </div>
          </div>
          <div class="space-y-2">
            <div class="h-4 w-32 animate-pulse rounded bg-muted" />
            <div class="h-10 w-full animate-pulse rounded bg-muted" />
          </div>
        </div>

        <!-- Customer card -->
        <div class="rounded-lg border bg-card p-6 space-y-4">
          <div class="flex items-center gap-2">
            <div class="h-5 w-5 animate-pulse rounded bg-muted" />
            <div class="h-5 w-16 animate-pulse rounded bg-muted" />
          </div>
          <div class="grid gap-4 sm:grid-cols-2">
            <div class="space-y-2">
              <div class="h-4 w-16 animate-pulse rounded bg-muted" />
              <div class="h-10 w-full animate-pulse rounded bg-muted" />
            </div>
            <div class="space-y-2">
              <div class="h-4 w-20 animate-pulse rounded bg-muted" />
              <div class="h-10 w-full animate-pulse rounded bg-muted" />
            </div>
          </div>
        </div>

        <!-- Services card -->
        <div class="rounded-lg border bg-card p-6 space-y-4">
          <div class="flex items-center gap-2">
            <div class="h-5 w-5 animate-pulse rounded bg-muted" />
            <div class="h-5 w-20 animate-pulse rounded bg-muted" />
          </div>
          <div class="h-10 w-full animate-pulse rounded bg-muted" />
          <div class="flex gap-2">
            <div class="h-6 w-24 animate-pulse rounded-full bg-muted" />
            <div class="h-6 w-20 animate-pulse rounded-full bg-muted" />
          </div>
          <div class="h-4 w-40 animate-pulse rounded bg-muted" />
        </div>
      </div>

      <!-- Right column -->
      <div class="space-y-6">
        <!-- Status card -->
        <div class="rounded-lg border bg-card p-6 space-y-4">
          <div class="h-5 w-16 animate-pulse rounded bg-muted" />
          <div class="h-10 w-full animate-pulse rounded bg-muted" />
          <div class="h-9 w-32 animate-pulse rounded bg-muted" />
        </div>

        <!-- ETA card -->
        <div class="rounded-lg border bg-card p-6 space-y-4">
          <div class="flex items-center gap-2">
            <div class="h-5 w-5 animate-pulse rounded bg-muted" />
            <div class="h-5 w-10 animate-pulse rounded bg-muted" />
          </div>
          <div class="h-4 w-32 animate-pulse rounded bg-muted" />
          <div class="h-10 w-full animate-pulse rounded bg-muted" />
        </div>

        <!-- Activity card -->
        <div class="rounded-lg border bg-card p-6 space-y-4">
          <div class="flex items-center gap-2">
            <div class="h-5 w-5 animate-pulse rounded bg-muted" />
            <div class="h-5 w-20 animate-pulse rounded bg-muted" />
          </div>
          <!-- Timeline skeleton -->
          <div class="space-y-4">
            <div v-for="i in 3" :key="i" class="flex gap-3">
              <div class="flex flex-col items-center">
                <div class="h-8 w-8 animate-pulse rounded-full bg-muted" />
                <div v-if="i < 3" class="mt-2 h-12 w-0.5 bg-muted" />
              </div>
              <div class="flex-1 space-y-2 pt-1">
                <div class="h-4 w-32 animate-pulse rounded bg-muted" />
                <div class="h-3 w-24 animate-pulse rounded bg-muted" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
