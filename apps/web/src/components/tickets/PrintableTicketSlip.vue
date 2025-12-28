<script setup lang="ts">
import { QRCode } from '@/components/ui'

interface Props {
  publicCode: string
  publicUrl: string
  vehicleLabel: string
  brandName?: string
  brandLogoUrl?: string | null
  preview?: boolean
}

withDefaults(defineProps<Props>(), {
  brandName: 'WashFlow',
  brandLogoUrl: null,
  preview: false,
})
</script>

<template>
  <div
    :class="[
      'bg-white text-black',
      preview ? 'p-4' : 'p-6',
    ]"
    :style="{ width: preview ? 'auto' : '80mm' }"
  >
    <!-- Header with branding -->
    <div class="mb-4 text-center">
      <!-- Logo -->
      <div v-if="brandLogoUrl" class="mb-2 flex justify-center">
        <img
          :src="brandLogoUrl"
          :alt="brandName"
          class="h-12 w-auto object-contain"
        />
      </div>
      <div v-else class="mb-2 flex justify-center">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-900 text-lg font-bold text-white">
          W
        </div>
      </div>

      <!-- Brand name -->
      <h1 class="text-lg font-bold">{{ brandName }}</h1>
    </div>

    <!-- Divider -->
    <div class="mb-4 border-t border-dashed border-gray-400" />

    <!-- QR Code -->
    <div class="mb-4 flex justify-center">
      <div class="rounded-lg bg-white p-2">
        <QRCode
          :value="publicUrl"
          :size="preview ? 120 : 150"
        />
      </div>
    </div>

    <!-- Folio -->
    <div class="mb-4 text-center">
      <p class="text-xs text-gray-500">FOLIO</p>
      <p class="font-mono text-2xl font-bold tracking-wider">{{ publicCode }}</p>
    </div>

    <!-- Vehicle -->
    <div class="mb-4 text-center">
      <p class="text-xs text-gray-500">VEHÍCULO</p>
      <p class="font-medium">{{ vehicleLabel }}</p>
    </div>

    <!-- Divider -->
    <div class="mb-4 border-t border-dashed border-gray-400" />

    <!-- Instructions -->
    <div class="mb-4 text-center">
      <p class="text-sm font-medium">Escanea para ver el estado</p>
      <p class="mt-1 text-xs text-gray-500">{{ publicUrl.replace('https://', '').replace('http://', '') }}</p>
    </div>

    <!-- Footer -->
    <div class="text-center">
      <p class="text-xs text-gray-400">
        Si tienes dudas, pregunta en recepción.
      </p>
    </div>
  </div>
</template>
