import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { CuestionarioNivel } from '../CuestionarioNivel'
import { NivelSuscripcion } from '../../../tipos'

// Mock de la API
vi.mock('../../../utilidades/apiClient', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

// Mock de los componentes hijos
vi.mock('../QuestionCard', () => ({
  QuestionCard: ({ pregunta, onAnswer, onNext, onPrevious }: any) => (
    <div data-testid="question-card">
      <h3>{pregunta?.texto}</h3>
      <button onClick={() => onAnswer(pregunta?.id, 'test-answer')}>
        Responder
      </button>
      <button onClick={onNext}>Siguiente</button>
      <button onClick={onPrevious}>Anterior</button>
    </div>
  )
}))

vi.mock('../EvaluationProgress', () => ({
  EvaluationProgress: ({ currentQuestion, totalQuestions }: any) => (
    <div data-testid="evaluation-progress">
      Progreso: {currentQuestion}/{totalQuestions}
    </div>
  )
}))

describe('CuestionarioNivel', () => {
  const mockProps = {
    nivel: 'gratuito' as NivelSuscripcion,
    idEvaluacion: 'test-eval-id',
    onCompletar: vi.fn(),
    onAutoGuardar: vi.fn()
  }

  const mockEvaluacion = {
    id: 'test-eval-id',
    nombre: 'Evaluación Test',
    estado: 'EN_PROGRESO',
    total_preguntas: 10,
    preguntas_completadas: 0
  }

  const mockPreguntas = [
    {
      id: 'pregunta-1',
      texto: '¿Tienes políticas de seguridad?',
      tipo_respuesta: 'multiple_choice',
      opciones: ['Sí', 'No', 'Parcialmente']
    },
    {
      id: 'pregunta-2',
      texto: '¿Realizas backups regulares?',
      tipo_respuesta: 'multiple_choice',
      opciones: ['Sí', 'No', 'Parcialmente']
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock de las llamadas a la API
    const { api } = require('../../../utilidades/apiClient')
    api.get.mockImplementation((url: string) => {
      if (url.includes('/evaluaciones/')) {
        return Promise.resolve(mockEvaluacion)
      }
      if (url.includes('/cuestionarios/nivel/')) {
        return Promise.resolve({ preguntas: mockPreguntas })
      }
      return Promise.resolve({})
    })
    
    api.post.mockResolvedValue({})
  })

  it('debe renderizar correctamente para nivel gratuito', async () => {
    render(<CuestionarioNivel {...mockProps} />)
    
    await waitFor(() => {
      expect(screen.getByText('Evaluación de Ciberseguridad - GRATUITO')).toBeInTheDocument()
    })
    
    expect(screen.getByText('Evaluación Test')).toBeInTheDocument()
    expect(screen.getByText('Tiempo estimado: 5 min')).toBeInTheDocument()
    expect(screen.getByText('Preguntas: 2')).toBeInTheDocument()
  })

  it('debe mostrar alerta específica para nivel gratuito', async () => {
    render(<CuestionarioNivel {...mockProps} />)
    
    await waitFor(() => {
      expect(screen.getByText(/Evaluación Básica/)).toBeInTheDocument()
    })
  })

  it('debe mostrar alerta específica para nivel pro', async () => {
    render(<CuestionarioNivel {...mockProps} nivel="pro" />)
    
    await waitFor(() => {
      expect(screen.getByText(/Plan Pro/)).toBeInTheDocument()
    })
  })

  it('debe mostrar alerta específica para nivel empresarial', async () => {
    render(<CuestionarioNivel {...mockProps} nivel="empresarial" />)
    
    await waitFor(() => {
      expect(screen.getByText(/Plan Empresarial/)).toBeInTheDocument()
    })
  })

  it('debe mostrar progreso solo para niveles pro y empresarial', async () => {
    const { rerender } = render(<CuestionarioNivel {...mockProps} nivel="gratuito" />)
    
    await waitFor(() => {
      expect(screen.queryByTestId('evaluation-progress')).not.toBeInTheDocument()
    })

    rerender(<CuestionarioNivel {...mockProps} nivel="pro" />)
    
    await waitFor(() => {
      expect(screen.getByTestId('evaluation-progress')).toBeInTheDocument()
    })
  })

  it('debe manejar errores de carga correctamente', async () => {
    const { api } = require('../../../utilidades/apiClient')
    api.get.mockRejectedValue(new Error('Error de red'))
    
    render(<CuestionarioNivel {...mockProps} />)
    
    await waitFor(() => {
      expect(screen.getByText(/No se pudo cargar el cuestionario/)).toBeInTheDocument()
    })
  })

  it('debe mostrar estado de carga inicial', () => {
    const { api } = require('../../../utilidades/apiClient')
    api.get.mockImplementation(() => new Promise(() => {})) // Never resolves
    
    render(<CuestionarioNivel {...mockProps} />)
    
    expect(screen.getByText('Cargando cuestionario...')).toBeInTheDocument()
  })

  it('debe mostrar información correcta por nivel', async () => {
    const { rerender } = render(<CuestionarioNivel {...mockProps} nivel="gratuito" />)
    
    await waitFor(() => {
      expect(screen.getByText('Tiempo estimado: 5 min')).toBeInTheDocument()
      expect(screen.getByText('Recomendaciones: 3')).toBeInTheDocument()
    })

    rerender(<CuestionarioNivel {...mockProps} nivel="pro" />)
    
    await waitFor(() => {
      expect(screen.getByText('Tiempo estimado: 20 min')).toBeInTheDocument()
      expect(screen.getByText('Recomendaciones: 15')).toBeInTheDocument()
    })

    rerender(<CuestionarioNivel {...mockProps} nivel="empresarial" />)
    
    await waitFor(() => {
      expect(screen.getByText('Tiempo estimado: 45 min')).toBeInTheDocument()
      expect(screen.getByText('Recomendaciones: 50')).toBeInTheDocument()
    })
  })
})

