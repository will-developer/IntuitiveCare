<script setup lang="ts">
import SearchBar from './components/SearchBar.vue'
import ResultsList from './components/ResultsList.vue'
import { useOperatorSearch } from './hooks/useOperatorSearch'

const { searchQuery, searchResults, isLoading, error } = useOperatorSearch()
</script>

<template>
  <div id="app-container">
    <h1>ANS Operator Search</h1>
    <SearchBar v-model="searchQuery" />
    <ResultsList
      :results="searchResults"
      :is-loading="isLoading"
      :error="error"
      :search-query="searchQuery"
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