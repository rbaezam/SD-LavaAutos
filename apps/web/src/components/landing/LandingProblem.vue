<script setup lang="ts">
import { AlertCircle, Clock, MessageCircle, FileQuestion, ArrowRight } from 'lucide-vue-next'
import LandingSection from './LandingSection.vue'

const problems = [
  {
    icon: MessageCircle,
    title: '"¿Ya está mi carro?"',
    description: 'Tus clientes interrumpen constantemente preguntando por el estado de su vehículo.',
    color: 'text-red-500',
    bg: 'bg-red-50',
  },
  {
    icon: Clock,
    title: 'Tiempos de espera inciertos',
    description: 'Sin un sistema, es imposible dar estimaciones precisas a tus clientes.',
    color: 'text-amber-500',
    bg: 'bg-amber-50',
  },
  {
    icon: FileQuestion,
    title: 'Tickets de papel perdidos',
    description: 'Controles manuales que se pierden, ensucian o son difíciles de organizar.',
    color: 'text-orange-500',
    bg: 'bg-orange-50',
  },
  {
    icon: AlertCircle,
    title: 'Sin visibilidad del negocio',
    description: 'No sabes cuántos autos atiendes al día ni cuáles servicios son más rentables.',
    color: 'text-purple-500',
    bg: 'bg-purple-50',
  },
]
</script>

<template>
  <LandingSection background="gray">
    <div class="text-center">
      <span class="inline-block rounded-full bg-red-100 px-4 py-1.5 text-sm font-medium text-red-700">
        El problema
      </span>
      <h2 class="mt-4 text-3xl font-bold text-gray-900 sm:text-4xl">
        ¿Te suena familiar?
      </h2>
      <p class="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
        Los autolavados tradicionales enfrentan estos problemas todos los días.
        No tienes que seguir así.
      </p>
    </div>

    <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:mt-16">
      <div
        v-for="(problem, index) in problems"
        :key="index"
        class="group relative overflow-hidden rounded-2xl border border-gray-200 bg-white p-6 transition-all hover:shadow-lg hover:border-gray-300"
      >
        <div class="flex items-start gap-4">
          <div :class="['flex h-12 w-12 shrink-0 items-center justify-center rounded-xl', problem.bg]">
            <component :is="problem.icon" :class="['h-6 w-6', problem.color]" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-900">{{ problem.title }}</h3>
            <p class="mt-2 text-gray-600">{{ problem.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Transition to solution -->
    <div class="mt-16 text-center">
      <div class="inline-flex items-center gap-2 text-primary font-medium">
        <span>Hay una mejor manera</span>
        <ArrowRight class="h-5 w-5 animate-pulse" />
      </div>
    </div>
  </LandingSection>
</template>
