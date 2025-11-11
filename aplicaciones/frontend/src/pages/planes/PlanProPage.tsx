import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { api } from '../../utilidades/apiClient'
import { toast } from 'sonner'

const PlanProPage: React.FC = () => {
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
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Plan Pro
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Para empresas en crecimiento que necesitan evaluaciones más profundas.
          </p>
        </div>
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-xl p-8">
            <h2 className="text-2xl font-bold text-purple-600 mb-4">
              ¡Excelente elección, {usuario?.nombres}!
            </h2>
            <p className="text-gray-700 mb-6">
              Tienes acceso a todas las funciones Pro de {usuario?.organizacion?.nombre}.
            </p>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <span className="text-green-500">✓</span>
                <span>Evaluación completa NIST CSF 2.0</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-green-500">✓</span>
                <span>Cuestionarios COBIT 2019</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-green-500">✓</span>
                <span>10 evaluaciones por mes</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-green-500">✓</span>
                <span>Reportes avanzados con gráficos</span>
              </div>
            </div>
            <div className="mt-8 flex gap-4">
        <button
          className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700"
          onClick={handleComenzarEvaluacion}
        >
          Comenzar Evaluación
        </button>
              <button 
                className="border border-purple-600 text-purple-600 px-6 py-3 rounded-lg hover:bg-purple-50"
                onClick={() => navigate('/app/usuarios')}
              >
                Gestionar Usuarios
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PlanProPage
