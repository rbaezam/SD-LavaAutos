<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Play, ArrowRight, Clock, CreditCard, Gift } from 'lucide-vue-next'
import { Button } from '@/components/ui'

function scrollToHowItWorks() {
  const element = document.querySelector('#como-funciona')
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>

<template>
  <section class="relative overflow-hidden bg-gradient-to-b from-blue-50/50 via-white to-white pt-24 pb-16 sm:pt-32 sm:pb-20 lg:pt-40 lg:pb-28">
    <!-- Background decorations -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-primary/5 blur-3xl" />
      <div class="absolute top-60 -left-40 h-80 w-80 rounded-full bg-blue-400/5 blur-3xl" />
      <div class="absolute bottom-0 left-1/2 -translate-x-1/2 h-60 w-full max-w-4xl bg-gradient-to-t from-primary/3 to-transparent blur-3xl" />
    </div>

    <div class="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-4xl text-center">
        <!-- Main heading - benefit focused -->
        <h1 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl">
          Deja de contestar
          <span class="relative">
            <span class="relative z-10 bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
              "¿Ya esta mi carro?"
            </span>
            <span class="absolute bottom-2 left-0 right-0 h-3 bg-primary/10 -rotate-1" />
          </span>
        </h1>

        <!-- Subtitle - clear value proposition -->
        <p class="mt-6 text-lg leading-relaxed text-gray-600 sm:text-xl lg:text-2xl">
          Tus clientes ven el avance de su vehiculo en tiempo real.
          <span class="text-gray-900 font-medium">Tu equipo trabaja sin interrupciones.</span>
        </p>

        <!-- CTA Buttons -->
        <div class="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <RouterLink to="/register">
            <Button size="lg" class="gap-2 px-8 text-base shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 transition-shadow">
              Empezar gratis
              <ArrowRight class="h-5 w-5" />
            </Button>
          </RouterLink>
          <Button
            variant="outline"
            size="lg"
            class="gap-2 px-8 text-base"
            @click="scrollToHowItWorks"
          >
            <Play class="h-5 w-5" />
            Ver como funciona
          </Button>
        </div>

        <!-- Trust indicators -->
        <div class="mt-12 flex flex-wrap items-center justify-center gap-8 text-sm text-gray-500">
          <div class="flex items-center gap-2">
            <Clock class="h-5 w-5 text-primary/60" />
            <span>Listo en 5 minutos</span>
          </div>
          <div class="flex items-center gap-2">
            <CreditCard class="h-5 w-5 text-primary/60" />
            <span>Sin tarjeta de credito</span>
          </div>
          <div class="flex items-center gap-2">
            <Gift class="h-5 w-5 text-primary/60" />
            <span>Plan gratis para siempre</span>
          </div>
        </div>
      </div>

      <!-- Hero Image / Dashboard Preview -->
      <div class="relative mt-16 sm:mt-20 lg:mt-24">
        <div class="absolute inset-0 bg-gradient-to-t from-white via-transparent to-transparent z-10 pointer-events-none" />

        <!-- Main screenshot placeholder -->
        <div class="relative mx-auto max-w-5xl">
          <div class="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-2xl shadow-gray-200/50">
            <!-- Browser chrome -->
            <div class="flex items-center gap-2 border-b border-gray-100 bg-gray-50 px-4 py-3">
              <div class="flex gap-1.5">
                <div class="h-3 w-3 rounded-full bg-gray-300" />
                <div class="h-3 w-3 rounded-full bg-gray-300" />
                <div class="h-3 w-3 rounded-full bg-gray-300" />
              </div>
              <div class="mx-auto flex h-7 w-full max-w-md items-center justify-center rounded-md bg-white text-xs text-gray-400 border border-gray-200">
                app.washflow.mx
              </div>
            </div>

            <!-- Dashboard preview - Simplified workflow visualization -->
            <div class="aspect-[16/10] bg-gradient-to-br from-gray-50 to-gray-100 p-4 sm:p-8">
              <div class="h-full grid grid-cols-3 gap-4">
                <!-- Column 1 - En espera -->
                <div class="rounded-lg bg-white border border-gray-200 p-3 overflow-hidden">
                  <div class="flex items-center gap-2 mb-3">
                    <div class="h-2 w-2 rounded-full bg-amber-400" />
                    <span class="text-xs font-medium text-gray-700">En espera</span>
                    <span class="text-xs text-gray-400 ml-auto">3</span>
                  </div>
                  <div class="space-y-2">
                    <div class="rounded-md bg-amber-50 border border-amber-100 p-2">
                      <p class="text-xs font-medium text-gray-800">ABC-123</p>
                      <p class="text-xs text-gray-500">Lavado completo</p>
                    </div>
                    <div class="rounded-md bg-amber-50 border border-amber-100 p-2">
                      <p class="text-xs font-medium text-gray-800">XYZ-789</p>
                      <p class="text-xs text-gray-500">Encerado</p>
                    </div>
                  </div>
                </div>
                <!-- Column 2 - En proceso -->
                <div class="rounded-lg bg-white border border-gray-200 p-3 overflow-hidden">
                  <div class="flex items-center gap-2 mb-3">
                    <div class="h-2 w-2 rounded-full bg-blue-500" />
                    <span class="text-xs font-medium text-gray-700">En proceso</span>
                    <span class="text-xs text-gray-400 ml-auto">2</span>
                  </div>
                  <div class="space-y-2">
                    <div class="rounded-md bg-blue-50 border border-blue-100 p-2">
                      <p class="text-xs font-medium text-gray-800">DEF-456</p>
                      <p class="text-xs text-gray-500">Detallado</p>
                    </div>
                  </div>
                </div>
                <!-- Column 3 - Listo -->
                <div class="rounded-lg bg-white border border-gray-200 p-3 overflow-hidden">
                  <div class="flex items-center gap-2 mb-3">
                    <div class="h-2 w-2 rounded-full bg-green-500" />
                    <span class="text-xs font-medium text-gray-700">Listo</span>
                    <span class="text-xs text-gray-400 ml-auto">4</span>
                  </div>
                  <div class="space-y-2">
                    <div class="rounded-md bg-green-50 border border-green-100 p-2">
                      <p class="text-xs font-medium text-gray-800">GHI-321</p>
                      <p class="text-xs text-gray-500">Lavado express</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Floating cards -->
          <div class="absolute -left-4 top-1/3 hidden lg:block">
            <div class="rounded-lg bg-white p-4 shadow-xl shadow-gray-200/50 border border-gray-100">
              <div class="flex items-center gap-3">
                <div class="flex h-10 w-10 items-center justify-center rounded-full bg-green-100">
                  <svg class="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">Vehiculo listo</p>
                  <p class="text-xs text-gray-500">Cliente notificado</p>
                </div>
              </div>
            </div>
          </div>

          <div class="absolute -right-4 top-1/2 hidden lg:block">
            <div class="rounded-lg bg-white p-4 shadow-xl shadow-gray-200/50 border border-gray-100">
              <div class="flex items-center gap-3">
                <div class="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100">
                  <svg class="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">WhatsApp enviado</p>
                  <p class="text-xs text-gray-500">Automaticamente</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
