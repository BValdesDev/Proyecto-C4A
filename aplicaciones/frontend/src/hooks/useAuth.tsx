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
  login: (data: LoginData) => Promise<void>
  logout: () => void
  loading: boolean
  error: string | null
}

// Contexto
const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Provider
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  // Cargar token del localStorage al inicializar
  useEffect(() => {
    const savedToken = localStorage.getItem('c4a_token')
    if (savedToken) {
      setToken(savedToken)
      // Verificar si el token es válido
      verificarToken(savedToken)
    }
  }, [])

  // Configurar interceptor de axios para incluir token
  useEffect(() => {
    if (token) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete apiClient.defaults.headers.common['Authorization']
    }
  }, [token])

  const verificarToken = async (tokenToVerify: string) => {
    try {
      setLoading(true)
      const response = await apiClient.get('/api/v1/auth/mi-perfil', {
        headers: { Authorization: `Bearer ${tokenToVerify}` }
      })
      
      setUsuario(response.data)
      setError(null)
    } catch (err) {
      // Token inválido, limpiar
      localStorage.removeItem('c4a_token')
      setToken(null)
      setUsuario(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (data: LoginData) => {
    try {
      setLoading(true)
      setError(null)

      const response = await apiClient.post('/api/v1/auth/iniciar-sesion', data)
      const { access_token, usuario: usuarioData } = response.data

      // Guardar token
      localStorage.setItem('c4a_token', access_token)
      setToken(access_token)
      setUsuario(usuarioData)

      toast.success(`¡Bienvenido, ${usuarioData.nombres}!`)
      
      // Redirigir al dashboard
      navigate('/app/dashboard')
    } catch (err: any) {
      const errorMessage = err.response?.data?.mensaje || 'Error al iniciar sesión'
      setError(errorMessage)
      toast.error(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    // Limpiar estado
    localStorage.removeItem('c4a_token')
    setToken(null)
    setUsuario(null)
    setError(null)
    
    // Limpiar headers de axios
    delete apiClient.defaults.headers.common['Authorization']
    
    toast.success('Sesión cerrada exitosamente')
    navigate('/')
  }

  const value: AuthContextType = {
    usuario,
    token,
    login,
    logout,
    loading,
    error
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