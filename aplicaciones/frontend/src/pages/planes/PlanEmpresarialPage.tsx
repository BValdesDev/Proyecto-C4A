import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { api } from '../../utilidades/apiClient'
import { toast } from 'sonner'

const PlanEmpresarialPage: React.FC = () => {
  const { usuario } = useAuth()
  const navigate = useNavigate()

  const handleComenzarEvaluacion = async () => {
    try {
      console.log('🔄 Obteniendo cuestionario principal...')
      console.log('Token actual:', localStorage.getItem('c4a_token'))
      
      // Obtener el cuestionario principal según el nivel de suscripción
      const response = await api.get('/api/v1/cuestionarios/principal')
      console.log('✅ Respuesta del servidor:', response)
      
      // Navegar directamente a las preguntas del cuestionario
      const ruta = `/app/diagnosticos/${response.id}/responder`
      console.log('🧭 Navegando a:', ruta)
      navigate(ruta)
      
    } catch (error: any) {
      console.error('❌ Error al obtener cuestionario principal:', error)
      console.error('Error response:', error.response)
      console.error('Error message:', error.message)
      console.error('Error details:', error.response?.data)
      toast.error('Error al cargar el cuestionario. Inténtalo de nuevo.')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Plan Empresarial
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            La solución completa para grandes empresas que requieren evaluaciones exhaustivas.
          </p>
        </div>
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-xl p-8">
            <h2 className="text-2xl font-bold text-amber-600 mb-4">
              ¡Acceso completo, {usuario?.nombres}!
            </h2>
            <p className="text-gray-700 mb-6">
              Tienes acceso a todas las funciones empresariales de {usuario?.organizacion?.nombre}.
            </p>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <span className="text-green-500">✓</span>
                <span>Evaluaciones ilimitadas</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-green-500">✓</span>
                <span>Usuarios ilimitados</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-green-500">✓</span>
                <span>Analytics avanzado</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-green-500">✓</span>
                <span>Soporte 24/7</span>
              </div>
            </div>
            <div className="mt-8 flex gap-4">
        <button
          className="bg-amber-600 text-white px-6 py-3 rounded-lg hover:bg-amber-700"
          onClick={handleComenzarEvaluacion}
        >
          Comenzar Evaluación
        </button>
              <button 
                className="border border-amber-600 text-amber-600 px-6 py-3 rounded-lg hover:bg-amber-50"
                onClick={() => navigate('/app/usuarios')}
              >
                Gestionar Equipo
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PlanEmpresarialPage
