<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { ArrowRight, Sparkles } from 'lucide-vue-next'
import { Button } from '@/components/ui'
import LandingSection from './LandingSection.vue'
</script>

<template>
  <LandingSection class="!py-0">
    <div class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary via-primary to-blue-600 px-6 py-16 sm:px-12 sm:py-20 lg:px-16 lg:py-24">
      <!-- Background decorations -->
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute -top-20 -right-20 h-60 w-60 rounded-full bg-white/10 blur-3xl" />
        <div class="absolute -bottom-20 -left-20 h-60 w-60 rounded-full bg-white/10 blur-3xl" />
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-80 w-80 rounded-full bg-white/5 blur-3xl" />
      </div>

      <div class="relative text-center">
        <!-- Badge -->
        <div class="mb-6 inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-1.5 text-sm font-medium text-white/90">
          <Sparkles class="h-4 w-4" />
          <span>Sin tarjeta de crédito requerida</span>
        </div>

        <h2 class="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
          Empieza gratis hoy
        </h2>
        <p class="mx-auto mt-4 max-w-2xl text-lg text-white/80 sm:text-xl">
          Configura tu autolavado en minutos. Mejora la experiencia de tus clientes desde el primer día.
        </p>

        <div class="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <RouterLink to="/register">
            <Button
              size="lg"
              class="gap-2 !bg-white !text-primary hover:!bg-white/90 px-8 text-base shadow-xl"
            >
              Crear cuenta gratis
              <ArrowRight class="h-5 w-5" />
            </Button>
          </RouterLink>
          <RouterLink to="/login">
            <Button
              size="lg"
              class="!bg-transparent !border !border-white/30 !text-white hover:!bg-white/10 px-8 text-base"
            >
              Ya tengo cuenta
            </Button>
          </RouterLink>
        </div>

        <!-- Trust text -->
        <p class="mt-8 text-sm text-white/60">
          Únete a autolavados que ya confían en WashFlow
        </p>
      </div>
    </div>
  </LandingSection>
</template>
