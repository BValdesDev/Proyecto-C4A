import axios from 'axios'

// Configuración base del cliente API
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para requests
apiClient.interceptors.request.use(
  (config) => {
    // Agregar token de autenticación
    const token = localStorage.getItem('c4a_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Agregar timestamp para evitar caché
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now(),
      }
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para responses
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Si es error 401 y no es un retry, intentar renovar token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('c4a_refresh_token')
        if (refreshToken) {
          const response = await axios.post(
            `${apiClient.defaults.baseURL}/api/v1/auth/renovar-token`,
            { refresh_token: refreshToken }
          )

          const { access_token } = response.data
          localStorage.setItem('c4a_token', access_token)
          
          // Reintentar request original
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // Si falla la renovación, limpiar tokens y redirigir
        localStorage.removeItem('c4a_token')
        localStorage.removeItem('c4a_refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Funciones helper para tipos de requests
export const api = {
  get: <T = any>(url: string, config?: any) => 
    apiClient.get<T>(url, config).then(res => res.data),
  
  post: <T = any>(url: string, data?: any, config?: any) => 
    apiClient.post<T>(url, data, config).then(res => res.data),
  
  put: <T = any>(url: string, data?: any, config?: any) => 
    apiClient.put<T>(url, data, config).then(res => res.data),
  
  delete: <T = any>(url: string, config?: any) => 
    apiClient.delete<T>(url, config).then(res => res.data),
  
  patch: <T = any>(url: string, data?: any, config?: any) => 
    apiClient.patch<T>(url, data, config).then(res => res.data),
}

export default apiClient
