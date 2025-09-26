import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Shield, Mail, Lock, Eye, EyeOff } from 'lucide-react'
import { toast } from 'sonner'

export const LoginPage: React.FC = () => {
  const { login, loading } = useAuth()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.email || !formData.password) {
      toast.error('Por favor complete todos los campos')
      return
    }

    try {
      await login(formData)
    } catch (error) {
      // El error ya se maneja en el hook useAuth
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleGoogleLogin = async () => {
    try {
      setGoogleLoading(true)
      
      // Simular login con Google (en producción esto se conectaría con Google OAuth)
      toast.info('Login con Google en desarrollo')
      
      // Aquí se implementaría la lógica real de Google OAuth
      // const response = await fetch('/api/v1/auth/google', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ provider: 'google' })
      // })
      
    } catch (error) {
      toast.error('Error al iniciar sesión con Google')
    } finally {
      setGoogleLoading(false)
    }
  }

  return (
    <div className="min-h-screen c4a-gradient flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo y título */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-full mb-4">
            <Shield className="w-8 h-8 text-c4a-blue-600" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">C4A SaaS</h1>
          <p className="text-c4a-blue-100">Evaluación de Ciberseguridad para PyMEs</p>
        </div>

        {/* Formulario de login */}
        <Card className="bg-white/95 backdrop-blur-sm">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Iniciar Sesión</CardTitle>
            <CardDescription>
              Ingrese sus credenciales para acceder a la plataforma
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Botón de Google */}
            <div className="mb-6">
              <Button
                type="button"
                variant="outline"
                className="w-full flex items-center justify-center space-x-2 border-gray-300 hover:bg-gray-50"
                onClick={handleGoogleLogin}
                disabled={googleLoading}
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                <span>{googleLoading ? 'Iniciando sesión...' : 'Continuar con Google'}</span>
              </Button>
            </div>

            {/* Separador */}
            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white px-2 text-muted-foreground">O</span>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email */}
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Correo electrónico
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="usuario@empresa.cl"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              {/* Contraseña */}
              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium">
                  Contraseña
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="pl-10 pr-10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Botón de login */}
              <Button
                type="submit"
                className="w-full c4a-button-primary"
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="loading-spinner w-4 h-4"></div>
                    <span>Iniciando sesión...</span>
                  </div>
                ) : (
                  'Iniciar Sesión'
                )}
              </Button>
            </form>

            {/* Enlaces adicionales */}
            <div className="mt-6 text-center space-y-2">
              <button
                type="button"
                onClick={() => toast.info('Funcionalidad en desarrollo')}
                className="text-sm text-c4a-blue-600 hover:text-c4a-blue-700 hover:underline"
              >
                ¿Olvidó su contraseña?
              </button>
              <div className="text-sm text-muted-foreground">
                ¿No tiene una cuenta?{' '}
                <button
                  type="button"
                  onClick={() => navigate('/registro')}
                  className="text-c4a-blue-600 hover:text-c4a-blue-700 hover:underline"
                >
                  Crear cuenta
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Información adicional */}
        <div className="mt-8 text-center text-c4a-blue-100 text-sm">
          <p>Plataforma segura para evaluaciones de ciberseguridad</p>
          <p className="mt-1">Cumplimiento con estándares NIST CSF 2.0 y COBIT 2019</p>
        </div>
      </div>
    </div>
  )
}

