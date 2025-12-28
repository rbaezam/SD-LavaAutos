<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { Menu, X, Droplets } from 'lucide-vue-next'
import { Button } from '@/components/ui'

const isScrolled = ref(false)
const isMobileMenuOpen = ref(false)

const navLinks = [
  { label: 'Beneficios', href: '#beneficios' },
  { label: 'Cómo funciona', href: '#como-funciona' },
  { label: 'Producto', href: '#producto' },
  { label: 'Precios', href: '#precios' },
]

function handleScroll() {
  isScrolled.value = window.scrollY > 20
}

function scrollToSection(href: string) {
  isMobileMenuOpen.value = false
  const element = document.querySelector(href)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <nav
    :class="[
      'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
      isScrolled
        ? 'bg-white/90 backdrop-blur-md shadow-sm border-b border-gray-100'
        : 'bg-transparent',
    ]"
  >
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 items-center justify-between">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center gap-2">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-white">
            <Droplets class="h-5 w-5" />
          </div>
          <span class="text-xl font-bold text-gray-900">WashFlow</span>
        </RouterLink>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex md:items-center md:gap-8">
          <button
            v-for="link in navLinks"
            :key="link.href"
            class="text-sm font-medium text-gray-600 transition-colors hover:text-gray-900"
            @click="scrollToSection(link.href)"
          >
            {{ link.label }}
          </button>
        </div>

        <!-- Desktop CTA -->
        <div class="hidden md:flex md:items-center md:gap-4">
          <RouterLink to="/login">
            <Button variant="ghost" size="sm">
              Iniciar sesión
            </Button>
          </RouterLink>
          <RouterLink to="/register">
            <Button size="sm">
              Probar gratis
            </Button>
          </RouterLink>
        </div>

        <!-- Mobile menu button -->
        <button
          class="md:hidden rounded-lg p-2 text-gray-600 hover:bg-gray-100"
          @click="isMobileMenuOpen = !isMobileMenuOpen"
        >
          <Menu v-if="!isMobileMenuOpen" class="h-6 w-6" />
          <X v-else class="h-6 w-6" />
        </button>
      </div>
    </div>

    <!-- Mobile Navigation -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div
        v-if="isMobileMenuOpen"
        class="absolute left-0 right-0 top-16 bg-white border-b border-gray-100 shadow-lg md:hidden"
      >
        <div class="space-y-1 px-4 py-4">
          <button
            v-for="link in navLinks"
            :key="link.href"
            class="block w-full rounded-lg px-4 py-3 text-left text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            @click="scrollToSection(link.href)"
          >
            {{ link.label }}
          </button>
          <div class="border-t border-gray-100 pt-4 mt-4 space-y-2">
            <RouterLink to="/login" class="block">
              <Button variant="outline" class="w-full">
                Iniciar sesión
              </Button>
            </RouterLink>
            <RouterLink to="/register" class="block">
              <Button class="w-full">
                Probar gratis
              </Button>
            </RouterLink>
          </div>
        </div>
      </div>
    </transition>
  </nav>
</template>
