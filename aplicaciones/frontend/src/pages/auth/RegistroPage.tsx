import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Shield, Mail, Lock, Eye, EyeOff, User, Building, ArrowLeft } from 'lucide-react'
import { toast } from 'sonner'
import { apiClient } from '../../utilidades/apiClient'

export const RegistroPage: React.FC = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    nombres: '',
    apellidos: '',
    nombre_organizacion: '',
    sector: '',
    tamaño: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validaciones básicas
    if (!formData.email || !formData.password || !formData.nombres || !formData.apellidos || !formData.nombre_organizacion) {
      toast.error('Por favor complete todos los campos obligatorios')
      return
    }

    if (formData.password !== formData.confirmPassword) {
      toast.error('Las contraseñas no coinciden')
      return
    }

    if (formData.password.length < 6) {
      toast.error('La contraseña debe tener al menos 6 caracteres')
      return
    }

    try {
      setLoading(true)
      
      const response = await apiClient.post('/api/v1/auth/registro', {
        email: formData.email,
        password: formData.password,
        nombres: formData.nombres,
        apellidos: formData.apellidos,
        nombre_organizacion: formData.nombre_organizacion,
        sector: formData.sector || undefined,
        tamaño: formData.tamaño || undefined
      })

      // Guardar token y datos del usuario
      localStorage.setItem('c4a_token', response.data.access_token)
      
      toast.success('¡Cuenta creada exitosamente!')
      navigate('/dashboard')
      
    } catch (error: any) {
      console.error('Error en registro:', error)
      const errorMessage = error.response?.data?.detail || 'Error al crear la cuenta'
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
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

        {/* Formulario de registro */}
        <Card className="shadow-xl">
          <CardHeader className="space-y-1">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl text-center">Crear Cuenta</CardTitle>
                <CardDescription className="text-center">
                  Complete la información para crear su cuenta
                </CardDescription>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/login')}
                className="text-gray-500 hover:text-gray-700"
              >
                <ArrowLeft className="w-4 h-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Información personal */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="nombres" className="text-sm font-medium">
                    Nombres *
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="nombres"
                      name="nombres"
                      type="text"
                      placeholder="Juan"
                      value={formData.nombres}
                      onChange={handleInputChange}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <label htmlFor="apellidos" className="text-sm font-medium">
                    Apellidos *
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="apellidos"
                      name="apellidos"
                      type="text"
                      placeholder="Pérez"
                      value={formData.apellidos}
                      onChange={handleInputChange}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Email */}
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Correo electrónico *
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
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

              {/* Contraseñas */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="password" className="text-sm font-medium">
                    Contraseña *
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={handleInputChange}
                      className="pl-10 pr-10"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
                <div className="space-y-2">
                  <label htmlFor="confirmPassword" className="text-sm font-medium">
                    Confirmar *
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      placeholder="••••••••"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      className="pl-10 pr-10"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                    >
                      {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </div>

              {/* Información de la organización */}
              <div className="space-y-2">
                <label htmlFor="nombre_organizacion" className="text-sm font-medium">
                  Nombre de la organización *
                </label>
                <div className="relative">
                  <Building className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="nombre_organizacion"
                    name="nombre_organizacion"
                    type="text"
                    placeholder="Mi Empresa S.A."
                    value={formData.nombre_organizacion}
                    onChange={handleInputChange}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              {/* Sector y tamaño */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="sector" className="text-sm font-medium">
                    Sector
                  </label>
                  <select
                    id="sector"
                    name="sector"
                    value={formData.sector}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-c4a-blue-500"
                  >
                    <option value="">Seleccionar sector</option>
                    <option value="tecnologia">Tecnología</option>
                    <option value="financiero">Financiero</option>
                    <option value="salud">Salud</option>
                    <option value="retail">Retail</option>
                    <option value="gobierno">Gobierno</option>
                    <option value="educacion">Educación</option>
                    <option value="manufactura">Manufactura</option>
                    <option value="servicios">Servicios</option>
                    <option value="otro">Otro</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label htmlFor="tamaño" className="text-sm font-medium">
                    Tamaño
                  </label>
                  <select
                    id="tamaño"
                    name="tamaño"
                    value={formData.tamaño}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-c4a-blue-500"
                  >
                    <option value="">Seleccionar tamaño</option>
                    <option value="micro">Micro (&lt; 10 empleados)</option>
                    <option value="pequeña">Pequeña (10-49 empleados)</option>
                    <option value="mediana">Mediana (50-199 empleados)</option>
                    <option value="grande">Grande (200+ empleados)</option>
                  </select>
                </div>
              </div>

              {/* Botón de registro */}
              <Button
                type="submit"
                className="w-full bg-c4a-blue-600 hover:bg-c4a-blue-700"
                disabled={loading}
              >
                {loading ? 'Creando cuenta...' : 'Crear Cuenta'}
              </Button>
            </form>

            {/* Enlaces */}
            <div className="mt-6 text-center space-y-2">
              <p className="text-sm text-gray-600">
                ¿Ya tiene una cuenta?{' '}
                <button
                  type="button"
                  onClick={() => navigate('/login')}
                  className="text-c4a-blue-600 hover:text-c4a-blue-700 font-medium"
                >
                  Iniciar sesión
                </button>
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="mt-8 text-center text-white text-sm">
          
        </div>
      </div>
    </div>
  )
}
