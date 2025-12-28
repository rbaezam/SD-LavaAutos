<script setup lang="ts">
import { computed } from 'vue'
import type { Status } from '@/stores/status'
import type { TicketListItem } from '@/stores/ticket'
import { getToneClasses, getEmptyMessage } from '@/composables/useDisplayTone'
import DisplayCard from './DisplayCard.vue'

interface Props {
  status: Status
  tickets: TicketListItem[]
  showEta?: boolean
  showElapsed?: boolean
  darkMode?: boolean
  isFocused?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showEta: true,
  showElapsed: true,
  darkMode: false,
  isFocused: false,
})

// Get tone classes for this status
const toneClasses = computed(() => getToneClasses(props.status.name, props.status.id))

// Empty message for this column
const emptyMessage = computed(() => getEmptyMessage(props.status.id))
</script>

<template>
  <div
    :class="[
      'flex h-full flex-col rounded-xl overflow-hidden transition-all duration-300',
      isFocused && !darkMode && 'ring-2 ring-primary/20',
      isFocused && darkMode && 'ring-2 ring-primary/30',
    ]"
  >
    <!-- Color bar at top -->
    <div
      :class="[
        'h-1 w-full',
        darkMode ? toneClasses.barDark : toneClasses.bar,
      ]"
    />

    <!-- Column header -->
    <div
      :class="[
        'flex items-center justify-between px-4 py-3 border-l-4 transition-colors duration-300',
        darkMode ? toneClasses.headerBgDark : toneClasses.headerBg,
        darkMode ? toneClasses.headerBorderDark : toneClasses.headerBorder,
      ]"
    >
      <h2
        :class="[
          'text-lg font-semibold uppercase tracking-wide',
          darkMode ? 'text-gray-100' : 'text-gray-700',
        ]"
      >
        {{ status.name }}
      </h2>
      <span
        :class="[
          'flex h-7 min-w-[28px] items-center justify-center rounded-full px-2.5 text-sm font-bold transition-colors duration-300',
          darkMode ? toneClasses.badgeDark : toneClasses.badge,
          darkMode ? toneClasses.badgeTextDark : toneClasses.badgeText,
        ]"
      >
        {{ tickets.length }}
      </span>
    </div>

    <!-- Tickets list -->
    <div
      :class="[
        'flex-1 space-y-3 overflow-y-auto p-3 transition-colors duration-300',
        darkMode ? 'bg-gray-900/30' : 'bg-white/50',
      ]"
    >
      <TransitionGroup
        name="card"
        tag="div"
        class="space-y-3"
      >
        <DisplayCard
          v-for="ticket in tickets"
          :key="ticket.id"
          :ticket="ticket"
          :show-eta="showEta"
          :show-elapsed="showElapsed"
          :dark-mode="darkMode"
        />
      </TransitionGroup>

      <!-- Empty state -->
      <div
        v-if="tickets.length === 0"
        :class="[
          'flex h-24 items-center justify-center rounded-xl border-2 border-dashed transition-colors duration-300',
          darkMode
            ? 'border-gray-700 text-gray-500'
            : 'border-gray-200 text-gray-400',
        ]"
      >
        <p class="text-sm text-center px-4">{{ emptyMessage }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Card transition animations */
.card-enter-active {
  transition: all 0.3s ease-out;
}

.card-leave-active {
  transition: all 0.2s ease-in;
}

.card-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.card-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

.card-move {
  transition: transform 0.3s ease;
}
</style>
