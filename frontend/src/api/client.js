import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // crawling + AI synthesis can take a while
})

export async function fetchModels() {
  const { data } = await client.get('/api/models')
  return data.models
}

export async function researchCompany(payload) {
  try {
    const { data } = await client.post('/api/research', payload)
    return data
  } catch (err) {
    if (err.response?.data?.error) {
      throw new Error(err.response.data.error)
    }
    if (err.code === 'ECONNABORTED') {
      throw new Error('The request timed out. The site may be slow to crawl — try again.')
    }
    throw new Error('Could not reach the research server. Check your connection and try again.')
  }
}

export default client
