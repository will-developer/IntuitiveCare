import { ref, watch } from 'vue'

interface OperatorResult {
  Registro_ANS: string | number
  CNPJ: string
  Razao_Social: string
  Nome_Fantasia?: string
  Cidade?: string
  UF?: string
  [key: string]: any
}

const API_URL = 'http://127.0.0.1:5000/api/search'

export function useOperatorSearch() {
  const searchQuery = ref('')
  const searchResults = ref<OperatorResult[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const debounceTimer = ref<number | null>(null)

  async function fetchResults() {
    const query = searchQuery.value.trim()
    if (!query) {
      searchResults.value = []
      error.value = null
      isLoading.value = false
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const url = `${API_URL}?q=${encodeURIComponent(query)}`
      const response = await fetch(url)

      if (!response.ok) {
        let errorMsg = `HTTP error! status: ${response.status}`
        try {
          const errorData = await response.json()
          errorMsg = errorData.error || errorMsg
        } catch (parseError) {}
        throw new Error(errorMsg)
      }

      const data = await response.json()
      searchResults.value = data as OperatorResult[]
    } catch (err: any) {
      console.error('Error fetching data:', err)
      error.value = err.message || 'Failed to fetch data.'
      searchResults.value = []
    } finally {
      isLoading.value = false
    }
  }

  watch(searchQuery, (newValue) => {
    if (debounceTimer.value) {
      clearTimeout(debounceTimer.value)
    }
    debounceTimer.value = window.setTimeout(() => {
      fetchResults()
    }, 500)
  })

  return {
    searchQuery,
    searchResults,
    isLoading,
    error,
  }
}
