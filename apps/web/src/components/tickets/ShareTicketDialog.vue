<script setup lang="ts">
import { ref, computed } from 'vue'
import { Link2, QrCode, Printer, Check, Copy } from 'lucide-vue-next'
import { Button, Dialog, QRCode } from '@/components/ui'
import PrintableTicketSlip from './PrintableTicketSlip.vue'

interface Props {
  publicCode: string
  vehicleLabel: string
  brandName?: string
  brandLogoUrl?: string | null
}

const props = defineProps<Props>()

const open = defineModel<boolean>('open', { default: false })
const activeTab = ref<'link' | 'qr' | 'print'>('qr')
const linkCopied = ref(false)
const linkCopyTimeout = ref<ReturnType<typeof setTimeout> | null>(null)

// Generate public URL
const publicUrl = computed(() => {
  return `${window.location.origin}/t/${props.publicCode}`
})

// Copy link to clipboard
async function copyLink() {
  try {
    await navigator.clipboard.writeText(publicUrl.value)
    linkCopied.value = true

    if (linkCopyTimeout.value) clearTimeout(linkCopyTimeout.value)
    linkCopyTimeout.value = setTimeout(() => {
      linkCopied.value = false
    }, 2000)
  } catch {
    // Fallback for older browsers
    const input = document.createElement('input')
    input.value = publicUrl.value
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    linkCopied.value = true
  }
}

// Print ticket slip
function printSlip() {
  window.print()
}
</script>

<template>
  <Dialog
    v-model:open="open"
    title="Compartir con cliente"
  >
    <template #content>
      <div class="space-y-4">
        <!-- Tabs -->
        <div class="flex gap-1 rounded-lg bg-muted p-1">
          <button
            :class="[
              'flex flex-1 items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors',
              activeTab === 'link'
                ? 'bg-background shadow-sm'
                : 'text-muted-foreground hover:text-foreground',
            ]"
            @click="activeTab = 'link'"
          >
            <Link2 class="h-4 w-4" />
            Enlace
          </button>
          <button
            :class="[
              'flex flex-1 items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors',
              activeTab === 'qr'
                ? 'bg-background shadow-sm'
                : 'text-muted-foreground hover:text-foreground',
            ]"
            @click="activeTab = 'qr'"
          >
            <QrCode class="h-4 w-4" />
            QR
          </button>
          <button
            :class="[
              'flex flex-1 items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors',
              activeTab === 'print'
                ? 'bg-background shadow-sm'
                : 'text-muted-foreground hover:text-foreground',
            ]"
            @click="activeTab = 'print'"
          >
            <Printer class="h-4 w-4" />
            Imprimir
          </button>
        </div>

        <!-- Tab content -->
        <div class="min-h-[300px]">
          <!-- Link tab -->
          <div v-if="activeTab === 'link'" class="space-y-4">
            <p class="text-sm text-muted-foreground">
              Comparte este enlace con el cliente para que pueda seguir el estado de su vehículo.
            </p>

            <div class="flex gap-2">
              <input
                type="text"
                :value="publicUrl"
                readonly
                class="flex-1 rounded-md border border-input bg-muted px-3 py-2 text-sm font-mono"
              />
              <Button
                :variant="linkCopied ? 'default' : 'outline'"
                :class="linkCopied && 'bg-green-600 hover:bg-green-600'"
                @click="copyLink"
              >
                <Check v-if="linkCopied" class="mr-2 h-4 w-4" />
                <Copy v-else class="mr-2 h-4 w-4" />
                {{ linkCopied ? 'Copiado' : 'Copiar' }}
              </Button>
            </div>

            <div class="rounded-lg border bg-muted/50 p-4">
              <p class="text-xs text-muted-foreground">
                El cliente podrá ver: folio, vehículo, estado actual, hora estimada y sucursal.
                <strong>No verá</strong> datos personales, precios ni detalles de servicios.
              </p>
            </div>
          </div>

          <!-- QR tab -->
          <div v-if="activeTab === 'qr'" class="flex flex-col items-center space-y-4">
            <div class="rounded-xl border bg-white p-4 shadow-sm">
              <QRCode :value="publicUrl" :size="200" />
            </div>

            <p class="text-center text-sm text-muted-foreground">
              Escanea para ver el estado del servicio
            </p>

            <p class="font-mono text-lg font-bold">{{ publicCode }}</p>
          </div>

          <!-- Print tab -->
          <div v-if="activeTab === 'print'" class="space-y-4">
            <p class="text-sm text-muted-foreground">
              Vista previa del recibo imprimible. Pégalo en el parabrisas o entrégalo al cliente.
            </p>

            <!-- Print preview -->
            <div class="overflow-hidden rounded-lg border bg-white shadow-sm">
              <PrintableTicketSlip
                :public-code="publicCode"
                :public-url="publicUrl"
                :vehicle-label="vehicleLabel"
                :brand-name="brandName"
                :brand-logo-url="brandLogoUrl"
                preview
              />
            </div>

            <Button class="w-full" @click="printSlip">
              <Printer class="mr-2 h-4 w-4" />
              Imprimir recibo
            </Button>
          </div>
        </div>
      </div>
    </template>
  </Dialog>

  <!-- Printable content (hidden, only shows when printing) -->
  <Teleport to="body">
    <div class="print-only">
      <PrintableTicketSlip
        :public-code="publicCode"
        :public-url="publicUrl"
        :vehicle-label="vehicleLabel"
        :brand-name="brandName"
        :brand-logo-url="brandLogoUrl"
      />
    </div>
  </Teleport>
</template>

<style>
/* Print styles */
@media print {
  body > *:not(.print-only) {
    display: none !important;
  }

  .print-only {
    display: block !important;
  }
}

@media screen {
  .print-only {
    display: none;
  }
}
</style>
