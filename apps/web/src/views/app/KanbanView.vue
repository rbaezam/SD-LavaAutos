<script setup lang="ts">
import PageHeader from '@/components/layout/PageHeader.vue'
import KanbanBoard from '@/components/kanban/KanbanBoard.vue'
import { useLocationStore } from '@/stores/location'

const locationStore = useLocationStore()
</script>

<template>
  <div class="flex h-[calc(100vh-8rem)] flex-col">
    <!-- Page Header -->
    <PageHeader
      title="Operación"
      :subtitle="
        locationStore.selectedLocation
          ? `Arrastra los tickets para actualizar su estado · ${locationStore.selectedLocation.name}`
          : 'Arrastra los tickets para actualizar su estado'
      "
    />

    <!-- Kanban Board -->
    <div class="mt-6 flex-1 min-h-0">
      <KanbanBoard />
    </div>
  </div>
</template>
