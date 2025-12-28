<script setup lang="ts">
interface Props {
  darkMode?: boolean
  columnCount?: number
}

withDefaults(defineProps<Props>(), {
  darkMode: false,
  columnCount: 4,
})
</script>

<template>
  <div class="h-full">
    <!-- Header skeleton -->
    <div
      :class="[
        'flex items-center justify-between px-6 py-4 border-b',
        darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200',
      ]"
    >
      <div class="flex items-center gap-4">
        <div
          :class="[
            'h-10 w-10 animate-pulse rounded-lg',
            darkMode ? 'bg-gray-800' : 'bg-gray-200',
          ]"
        />
        <div class="space-y-2">
          <div
            :class="[
              'h-5 w-48 animate-pulse rounded',
              darkMode ? 'bg-gray-800' : 'bg-gray-200',
            ]"
          />
          <div
            :class="[
              'h-4 w-32 animate-pulse rounded',
              darkMode ? 'bg-gray-800' : 'bg-gray-200',
            ]"
          />
        </div>
      </div>
      <div class="text-right space-y-2">
        <div
          :class="[
            'h-7 w-20 animate-pulse rounded ml-auto',
            darkMode ? 'bg-gray-800' : 'bg-gray-200',
          ]"
        />
        <div
          :class="[
            'h-4 w-36 animate-pulse rounded',
            darkMode ? 'bg-gray-800' : 'bg-gray-200',
          ]"
        />
      </div>
    </div>

    <!-- Toolbar skeleton -->
    <div
      :class="[
        'flex items-center justify-between px-6 py-3 border-b',
        darkMode ? 'bg-gray-900/50 border-gray-800' : 'bg-gray-50 border-gray-200',
      ]"
    >
      <div
        :class="[
          'h-8 w-40 animate-pulse rounded-lg',
          darkMode ? 'bg-gray-800' : 'bg-gray-200',
        ]"
      />
      <div class="flex gap-2">
        <div
          v-for="i in 4"
          :key="i"
          :class="[
            'h-8 w-24 animate-pulse rounded-lg',
            darkMode ? 'bg-gray-800' : 'bg-gray-200',
          ]"
        />
      </div>
    </div>

    <!-- Board skeleton -->
    <div
      :class="[
        'flex-1 p-6',
        darkMode ? 'bg-gray-950' : 'bg-gray-100',
      ]"
    >
      <div
        class="grid h-full gap-4"
        :style="{
          gridTemplateColumns: `repeat(${columnCount}, minmax(280px, 1fr))`,
        }"
      >
        <div v-for="col in columnCount" :key="col" class="space-y-4">
          <!-- Column header -->
          <div
            :class="[
              'flex items-center justify-between rounded-lg px-4 py-3',
              darkMode ? 'bg-gray-800' : 'bg-gray-100',
            ]"
          >
            <div
              :class="[
                'h-5 w-24 animate-pulse rounded',
                darkMode ? 'bg-gray-700' : 'bg-gray-300',
              ]"
            />
            <div
              :class="[
                'h-6 w-6 animate-pulse rounded-full',
                darkMode ? 'bg-gray-700' : 'bg-gray-300',
              ]"
            />
          </div>

          <!-- Card skeletons -->
          <div
            v-for="card in 3"
            :key="card"
            :class="[
              'rounded-xl p-4 space-y-2',
              darkMode ? 'bg-gray-800' : 'bg-white',
            ]"
          >
            <div
              :class="[
                'h-6 w-24 animate-pulse rounded',
                darkMode ? 'bg-gray-700' : 'bg-gray-200',
              ]"
            />
            <div
              :class="[
                'h-4 w-32 animate-pulse rounded',
                darkMode ? 'bg-gray-700' : 'bg-gray-200',
              ]"
            />
            <div
              :class="[
                'h-3 w-20 animate-pulse rounded',
                darkMode ? 'bg-gray-700' : 'bg-gray-200',
              ]"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
