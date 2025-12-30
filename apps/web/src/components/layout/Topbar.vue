<script setup lang="ts">
import { computed, ref } from 'vue'
import { ChevronDown, LogOut, MapPin, Menu, Settings } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { Button, Select } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'
import { useLocationStore } from '@/stores/location'
import { cn } from '@/lib/utils'

const emit = defineEmits<{
  toggleSidebar: []
}>()

const authStore = useAuthStore()
const locationStore = useLocationStore()
const router = useRouter()

const showUserMenu = ref(false)

const locationOptions = computed(() =>
  locationStore.locations.map((loc) => ({
    value: loc.id,
    label: loc.name,
  }))
)

const selectedLocation = computed({
  get: () => locationStore.selectedLocationId || '',
  set: (value: string) => locationStore.setSelectedLocation(value),
})

const userInitials = computed(() => {
  const email = authStore.user?.email || ''
  if (email) {
    return email.substring(0, 2).toUpperCase()
  }
  return 'U'
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function closeUserMenu() {
  showUserMenu.value = false
}
</script>

<template>
  <header class="flex h-16 items-center justify-between border-b bg-card/50 backdrop-blur-sm px-4 sm:px-6">
    <div class="flex items-center gap-4">
      <Button variant="ghost" size="icon" class="shrink-0" @click="emit('toggleSidebar')">
        <Menu class="h-5 w-5" />
      </Button>

      <!-- Location Selector -->
      <div v-if="locationStore.hasLocations" class="hidden items-center gap-2 sm:flex">
        <div class="flex items-center gap-1.5 rounded-lg bg-muted/50 px-2 py-1">
          <MapPin class="h-3.5 w-3.5 text-muted-foreground" />
          <span class="text-xs text-muted-foreground">Sucursal</span>
        </div>
        <Select
          v-model="selectedLocation"
          :options="locationOptions"
          :disabled="!locationStore.canChangeLocation"
          placeholder="Seleccionar"
          class="w-44"
        />
      </div>
    </div>

    <div class="flex items-center gap-2">
      <!-- User Menu -->
      <div class="relative">
        <button
          type="button"
          :class="
            cn(
              'flex items-center gap-2 rounded-lg px-2 py-1.5 transition-colors hover:bg-accent',
              showUserMenu && 'bg-accent'
            )
          "
          @click="showUserMenu = !showUserMenu"
        >
          <div
            class="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-xs font-medium text-primary-foreground"
          >
            {{ userInitials }}
          </div>
          <div class="hidden text-left sm:block">
            <p class="text-sm font-medium leading-none">
              {{ authStore.user?.email?.split('@')[0] || 'Usuario' }}
            </p>
            <p class="text-xs text-muted-foreground">
              {{ authStore.user?.role || 'staff' }}
            </p>
          </div>
          <ChevronDown class="hidden h-4 w-4 text-muted-foreground sm:block" />
        </button>

        <!-- Dropdown -->
        <Transition
          enter-active-class="transition duration-100 ease-out"
          enter-from-class="transform scale-95 opacity-0"
          enter-to-class="transform scale-100 opacity-100"
          leave-active-class="transition duration-75 ease-in"
          leave-from-class="transform scale-100 opacity-100"
          leave-to-class="transform scale-95 opacity-0"
        >
          <div
            v-if="showUserMenu"
            class="absolute right-0 top-full z-[60] mt-2 w-56 rounded-lg border bg-popover p-1 shadow-lg"
          >
            <div class="px-3 py-2 sm:hidden">
              <p class="text-sm font-medium">{{ authStore.user?.email || 'Usuario' }}</p>
              <p class="text-xs text-muted-foreground">{{ authStore.user?.role || 'staff' }}</p>
            </div>
            <div class="my-1 h-px bg-border sm:hidden" />
            <button
              type="button"
              class="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-accent"
              @click="router.push('/app/settings'); closeUserMenu()"
            >
              <Settings class="h-4 w-4" />
              Configuración
            </button>
            <div class="my-1 h-px bg-border" />
            <button
              type="button"
              class="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-destructive hover:bg-destructive/10"
              @click="handleLogout"
            >
              <LogOut class="h-4 w-4" />
              Cerrar sesión
            </button>
          </div>
        </Transition>
      </div>
    </div>
  </header>

  <!-- Click outside to close -->
  <Teleport to="body">
    <div
      v-if="showUserMenu"
      class="fixed inset-0 z-[45]"
      @click="closeUserMenu"
    />
  </Teleport>
</template>
