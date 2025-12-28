import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '@/lib/api'

export interface User {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  organization_id: string
  location_id: string | null
  role: 'owner' | 'admin' | 'staff'
  created_at: string
}

interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value)
  const isManager = computed(() => user.value?.role === 'owner' || user.value?.role === 'admin')
  const isOwner = computed(() => user.value?.role === 'owner')

  function setTokens(tokens: TokenResponse) {
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
  }

  function clearTokens() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function register(email: string, password: string, fullName?: string) {
    const response = await api.post<TokenResponse>('/api/v1/auth/register', {
      email,
      password,
      full_name: fullName,
    })
    setTokens(response.data)
    await fetchUser()
    return response.data
  }

  async function login(email: string, password: string) {
    const response = await api.post<TokenResponse>('/api/v1/auth/login', {
      email,
      password,
    })
    setTokens(response.data)
    await fetchUser()
    return response.data
  }

  async function refresh(): Promise<boolean> {
    if (!refreshToken.value) return false

    try {
      const response = await api.post<TokenResponse>('/api/v1/auth/refresh', {
        refresh_token: refreshToken.value,
      })
      setTokens(response.data)
      return true
    } catch {
      clearTokens()
      return false
    }
  }

  async function fetchUser() {
    try {
      const response = await api.get<User>('/api/v1/auth/me')
      user.value = response.data
    } catch {
      clearTokens()
    }
  }

  function logout() {
    clearTokens()
  }

  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated,
    isManager,
    isOwner,
    register,
    login,
    refresh,
    fetchUser,
    logout,
  }
})
