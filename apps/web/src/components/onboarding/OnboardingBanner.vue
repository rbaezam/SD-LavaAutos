<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, Sparkles } from 'lucide-vue-next'
import { Button } from '@/components/ui'
import { useOnboardingStore } from '@/stores/onboarding'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const onboardingStore = useOnboardingStore()
const authStore = useAuthStore()

// Only show for managers
const isManager = computed(() => authStore.isManager)

const remainingSteps = computed(() => {
  if (!onboardingStore.status) return 0
  return Math.max(0, 4 - onboardingStore.status.onboarding_step)
})

const shouldShow = computed(() => {
  return isManager.value && onboardingStore.shouldShowBanner && remainingSteps.value > 0
})

const message = computed(() => {
  if (remainingSteps.value === 1) {
    return 'Te falta 1 paso para terminar tu configuración.'
  }
  return `Te faltan ${remainingSteps.value} pasos para terminar tu configuración.`
})

onMounted(async () => {
  if (isManager.value && !onboardingStore.status) {
    await onboardingStore.fetchStatus()
  }
})

function continueOnboarding() {
  router.push({ name: 'onboarding' })
}
</script>

<template>
  <div
    v-if="shouldShow"
    class="border-b bg-gradient-to-r from-amber-50 to-orange-50 px-4 py-3"
  >
    <div class="mx-auto flex max-w-7xl items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="flex h-8 w-8 items-center justify-center rounded-full bg-amber-100">
          <Sparkles class="h-4 w-4 text-amber-600" />
        </div>
        <p class="text-sm font-medium text-amber-900">
          {{ message }}
        </p>
      </div>
      <Button size="sm" variant="outline" class="shrink-0" @click="continueOnboarding">
        Continuar onboarding
        <ArrowRight class="ml-2 h-4 w-4" />
      </Button>
    </div>
  </div>
</template>
