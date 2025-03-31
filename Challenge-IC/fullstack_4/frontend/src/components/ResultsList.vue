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
      <ul v-else class="results-list">
        <li v-for="(item, index) in results" :key="index">
          {{ item }}
        </li>
      </ul>
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

.results-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.results-list li {
  border: 1px solid #eee;
  padding: 10px;
  margin-bottom: 5px;
  background-color: #fff;
}
</style>