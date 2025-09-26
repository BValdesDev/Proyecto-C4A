import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { DashboardNivel } from '../DashboardNivel'
import { NivelSuscripcion } from '../../../tipos'

// Mock de la API
vi.mock('../../../utilidades/apiClient', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

// Mock de los componentes hijos
vi.mock('../QuickActions', () => ({
  QuickActions: ({ nivel }: any) => (
    <div data-testid="quick-actions">
      Acciones rápidas para {nivel}
    </div>
  )
}))

vi.mock('../StatsCard', () => ({
  StatsCard: ({ titulo, valor, icono }: any) => (
    <div data-testid="stats-card">
      {titulo}: {valor}
    </div>
  )
}))

describe('DashboardNivel', () => {
  const mockProps = {
    nivelUsuario: 'gratuito' as NivelSuscripcion,
    organizacionId: 'test-org-id'
  }

  const mockEstadisticas = {
    total_evaluaciones: 5,
    evaluaciones_completadas: 3,
    puntuacion_promedio: 75,
    ultima_evaluacion: '2025-09-23T10:00:00Z'
  }

  const mockBenchmarking = {
    puntuacion_organizacion: 75,
    promedio_sector: 68,
    percentil: 85,
    comparacion_competencia: 72
  }

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock de las llamadas a la API
    const { api } = require('../../../utilidades/apiClient')
    api.get.mockImplementation((url: string) => {
      if (url.includes('/organizaciones/') && url.includes('/estadisticas')) {
        return Promise.resolve(mockEstadisticas)
      }
      if (url.includes('/analytics/benchmarks-industria/')) {
        return Promise.resolve(mockBenchmarking)
      }
      return Promise.resolve({})
    })
  })

  it('debe renderizar correctamente para nivel gratuito', async () => {
    render(<DashboardNivel {...mockProps} />)
    
    await waitFor(() => {
      expect(screen.getByText('Dashboard - GRATUITO')).toBeInTheDocument()
    })
    
    expect(screen.getByText('Estadísticas Básicas')).toBeInTheDocument()
    expect(screen.queryByText('Benchmarking Sectorial')).not.toBeInTheDocument()
    expect(screen.queryByText('Analytics Avanzado')).not.toBeInTheDocument()
  })

  it('debe mostrar benchmarking para nivel pro', async () => {
    render(<DashboardNivel {...mockProps} nivelUsuario="pro" />)
    
    await waitFor(() => {
      expect(screen.getByText('Benchmarking Sectorial')).toBeInTheDocument()
    })
  })

  it('debe mostrar analytics avanzado para nivel empresarial', async () => {
    render(<DashboardNivel {...mockProps} nivelUsuario="empresarial" />)
    
    await waitFor(() => {
      expect(screen.getByText('Analytics Avanzado')).toBeInTheDocument()
    })
  })

  it('debe mostrar estadísticas básicas para todos los niveles', async () => {
    const { rerender } = render(<DashboardNivel {...mockProps} nivelUsuario="gratuito" />)
    
    await waitFor(() => {
      expect(screen.getByText('Estadísticas Básicas')).toBeInTheDocument()
    })

    rerender(<DashboardNivel {...mockProps} nivelUsuario="pro" />)
    
    await waitFor(() => {
      expect(screen.getByText('Estadísticas Básicas')).toBeInTheDocument()
    })

    rerender(<DashboardNivel {...mockProps} nivelUsuario="empresarial" />)
    
    await waitFor(() => {
      expect(screen.getByText('Estadísticas Básicas')).toBeInTheDocument()
    })
  })

  it('debe mostrar acciones rápidas diferenciadas por nivel', async () => {
    const { rerender } = render(<DashboardNivel {...mockProps} nivelUsuario="gratuito" />)
    
    await waitFor(() => {
      expect(screen.getByTestId('quick-actions')).toBeInTheDocument()
      expect(screen.getByText('Acciones rápidas para gratuito')).toBeInTheDocument()
    })

    rerender(<DashboardNivel {...mockProps} nivelUsuario="pro" />)
    
    await waitFor(() => {
      expect(screen.getByText('Acciones rápidas para pro')).toBeInTheDocument()
    })

    rerender(<DashboardNivel {...mockProps} nivelUsuario="empresarial" />)
    
    await waitFor(() => {
      expect(screen.getByText('Acciones rápidas para empresarial')).toBeInTheDocument()
    })
  })

  it('debe manejar errores de carga correctamente', async () => {
    const { api } = require('../../../utilidades/apiClient')
    api.get.mockRejectedValue(new Error('Error de red'))
    
    render(<DashboardNivel {...mockProps} />)
    
    await waitFor(() => {
      expect(screen.getByText(/Error cargando dashboard/)).toBeInTheDocument()
    })
  })

  it('debe mostrar estado de carga inicial', () => {
    const { api } = require('../../../utilidades/apiClient')
    api.get.mockImplementation(() => new Promise(() => {})) // Never resolves
    
    render(<DashboardNivel {...mockProps} />)
    
    expect(screen.getByText('Cargando dashboard...')).toBeInTheDocument()
  })

  it('debe mostrar información específica por nivel', async () => {
    const { rerender } = render(<DashboardNivel {...mockProps} nivelUsuario="gratuito" />)
    
    await waitFor(() => {
      expect(screen.getByText(/Plan Gratuito/)).toBeInTheDocument()
    })

    rerender(<DashboardNivel {...mockProps} nivelUsuario="pro" />)
    
    await waitFor(() => {
      expect(screen.getByText(/Plan Pro/)).toBeInTheDocument()
    })

    rerender(<DashboardNivel {...mockProps} nivelUsuario="empresarial" />)
    
    await waitFor(() => {
      expect(screen.getByText(/Plan Empresarial/)).toBeInTheDocument()
    })
  })
})

