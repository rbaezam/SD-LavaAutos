import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/lib/api'

// Types
export type NotificationChannel = 'sms' | 'whatsapp'
export type NotificationEvent =
  | 'ticket_created'
  | 'status_changed'
  | 'ready'
  | 'delivered'
  | 'manual'
export type NotificationStatus = 'pending' | 'sent' | 'failed' | 'simulated'

export interface NotificationTemplate {
  id: string
  organization_id: string
  channel: NotificationChannel
  event: NotificationEvent
  title: string
  message_template: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface NotificationLog {
  id: string
  organization_id: string
  ticket_id: string | null
  template_id: string | null
  channel: NotificationChannel
  provider: string
  event: NotificationEvent
  status: NotificationStatus
  recipient: string
  message: string
  error_message: string | null
  created_at: string
  sent_at: string | null
}

export interface TemplateVariable {
  name: string
  description: string
  example: string
}

export interface SendNotificationResponse {
  success: boolean
  log_id: string
  status: NotificationStatus
  message: string | null
  error: string | null
}

export interface PreviewNotificationResponse {
  recipient: string
  message: string
  channel: NotificationChannel
  event: NotificationEvent
}

export const useNotificationStore = defineStore('notification', () => {
  // State
  const templates = ref<NotificationTemplate[]>([])
  const logs = ref<NotificationLog[]>([])
  const variables = ref<TemplateVariable[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const logsTotal = ref(0)

  // Template Actions
  async function fetchTemplates(channel?: NotificationChannel, event?: NotificationEvent) {
    loading.value = true
    error.value = null
    try {
      const params: Record<string, string> = {}
      if (channel) params.channel = channel
      if (event) params.event = event

      const response = await api.get<{ items: NotificationTemplate[]; total: number }>(
        '/api/v1/notifications/templates',
        { params }
      )
      templates.value = response.data.items
    } catch (err) {
      error.value = 'Error al cargar plantillas'
      console.error('Error fetching templates:', err)
    } finally {
      loading.value = false
    }
  }

  async function createTemplate(data: {
    channel: NotificationChannel
    event: NotificationEvent
    title: string
    message_template: string
    is_active?: boolean
  }): Promise<NotificationTemplate | null> {
    loading.value = true
    error.value = null
    try {
      const response = await api.post<NotificationTemplate>(
        '/api/v1/notifications/templates',
        data
      )
      templates.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = 'Error al crear plantilla'
      console.error('Error creating template:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateTemplate(
    id: string,
    data: {
      title?: string
      message_template?: string
      is_active?: boolean
    }
  ): Promise<NotificationTemplate | null> {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch<NotificationTemplate>(
        `/api/v1/notifications/templates/${id}`,
        data
      )
      const index = templates.value.findIndex((t) => t.id === id)
      if (index !== -1) {
        templates.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = 'Error al actualizar plantilla'
      console.error('Error updating template:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  async function deleteTemplate(id: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/api/v1/notifications/templates/${id}`)
      templates.value = templates.value.filter((t) => t.id !== id)
      return true
    } catch (err) {
      error.value = 'Error al eliminar plantilla'
      console.error('Error deleting template:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchVariables() {
    try {
      const response = await api.get<{ variables: TemplateVariable[] }>(
        '/api/v1/notifications/templates/variables'
      )
      variables.value = response.data.variables
    } catch (err) {
      console.error('Error fetching variables:', err)
    }
  }

  // Log Actions
  async function fetchLogs(ticketId?: string, limit = 50, offset = 0) {
    loading.value = true
    error.value = null
    try {
      const params: Record<string, string | number> = { limit, offset }
      if (ticketId) params.ticket_id = ticketId

      const response = await api.get<{ items: NotificationLog[]; total: number }>(
        '/api/v1/notifications/logs',
        { params }
      )
      logs.value = response.data.items
      logsTotal.value = response.data.total
    } catch (err) {
      error.value = 'Error al cargar historial'
      console.error('Error fetching logs:', err)
    } finally {
      loading.value = false
    }
  }

  // Send Actions
  async function sendNotification(
    ticketId: string,
    channel: NotificationChannel,
    templateId: string,
    dryRun = false
  ): Promise<SendNotificationResponse | null> {
    loading.value = true
    error.value = null
    try {
      const response = await api.post<SendNotificationResponse>(
        '/api/v1/notifications/send',
        {
          ticket_id: ticketId,
          channel,
          template_id: templateId,
          dry_run: dryRun,
        }
      )
      return response.data
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } }
      error.value = axiosError.response?.data?.detail || 'Error al enviar notificación'
      console.error('Error sending notification:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  async function previewNotification(
    ticketId: string,
    templateId: string
  ): Promise<PreviewNotificationResponse | null> {
    try {
      const response = await api.post<PreviewNotificationResponse>(
        '/api/v1/notifications/preview',
        {
          ticket_id: ticketId,
          template_id: templateId,
        }
      )
      return response.data
    } catch (err) {
      console.error('Error previewing notification:', err)
      return null
    }
  }

  // Helpers
  function getTemplatesByChannel(channel: NotificationChannel): NotificationTemplate[] {
    return templates.value.filter((t) => t.channel === channel && t.is_active)
  }

  function getEventLabel(event: NotificationEvent): string {
    const labels: Record<NotificationEvent, string> = {
      ticket_created: 'Ticket creado',
      status_changed: 'Cambio de estado',
      ready: 'Listo para entrega',
      delivered: 'Entregado',
      manual: 'Manual',
    }
    return labels[event] || event
  }

  function getChannelLabel(channel: NotificationChannel): string {
    return channel === 'whatsapp' ? 'WhatsApp' : 'SMS'
  }

  function getStatusLabel(status: NotificationStatus): string {
    const labels: Record<NotificationStatus, string> = {
      pending: 'Pendiente',
      sent: 'Enviado',
      failed: 'Error',
      simulated: 'Simulado',
    }
    return labels[status] || status
  }

  return {
    // State
    templates,
    logs,
    variables,
    loading,
    error,
    logsTotal,

    // Template Actions
    fetchTemplates,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    fetchVariables,

    // Log Actions
    fetchLogs,

    // Send Actions
    sendNotification,
    previewNotification,

    // Helpers
    getTemplatesByChannel,
    getEventLabel,
    getChannelLabel,
    getStatusLabel,
  }
})
