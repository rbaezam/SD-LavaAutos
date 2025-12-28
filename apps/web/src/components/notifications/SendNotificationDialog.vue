<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { MessageCircle, Smartphone, Send, FlaskConical, Loader2 } from 'lucide-vue-next'
import { Button, Dialog, Select, Alert } from '@/components/ui'
import NotificationPreview from './NotificationPreview.vue'
import { useNotificationStore, type NotificationChannel } from '@/stores/notification'

interface Ticket {
  id: string
  public_code: string
  customer_name?: string | null
  customer_whatsapp?: string | null
}

interface Props {
  ticket: Ticket
}

const props = defineProps<Props>()

const open = defineModel<boolean>('open', { default: false })
const emit = defineEmits<{
  sent: [{ success: boolean; simulated: boolean }]
}>()

const notificationStore = useNotificationStore()

// Local state
const selectedChannel = ref<NotificationChannel>('whatsapp')
const selectedTemplateId = ref<string>('')
const previewMessage = ref<string>('')
const previewLoading = ref(false)
const sending = ref(false)
const sendError = ref<string | null>(null)
const sendSuccess = ref<{ simulated: boolean } | null>(null)

// Feature flags - hardcoded for now, can be made dynamic later
const features = {
  whatsapp: false, // Disabled until real provider configured
  sms: true,
}

// Computed
const hasRecipient = computed(() => !!props.ticket.customer_whatsapp)

const availableChannels = computed(() => {
  const channels: { value: NotificationChannel; label: string; icon: typeof MessageCircle; enabled: boolean }[] = [
    { value: 'whatsapp', label: 'WhatsApp', icon: MessageCircle, enabled: features.whatsapp },
    { value: 'sms', label: 'SMS', icon: Smartphone, enabled: features.sms },
  ]
  return channels.filter((c) => c.enabled)
})

const channelTemplates = computed(() => {
  return notificationStore.getTemplatesByChannel(selectedChannel.value)
})

const templateOptions = computed(() => {
  return channelTemplates.value.map((t) => ({
    value: t.id,
    label: t.title,
    description: notificationStore.getEventLabel(t.event),
  }))
})

const canSend = computed(() => {
  return hasRecipient.value && selectedTemplateId.value && !sending.value
})

// Load templates when dialog opens
watch(open, async (isOpen) => {
  if (isOpen) {
    sendError.value = null
    sendSuccess.value = null
    previewMessage.value = ''

    // Set default channel to first available
    if (availableChannels.value.length > 0 && !availableChannels.value.find((c) => c.value === selectedChannel.value)) {
      selectedChannel.value = availableChannels.value[0].value
    }

    await notificationStore.fetchTemplates()

    // Auto-select first template if available
    if (channelTemplates.value.length > 0 && !selectedTemplateId.value) {
      selectedTemplateId.value = channelTemplates.value[0].id
    }
  }
})

// Update template selection when channel changes
watch(selectedChannel, () => {
  selectedTemplateId.value = ''
  previewMessage.value = ''
  if (channelTemplates.value.length > 0) {
    selectedTemplateId.value = channelTemplates.value[0].id
  }
})

// Load preview when template changes
watch(selectedTemplateId, async (templateId) => {
  if (!templateId) {
    previewMessage.value = ''
    return
  }

  previewLoading.value = true
  try {
    const preview = await notificationStore.previewNotification(props.ticket.id, templateId)
    if (preview) {
      previewMessage.value = preview.message
    }
  } finally {
    previewLoading.value = false
  }
})

// Actions
async function send(dryRun = false) {
  if (!selectedTemplateId.value) return

  sending.value = true
  sendError.value = null
  sendSuccess.value = null

  try {
    const result = await notificationStore.sendNotification(
      props.ticket.id,
      selectedChannel.value,
      selectedTemplateId.value,
      dryRun
    )

    if (result) {
      if (result.success) {
        sendSuccess.value = { simulated: result.status === 'simulated' }
        emit('sent', { success: true, simulated: result.status === 'simulated' })

        // Close dialog after short delay on success
        setTimeout(() => {
          open.value = false
        }, 1500)
      } else {
        sendError.value = result.error || 'Error al enviar notificación'
      }
    } else {
      sendError.value = notificationStore.error || 'Error al enviar notificación'
    }
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <Dialog v-model:open="open" title="Enviar notificación" description="Envía un mensaje al cliente sobre su vehículo">
    <div class="space-y-4">
      <!-- No recipient warning -->
      <Alert v-if="!hasRecipient" variant="warning">
        <p class="text-sm">
          Este ticket no tiene número de teléfono registrado.
          Edita el ticket para agregar el WhatsApp del cliente.
        </p>
      </Alert>

      <!-- Recipient info -->
      <div v-else class="rounded-lg border p-3 bg-muted/50">
        <p class="text-sm text-muted-foreground">Destinatario</p>
        <p class="font-mono text-sm">{{ ticket.customer_whatsapp }}</p>
        <p v-if="ticket.customer_name" class="text-sm text-muted-foreground">
          {{ ticket.customer_name }}
        </p>
      </div>

      <!-- Channel selector -->
      <div v-if="availableChannels.length > 1" class="space-y-2">
        <label class="text-sm font-medium">Canal</label>
        <div class="flex gap-2">
          <button
            v-for="channel in availableChannels"
            :key="channel.value"
            :class="[
              'flex flex-1 items-center justify-center gap-2 rounded-lg border-2 p-3 transition-colors',
              selectedChannel === channel.value
                ? 'border-primary bg-primary/5'
                : 'border-transparent bg-muted hover:bg-muted/80',
            ]"
            @click="selectedChannel = channel.value"
          >
            <component :is="channel.icon" class="h-5 w-5" />
            <span class="font-medium">{{ channel.label }}</span>
          </button>
        </div>
      </div>

      <!-- Template selector -->
      <div class="space-y-2">
        <label class="text-sm font-medium">Plantilla</label>
        <Select
          v-model="selectedTemplateId"
          :options="templateOptions"
          placeholder="Seleccionar plantilla..."
          :disabled="!hasRecipient || channelTemplates.length === 0"
        />
        <p v-if="channelTemplates.length === 0" class="text-xs text-muted-foreground">
          No hay plantillas activas para este canal.
          Crea una en Configuración → Notificaciones.
        </p>
      </div>

      <!-- Preview -->
      <div v-if="selectedTemplateId" class="space-y-2">
        <label class="text-sm font-medium">Vista previa</label>
        <div class="rounded-lg border p-4 bg-background">
          <div v-if="previewLoading" class="flex items-center justify-center py-4">
            <Loader2 class="h-5 w-5 animate-spin text-muted-foreground" />
          </div>
          <NotificationPreview
            v-else-if="previewMessage"
            :message="previewMessage"
            :channel="selectedChannel"
          />
          <p v-else class="text-sm text-muted-foreground text-center py-4">
            Selecciona una plantilla para ver la vista previa
          </p>
        </div>
      </div>

      <!-- Success message -->
      <Alert v-if="sendSuccess" variant="success">
        <p class="text-sm">
          {{ sendSuccess.simulated ? 'Notificación simulada correctamente' : 'Notificación enviada correctamente' }}
        </p>
      </Alert>

      <!-- Error message -->
      <Alert v-if="sendError" variant="destructive">
        <p class="text-sm">{{ sendError }}</p>
      </Alert>

      <!-- Actions -->
      <div class="flex gap-2 pt-2">
        <Button
          variant="outline"
          class="flex-1"
          :disabled="!canSend"
          @click="send(true)"
        >
          <FlaskConical class="mr-2 h-4 w-4" />
          Simular
        </Button>
        <Button
          class="flex-1"
          :disabled="!canSend"
          @click="send(false)"
        >
          <Loader2 v-if="sending" class="mr-2 h-4 w-4 animate-spin" />
          <Send v-else class="mr-2 h-4 w-4" />
          Enviar
        </Button>
      </div>
    </div>
  </Dialog>
</template>
