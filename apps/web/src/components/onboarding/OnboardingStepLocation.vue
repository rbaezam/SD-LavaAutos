<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { MapPin, Check, Loader2, Plus } from 'lucide-vue-next'
import { Button, Input, Label, Alert } from '@/components/ui'
import { useLocationStore } from '@/stores/location'
import { useOnboardingStore } from '@/stores/onboarding'

const locationStore = useLocationStore()
const onboardingStore = useOnboardingStore()

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const showForm = ref(false)

const form = ref({
  name: '',
  address: '',
})

const hasLocation = computed(() => locationStore.locations.length > 0)
const firstLocation = computed(() => locationStore.locations[0])

onMounted(async () => {
  await locationStore.fetchLocations()
  loading.value = false

  // Show form if no locations
  if (!hasLocation.value) {
    showForm.value = true
    form.value.name = 'Sucursal Principal'
  }
})

async function createLocation() {
  if (!form.value.name.trim()) {
    error.value = 'El nombre es requerido'
    return
  }

  saving.value = true
  error.value = ''

  try {
    await locationStore.createLocation(form.value.name.trim(), form.value.address.trim())
    await onboardingStore.fetchStatus()
    showForm.value = false
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      error.value = axiosErr.response?.data?.detail || 'Error al crear sucursal'
    } else {
      error.value = 'Error al crear sucursal'
    }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h2 class="flex items-center gap-2 text-xl font-semibold">
        <MapPin class="h-5 w-5 text-primary" />
        Tu sucursal
      </h2>
      <p class="mt-1 text-sm text-muted-foreground">
        Configura la ubicación donde operas. Puedes agregar más sucursales después.
      </p>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-8">
      <Loader2 class="h-6 w-6 animate-spin text-muted-foreground" />
    </div>

    <template v-else>
      <Alert v-if="error" variant="destructive" class="mb-4">
        {{ error }}
      </Alert>

      <!-- Existing location -->
      <div v-if="hasLocation && !showForm" class="space-y-4">
        <div class="rounded-lg border bg-emerald-50 p-4">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100">
              <Check class="h-5 w-5 text-emerald-600" />
            </div>
            <div>
              <p class="font-medium text-emerald-900">{{ firstLocation?.name }}</p>
              <p v-if="firstLocation?.address" class="text-sm text-emerald-700">
                {{ firstLocation.address }}
              </p>
              <p v-else class="text-sm text-emerald-600">
                Sucursal configurada correctamente
              </p>
            </div>
          </div>
        </div>

        <p class="text-sm text-muted-foreground">
          Puedes administrar tus sucursales desde Configuración después de completar el asistente.
        </p>
      </div>

      <!-- Create form -->
      <div v-else class="space-y-4">
        <div class="space-y-2">
          <Label for="location_name">Nombre de la sucursal</Label>
          <Input
            id="location_name"
            v-model="form.name"
            placeholder="Ej: Sucursal Centro"
            :disabled="saving"
          />
        </div>

        <div class="space-y-2">
          <Label for="location_address">Dirección (opcional)</Label>
          <Input
            id="location_address"
            v-model="form.address"
            placeholder="Ej: Av. Principal #123, Colonia Centro"
            :disabled="saving"
          />
        </div>

        <Button :disabled="saving || !form.name.trim()" @click="createLocation">
          <Loader2 v-if="saving" class="mr-2 h-4 w-4 animate-spin" />
          <Plus v-else class="mr-2 h-4 w-4" />
          Crear sucursal
        </Button>
      </div>
    </template>
  </div>
</template>
