<script setup lang="ts">
import {
  Clock,
  TrendingUp,
  Smartphone,
  BarChart3,
  Shield,
  Zap
} from 'lucide-vue-next'
import LandingSection from './LandingSection.vue'

const benefits = [
  {
    icon: Clock,
    title: 'Reduce preguntas en 80%',
    description: 'Tus clientes ven el estado de su vehículo en tiempo real. Ya no interrumpen a tu equipo.',
    color: 'text-blue-600',
    bg: 'bg-blue-50',
  },
  {
    icon: TrendingUp,
    title: 'Aumenta la productividad',
    description: 'Tu equipo se enfoca en lavar, no en responder preguntas. Más autos, más ganancias.',
    color: 'text-green-600',
    bg: 'bg-green-50',
  },
  {
    icon: Smartphone,
    title: 'Notificaciones automáticas',
    description: 'WhatsApp y SMS cuando el auto está listo. Tus clientes regresan puntuales.',
    color: 'text-purple-600',
    bg: 'bg-purple-50',
  },
  {
    icon: BarChart3,
    title: 'Métricas que importan',
    description: 'Conoce tus servicios más vendidos, tiempos promedio y tendencias de tu negocio.',
    color: 'text-amber-600',
    bg: 'bg-amber-50',
  },
  {
    icon: Shield,
    title: 'Experiencia profesional',
    description: 'Impresiona a tus clientes con tecnología moderna. Diferénciate de la competencia.',
    color: 'text-indigo-600',
    bg: 'bg-indigo-50',
  },
  {
    icon: Zap,
    title: 'Fácil de usar',
    description: 'Interfaz intuitiva que cualquier empleado puede usar. Sin capacitación complicada.',
    color: 'text-rose-600',
    bg: 'bg-rose-50',
  },
]
</script>

<template>
  <LandingSection id="beneficios" background="gradient">
    <div class="text-center">
      <span class="inline-block rounded-full bg-green-100 px-4 py-1.5 text-sm font-medium text-green-700">
        Beneficios
      </span>
      <h2 class="mt-4 text-3xl font-bold text-gray-900 sm:text-4xl">
        Todo lo que necesitas para modernizar tu autolavado
      </h2>
      <p class="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
        WashFlow te da las herramientas para operar de forma eficiente y ofrecer una mejor experiencia.
      </p>
    </div>

    <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:mt-16 lg:grid-cols-3">
      <div
        v-for="(benefit, index) in benefits"
        :key="index"
        class="group rounded-2xl border border-gray-100 bg-white p-6 transition-all hover:shadow-lg hover:border-primary/20 hover:-translate-y-1"
      >
        <div :class="['inline-flex h-12 w-12 items-center justify-center rounded-xl', benefit.bg]">
          <component :is="benefit.icon" :class="['h-6 w-6', benefit.color]" />
        </div>
        <h3 class="mt-4 text-lg font-semibold text-gray-900">{{ benefit.title }}</h3>
        <p class="mt-2 text-gray-600 leading-relaxed">{{ benefit.description }}</p>
      </div>
    </div>
  </LandingSection>
</template>
