<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Check, Loader2, ArrowRight, ArrowLeft, Sparkles } from 'lucide-vue-next'
import { Button, Card, CardContent } from '@/components/ui'
import { useOnboardingStore } from '@/stores/onboarding'
import OnboardingStepBusiness from './OnboardingStepBusiness.vue'
import OnboardingStepLocation from './OnboardingStepLocation.vue'
import OnboardingStepStatuses from './OnboardingStepStatuses.vue'
import OnboardingStepServices from './OnboardingStepServices.vue'

const emit = defineEmits<{
  complete: []
}>()

const onboardingStore = useOnboardingStore()

const steps = [
  { id: 1, title: 'Tu negocio', description: 'Personaliza tu marca' },
  { id: 2, title: 'Sucursal', description: 'Configura tu ubicación' },
  { id: 3, title: 'Estados', description: 'Define el flujo de trabajo' },
  { id: 4, title: 'Servicios', description: 'Agrega tus servicios' },
]

const currentStep = ref(1)
const saving = ref(false)
const showSuccess = ref(false)

// Initialize from store
watch(
  () => onboardingStore.status,
  (status) => {
    if (status && status.onboarding_step > 0 && status.onboarding_step < 5) {
      currentStep.value = status.onboarding_step
    }
  },
  { immediate: true }
)

const isLastStep = computed(() => currentStep.value === 4)
const isFirstStep = computed(() => currentStep.value === 1)

// Check if current step is valid to proceed
const canProceed = computed(() => {
  if (!onboardingStore.status) return false
  const status = onboardingStore.status

  switch (currentStep.value) {
    case 1:
      return true // Branding is optional
    case 2:
      return status.has_location
    case 3:
      return status.has_statuses
    case 4:
      return status.has_services
    default:
      return true
  }
})

async function nextStep() {
  if (saving.value) return

  saving.value = true
  try {
    // Save current step
    await onboardingStore.updateStep(currentStep.value)

    if (isLastStep.value) {
      // Complete onboarding
      await onboardingStore.complete()
      showSuccess.value = true
      setTimeout(() => {
        emit('complete')
      }, 2000)
    } else {
      currentStep.value++
    }
  } catch {
    // Error handled in store
  } finally {
    saving.value = false
  }
}

function prevStep() {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}
</script>

<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h1 class="text-3xl font-bold text-slate-900">Configura tu negocio</h1>
      <p class="mt-2 text-lg text-slate-600">Te tomará menos de 5 minutos.</p>
    </div>

    <!-- Success state -->
    <Card v-if="showSuccess" class="border-emerald-200 bg-emerald-50">
      <CardContent class="py-12 text-center">
        <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
          <Sparkles class="h-8 w-8 text-emerald-600" />
        </div>
        <h2 class="text-2xl font-bold text-emerald-900">¡Listo!</h2>
        <p class="mt-2 text-lg text-emerald-700">
          Ya puedes registrar vehículos.
        </p>
      </CardContent>
    </Card>

    <template v-else>
      <!-- Progress -->
      <div class="relative">
        <!-- Progress bar background -->
        <div class="absolute left-0 top-5 h-0.5 w-full bg-slate-200" />
        <!-- Progress bar fill -->
        <div
          class="absolute left-0 top-5 h-0.5 bg-primary transition-all duration-300"
          :style="{ width: `${((currentStep - 1) / (steps.length - 1)) * 100}%` }"
        />

        <!-- Steps -->
        <div class="relative flex justify-between">
          <div
            v-for="step in steps"
            :key="step.id"
            class="flex flex-col items-center"
          >
            <div
              :class="[
                'flex h-10 w-10 items-center justify-center rounded-full border-2 text-sm font-semibold transition-all',
                step.id < currentStep
                  ? 'border-primary bg-primary text-white'
                  : step.id === currentStep
                    ? 'border-primary bg-white text-primary'
                    : 'border-slate-300 bg-white text-slate-400',
              ]"
            >
              <Check v-if="step.id < currentStep" class="h-5 w-5" />
              <span v-else>{{ step.id }}</span>
            </div>
            <div class="mt-2 text-center">
              <p
                :class="[
                  'text-sm font-medium',
                  step.id <= currentStep ? 'text-slate-900' : 'text-slate-400',
                ]"
              >
                {{ step.title }}
              </p>
              <p class="hidden text-xs text-slate-500 sm:block">
                {{ step.description }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Step content -->
      <Card>
        <CardContent class="p-6">
          <OnboardingStepBusiness v-if="currentStep === 1" />
          <OnboardingStepLocation v-else-if="currentStep === 2" />
          <OnboardingStepStatuses v-else-if="currentStep === 3" />
          <OnboardingStepServices v-else-if="currentStep === 4" />
        </CardContent>
      </Card>

      <!-- Navigation -->
      <div class="flex items-center justify-between">
        <Button
          v-if="!isFirstStep"
          variant="outline"
          :disabled="saving"
          @click="prevStep"
        >
          <ArrowLeft class="mr-2 h-4 w-4" />
          Atrás
        </Button>
        <div v-else />

        <div class="flex items-center gap-4">
          <p v-if="isLastStep" class="text-sm text-slate-500">
            Ya casi terminas. Solo falta un paso.
          </p>
          <Button
            :disabled="saving || !canProceed"
            @click="nextStep"
          >
            <Loader2 v-if="saving" class="mr-2 h-4 w-4 animate-spin" />
            <template v-if="isLastStep">
              Terminar configuración
            </template>
            <template v-else>
              Continuar
              <ArrowRight class="ml-2 h-4 w-4" />
            </template>
          </Button>
        </div>
      </div>
    </template>
  </div>
</template>
