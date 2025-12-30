<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { z } from 'zod'
import { Droplets, Check } from 'lucide-vue-next'
import { Button, Input, Label, Alert } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const fullName = ref('')
const error = ref('')
const loading = ref(false)

const registerSchema = z
  .object({
    email: z.string().email('Correo electrónico inválido'),
    password: z.string().min(8, 'La contraseña debe tener al menos 8 caracteres'),
    confirmPassword: z.string(),
    fullName: z.string().optional(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Las contraseñas no coinciden',
    path: ['confirmPassword'],
  })

async function handleSubmit() {
  error.value = ''

  const validation = registerSchema.safeParse({
    email: email.value,
    password: password.value,
    confirmPassword: confirmPassword.value,
    fullName: fullName.value || undefined,
  })

  if (!validation.success) {
    error.value = validation.error.errors[0].message
    return
  }

  loading.value = true
  try {
    await authStore.register(
      email.value,
      password.value,
      fullName.value || undefined
    )
    router.push('/app/dashboard')
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      error.value = axiosErr.response?.data?.detail || 'Error al crear la cuenta'
    } else {
      error.value = 'Error al crear la cuenta'
    }
  } finally {
    loading.value = false
  }
}

const benefits = [
  'Flujo de trabajo visual para tus tickets',
  'Notificaciones automáticas por WhatsApp',
  'Pantalla de espera para tus clientes',
  'Reportes y métricas de tu negocio',
]
</script>

<template>
  <div class="flex min-h-screen">
    <!-- Left side - Branding -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary via-primary to-blue-600 p-12 flex-col justify-between">
      <div>
        <RouterLink to="/" class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-white/20 backdrop-blur-sm">
            <Droplets class="h-6 w-6 text-white" />
          </div>
          <span class="text-2xl font-bold text-white">WashFlow</span>
        </RouterLink>
      </div>

      <div class="space-y-8">
        <div class="space-y-4">
          <h1 class="text-4xl font-bold text-white leading-tight">
            Digitaliza tu autolavado en minutos
          </h1>
          <p class="text-lg text-white/80">
            Únete a los negocios que ya están mejorando la experiencia de sus clientes.
          </p>
        </div>

        <div class="space-y-3">
          <div
            v-for="benefit in benefits"
            :key="benefit"
            class="flex items-center gap-3"
          >
            <div class="flex h-6 w-6 items-center justify-center rounded-full bg-white/20">
              <Check class="h-4 w-4 text-white" />
            </div>
            <span class="text-white/90">{{ benefit }}</span>
          </div>
        </div>
      </div>

      <p class="text-sm text-white/50">
        © 2024 WashFlow. Todos los derechos reservados.
      </p>
    </div>

    <!-- Right side - Register Form -->
    <div class="flex w-full lg:w-1/2 items-center justify-center p-6 sm:p-12 bg-background">
      <div class="w-full max-w-md space-y-8">
        <!-- Mobile logo -->
        <div class="lg:hidden text-center">
          <RouterLink to="/" class="inline-flex items-center gap-2">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary">
              <Droplets class="h-6 w-6 text-white" />
            </div>
            <span class="text-2xl font-bold">WashFlow</span>
          </RouterLink>
        </div>

        <div class="space-y-2 text-center lg:text-left">
          <h2 class="text-3xl font-bold tracking-tight">Crea tu cuenta</h2>
          <p class="text-muted-foreground">
            Comienza gratis, sin tarjeta de crédito
          </p>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <Alert v-if="error" variant="destructive">
            {{ error }}
          </Alert>

          <div class="space-y-4">
            <div class="space-y-2">
              <Label for="fullName">Nombre completo <span class="text-muted-foreground">(opcional)</span></Label>
              <Input
                id="fullName"
                v-model="fullName"
                type="text"
                placeholder="Juan Pérez"
                :disabled="loading"
                class="h-11"
              />
            </div>

            <div class="space-y-2">
              <Label for="email">Correo electrónico</Label>
              <Input
                id="email"
                v-model="email"
                type="email"
                placeholder="tu@email.com"
                :disabled="loading"
                class="h-11"
              />
            </div>

            <div class="space-y-2">
              <Label for="password">Contraseña</Label>
              <Input
                id="password"
                v-model="password"
                type="password"
                placeholder="Mínimo 8 caracteres"
                :disabled="loading"
                class="h-11"
              />
            </div>

            <div class="space-y-2">
              <Label for="confirmPassword">Confirmar contraseña</Label>
              <Input
                id="confirmPassword"
                v-model="confirmPassword"
                type="password"
                placeholder="Repite tu contraseña"
                :disabled="loading"
                class="h-11"
              />
            </div>
          </div>

          <div class="space-y-4">
            <Button type="submit" class="w-full h-11 text-base" :disabled="loading">
              {{ loading ? 'Creando cuenta...' : 'Crear cuenta gratis' }}
            </Button>

            <p class="text-xs text-center text-muted-foreground">
              Al registrarte, aceptas nuestros
              <RouterLink to="/terms" class="text-primary hover:underline">Términos de servicio</RouterLink>
              y
              <RouterLink to="/privacy" class="text-primary hover:underline">Política de privacidad</RouterLink>
            </p>
          </div>
        </form>

        <p class="text-center text-sm text-muted-foreground">
          ¿Ya tienes una cuenta?
          <RouterLink to="/login" class="font-medium text-primary hover:underline">
            Inicia sesión
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
