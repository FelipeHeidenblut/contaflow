<script setup lang="ts">
defineProps<{ name: string }>()
</script>

<template>
  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
    <path
      v-if="name === 'home'"
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="1.9"
      d="M3 11.5 12 4l9 7.5M5.5 10v9.5h5v-5h3v5h5V10"
    />
    <path
      v-else-if="name === 'users'"
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="1.9"
      d="M16 20v-1.5a4.5 4.5 0 0 0-4.5-4.5h-4A4.5 4.5 0 0 0 3 18.5V20m6.5-9a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Zm7-1a3 3 0 1 0 0-6m1 16v-1.5a4.5 4.5 0 0 0-3-4.24"
    />
    <path
      v-else-if="name === 'clock'"
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="1.9"
      d="M12 7v5l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
    />
    <path
      v-else-if="name === 'calendar'"
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="1.9"
      d="M7 3v3m10-3v3M4 9h16M5 5h14a1 1 0 0 1 1 1v14H4V6a1 1 0 0 1 1-1Z"
    />
    <path
      v-else-if="name === 'folder'"
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="1.9"
      d="M3.5 7.5v11h17v-10h-9l-2-3h-6v2Z"
    />
    <path
      v-else-if="name === 'team'"
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="1.9"
      d="M8.5 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm7-1a2.5 2.5 0 1 0 0-5m-13 14v-1a5 5 0 0 1 10 0v1h-10Zm11 0v-1a5 5 0 0 0-2.1-4.08"
    />
    <path
      v-else-if="name === 'card'"
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="1.9"
      d="M3.5 7h17v11h-17V7Zm0 4h17M7 15h3"
    />
    <path
      v-else-if="name === 'reports'"
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="1.9"
      d="M5 20V10m7 10V4m7 16v-7M3 20h18"
    />
  </svg>
</template>
