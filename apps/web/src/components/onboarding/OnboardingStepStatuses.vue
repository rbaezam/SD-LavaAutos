<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Workflow, Check, Loader2, Sparkles, Pencil } from 'lucide-vue-next'
import { Button, Alert, Badge } from '@/components/ui'
import { useStatusStore } from '@/stores/status'
import { useOnboardingStore } from '@/stores/onboarding'

const statusStore = useStatusStore()
const onboardingStore = useOnboardingStore()

const loading = ref(true)
const applying = ref(false)
const error = ref('')
const mode = ref<'choose' | 'preset' | 'custom'>('choose')

const hasStatuses = computed(() => statusStore.statuses.length > 0)

// Preset statuses for display
const presetStatuses = [
  { name: 'En espera', is_terminal: false },
  { name: 'En lavado', is_terminal: false },
  { name: 'En secado', is_terminal: false },
  { name: 'Detallado', is_terminal: false },
  { name: 'Listo', is_terminal: false },
  { name: 'Entregado', is_terminal: true },
]

onMounted(async () => {
  await statusStore.fetchStatuses()
  loading.value = false

  // If already has statuses, show them
  if (hasStatuses.value) {
    mode.value = 'preset'
  }
})

async function applyPreset() {
  applying.value = true
  error.value = ''

  try {
    await onboardingStore.applyStatusPreset()
    await statusStore.fetchStatuses()
    mode.value = 'preset'
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
</script>

<template>
  <div class="space-y-6">
    <div>
      <h2 class="flex items-center gap-2 text-xl font-semibold">
        <Workflow class="h-5 w-5 text-primary" />
        Estados del flujo de trabajo
      </h2>
      <p class="mt-1 text-sm text-muted-foreground">
        Define los pasos por los que pasa cada vehículo en tu negocio.
      </p>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-8">
      <Loader2 class="h-6 w-6 animate-spin text-muted-foreground" />
    </div>

    <template v-else>
      <Alert v-if="error" variant="destructive" class="mb-4">
        {{ error }}
      </Alert>

      <!-- Choose mode -->
      <div v-if="mode === 'choose' && !hasStatuses" class="grid gap-4 sm:grid-cols-2">
        <button
          type="button"
          class="group rounded-lg border-2 border-primary bg-primary/5 p-6 text-left transition-all hover:bg-primary/10"
          :disabled="applying"
          @click="applyPreset"
        >
          <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Sparkles class="h-6 w-6" />
          </div>
          <h3 class="font-semibold text-slate-900">Usar flujo recomendado</h3>
          <p class="mt-1 text-sm text-slate-600">
            Flujo típico de autolavado con 6 estados predefinidos.
          </p>
          <div class="mt-3">
            <Badge variant="success">Recomendado</Badge>
          </div>
        </button>

        <button
          type="button"
          class="group rounded-lg border-2 border-slate-200 p-6 text-left transition-all hover:border-slate-300 hover:bg-slate-50"
          @click="mode = 'custom'"
        >
          <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
            <Pencil class="h-6 w-6" />
          </div>
          <h3 class="font-semibold text-slate-900">Personalizar</h3>
          <p class="mt-1 text-sm text-slate-600">
            Crea tus propios estados según tu operación.
          </p>
        </button>
      </div>

      <!-- Preset preview / applied -->
      <div v-if="mode === 'preset' || hasStatuses" class="space-y-4">
        <div class="rounded-lg border bg-emerald-50 p-4">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100">
              <Check class="h-5 w-5 text-emerald-600" />
            </div>
            <div>
              <p class="font-medium text-emerald-900">Flujo configurado</p>
              <p class="text-sm text-emerald-700">
                {{ statusStore.statuses.length }} estados definidos
              </p>
            </div>
          </div>
        </div>

        <!-- Show statuses -->
        <div class="rounded-lg border bg-slate-50 p-4">
          <p class="mb-3 text-sm font-medium text-slate-600">Tu flujo de trabajo:</p>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="(status, index) in statusStore.statuses"
              :key="status.id"
              class="flex items-center gap-2"
            >
              <span
                class="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary"
              >
                {{ index + 1 }}
              </span>
              <span class="text-sm font-medium">{{ status.name }}</span>
              <Badge v-if="status.is_terminal" variant="success" class="text-xs">
                Terminal
              </Badge>
              <span v-if="index < statusStore.statuses.length - 1" class="text-slate-300">→</span>
            </div>
          </div>
        </div>

        <p class="text-sm text-muted-foreground">
          Puedes modificar los estados desde Configuración después de completar el asistente.
        </p>
      </div>

      <!-- Custom mode (simplified) -->
      <div v-if="mode === 'custom' && !hasStatuses" class="space-y-4">
        <p class="text-sm text-slate-600">
          Para personalizar tu flujo, te recomendamos primero usar el flujo recomendado y después editarlo desde Configuración.
        </p>

        <div class="rounded-lg border bg-slate-50 p-4">
          <p class="mb-3 text-sm font-medium text-slate-600">Flujo recomendado:</p>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="(status, index) in presetStatuses"
              :key="status.name"
              class="flex items-center gap-2"
            >
              <span
                class="flex h-6 w-6 items-center justify-center rounded-full bg-slate-200 text-xs font-semibold text-slate-600"
              >
                {{ index + 1 }}
              </span>
              <span class="text-sm">{{ status.name }}</span>
              <Badge v-if="status.is_terminal" variant="outline" class="text-xs">
                Terminal
              </Badge>
              <span v-if="index < presetStatuses.length - 1" class="text-slate-300">→</span>
            </div>
          </div>
        </div>

        <div class="flex gap-3">
          <Button variant="outline" @click="mode = 'choose'">
            Volver
          </Button>
          <Button :disabled="applying" @click="applyPreset">
            <Loader2 v-if="applying" class="mr-2 h-4 w-4 animate-spin" />
            Usar flujo recomendado
          </Button>
        </div>
      </div>
    </template>
  </div>
</template>
