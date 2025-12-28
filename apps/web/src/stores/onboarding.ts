import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/lib/api'

export interface OnboardingStatus {
  onboarding_step: number
  onboarding_completed_at: string | null
  has_location: boolean
  has_statuses: boolean
  has_services: boolean
  has_branding: boolean
}

export const useOnboardingStore = defineStore('onboarding', () => {
  const status = ref<OnboardingStatus | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed properties
  const currentStep = computed(() => status.value?.onboarding_step ?? 0)
  const isCompleted = computed(() => !!status.value?.onboarding_completed_at)
  const remainingSteps = computed(() => {
    if (!status.value) return 4
    return Math.max(0, 4 - status.value.onboarding_step)
  })

  // Check if should show banner (incomplete onboarding)
  const shouldShowBanner = computed(() => {
    return status.value !== null && !status.value.onboarding_completed_at
  })

  // Fetch onboarding status
  async function fetchStatus() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get<OnboardingStatus>('/api/v1/org/onboarding')
      status.value = response.data
    } catch (err) {
      error.value = 'Error al cargar estado del onboarding'
      console.error('Failed to fetch onboarding status:', err)
    } finally {
      loading.value = false
    }
  }

  // Update onboarding step
  async function updateStep(step: number) {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch<OnboardingStatus>('/api/v1/org/onboarding', {
        onboarding_step: step,
      })
      status.value = response.data
    } catch (err) {
      error.value = 'Error al actualizar paso'
      console.error('Failed to update onboarding step:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Complete onboarding
  async function complete() {
    loading.value = true
    error.value = null
    try {
      const response = await api.post<OnboardingStatus>('/api/v1/org/onboarding/complete')
      status.value = response.data
    } catch (err) {
      error.value = 'Error al completar onboarding'
      console.error('Failed to complete onboarding:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Apply status preset
  async function applyStatusPreset() {
    loading.value = true
    error.value = null
    try {
      const response = await api.post<OnboardingStatus>(
        '/api/v1/org/onboarding/apply-status-preset'
      )
      status.value = response.data
    } catch (err) {
      error.value = 'Error al aplicar preset de estados'
      console.error('Failed to apply status preset:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Apply service preset
  async function applyServicePreset() {
    loading.value = true
    error.value = null
    try {
      const response = await api.post<OnboardingStatus>(
        '/api/v1/org/onboarding/apply-service-preset'
      )
      status.value = response.data
    } catch (err) {
      error.value = 'Error al aplicar preset de servicios'
      console.error('Failed to apply service preset:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Reset store
  function reset() {
    status.value = null
    loading.value = false
    error.value = null
  }

  return {
    status,
    loading,
    error,
    currentStep,
    isCompleted,
    remainingSteps,
    shouldShowBanner,
    fetchStatus,
    updateStep,
    complete,
    applyStatusPreset,
    applyServicePreset,
    reset,
  }
})
