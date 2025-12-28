<script setup lang="ts">
import { ClipboardList, MonitorPlay, Bell } from 'lucide-vue-next'
import LandingSection from './LandingSection.vue'

const steps = [
  {
    number: '01',
    icon: ClipboardList,
    title: 'Registra el vehículo',
    description: 'Crea un ticket con la placa, servicios y datos del cliente. Obtén un código único al instante.',
    color: 'from-blue-500 to-blue-600',
  },
  {
    number: '02',
    icon: MonitorPlay,
    title: 'Visualiza en pantalla',
    description: 'Muestra el tablero en tu sala de espera. Tus clientes ven el estado en tiempo real.',
    color: 'from-primary to-blue-600',
  },
  {
    number: '03',
    icon: Bell,
    title: 'Notifica automáticamente',
    description: 'Envía WhatsApp o SMS cuando el vehículo esté listo. Sin que tu equipo haga nada.',
    color: 'from-green-500 to-emerald-600',
  },
]
</script>

<template>
  <LandingSection id="como-funciona">
    <div class="text-center">
      <span class="inline-block rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
        Cómo funciona
      </span>
      <h2 class="mt-4 text-3xl font-bold text-gray-900 sm:text-4xl">
        Simple como 1, 2, 3
      </h2>
      <p class="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
        Configura WashFlow en minutos y transforma la experiencia de tu autolavado.
      </p>
    </div>

    <div class="relative mt-16 lg:mt-20">
      <!-- Connection line (desktop) -->
      <div class="absolute left-0 right-0 top-24 hidden h-0.5 bg-gradient-to-r from-blue-200 via-primary/30 to-green-200 lg:block" />

      <div class="grid gap-8 lg:grid-cols-3 lg:gap-12">
        <div
          v-for="(step, index) in steps"
          :key="index"
          class="relative"
        >
          <!-- Step card -->
          <div class="relative rounded-2xl border border-gray-100 bg-white p-8 shadow-sm transition-all hover:shadow-lg hover:border-primary/20">
            <!-- Number badge -->
            <div
              :class="[
                'absolute -top-5 left-8 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br text-white font-bold shadow-lg',
                step.color,
              ]"
            >
              {{ step.number }}
            </div>

            <!-- Icon -->
            <div class="mt-4 mb-6">
              <div class="inline-flex h-14 w-14 items-center justify-center rounded-xl bg-gray-50">
                <component :is="step.icon" class="h-7 w-7 text-gray-700" />
              </div>
            </div>

            <!-- Content -->
            <h3 class="text-xl font-semibold text-gray-900">{{ step.title }}</h3>
            <p class="mt-3 text-gray-600 leading-relaxed">{{ step.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </LandingSection>
</template>
