<script setup lang="ts">
import { SearchX } from 'lucide-vue-next'

interface Props {
  publicCode: string
}

defineProps<Props>()
</script>

<template>
  <div class="overflow-hidden rounded-2xl bg-white shadow-xl">
    <!-- Main content -->
    <div class="px-6 py-12 text-center">
      <!-- Icon -->
      <div class="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-slate-100">
        <SearchX class="h-10 w-10 text-slate-400" />
      </div>

      <!-- Title -->
      <h2 class="text-xl font-semibold text-slate-900">
        Ticket no encontrado
      </h2>

      <!-- Message -->
      <p class="mx-auto mt-3 max-w-sm text-slate-600">
        No encontramos un ticket con el código
        <span class="font-mono font-semibold">{{ publicCode }}</span>.
        Por favor verifica que el código sea correcto.
      </p>

      <!-- Suggestions -->
      <div class="mt-8 rounded-xl bg-slate-50 p-4">
        <p class="text-sm font-medium text-slate-700">Sugerencias:</p>
        <ul class="mt-2 space-y-1 text-left text-sm text-slate-600">
          <li class="flex items-start gap-2">
            <span class="mt-1 text-slate-400">•</span>
            <span>Verifica que el código esté escrito correctamente</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="mt-1 text-slate-400">•</span>
            <span>El código tiene el formato WF-XXXX (ej: WF-2K9A)</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="mt-1 text-slate-400">•</span>
            <span>Consulta tu recibo o pregunta al personal</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
