<script setup lang="ts">
interface Props {
  id?: string
  class?: string
  container?: boolean
  background?: 'white' | 'gray' | 'gradient'
}

withDefaults(defineProps<Props>(), {
  container: true,
  background: 'white',
})
</script>

<template>
  <section
    :id="id"
    :class="[
      'py-16 sm:py-20 lg:py-24',
      background === 'white' && 'bg-white',
      background === 'gray' && 'bg-gray-50',
      background === 'gradient' && 'bg-gradient-to-b from-primary/5 to-white',
      $props.class,
    ]"
  >
    <div v-if="container" class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <slot />
    </div>
    <slot v-else />
  </section>
</template>
