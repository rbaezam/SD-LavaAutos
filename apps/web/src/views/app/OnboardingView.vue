<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useOnboardingStore } from '@/stores/onboarding'
import OnboardingWizard from '@/components/onboarding/OnboardingWizard.vue'
import { Loader2 } from 'lucide-vue-next'

const router = useRouter()
const onboardingStore = useOnboardingStore()

onMounted(async () => {
  await onboardingStore.fetchStatus()

  // If already completed, redirect to dashboard
  if (onboardingStore.isCompleted) {
    router.replace({ name: 'dashboard' })
  }
})

function handleComplete() {
  router.push({ name: 'tickets' })
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
    <!-- Header -->
    <header class="border-b bg-white px-6 py-4">
      <div class="mx-auto max-w-3xl">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary font-bold text-white">
            W
          </div>
          <div>
            <h1 class="text-lg font-semibold">WashFlow</h1>
            <p class="text-sm text-muted-foreground">Configuración inicial</p>
          </div>
        </div>
      </div>
    </header>

    <!-- Main content -->
    <main class="px-4 py-8">
      <div class="mx-auto max-w-3xl">
        <!-- Loading -->
        <div v-if="onboardingStore.loading && !onboardingStore.status" class="flex items-center justify-center py-20">
          <Loader2 class="h-8 w-8 animate-spin text-primary" />
        </div>

        <!-- Wizard -->
        <OnboardingWizard
          v-else-if="onboardingStore.status"
          @complete="handleComplete"
        />
      </div>
    </main>
  </div>
</template>
