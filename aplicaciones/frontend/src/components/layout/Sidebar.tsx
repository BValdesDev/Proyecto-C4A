import React from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { cn } from '../../utilidades/cn'
import {
  LayoutDashboard,
  FileText,
  BarChart3,
  CreditCard,
  Users,
  Settings,
  Shield,
  HelpCircle
} from 'lucide-react'

const menuItems = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    path: '/app/dashboard',
    nivel_requerido: 'gratuito'
  },
  {
    id: 'evaluaciones',
    label: 'Evaluaciones',
    icon: FileText,
    path: '/app/evaluaciones',
    nivel_requerido: 'gratuito'
  },
  {
    id: 'reportes',
    label: 'Reportes',
    icon: BarChart3,
    path: '/app/reportes',
    nivel_requerido: 'gratuito'
  },
  {
    id: 'suscripciones',
    label: 'Suscripciones',
    icon: CreditCard,
    path: '/app/suscripciones',
    nivel_requerido: 'gratuito'
  },
  {
    id: 'usuarios',
    label: 'Usuarios',
    icon: Users,
    path: '/app/usuarios',
    nivel_requerido: 'pro'
  },
  {
    id: 'configuracion',
    label: 'Configuración',
    icon: Settings,
    path: '/app/perfil',
    nivel_requerido: 'gratuito'
  }
]

export const Sidebar: React.FC = () => {
  const { usuario } = useAuth()

  if (!usuario) return null

  const canAccess = (nivelRequerido: string) => {
    const niveles = ['gratuito', 'pro', 'empresarial']
    const nivelUsuario = niveles.indexOf(usuario.organizacion.nivel_suscripcion)
    const nivelRequeridoIndex = niveles.indexOf(nivelRequerido)
    return nivelUsuario >= nivelRequeridoIndex
  }

  return (
    <aside className="w-64 bg-white border-r border-border flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-br from-c4a-blue-600 to-c4a-purple-600 rounded-lg flex items-center justify-center">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-foreground">C4A SaaS</h2>
            <p className="text-xs text-muted-foreground">Ciberseguridad</p>
          </div>
        </div>
      </div>

      {/* Navegación */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const canAccessItem = canAccess(item.nivel_requerido)
          
          if (!canAccessItem) return null

          return (
            <NavLink
              key={item.id}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                )
              }
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      {/* Información de la organización */}
      <div className="p-4 border-t border-border">
        <div className="bg-muted rounded-lg p-3">
          <p className="text-xs font-medium text-foreground">
            {usuario.organizacion.nombre}
          </p>
          <p className="text-xs text-muted-foreground">
            Plan {usuario.organizacion.nivel_suscripcion.toUpperCase()}
          </p>
          {usuario.organizacion.nivel_suscripcion === 'gratuito' && (
            <p className="text-xs text-c4a-blue-600 mt-1">
              Actualizar para más funciones
            </p>
          )}
        </div>
      </div>

      {/* Ayuda */}
      <div className="p-4">
        <button className="flex items-center space-x-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
          <HelpCircle className="w-4 h-4" />
          <span>Ayuda</span>
        </button>
      </div>
    </aside>
  )
}
