<script setup lang="ts">
import { computed } from 'vue'
import { MessageCircle, Smartphone } from 'lucide-vue-next'
import type { NotificationChannel } from '@/stores/notification'

interface Props {
  message: string
  channel: NotificationChannel
  recipient?: string
}

const props = defineProps<Props>()

const isWhatsApp = computed(() => props.channel === 'whatsapp')
</script>

<template>
  <div class="space-y-2">
    <!-- Channel indicator -->
    <div class="flex items-center gap-2 text-sm text-muted-foreground">
      <component :is="isWhatsApp ? MessageCircle : Smartphone" class="h-4 w-4" />
      <span>{{ isWhatsApp ? 'WhatsApp' : 'SMS' }}</span>
      <span v-if="recipient" class="font-mono">{{ recipient }}</span>
    </div>

    <!-- Message bubble -->
    <div
      :class="[
        'relative max-w-sm rounded-lg p-3 text-sm',
        isWhatsApp
          ? 'bg-green-100 text-green-900 dark:bg-green-900/30 dark:text-green-100'
          : 'bg-muted text-foreground',
      ]"
    >
      <!-- WhatsApp tail -->
      <div
        v-if="isWhatsApp"
        class="absolute -left-1.5 top-2 h-3 w-3 rotate-45 bg-green-100 dark:bg-green-900/30"
      />
      <!-- SMS tail -->
      <div
        v-else
        class="absolute -left-1.5 top-2 h-3 w-3 rotate-45 bg-muted"
      />

      <p class="relative whitespace-pre-wrap">{{ message }}</p>
    </div>
  </div>
</template>
