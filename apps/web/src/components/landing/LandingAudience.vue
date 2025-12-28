<script setup lang="ts">
import { Car, Sparkles, Wrench, Building2 } from 'lucide-vue-next'
import LandingSection from './LandingSection.vue'

const audiences = [
  {
    icon: Car,
    title: 'Autolavados',
    description: 'Desde lavados express hasta servicios completos. WashFlow se adapta a tu operación.',
    examples: ['Lavado a mano', 'Lavado express', 'Túneles de lavado'],
  },
  {
    icon: Sparkles,
    title: 'Estéticas automotrices',
    description: 'Gestiona servicios de detallado, pulido y protección con tiempos más largos.',
    examples: ['Detailing', 'Pulido', 'Coating cerámico'],
  },
  {
    icon: Wrench,
    title: 'Centros de detallado',
    description: 'Múltiples bahías, varios técnicos. Controla todo desde un solo lugar.',
    examples: ['Corrección de pintura', 'Restauración', 'PPF'],
  },
  {
    icon: Building2,
    title: 'Multi-sucursal',
    description: 'Administra todas tus ubicaciones desde una cuenta. Métricas consolidadas.',
    examples: ['Franquicias', 'Cadenas', 'Grupos empresariales'],
  },
]
</script>

<template>
  <LandingSection>
    <div class="text-center">
      <span class="inline-block rounded-full bg-blue-100 px-4 py-1.5 text-sm font-medium text-blue-700">
        Para quién es
      </span>
      <h2 class="mt-4 text-3xl font-bold text-gray-900 sm:text-4xl">
        Diseñado para negocios como el tuyo
      </h2>
      <p class="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
        Sin importar el tamaño de tu operación, WashFlow te ayuda a crecer.
      </p>
    </div>

    <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:mt-16 lg:gap-8">
      <div
        v-for="(audience, index) in audiences"
        :key="index"
        class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-gradient-to-br from-white to-gray-50 p-6 transition-all hover:shadow-lg hover:border-primary/20"
      >
        <!-- Background decoration -->
        <div class="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-primary/5 transition-transform group-hover:scale-150" />

        <div class="relative">
          <div class="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
            <component :is="audience.icon" class="h-6 w-6 text-primary" />
          </div>

          <h3 class="mt-4 text-xl font-semibold text-gray-900">{{ audience.title }}</h3>
          <p class="mt-2 text-gray-600">{{ audience.description }}</p>

          <!-- Examples -->
          <div class="mt-4 flex flex-wrap gap-2">
            <span
              v-for="example in audience.examples"
              :key="example"
              class="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600"
            >
              {{ example }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </LandingSection>
</template>
