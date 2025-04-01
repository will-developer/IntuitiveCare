<script setup lang="ts">
defineProps<{
  modelValue: string 
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

function handleInput(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="search-container">
    <label for="search-input">Procurar:</label>
    <input
      id="search-input"
      type="text"
      :value="modelValue"
      @input="handleInput"
      placeholder="Digite Razão Social, Fantasia, CNPJ, Cidade.."
      aria-label="Campo de busca de operadoras"
    />
  </div>
</template>

<style scoped>
.search-container {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-container label {
  font-weight: bold;
  color: #555;
}

#search-input {
  flex-grow: 1;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

#search-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}
</style>