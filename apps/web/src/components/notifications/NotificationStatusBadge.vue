<script setup lang="ts">
import { computed } from 'vue'
import { Check, X, FlaskConical, Clock } from 'lucide-vue-next'
import { Badge } from '@/components/ui'
import type { NotificationStatus } from '@/stores/notification'

interface Props {
  status: NotificationStatus
}

const props = defineProps<Props>()

const config = computed(() => {
  const configs: Record<
    NotificationStatus,
    {
      label: string
      variant: 'success' | 'destructive' | 'secondary' | 'warning'
      icon: typeof Check
    }
  > = {
    sent: {
      label: 'Enviado',
      variant: 'success',
      icon: Check,
    },
    failed: {
      label: 'Error',
      variant: 'destructive',
      icon: X,
    },
    simulated: {
      label: 'Simulado',
      variant: 'secondary',
      icon: FlaskConical,
    },
    pending: {
      label: 'Pendiente',
      variant: 'warning',
      icon: Clock,
    },
  }
  return configs[props.status]
})
</script>

<template>
  <Badge :variant="config.variant" class="gap-1">
    <component :is="config.icon" class="h-3 w-3" />
    {{ config.label }}
  </Badge>
</template>
