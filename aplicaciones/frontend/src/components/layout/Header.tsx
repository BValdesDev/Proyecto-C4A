import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { Button } from '../ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu'
import { Bell, Settings, LogOut, User, Home } from 'lucide-react'
import { Badge } from '../ui/badge'

export const Header: React.FC = () => {
  const { usuario, logout } = useAuth()
  const navigate = useNavigate()

  if (!usuario) return null

  const getNivelBadgeColor = (nivel: string) => {
    switch (nivel) {
      case 'gratuito':
        return 'bg-gray-100 text-gray-800'
      case 'pro':
        return 'bg-c4a-blue-100 text-c4a-blue-800'
      case 'empresarial':
        return 'bg-c4a-purple-100 text-c4a-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <header className="bg-white border-b border-border px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Título de la página actual */}
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/app/dashboard')}
            className="flex items-center space-x-2"
          >
            <Home className="w-4 h-4" />
            <span>Dashboard</span>
          </Button>
          <div>
            <h1 className="text-2xl font-semibold text-foreground">
              C4A SaaS
            </h1>
            <p className="text-sm text-muted-foreground">
              Evaluación de Ciberseguridad
            </p>
          </div>
        </div>

        {/* Acciones del header */}
        <div className="flex items-center space-x-4">
          {/* Notificaciones */}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-5 w-5" />
            <Badge 
              variant="destructive" 
              className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full p-0 text-xs flex items-center justify-center min-w-4"
            >
              3
            </Badge>
          </Button>

          {/* Información del usuario */}
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <p className="text-sm font-medium text-foreground">
                {usuario.nombres} {usuario.apellidos}
              </p>
              <p className="text-xs text-muted-foreground">
                {usuario.organizacion.nombre}
              </p>
            </div>
            
            <Badge className={getNivelBadgeColor(usuario.organizacion.nivel_suscripcion)}>
              {usuario.organizacion.nivel_suscripcion.toUpperCase()}
            </Badge>

            {/* Menú de usuario */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src="" alt={usuario.nombres} />
                    <AvatarFallback>
                      {usuario.nombres.charAt(0)}{usuario.apellidos.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">
                      {usuario.nombres} {usuario.apellidos}
                    </p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {usuario.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <User className="mr-2 h-4 w-4" />
                  <span>Perfil</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Configuración</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={logout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Cerrar sesión</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </header>
  )
}
