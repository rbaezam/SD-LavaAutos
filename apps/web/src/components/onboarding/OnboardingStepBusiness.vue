<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Palette, Check, Loader2 } from 'lucide-vue-next'
import { Button, Input, Label, Alert } from '@/components/ui'
import api from '@/lib/api'

interface Branding {
  brand_name: string | null
  brand_logo_url: string | null
  brand_primary_color: string | null
}

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const saved = ref(false)

const form = ref({
  brand_name: '',
  brand_logo_url: '',
  brand_primary_color: '#2563eb',
})

const previewColor = computed(() => form.value.brand_primary_color || '#2563eb')
const previewName = computed(() => form.value.brand_name || 'Mi Autolavado')

onMounted(async () => {
  try {
    const response = await api.get<Branding>('/api/v1/org/branding')
    form.value.brand_name = response.data.brand_name || ''
    form.value.brand_logo_url = response.data.brand_logo_url || ''
    form.value.brand_primary_color = response.data.brand_primary_color || '#2563eb'
  } catch {
    // Ignore, use defaults
  } finally {
    loading.value = false
  }
})

async function save() {
  saving.value = true
  error.value = ''
  saved.value = false

  try {
    await api.patch('/api/v1/org/branding', {
      brand_name: form.value.brand_name.trim() || null,
      brand_logo_url: form.value.brand_logo_url.trim() || null,
      brand_primary_color: form.value.brand_primary_color.trim() || null,
    })
    saved.value = true
    setTimeout(() => {
      saved.value = false
    }, 2000)
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      error.value = axiosErr.response?.data?.detail || 'Error al guardar'
    } else {
      error.value = 'Error al guardar'
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
        <Palette class="h-5 w-5 text-primary" />
        Personaliza tu marca
      </h2>
      <p class="mt-1 text-sm text-muted-foreground">
        Esta información aparecerá en la página pública de seguimiento de vehículos.
      </p>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-8">
      <Loader2 class="h-6 w-6 animate-spin text-muted-foreground" />
    </div>

    <template v-else>
      <Alert v-if="error" variant="destructive" class="mb-4">
        {{ error }}
      </Alert>

      <div class="grid gap-6 lg:grid-cols-2">
        <!-- Form -->
        <div class="space-y-4">
          <div class="space-y-2">
            <Label for="brand_name">Nombre de tu negocio</Label>
            <Input
              id="brand_name"
              v-model="form.brand_name"
              placeholder="Ej: AutoLavado Express"
              :disabled="saving"
            />
          </div>

          <div class="space-y-2">
            <Label for="brand_logo_url">URL del logo (opcional)</Label>
            <Input
              id="brand_logo_url"
              v-model="form.brand_logo_url"
              placeholder="https://ejemplo.com/logo.png"
              type="url"
              :disabled="saving"
            />
            <p class="text-xs text-muted-foreground">
              Pega la URL de tu logo (PNG, JPG o SVG)
            </p>
          </div>

          <div class="space-y-2">
            <Label for="brand_primary_color">Color principal</Label>
            <div class="flex items-center gap-3">
              <input
                id="brand_primary_color_picker"
                v-model="form.brand_primary_color"
                type="color"
                class="h-10 w-14 cursor-pointer rounded border"
                :disabled="saving"
              />
              <Input
                id="brand_primary_color"
                v-model="form.brand_primary_color"
                placeholder="#2563eb"
                class="flex-1 font-mono"
                :disabled="saving"
              />
            </div>
          </div>

          <Button :disabled="saving" @click="save">
            <Loader2 v-if="saving" class="mr-2 h-4 w-4 animate-spin" />
            <Check v-else-if="saved" class="mr-2 h-4 w-4" />
            {{ saved ? 'Guardado' : 'Guardar cambios' }}
          </Button>
        </div>

        <!-- Preview -->
        <div class="rounded-lg border bg-slate-50 p-4">
          <p class="mb-3 text-sm font-medium text-slate-600">Vista previa</p>
          <div class="overflow-hidden rounded-lg bg-white shadow-sm">
            <!-- Header -->
            <div class="flex items-center gap-3 border-b p-3">
              <div
                v-if="!form.brand_logo_url"
                class="flex h-10 w-10 items-center justify-center rounded-lg text-lg font-bold text-white"
                :style="{ backgroundColor: previewColor }"
              >
                {{ previewName.charAt(0).toUpperCase() }}
              </div>
              <img
                v-else
                :src="form.brand_logo_url"
                :alt="previewName"
                class="h-10 w-10 rounded-lg object-contain"
                @error="($event.target as HTMLImageElement).style.display = 'none'"
              />
              <div>
                <p class="font-semibold">{{ previewName }}</p>
                <p class="text-xs text-slate-500">Seguimiento de tu vehículo</p>
              </div>
            </div>

            <!-- Status card preview -->
            <div
              class="p-4 text-center text-white"
              :style="{ backgroundColor: previewColor }"
            >
              <p class="text-sm font-semibold uppercase">En lavado</p>
              <p class="mt-1 text-xs opacity-80">Tu vehículo está siendo atendido</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
