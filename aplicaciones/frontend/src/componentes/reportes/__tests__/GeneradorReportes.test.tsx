import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { GeneradorReportes } from '../GeneradorReportes'
import { NivelSuscripcion } from '../../../tipos'

// Mock de la API
vi.mock('../../../utilidades/apiClient', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

describe('GeneradorReportes', () => {
  const mockProps = {
    nivelUsuario: 'gratuito' as NivelSuscripcion,
    evaluacionId: 'test-eval-id'
  }

  const mockReportes = [
    {
      id: 'reporte-1',
      nombre: 'Reporte Básico',
      tipo: 'pdf',
      fecha_creacion: '2025-09-23T10:00:00Z',
      estado: 'completado'
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock de las llamadas a la API
    const { api } = require('../../../utilidades/apiClient')
    api.get.mockImplementation((url: string) => {
      if (url.includes('/evaluaciones/') && url.includes('/reportes')) {
        return Promise.resolve({ reportes: mockReportes })
      }
      return Promise.resolve({})
    })
    
    api.post.mockResolvedValue({})
  })

  it('debe renderizar correctamente para nivel gratuito', async () => {
    render(<GeneradorReportes {...mockProps} />)
    
    await waitFor(() => {
      expect(screen.getByText('Generador de Reportes - GRATUITO')).toBeInTheDocument()
    })
    
    expect(screen.getByText('Configuración Básica')).toBeInTheDocument()
    expect(screen.queryByText('Configuración Avanzada')).not.toBeInTheDocument()
  })

  it('debe mostrar configuración avanzada para nivel pro', async () => {
    render(<GeneradorReportes {...mockProps} nivelUsuario="pro" />)
    
    await waitFor(() => {
      expect(screen.getByText('Configuración Avanzada')).toBeInTheDocument()
    })
  })

  it('debe mostrar configuración empresarial para nivel empresarial', async () => {
    render(<GeneradorReportes {...mockProps} nivelUsuario="empresarial" />)
    
    await waitFor(() => {
      expect(screen.getByText('Configuración Empresarial')).toBeInTheDocument()
    })
  })

  it('debe mostrar marca de agua para nivel gratuito', async () => {
    render(<GeneradorReportes {...mockProps} nivelUsuario="gratuito" />)
    
    await waitFor(() => {
      expect(screen.getByText(/Marca de agua/)).toBeInTheDocument()
    })
  })

  it('debe permitir exportación múltiple para niveles pro y empresarial', async () => {
    const { rerender } = render(<GeneradorReportes {...mockProps} nivelUsuario="pro" />)
    
    await waitFor(() => {
      expect(screen.getByText('Exportar PDF')).toBeInTheDocument()
      expect(screen.getByText('Exportar Excel')).toBeInTheDocument()
    })

    rerender(<GeneradorReportes {...mockProps} nivelUsuario="empresarial" />)
    
    await waitFor(() => {
      expect(screen.getByText('Exportar PDF')).toBeInTheDocument()
      expect(screen.getByText('Exportar Excel')).toBeInTheDocument()
    })
  })

  it('debe manejar la generación de reportes correctamente', async () => {
    render(<GeneradorReportes {...mockProps} />)
    
    const generarButton = screen.getByText('Generar Reporte')
    fireEvent.click(generarButton)
    
    await waitFor(() => {
      expect(screen.getByText('Generando reporte...')).toBeInTheDocument()
    })
  })

  it('debe mostrar historial de reportes', async () => {
    render(<GeneradorReportes {...mockProps} />)
    
    await waitFor(() => {
      expect(screen.getByText('Historial de Reportes')).toBeInTheDocument()
      expect(screen.getByText('Reporte Básico')).toBeInTheDocument()
    })
  })

  it('debe manejar errores de generación correctamente', async () => {
    const { api } = require('../../../utilidades/apiClient')
    api.post.mockRejectedValue(new Error('Error generando reporte'))
    
    render(<GeneradorReportes {...mockProps} />)
    
    const generarButton = screen.getByText('Generar Reporte')
    fireEvent.click(generarButton)
    
    await waitFor(() => {
      expect(screen.getByText(/Error generando reporte/)).toBeInTheDocument()
    })
  })

  it('debe mostrar estado de carga inicial', () => {
    const { api } = require('../../../utilidades/apiClient')
    api.get.mockImplementation(() => new Promise(() => {})) // Never resolves
    
    render(<GeneradorReportes {...mockProps} />)
    
    expect(screen.getByText('Cargando generador...')).toBeInTheDocument()
  })

  it('debe mostrar información específica por nivel', async () => {
    const { rerender } = render(<GeneradorReportes {...mockProps} nivelUsuario="gratuito" />)
    
    await waitFor(() => {
      expect(screen.getByText(/Plan Gratuito/)).toBeInTheDocument()
    })

    rerender(<GeneradorReportes {...mockProps} nivelUsuario="pro" />)
    
    await waitFor(() => {
      expect(screen.getByText(/Plan Pro/)).toBeInTheDocument()
    })

    rerender(<GeneradorReportes {...mockProps} nivelUsuario="empresarial" />)
    
    await waitFor(() => {
      expect(screen.getByText(/Plan Empresarial/)).toBeInTheDocument()
    })
  })
})

