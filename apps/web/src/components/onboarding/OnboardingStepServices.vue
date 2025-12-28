<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Tag, Check, Loader2, Sparkles, Plus, X } from 'lucide-vue-next'
import { Button, Input, Label, Alert, Badge } from '@/components/ui'
import { useServiceStore } from '@/stores/service'
import { useOnboardingStore } from '@/stores/onboarding'

const serviceStore = useServiceStore()
const onboardingStore = useOnboardingStore()

const loading = ref(true)
const applying = ref(false)
const error = ref('')
const showAddForm = ref(false)

const form = ref({
  name: '',
  base_price: '',
})

const hasServices = computed(() => serviceStore.services.length > 0)

// Preset services for display
const presetServices = [
  { name: 'Lavado exterior', price: '$80' },
  { name: 'Lavado completo', price: '$150' },
  { name: 'Aspirado', price: '$50' },
  { name: 'Encerado', price: '$100' },
  { name: 'Detallado', price: '$300' },
]

onMounted(async () => {
  await serviceStore.fetchServices()
  loading.value = false
})

async function applyPreset() {
  applying.value = true
  error.value = ''

  try {
    await onboardingStore.applyServicePreset()
    await serviceStore.fetchServices()
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      error.value = axiosErr.response?.data?.detail || 'Error al aplicar preset'
    } else {
      error.value = 'Error al aplicar preset'
    }
  } finally {
    applying.value = false
  }
}

async function addCustomService() {
  if (!form.value.name.trim()) {
    error.value = 'El nombre es requerido'
    return
  }

  applying.value = true
  error.value = ''

  try {
    await serviceStore.createService({
      name: form.value.name.trim(),
      price_mxn: form.value.base_price ? parseFloat(form.value.base_price) : undefined,
    })
    await onboardingStore.fetchStatus()
    form.value.name = ''
    form.value.base_price = ''
    showAddForm.value = false
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      error.value = axiosErr.response?.data?.detail || 'Error al crear servicio'
    } else {
      error.value = 'Error al crear servicio'
    }
  } finally {
    applying.value = false
  }
}

function formatPrice(price: number | null | undefined): string {
  if (price == null) return '-'
  return `$${price.toFixed(0)}`
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h2 class="flex items-center gap-2 text-xl font-semibold">
        <Tag class="h-5 w-5 text-primary" />
        Servicios
      </h2>
      <p class="mt-1 text-sm text-muted-foreground">
        Define los servicios que ofreces. Los precios son opcionales.
      </p>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-8">
      <Loader2 class="h-6 w-6 animate-spin text-muted-foreground" />
    </div>

    <template v-else>
      <Alert v-if="error" variant="destructive" class="mb-4">
        {{ error }}
      </Alert>

      <!-- No services yet -->
      <div v-if="!hasServices" class="space-y-4">
        <div class="rounded-lg border bg-slate-50 p-4">
          <p class="mb-3 text-sm font-medium text-slate-600">Servicios comunes:</p>
          <div class="flex flex-wrap gap-2">
            <Badge v-for="service in presetServices" :key="service.name" variant="secondary">
              {{ service.name }} - {{ service.price }}
            </Badge>
          </div>
        </div>

        <Button :disabled="applying" @click="applyPreset">
          <Loader2 v-if="applying" class="mr-2 h-4 w-4 animate-spin" />
          <Sparkles v-else class="mr-2 h-4 w-4" />
          Usar servicios comunes
        </Button>
      </div>

      <!-- Has services -->
      <div v-else class="space-y-4">
        <div class="rounded-lg border bg-emerald-50 p-4">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100">
              <Check class="h-5 w-5 text-emerald-600" />
            </div>
            <div>
              <p class="font-medium text-emerald-900">Servicios configurados</p>
              <p class="text-sm text-emerald-700">
                {{ serviceStore.services.length }} servicios definidos
              </p>
            </div>
          </div>
        </div>

        <!-- Services list -->
        <div class="rounded-lg border divide-y">
          <div
            v-for="service in serviceStore.services"
            :key="service.id"
            class="flex items-center justify-between px-4 py-3"
          >
            <span class="font-medium">{{ service.name }}</span>
            <span class="text-sm text-muted-foreground">
              {{ formatPrice(service.price_mxn) }}
            </span>
          </div>
        </div>

        <!-- Add custom service -->
        <div v-if="!showAddForm">
          <Button variant="outline" size="sm" @click="showAddForm = true">
            <Plus class="mr-2 h-4 w-4" />
            Agregar servicio
          </Button>
        </div>

        <div v-else class="rounded-lg border bg-slate-50 p-4">
          <div class="mb-3 flex items-center justify-between">
            <p class="text-sm font-medium">Nuevo servicio</p>
            <button
              type="button"
              class="text-slate-400 hover:text-slate-600"
              @click="showAddForm = false"
            >
              <X class="h-4 w-4" />
            </button>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <div class="space-y-2">
              <Label for="service_name">Nombre</Label>
              <Input
                id="service_name"
                v-model="form.name"
                placeholder="Ej: Lavado de motor"
                :disabled="applying"
              />
            </div>
            <div class="space-y-2">
              <Label for="service_price">Precio (opcional)</Label>
              <Input
                id="service_price"
                v-model="form.base_price"
                type="number"
                placeholder="150"
                :disabled="applying"
              />
            </div>
          </div>

          <div class="mt-4">
            <Button
              size="sm"
              :disabled="applying || !form.name.trim()"
              @click="addCustomService"
            >
              <Loader2 v-if="applying" class="mr-2 h-4 w-4 animate-spin" />
              <Plus v-else class="mr-2 h-4 w-4" />
              Agregar
            </Button>
          </div>
        </div>

        <p class="text-sm text-muted-foreground">
          Puedes administrar tus servicios desde el menú de Servicios después de completar el asistente.
        </p>
      </div>
    </template>
  </div>
</template>
