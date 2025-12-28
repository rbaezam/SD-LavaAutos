<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Droplets } from 'lucide-vue-next'

const currentYear = new Date().getFullYear()

const footerLinks = {
  producto: [
    { label: 'Beneficios', href: '#beneficios' },
    { label: 'Cómo funciona', href: '#como-funciona' },
    { label: 'Precios', href: '#precios' },
  ],
  empresa: [
    { label: 'Acerca de', href: '/about' },
    { label: 'Blog', href: '/blog' },
    { label: 'Contacto', href: 'mailto:hola@washflow.mx' },
  ],
  legal: [
    { label: 'Términos de servicio', href: '/terms' },
    { label: 'Política de privacidad', href: '/privacy' },
  ],
}

function scrollToSection(href: string) {
  if (href.startsWith('#')) {
    const element = document.querySelector(href)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }
}
</script>

<template>
  <footer class="border-t border-gray-100 bg-gray-50">
    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-16">
      <div class="grid gap-8 lg:grid-cols-4">
        <!-- Brand -->
        <div class="lg:col-span-1">
          <RouterLink to="/" class="flex items-center gap-2">
            <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-white">
              <Droplets class="h-5 w-5" />
            </div>
            <span class="text-xl font-bold text-gray-900">WashFlow</span>
          </RouterLink>
          <p class="mt-4 text-sm text-gray-600 max-w-xs">
            La plataforma moderna para gestionar tu autolavado y mejorar la experiencia de tus clientes.
          </p>
        </div>

        <!-- Links -->
        <div class="grid grid-cols-2 gap-8 sm:grid-cols-3 lg:col-span-3">
          <!-- Producto -->
          <div>
            <h3 class="text-sm font-semibold text-gray-900">Producto</h3>
            <ul class="mt-4 space-y-3">
              <li v-for="link in footerLinks.producto" :key="link.label">
                <button
                  v-if="link.href.startsWith('#')"
                  class="text-sm text-gray-600 hover:text-gray-900 transition-colors"
                  @click="scrollToSection(link.href)"
                >
                  {{ link.label }}
                </button>
                <RouterLink
                  v-else
                  :to="link.href"
                  class="text-sm text-gray-600 hover:text-gray-900 transition-colors"
                >
                  {{ link.label }}
                </RouterLink>
              </li>
            </ul>
          </div>

          <!-- Empresa -->
          <div>
            <h3 class="text-sm font-semibold text-gray-900">Empresa</h3>
            <ul class="mt-4 space-y-3">
              <li v-for="link in footerLinks.empresa" :key="link.label">
                <a
                  v-if="link.href.startsWith('mailto:')"
                  :href="link.href"
                  class="text-sm text-gray-600 hover:text-gray-900 transition-colors"
                >
                  {{ link.label }}
                </a>
                <RouterLink
                  v-else
                  :to="link.href"
                  class="text-sm text-gray-600 hover:text-gray-900 transition-colors"
                >
                  {{ link.label }}
                </RouterLink>
              </li>
            </ul>
          </div>

          <!-- Legal -->
          <div>
            <h3 class="text-sm font-semibold text-gray-900">Legal</h3>
            <ul class="mt-4 space-y-3">
              <li v-for="link in footerLinks.legal" :key="link.label">
                <RouterLink
                  :to="link.href"
                  class="text-sm text-gray-600 hover:text-gray-900 transition-colors"
                >
                  {{ link.label }}
                </RouterLink>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Bottom -->
      <div class="mt-12 border-t border-gray-200 pt-8">
        <div class="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <p class="text-sm text-gray-500">
            &copy; {{ currentYear }} WashFlow. Todos los derechos reservados.
          </p>
          <p class="text-sm text-gray-500">
            Hecho con <span class="text-red-500">&hearts;</span> en México
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>
