import React from 'react'
import { useAuth } from '../../hooks/useAuth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '../../components/ui/avatar'
import { User, Mail, Building, Shield, Calendar } from 'lucide-react'

export const PerfilPage: React.FC = () => {
  const { usuario } = useAuth()

  if (!usuario) return null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Mi Perfil</h1>
          <p className="text-muted-foreground">
            Gestiona tu información personal y configuración
          </p>
        </div>
        <Button>
          Editar Perfil
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Información personal */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Información Personal</CardTitle>
              <CardDescription>
                Tu información de contacto y perfil
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex items-center space-x-4">
                  <Avatar className="w-20 h-20">
                    <AvatarImage src="" alt={usuario.nombres} />
                    <AvatarFallback className="text-lg">
                      {usuario.nombres.charAt(0)}{usuario.apellidos.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h3 className="text-xl font-semibold">
                      {usuario.nombres} {usuario.apellidos}
                    </h3>
                    <p className="text-muted-foreground">{usuario.email}</p>
                    <Badge className="mt-2">
                      {usuario.rol.nombre_mostrar}
                    </Badge>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Nombres</label>
                    <div className="flex items-center space-x-2 p-3 border rounded-lg">
                      <User className="w-4 h-4 text-muted-foreground" />
                      <span>{usuario.nombres}</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Apellidos</label>
                    <div className="flex items-center space-x-2 p-3 border rounded-lg">
                      <User className="w-4 h-4 text-muted-foreground" />
                      <span>{usuario.apellidos}</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Correo electrónico</label>
                    <div className="flex items-center space-x-2 p-3 border rounded-lg">
                      <Mail className="w-4 h-4 text-muted-foreground" />
                      <span>{usuario.email}</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Estado de cuenta</label>
                    <div className="flex items-center space-x-2 p-3 border rounded-lg">
                      <Shield className="w-4 h-4 text-muted-foreground" />
                      <Badge className="bg-green-100 text-green-800">
                        {usuario.estado_cuenta}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Información de la organización */}
          <Card>
            <CardHeader>
              <CardTitle>Organización</CardTitle>
              <CardDescription>
                Información de tu organización
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <Building className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <h4 className="font-medium">{usuario.organizacion.nombre}</h4>
                    <p className="text-sm text-muted-foreground">
                      {usuario.organizacion.sector} • {usuario.organizacion.tamaño}
                    </p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Sector</label>
                    <div className="p-3 border rounded-lg">
                      <span className="capitalize">{usuario.organizacion.sector}</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Tamaño</label>
                    <div className="p-3 border rounded-lg">
                      <span className="capitalize">{usuario.organizacion.tamaño}</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Plan actual */}
          <Card>
            <CardHeader>
              <CardTitle>Plan Actual</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center space-y-4">
                <Badge className="text-lg px-4 py-2">
                  {usuario.organizacion.nivel_suscripcion.toUpperCase()}
                </Badge>
                <p className="text-sm text-muted-foreground">
                  {usuario.organizacion.nivel_suscripcion === 'gratuito' && 'Plan básico gratuito'}
                  {usuario.organizacion.nivel_suscripcion === 'pro' && 'Plan profesional'}
                  {usuario.organizacion.nivel_suscripcion === 'empresarial' && 'Plan empresarial'}
                </p>
                {usuario.organizacion.nivel_suscripcion === 'gratuito' && (
                  <Button className="w-full">
                    Actualizar Plan
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Actividad reciente */}
          <Card>
            <CardHeader>
              <CardTitle>Actividad Reciente</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Último acceso</p>
                    <p className="text-xs text-muted-foreground">
                      {usuario.fecha_ultimo_acceso 
                        ? new Date(usuario.fecha_ultimo_acceso).toLocaleDateString('es-CL')
                        : 'Nunca'
                      }
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Cuenta creada</p>
                    <p className="text-xs text-muted-foreground">
                      Hace 30 días
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Acciones rápidas */}
          <Card>
            <CardHeader>
              <CardTitle>Acciones Rápidas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Button variant="outline" className="w-full justify-start">
                  Cambiar Contraseña
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  Configuración de Notificaciones
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  Exportar Datos
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
