import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { apiClient } from '../utilidades/apiClient'

// Tipos
interface Usuario {
  id: string
  email: string
  nombres: string
  apellidos: string
  organizacion: {
    id: string
    nombre: string
    nivel_suscripcion: string
    sector?: string
    tamaño?: string
  }
  rol: {
    id: string
    nombre: string
    nombre_mostrar: string
  }
  mfa_habilitado?: boolean
  estado_cuenta?: string
  fecha_ultimo_acceso?: string | null
}

interface LoginData {
  email: string
  password: string
}

interface AuthContextType {
  usuario: Usuario | null
  token: string | null
  refreshToken: string | null
  login: (data: LoginData) => Promise<void>
  logout: () => void
  refreshAuthToken: () => Promise<boolean>
  loading: boolean
  error: string | null
  isTokenExpired: boolean
  isAdmin: () => boolean
}

// Contexto
const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Provider
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [refreshToken, setRefreshToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isTokenExpired, setIsTokenExpired] = useState(false)
  const navigate = useNavigate()

  // Cargar tokens del localStorage al inicializar
  useEffect(() => {
    const savedToken = localStorage.getItem('c4a_token')
    const savedRefreshToken = localStorage.getItem('c4a_refresh_token')
    
    if (savedToken && savedRefreshToken) {
      setToken(savedToken)
      setRefreshToken(savedRefreshToken)
      // Verificar si el token es válido
      verificarToken(savedToken)
    }
  }, [])

  // Configurar interceptor de axios para incluir token y manejar renovación automática
  useEffect(() => {
    if (token) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete apiClient.defaults.headers.common['Authorization']
    }
  }, [token])

  // Interceptor para manejar errores 401 y renovar tokens automáticamente
  useEffect(() => {
    const interceptor = apiClient.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true
          
          // Intentar renovar el token
          const success = await refreshAuthToken()
          if (success) {
            // Reintentar la petición original con el nuevo token
            originalRequest.headers['Authorization'] = `Bearer ${token}`
            return apiClient(originalRequest)
          } else {
            // Si no se puede renovar, hacer logout
            logout()
            return Promise.reject(error)
          }
        }
        
        return Promise.reject(error)
      }
    )

    return () => {
      apiClient.interceptors.response.eject(interceptor)
    }
  }, [token, refreshToken])

  const verificarToken = async (tokenToVerify: string) => {
    try {
      setLoading(true)
      setIsTokenExpired(false)
      
      const response = await apiClient.get('/api/v1/auth/mi-perfil', {
        headers: { Authorization: `Bearer ${tokenToVerify}` }
      })
      
      setUsuario(response.data)
      setError(null)
    } catch (err: any) {
      // Token inválido o expirado
      if (err.response?.status === 401) {
        setIsTokenExpired(true)
        // Intentar renovar con refresh token
        const success = await refreshAuthToken()
        if (!success) {
          // Si no se puede renovar, limpiar todo
          localStorage.removeItem('c4a_token')
          localStorage.removeItem('c4a_refresh_token')
          setToken(null)
          setRefreshToken(null)
          setUsuario(null)
        }
      } else {
        // Otro tipo de error
        localStorage.removeItem('c4a_token')
        localStorage.removeItem('c4a_refresh_token')
        setToken(null)
        setRefreshToken(null)
        setUsuario(null)
      }
    } finally {
      setLoading(false)
    }
  }

  const login = async (data: LoginData) => {
    try {
      setLoading(true)
      setError(null)
      setIsTokenExpired(false)

      const response = await apiClient.post('/api/v1/auth/iniciar-sesion', data)
      const { access_token, refresh_token, usuario: usuarioData } = response.data

      // Guardar tokens
      localStorage.setItem('c4a_token', access_token)
      localStorage.setItem('c4a_refresh_token', refresh_token)
      setToken(access_token)
      setRefreshToken(refresh_token)
      setUsuario(usuarioData)

      toast.success(`¡Bienvenido, ${usuarioData.nombres}!`)
      
      // Redirigir según el nivel de suscripción del usuario
      const nivelSuscripcion = usuarioData.organizacion?.nivel_suscripcion
      
      if (usuarioData.rol?.nombre === 'admin_sistema' || usuarioData.rol?.nombre === 'admin_empresa') {
        navigate('/admin/dashboard')
      } else {
        // Redirigir según el nivel de suscripción
        switch (nivelSuscripcion) {
          case 'gratuito':
            navigate('/app/plan-gratuito')
            break
          case 'pro':
            navigate('/app/plan-pro')
            break
          case 'empresarial':
            navigate('/app/plan-empresarial')
            break
          default:
            navigate('/app/dashboard')
        }
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.response?.data?.mensaje || 'Error al iniciar sesión'
      setError(errorMessage)
      toast.error(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const refreshAuthToken = async (): Promise<boolean> => {
    if (!refreshToken) {
      return false
    }

    try {
      const response = await apiClient.post('/api/v1/auth/renovar-token', {
        refresh_token: refreshToken
      })

      const { access_token } = response.data
      
      // Actualizar token
      localStorage.setItem('c4a_token', access_token)
      setToken(access_token)
      setIsTokenExpired(false)
      
      return true
    } catch (err) {
      // Refresh token inválido o expirado
      return false
    }
  }

  const logout = async () => {
    try {
      // Intentar cerrar sesión en el servidor
      if (token) {
        await apiClient.post('/api/v1/auth/cerrar-sesion')
      }
    } catch (err) {
        console.error('Error cerrando sesión en servidor:', err)
    } finally {
      // Limpiar estado local siempre
      localStorage.removeItem('c4a_token')
      localStorage.removeItem('c4a_refresh_token')
      setToken(null)
      setRefreshToken(null)
      setUsuario(null)
      setError(null)
      setIsTokenExpired(false)
      
      // Limpiar headers de axios
      delete apiClient.defaults.headers.common['Authorization']
      
      toast.success('Sesión cerrada exitosamente')
      navigate('/')
    }
  }

  const isAdmin = (): boolean => {
    const isAdminUser = usuario?.rol?.nombre === 'admin_sistema' || usuario?.rol?.nombre === 'admin_empresa'
    return isAdminUser
  }

  const value: AuthContextType = {
    usuario,
    token,
    refreshToken,
    login,
    logout,
    refreshAuthToken,
    loading,
    error,
    isTokenExpired,
    isAdmin
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook personalizado
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider')
  }
  return context
}