<script setup lang="ts">
import { ref } from 'vue'
import SearchBar from './components/SearchBar.vue'
import ResultsList from './components/ResultsList.vue'

const searchQuery = ref('')
const searchResults = ref<any[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)
</script>

<template>
  <div id="app-container">
    <h1>ANS Operator Search</h1>
    <SearchBar v-model="searchQuery" />
    <ResultsList
      :results="searchResults"
      :is-loading="isLoading"
      :error="error"
    />
  </div>
</template>

<style scoped>
#app-container {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  color: #2c3e50;
}

h1 {
  text-align: center;
  margin-bottom: 25px;
}
</style>