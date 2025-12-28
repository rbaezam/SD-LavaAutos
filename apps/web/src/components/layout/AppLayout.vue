<script setup lang="ts">
import { ref } from 'vue'
import { RouterView } from 'vue-router'
import Sidebar from './Sidebar.vue'
import Topbar from './Topbar.vue'
import OnboardingBanner from '@/components/onboarding/OnboardingBanner.vue'

const sidebarCollapsed = ref(false)

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>

<template>
  <div class="flex h-screen bg-background">
    <Sidebar :collapsed="sidebarCollapsed" />
    <div class="flex flex-1 flex-col overflow-hidden">
      <Topbar @toggle-sidebar="toggleSidebar" />
      <OnboardingBanner />
      <main class="flex-1 overflow-y-auto bg-muted/30 p-4 sm:p-6">
        <div class="mx-auto max-w-7xl">
          <RouterView />
        </div>
      </main>
    </div>
  </div>
</template>
