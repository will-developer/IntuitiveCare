<script setup lang="ts">
interface OperatorResult {
  Registro_ANS: string | number
  CNPJ: string
  Razao_Social: string
  Nome_Fantasia?: string
  Cidade?: string
  UF?: string
  [key: string]: any
}

defineProps<{
  results: OperatorResult[]
  isLoading: boolean
  error: string | null
  searchQuery: string
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
      <ul v-if="results.length > 0" class="results-list">
        <li v-for="item in results" :key="item.Registro_ANS || item.CNPJ" class="result-item">
          <h2>{{ item.Razao_Social }}</h2>
          <p v-if="item.Nome_Fantasia"><strong>Fantasia:</strong> {{ item.Nome_Fantasia }}</p>
          <p><strong>Registro ANS:</strong> {{ item.Registro_ANS }}</p>
          <p><strong>CNPJ:</strong> {{ item.CNPJ }}</p>
          <p v-if="item.Cidade && item.UF"><strong>Cidade/UF:</strong> {{ item.Cidade }} / {{ item.UF }}</p>
        </li>
      </ul>
      <p v-else-if="searchQuery.trim() && !isLoading">
        No results found for "{{ searchQuery }}".
      </p>
      <p v-else-if="!searchQuery.trim() && !isLoading">
        Enter a search term to see results.
      </p>
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

.result-item {
  background-color: #fff;
  border: 1px solid #eee;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.result-item h2 {
  margin: 0 0 8px 0;
  font-size: 1.2em;
  color: #0056b3;
}

.result-item p {
  margin: 4px 0;
  font-size: 0.95em;
  color: #444;
  line-height: 1.4;
}

.result-item strong {
    color: #333;
    margin-right: 5px;
}
</style>