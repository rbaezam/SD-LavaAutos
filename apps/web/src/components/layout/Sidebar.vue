<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { Columns3, Layers, LayoutDashboard, MapPin, Package2, Settings, Ticket } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

interface Props {
  collapsed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  collapsed: false,
})

const route = useRoute()

const navItems = [
  { name: 'Dashboard', to: '/app/dashboard', icon: LayoutDashboard },
  { name: 'Tickets', to: '/app/tickets', icon: Ticket },
  { name: 'Operación', to: '/app/kanban', icon: Columns3 },
  { name: 'Sucursales', to: '/app/locations', icon: MapPin },
  { name: 'Servicios', to: '/app/services', icon: Layers },
  { name: 'Paquetes', to: '/app/packages', icon: Package2 },
  { name: 'Configuración', to: '/app/settings', icon: Settings },
]

const sidebarWidth = computed(() => (props.collapsed ? 'w-16' : 'w-64'))

function isActive(path: string) {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<template>
  <aside
    :class="
      cn(
        'flex flex-col border-r bg-card/50 backdrop-blur-sm transition-all duration-300',
        sidebarWidth
      )
    "
  >
    <!-- Logo -->
    <div class="flex h-16 items-center border-b px-4" :class="collapsed ? 'justify-center' : ''">
      <div class="flex items-center gap-2">
        <div
          class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary font-bold text-primary-foreground"
        >
          W
        </div>
        <span
          v-if="!collapsed"
          class="text-lg font-semibold tracking-tight"
        >
          WashFlow
        </span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 space-y-1 p-3">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        :class="
          cn(
            'group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all',
            isActive(item.to)
              ? 'bg-primary/10 text-primary'
              : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
            collapsed && 'justify-center px-2'
          )
        "
      >
        <!-- Active indicator -->
        <div
          v-if="isActive(item.to)"
          class="absolute left-0 top-1/2 h-6 w-1 -translate-y-1/2 rounded-r-full bg-primary"
        />
        <component
          :is="item.icon"
          :class="
            cn(
              'h-5 w-5 flex-shrink-0 transition-colors',
              isActive(item.to) ? 'text-primary' : 'text-muted-foreground group-hover:text-foreground'
            )
          "
        />
        <span v-if="!collapsed" :class="isActive(item.to) ? 'font-semibold' : ''">
          {{ item.name }}
        </span>
        <!-- Tooltip for collapsed state -->
        <div
          v-if="collapsed"
          class="pointer-events-none absolute left-full ml-2 hidden rounded-md bg-popover px-2 py-1 text-xs font-medium text-popover-foreground shadow-md group-hover:block"
        >
          {{ item.name }}
        </div>
      </RouterLink>
    </nav>

    <!-- Footer -->
    <div class="border-t p-3">
      <div
        :class="
          cn(
            'flex items-center gap-2 rounded-lg bg-muted/50 px-3 py-2',
            collapsed && 'justify-center px-2'
          )
        "
      >
        <div class="h-2 w-2 rounded-full bg-green-500" />
        <span v-if="!collapsed" class="text-xs text-muted-foreground">Sistema operando</span>
      </div>
    </div>
  </aside>
</template>
