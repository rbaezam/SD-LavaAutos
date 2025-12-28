<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import QRCodeLib from 'qrcode'

interface Props {
  value: string
  size?: number
  margin?: number
  darkColor?: string
  lightColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 200,
  margin: 2,
  darkColor: '#000000',
  lightColor: '#ffffff',
})

const svgContent = ref('')

async function generateQR() {
  try {
    const svg = await QRCodeLib.toString(props.value, {
      type: 'svg',
      width: props.size,
      margin: props.margin,
      color: {
        dark: props.darkColor,
        light: props.lightColor,
      },
    })
    svgContent.value = svg
  } catch (err) {
    console.error('QR generation error:', err)
    svgContent.value = ''
  }
}

onMounted(generateQR)
watch(() => [props.value, props.size, props.darkColor, props.lightColor], generateQR)
</script>

<template>
  <div
    class="inline-flex items-center justify-center"
    v-html="svgContent"
  />
</template>
