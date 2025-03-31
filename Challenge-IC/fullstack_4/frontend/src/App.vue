<script setup lang="ts">
import { ref, watch } from 'vue'
import SearchBar from './components/SearchBar.vue'
import ResultsList from './components/ResultsList.vue'

const searchQuery = ref('')
const searchResults = ref<any[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)

const API_URL = 'http://127.0.0.1:5000/api/search'

async function fetchResults() {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    error.value = null
    return
  }

  isLoading.value = true
  error.value = null
  searchResults.value = []

  try {
    const url = `${API_URL}?q=${encodeURIComponent(searchQuery.value.trim())}`
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    searchResults.value = data

  } catch (err: any) {
    console.error("Error fetching data:", err)
    error.value = err.message || 'Failed to fetch data.'
    searchResults.value = []
  } finally {
    isLoading.value = false
  }
}

watch(searchQuery, () => {
  fetchResults()
})
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