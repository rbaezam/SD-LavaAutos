<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { z } from 'zod'
import { Droplets } from 'lucide-vue-next'
import { Button, Input, Label, Alert } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const loginSchema = z.object({
  email: z.string().email('Correo electrónico inválido'),
  password: z.string().min(1, 'La contraseña es requerida'),
})

async function handleSubmit() {
  error.value = ''

  const validation = loginSchema.safeParse({
    email: email.value,
    password: password.value,
  })

  if (!validation.success) {
    error.value = validation.error.errors[0].message
    return
  }

  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    const redirect = route.query.redirect as string
    router.push(redirect || '/app/dashboard')
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      error.value = axiosErr.response?.data?.detail || 'Error al iniciar sesión'
    } else {
      error.value = 'Error al iniciar sesión'
    }
  } finally {
    loading.value = false
  }
}
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

      <div class="space-y-6">
        <h1 class="text-4xl font-bold text-white leading-tight">
          Gestiona tu autolavado de forma inteligente
        </h1>
        <p class="text-lg text-white/80">
          Controla tus tickets, notifica a tus clientes y mejora la experiencia de tu negocio.
        </p>
        <div class="flex items-center gap-4 text-white/70 text-sm">
          <div class="flex items-center gap-2">
            <div class="h-2 w-2 rounded-full bg-green-400"></div>
            <span>Sin tarjeta de crédito</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="h-2 w-2 rounded-full bg-green-400"></div>
            <span>Plan gratis disponible</span>
          </div>
        </div>
      </div>

      <p class="text-sm text-white/50">
        © 2024 WashFlow. Todos los derechos reservados.
      </p>
    </div>

    <!-- Right side - Login Form -->
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
          <h2 class="text-3xl font-bold tracking-tight">Bienvenido de vuelta</h2>
          <p class="text-muted-foreground">
            Ingresa tus credenciales para acceder a tu cuenta
          </p>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <Alert v-if="error" variant="destructive">
            {{ error }}
          </Alert>

          <div class="space-y-4">
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
              <div class="flex items-center justify-between">
                <Label for="password">Contraseña</Label>
                <a href="#" class="text-sm text-primary hover:underline">
                  ¿Olvidaste tu contraseña?
                </a>
              </div>
              <Input
                id="password"
                v-model="password"
                type="password"
                placeholder="Tu contraseña"
                :disabled="loading"
                class="h-11"
              />
            </div>
          </div>

          <Button type="submit" class="w-full h-11 text-base" :disabled="loading">
            {{ loading ? 'Iniciando sesión...' : 'Iniciar sesión' }}
          </Button>
        </form>

        <p class="text-center text-sm text-muted-foreground">
          ¿No tienes una cuenta?
          <RouterLink to="/register" class="font-medium text-primary hover:underline">
            Regístrate gratis
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
