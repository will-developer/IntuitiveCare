<script setup lang="ts">
defineProps<{
  results: any[]
  isLoading: boolean
  error: string | null
}>()
</script>

<template>
  <div class="results-display">
    <div v-if="isLoading" class="loading">
      Loading...
    </div>
    <div v-else-if="error" class="error-message">
      <p><strong>Error:</strong> {{ error }}</p>
    </div>
    <div v-else class="results-container">
      <p v-if="!results.length">Enter a search term to see results.</p>
      <pre v-else>{{ JSON.stringify(results, null, 2) }}</pre>
    </div>
  </div>
</template>

<style scoped>
.loading {
  text-align: center;
  padding: 20px;
  color: #555;
  font-style: italic;
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #e57373;
  padding: 15px;
  margin-top: 15px;
  border-radius: 4px;
  text-align: center;
}

.results-container {
  margin-top: 20px;
}

pre {
  background-color: #f4f4f4;
  border: 1px solid #ddd;
  padding: 10px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>