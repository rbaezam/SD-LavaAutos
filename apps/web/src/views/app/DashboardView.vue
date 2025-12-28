<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDashboardStore } from '@/stores/dashboard'
import { useLocationStore } from '@/stores/location'
import DashboardKPIs from '@/components/dashboard/DashboardKPIs.vue'
import DashboardFlowStrip from '@/components/dashboard/DashboardFlowStrip.vue'
import DashboardTimelineChart from '@/components/dashboard/DashboardTimelineChart.vue'
import DashboardRangePicker from '@/components/dashboard/DashboardRangePicker.vue'
import DashboardSkeleton from '@/components/dashboard/DashboardSkeleton.vue'
import { Alert } from '@/components/ui'
import type { DateRange } from '@/stores/dashboard'

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()
const locationStore = useLocationStore()

// Greeting based on time
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Buenos días'
  if (hour < 19) return 'Buenas tardes'
  return 'Buenas noches'
})

// User name
const userName = computed(() => {
  const name = authStore.user?.full_name
  if (!name) return ''
  // Get first name only
  return name.split(' ')[0]
})

// Check if we have a location selected
const hasLocation = computed(() => !!locationStore.selectedLocationId)

// Handle range change
function handleRangeChange(range: DateRange, from?: string, to?: string) {
  dashboardStore.setRange(range, from, to)
}

// Handle refresh
function handleRefresh() {
  dashboardStore.refresh()
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p class="text-muted-foreground">
          {{ greeting }}{{ userName ? `, ${userName}` : '' }}
        </p>
      </div>

      <!-- Range picker -->
      <DashboardRangePicker
        v-if="hasLocation"
        :current-range="dashboardStore.range"
        :loading="dashboardStore.loading"
        @change="handleRangeChange"
        @refresh="handleRefresh"
      />
    </div>

    <!-- No location selected -->
    <Alert v-if="!hasLocation" variant="default">
      <p>Selecciona una sucursal para ver las métricas del dashboard.</p>
    </Alert>

    <!-- Error state -->
    <Alert v-else-if="dashboardStore.error" variant="destructive">
      {{ dashboardStore.error }}
    </Alert>

    <!-- Loading skeleton -->
    <DashboardSkeleton v-else-if="dashboardStore.loading && !dashboardStore.summary" />

    <!-- Dashboard content -->
    <template v-else-if="hasLocation">
      <!-- KPIs -->
      <DashboardKPIs
        :summary="dashboardStore.summary"
        :loading="dashboardStore.loading"
      />

      <!-- Flow strip -->
      <DashboardFlowStrip
        :flow="dashboardStore.flow"
        :loading="dashboardStore.loading"
      />

      <!-- Timeline chart -->
      <DashboardTimelineChart
        :timeline="dashboardStore.timeline"
        :loading="dashboardStore.loading"
        :range="dashboardStore.range"
      />
    </template>
  </div>
</template>
