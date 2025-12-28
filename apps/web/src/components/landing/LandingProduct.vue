<script setup lang="ts">
import { ref } from 'vue'
import { LayoutDashboard, MonitorPlay, Smartphone } from 'lucide-vue-next'
import LandingSection from './LandingSection.vue'

const activeTab = ref(0)

const screens = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    title: 'Panel de control inteligente',
    description: 'Visualiza todos tus tickets en un flujo de trabajo visual. Arrastra y suelta para cambiar estados. Ve métricas en tiempo real.',
    features: ['Flujo visual de trabajo', 'Métricas del día', 'Búsqueda rápida', 'Filtros por estado'],
  },
  {
    id: 'display',
    label: 'Pantalla de sala',
    icon: MonitorPlay,
    title: 'Pantalla para tus clientes',
    description: 'Muestra el estado de los vehículos en tu sala de espera. Actualización automática. Personalizable con tu marca.',
    features: ['Tiempo real', 'Tu logo y colores', 'Modo oscuro', 'Pantalla completa'],
  },
  {
    id: 'public',
    label: 'Vista pública',
    icon: Smartphone,
    title: 'Seguimiento desde el celular',
    description: 'Cada ticket tiene un código QR. Tus clientes escanean y ven el estado de su vehículo desde cualquier lugar.',
    features: ['Código QR', 'Sin app', 'Compartir por WhatsApp', 'Historial de estados'],
  },
]
</script>

<template>
  <LandingSection id="producto" background="gray">
    <div class="text-center">
      <span class="inline-block rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
        Producto
      </span>
      <h2 class="mt-4 text-3xl font-bold text-gray-900 sm:text-4xl">
        Una plataforma completa
      </h2>
      <p class="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
        Desde el registro del vehículo hasta la entrega, WashFlow te acompaña en cada paso.
      </p>
    </div>

    <!-- Tab selector -->
    <div class="mt-12 flex justify-center">
      <div class="inline-flex rounded-xl bg-white p-1.5 shadow-sm border border-gray-100">
        <button
          v-for="(screen, index) in screens"
          :key="screen.id"
          :class="[
            'flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all',
            activeTab === index
              ? 'bg-primary text-white shadow-sm'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50',
          ]"
          @click="activeTab = index"
        >
          <component :is="screen.icon" class="h-4 w-4" />
          <span class="hidden sm:inline">{{ screen.label }}</span>
        </button>
      </div>
    </div>

    <!-- Screen preview -->
    <div class="mt-10 lg:mt-12">
      <transition
        mode="out-in"
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div :key="activeTab" class="grid gap-8 lg:grid-cols-2 lg:items-center">
          <!-- Info -->
          <div class="order-2 lg:order-1">
            <h3 class="text-2xl font-bold text-gray-900 sm:text-3xl">
              {{ screens[activeTab].title }}
            </h3>
            <p class="mt-4 text-lg text-gray-600 leading-relaxed">
              {{ screens[activeTab].description }}
            </p>

            <!-- Features list -->
            <ul class="mt-6 space-y-3">
              <li
                v-for="feature in screens[activeTab].features"
                :key="feature"
                class="flex items-center gap-3"
              >
                <div class="flex h-6 w-6 items-center justify-center rounded-full bg-green-100">
                  <svg class="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span class="text-gray-700">{{ feature }}</span>
              </li>
            </ul>
          </div>

          <!-- Screenshot placeholder -->
          <div class="order-1 lg:order-2">
            <div class="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-xl">
              <!-- Browser chrome -->
              <div class="flex items-center gap-2 border-b border-gray-100 bg-gray-50 px-4 py-3">
                <div class="flex gap-1.5">
                  <div class="h-3 w-3 rounded-full bg-gray-300" />
                  <div class="h-3 w-3 rounded-full bg-gray-300" />
                  <div class="h-3 w-3 rounded-full bg-gray-300" />
                </div>
              </div>

              <!-- Screen content placeholder -->
              <div class="aspect-[4/3] bg-gradient-to-br from-gray-50 to-gray-100 p-6">
                <div class="h-full rounded-lg border-2 border-dashed border-gray-200 flex items-center justify-center">
                  <div class="text-center">
                    <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                      <component :is="screens[activeTab].icon" class="h-8 w-8 text-primary" />
                    </div>
                    <p class="text-lg font-medium text-gray-900">{{ screens[activeTab].label }}</p>
                    <p class="mt-1 text-sm text-gray-500">Captura de pantalla próximamente</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </LandingSection>
</template>
