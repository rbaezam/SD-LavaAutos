<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Check, Sparkles } from 'lucide-vue-next'
import { Button } from '@/components/ui'
import LandingSection from './LandingSection.vue'

const plans = [
  {
    name: 'Gratis',
    description: 'Para empezar a digitalizar tu negocio',
    price: '$0',
    period: 'para siempre',
    featured: false,
    features: [
      '1 sucursal',
      'Hasta 50 tickets/mes',
      'Flujo de trabajo visual',
      'Pantalla de sala de espera',
      'Vista pública con QR',
      'Soporte por email',
    ],
    cta: 'Empezar gratis',
    ctaLink: '/register',
  },
  {
    name: 'Pro',
    description: 'Para negocios en crecimiento',
    price: '$299',
    period: 'MXN/mes',
    featured: true,
    features: [
      'Hasta 3 sucursales',
      'Tickets ilimitados',
      'Todo lo del plan Gratis',
      'Notificaciones WhatsApp/SMS',
      'Reportes básicos',
      'Personalización de marca',
      'Hasta 10 usuarios',
      'Soporte prioritario',
    ],
    cta: 'Probar 14 días gratis',
    ctaLink: '/register?plan=pro',
  },
  {
    name: 'Business',
    description: 'Para cadenas y franquicias',
    price: '$599',
    period: 'MXN/mes',
    featured: false,
    features: [
      'Sucursales ilimitadas',
      'Tickets ilimitados',
      'Todo lo del plan Pro',
      'Reportes avanzados',
      'API para integraciones',
      'Usuarios ilimitados',
      'Soporte dedicado',
      'Onboarding personalizado',
    ],
    cta: 'Contactar ventas',
    ctaLink: '/register?plan=business',
  },
]
</script>

<template>
  <LandingSection id="precios" background="gray">
    <div class="text-center">
      <span class="inline-block rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
        Precios
      </span>
      <h2 class="mt-4 text-3xl font-bold text-gray-900 sm:text-4xl">
        Simple y transparente
      </h2>
      <p class="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
        Empieza gratis, crece cuando lo necesites. Sin sorpresas.
      </p>
    </div>

    <div class="mx-auto mt-12 grid max-w-5xl gap-8 lg:mt-16 lg:grid-cols-3">
      <div
        v-for="(plan, index) in plans"
        :key="index"
        :class="[
          'relative overflow-hidden rounded-2xl border bg-white p-8 transition-all',
          plan.featured
            ? 'border-primary shadow-xl shadow-primary/10 lg:-mt-4 lg:mb-4'
            : 'border-gray-200 hover:border-gray-300 hover:shadow-lg',
        ]"
      >
        <!-- Featured badge -->
        <div
          v-if="plan.featured"
          class="absolute right-6 top-6 flex items-center gap-1 rounded-full bg-primary px-3 py-1 text-xs font-medium text-white"
        >
          <Sparkles class="h-3 w-3" />
          Popular
        </div>

        <!-- Plan header -->
        <div>
          <h3 class="text-xl font-semibold text-gray-900">{{ plan.name }}</h3>
          <p class="mt-1 text-gray-600">{{ plan.description }}</p>
        </div>

        <!-- Price -->
        <div class="mt-6">
          <span class="text-4xl font-bold text-gray-900">{{ plan.price }}</span>
          <span class="text-gray-600"> {{ plan.period }}</span>
        </div>

        <!-- CTA -->
        <RouterLink :to="plan.ctaLink" class="mt-6 block">
          <Button
            :variant="plan.featured ? 'default' : 'outline'"
            class="w-full"
            size="lg"
          >
            {{ plan.cta }}
          </Button>
        </RouterLink>

        <!-- Features -->
        <ul class="mt-8 space-y-3">
          <li
            v-for="feature in plan.features"
            :key="feature"
            class="flex items-center gap-3"
          >
            <div :class="[
              'flex h-5 w-5 shrink-0 items-center justify-center rounded-full',
              plan.featured ? 'bg-primary/10' : 'bg-gray-100',
            ]">
              <Check :class="[
                'h-3 w-3',
                plan.featured ? 'text-primary' : 'text-gray-600',
              ]" />
            </div>
            <span class="text-gray-600">{{ feature }}</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Enterprise note -->
    <div class="mt-12 text-center">
      <p class="text-gray-600">
        ¿Necesitas algo más?
        <a href="mailto:ventas@washflow.mx" class="text-primary font-medium hover:underline">
          Contáctanos
        </a>
        para un plan personalizado.
      </p>
    </div>
  </LandingSection>
</template>
