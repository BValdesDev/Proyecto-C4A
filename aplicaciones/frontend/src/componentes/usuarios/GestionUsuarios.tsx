import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Input } from '../../components/ui/input'
import { Label } from '../../components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select'
import { Alert, AlertDescription } from '../../components/ui/alert'
import { 
  Users, 
  UserPlus, 
  UserMinus, 
  Edit, 
  Trash2, 
  Shield, 
  Mail, 
  Phone,
  Building,
  Calendar,
  CheckCircle,
  AlertCircle,
  Clock,
  Eye,
  EyeOff,
  Search,
  Filter,
  Download,
  Upload,
  RefreshCw,
  Settings,
  Key,
  Lock,
  Unlock
} from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../../utilidades/apiClient'

// Interfaces según prompt maestro
interface PropiedadesGestionUsuarios {
  organizacionId: string
  nivelUsuario: 'pro' | 'empresarial'
  usuarioActual: {
    id: string
    email: string
    rol: string
  }
}

interface Usuario {
  id: string
  email: string
  nombres: string
  apellidos: string
  rol: 'admin_empresa' | 'evaluador' | 'usuario_basico'
  estado: 'activo' | 'inactivo' | 'pendiente' | 'bloqueado'
  fecha_creacion: string
  ultimo_acceso?: string
  telefono?: string
  departamento?: string
  permisos: string[]
  mfa_habilitado: boolean
  intentos_login_fallidos: number
  cuenta_bloqueada_hasta?: string
}

interface Rol {
  id: string
  nombre: string
  descripcion: string
  permisos: string[]
  nivel_requerido: 'pro' | 'empresarial'
}

interface Invitacion {
  id: string
  email: string
  rol: string
  estado: 'pendiente' | 'aceptada' | 'expirada' | 'cancelada'
  fecha_invitacion: string
  fecha_expiracion: string
  invitado_por: string
}

interface EstadisticasUsuarios {
  total_usuarios: number
  usuarios_activos: number
  usuarios_inactivos: number
  usuarios_pendientes: number
  usuarios_bloqueados: number
  limite_usuarios: number
  uso_porcentaje: number
}

// Componente principal según prompt maestro
export const GestionUsuarios: React.FC<PropiedadesGestionUsuarios> = ({ 
  organizacionId, 
  nivelUsuario,
  usuarioActual
}) => {
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [roles, setRoles] = useState<Rol[]>([])
  const [invitaciones, setInvitaciones] = useState<Invitacion[]>([])
  const [estadisticas, setEstadisticas] = useState<EstadisticasUsuarios | null>(null)
  const [cargando, setCargando] = useState(true)
  const [procesando, setProcesando] = useState(false)
  const [mostrarFormularioUsuario, setMostrarFormularioUsuario] = useState(false)
  const [mostrarFormularioInvitacion, setMostrarFormularioInvitacion] = useState(false)
  const [usuarioSeleccionado, setUsuarioSeleccionado] = useState<Usuario | null>(null)
  const [filtros, setFiltros] = useState({
    busqueda: '',
    rol: 'todos',
    estado: 'todos'
  })

  // Formulario de nuevo usuario
  const [nuevoUsuario, setNuevoUsuario] = useState({
    email: '',
    nombres: '',
    apellidos: '',
    rol: '',
    telefono: '',
    departamento: ''
  })

  // Formulario de invitación
  const [nuevaInvitacion, setNuevaInvitacion] = useState({
    email: '',
    rol: '',
    mensaje: ''
  })

  useEffect(() => {
    cargarDatosUsuarios()
  }, [organizacionId])

  const cargarDatosUsuarios = async () => {
    try {
      setCargando(true)
      
      // Cargar usuarios
      const usuariosResponse = await api.get(`/api/v1/organizaciones/${organizacionId}/usuarios`)
      setUsuarios(usuariosResponse.data.usuarios)

      // Cargar roles disponibles
      const rolesResponse = await api.get('/api/v1/roles')
      setRoles(rolesResponse.data.roles)

      // Cargar invitaciones
      const invitacionesResponse = await api.get(`/api/v1/organizaciones/${organizacionId}/invitaciones`)
      setInvitaciones(invitacionesResponse.data.invitaciones)

      // Cargar estadísticas
      const estadisticasResponse = await api.get(`/api/v1/organizaciones/${organizacionId}/estadisticas-usuarios`)
      setEstadisticas(estadisticasResponse.data)

    } catch (error) {
      toast.error('Error al cargar los datos de usuarios')
    } finally {
      setCargando(false)
    }
  }

  const crearUsuario = async () => {
    try {
      setProcesando(true)
      
      await api.post(`/api/v1/organizaciones/${organizacionId}/usuarios`, nuevoUsuario)
      
      toast.success('Usuario creado exitosamente')
      setMostrarFormularioUsuario(false)
      setNuevoUsuario({
        email: '',
        nombres: '',
        apellidos: '',
        rol: '',
        telefono: '',
        departamento: ''
      })
      await cargarDatosUsuarios()
      
    } catch (error) {
      toast.error('Error al crear el usuario')
    } finally {
      setProcesando(false)
    }
  }

  const enviarInvitacion = async () => {
    try {
      setProcesando(true)
      
      await api.post(`/api/v1/organizaciones/${organizacionId}/invitaciones`, nuevaInvitacion)
      
      toast.success('Invitación enviada exitosamente')
      setMostrarFormularioInvitacion(false)
      setNuevaInvitacion({
        email: '',
        rol: '',
        mensaje: ''
      })
      await cargarDatosUsuarios()
      
    } catch (error) {
      console.error('Error enviando invitación:', error)
      toast.error('Error al enviar la invitación')
    } finally {
      setProcesando(false)
    }
  }

  const actualizarUsuario = async (usuarioId: string, datos: Partial<Usuario>) => {
    try {
      setProcesando(true)
      
      await api.put(`/api/v1/usuarios/${usuarioId}`, datos)
      
      toast.success('Usuario actualizado exitosamente')
      await cargarDatosUsuarios()
      
    } catch (error) {
      toast.error('Error al actualizar el usuario')
    } finally {
      setProcesando(false)
    }
  }

  const eliminarUsuario = async (usuarioId: string) => {
    try {
      setProcesando(true)
      
      await api.delete(`/api/v1/usuarios/${usuarioId}`)
      
      toast.success('Usuario eliminado exitosamente')
      await cargarDatosUsuarios()
      
    } catch (error) {
      toast.error('Error al eliminar el usuario')
    } finally {
      setProcesando(false)
    }
  }

  const bloquearUsuario = async (usuarioId: string) => {
    try {
      setProcesando(true)
      
      await api.post(`/api/v1/usuarios/${usuarioId}/bloquear`)
      
      toast.success('Usuario bloqueado exitosamente')
      await cargarDatosUsuarios()
      
    } catch (error) {
      toast.error('Error al bloquear el usuario')
    } finally {
      setProcesando(false)
    }
  }

  const desbloquearUsuario = async (usuarioId: string) => {
    try {
      setProcesando(true)
      
      await api.post(`/api/v1/usuarios/${usuarioId}/desbloquear`)
      
      toast.success('Usuario desbloqueado exitosamente')
      await cargarDatosUsuarios()
      
    } catch (error) {
      toast.error('Error al desbloquear el usuario')
    } finally {
      setProcesando(false)
    }
  }

  const cancelarInvitacion = async (invitacionId: string) => {
    try {
      setProcesando(true)
      
      await api.delete(`/api/v1/invitaciones/${invitacionId}`)
      
      toast.success('Invitación cancelada exitosamente')
      await cargarDatosUsuarios()
      
    } catch (error) {
      console.error('Error cancelando invitación:', error)
      toast.error('Error al cancelar la invitación')
    } finally {
      setProcesando(false)
    }
  }

  const getColorEstado = (estado: string) => {
    switch (estado) {
      case 'activo': return 'bg-green-100 text-green-800'
      case 'inactivo': return 'bg-gray-100 text-gray-800'
      case 'pendiente': return 'bg-yellow-100 text-yellow-800'
      case 'bloqueado': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getColorRol = (rol: string) => {
    switch (rol) {
      case 'admin_empresa': return 'bg-purple-100 text-purple-800'
      case 'evaluador': return 'bg-blue-100 text-blue-800'
      case 'usuario_basico': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getIconoEstado = (estado: string) => {
    switch (estado) {
      case 'activo': return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'inactivo': return <Clock className="w-4 h-4 text-gray-600" />
      case 'pendiente': return <AlertCircle className="w-4 h-4 text-yellow-600" />
      case 'bloqueado': return <Lock className="w-4 h-4 text-red-600" />
      default: return <AlertCircle className="w-4 h-4 text-gray-600" />
    }
  }

  const usuariosFiltrados = usuarios.filter(usuario => {
    const cumpleBusqueda = !filtros.busqueda || 
      usuario.nombres.toLowerCase().includes(filtros.busqueda.toLowerCase()) ||
      usuario.apellidos.toLowerCase().includes(filtros.busqueda.toLowerCase()) ||
      usuario.email.toLowerCase().includes(filtros.busqueda.toLowerCase())
    
    const cumpleRol = filtros.rol === 'todos' || usuario.rol === filtros.rol
    const cumpleEstado = filtros.estado === 'todos' || usuario.estado === filtros.estado
    
    return cumpleBusqueda && cumpleRol && cumpleEstado
  })

  if (cargando) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando gestión de usuarios...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="w-6 h-6 text-c4a-blue-600" />
            <span>Gestión de Usuarios</span>
            <Badge className="bg-blue-100 text-blue-800">{nivelUsuario.toUpperCase()}</Badge>
          </CardTitle>
          <CardDescription>
            Gestione usuarios, roles y permisos de su organización
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Estadísticas */}
      {estadisticas && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2">
                <Users className="w-5 h-5 text-blue-600" />
                <div>
                  <p className="text-sm font-medium">Total Usuarios</p>
                  <p className="text-2xl font-bold">{estadisticas.total_usuarios}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <div>
                  <p className="text-sm font-medium">Activos</p>
                  <p className="text-2xl font-bold">{estadisticas.usuarios_activos}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2">
                <Clock className="w-5 h-5 text-yellow-600" />
                <div>
                  <p className="text-sm font-medium">Pendientes</p>
                  <p className="text-2xl font-bold">{estadisticas.usuarios_pendientes}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2">
                <Lock className="w-5 h-5 text-red-600" />
                <div>
                  <p className="text-sm font-medium">Bloqueados</p>
                  <p className="text-2xl font-bold">{estadisticas.usuarios_bloqueados}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-purple-600" />
                <div>
                  <p className="text-sm font-medium">Límite</p>
                  <p className="text-2xl font-bold">{estadisticas.limite_usuarios}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Barra de herramientas */}
      <Card>
        <CardHeader>
          <CardTitle>Herramientas de Gestión</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <Button onClick={() => setMostrarFormularioUsuario(true)}>
              <UserPlus className="w-4 h-4 mr-2" />
              Agregar Usuario
            </Button>
            <Button variant="outline" onClick={() => setMostrarFormularioInvitacion(true)}>
              <Mail className="w-4 h-4 mr-2" />
              Enviar Invitación
            </Button>
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Exportar Lista
            </Button>
            <Button variant="outline">
              <Upload className="w-4 h-4 mr-2" />
              Importar Usuarios
            </Button>
            <Button variant="outline" onClick={cargarDatosUsuarios}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Actualizar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros y Búsqueda</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label>Buscar</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar usuarios..."
                  value={filtros.busqueda}
                  onChange={(e) => setFiltros(prev => ({ ...prev, busqueda: e.target.value }))}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Rol</Label>
              <Select 
                value={filtros.rol} 
                onValueChange={(value) => setFiltros(prev => ({ ...prev, rol: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos los roles</SelectItem>
                  <SelectItem value="admin_empresa">Administrador</SelectItem>
                  <SelectItem value="evaluador">Evaluador</SelectItem>
                  <SelectItem value="usuario_basico">Usuario Básico</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Estado</Label>
              <Select 
                value={filtros.estado} 
                onValueChange={(value) => setFiltros(prev => ({ ...prev, estado: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos los estados</SelectItem>
                  <SelectItem value="activo">Activo</SelectItem>
                  <SelectItem value="inactivo">Inactivo</SelectItem>
                  <SelectItem value="pendiente">Pendiente</SelectItem>
                  <SelectItem value="bloqueado">Bloqueado</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Acciones</Label>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">
                  <Filter className="w-4 h-4 mr-1" />
                  Filtros
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setFiltros({ busqueda: '', rol: 'todos', estado: 'todos' })}
                >
                  Limpiar
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lista de usuarios */}
      <Card>
        <CardHeader>
          <CardTitle>Usuarios ({usuariosFiltrados.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {usuariosFiltrados.length > 0 ? (
            <div className="space-y-4">
              {usuariosFiltrados.map((usuario) => (
                <div key={usuario.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-c4a-blue-100 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-c4a-blue-600" />
                      </div>
                      <div>
                        <h4 className="font-medium">{usuario.nombres} {usuario.apellidos}</h4>
                        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                          <Mail className="w-3 h-3" />
                          <span>{usuario.email}</span>
                          <span>•</span>
                          <Badge className={getColorRol(usuario.rol)}>
                            {usuario.rol.replace('_', ' ').toUpperCase()}
                          </Badge>
                          <span>•</span>
                          <div className="flex items-center space-x-1">
                            {getIconoEstado(usuario.estado)}
                            <Badge className={getColorEstado(usuario.estado)}>
                              {usuario.estado.toUpperCase()}
                            </Badge>
                          </div>
                        </div>
                        {usuario.telefono && (
                          <div className="flex items-center space-x-1 text-sm text-muted-foreground mt-1">
                            <Phone className="w-3 h-3" />
                            <span>{usuario.telefono}</span>
                          </div>
                        )}
                        {usuario.departamento && (
                          <div className="flex items-center space-x-1 text-sm text-muted-foreground mt-1">
                            <Building className="w-3 h-3" />
                            <span>{usuario.departamento}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setUsuarioSeleccionado(usuario)}
                      >
                        <Edit className="w-4 h-4 mr-1" />
                        Editar
                      </Button>
                      {usuario.estado === 'bloqueado' ? (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => desbloquearUsuario(usuario.id)}
                          disabled={procesando}
                        >
                          <Unlock className="w-4 h-4 mr-1" />
                          Desbloquear
                        </Button>
                      ) : (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => bloquearUsuario(usuario.id)}
                          disabled={procesando}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Lock className="w-4 h-4 mr-1" />
                          Bloquear
                        </Button>
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => eliminarUsuario(usuario.id)}
                        disabled={procesando}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4 mr-1" />
                        Eliminar
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Users className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No hay usuarios</h3>
              <p className="text-muted-foreground mb-4">
                Agregue usuarios o envíe invitaciones para comenzar
              </p>
              <Button onClick={() => setMostrarFormularioUsuario(true)}>
                <UserPlus className="w-4 h-4 mr-2" />
                Agregar Usuario
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Lista de invitaciones */}
      {invitaciones.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Invitaciones Pendientes ({invitaciones.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {invitaciones.map((invitacion) => (
                <div key={invitacion.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Mail className="w-5 h-5 text-muted-foreground" />
                      <div>
                        <h4 className="font-medium">{invitacion.email}</h4>
                        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                          <Badge className={getColorRol(invitacion.rol)}>
                            {invitacion.rol.replace('_', ' ').toUpperCase()}
                          </Badge>
                          <span>•</span>
                          <Badge className={getColorEstado(invitacion.estado)}>
                            {invitacion.estado.toUpperCase()}
                          </Badge>
                          <span>•</span>
                          <span>Invitado el {new Date(invitacion.fecha_invitacion).toLocaleDateString('es-CL')}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => cancelarInvitacion(invitacion.id)}
                        disabled={procesando}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4 mr-1" />
                        Cancelar
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Modal de nuevo usuario */}
      {mostrarFormularioUsuario && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Agregar Usuario</CardTitle>
              <CardDescription>
                Complete la información del nuevo usuario
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Email</Label>
                <Input
                  type="email"
                  value={nuevoUsuario.email}
                  onChange={(e) => setNuevoUsuario(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="usuario@empresa.cl"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Nombres</Label>
                  <Input
                    value={nuevoUsuario.nombres}
                    onChange={(e) => setNuevoUsuario(prev => ({ ...prev, nombres: e.target.value }))}
                    placeholder="Juan"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Apellidos</Label>
                  <Input
                    value={nuevoUsuario.apellidos}
                    onChange={(e) => setNuevoUsuario(prev => ({ ...prev, apellidos: e.target.value }))}
                    placeholder="Pérez"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Rol</Label>
                <Select 
                  value={nuevoUsuario.rol} 
                  onValueChange={(value) => setNuevoUsuario(prev => ({ ...prev, rol: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar rol" />
                  </SelectTrigger>
                  <SelectContent>
                    {roles.map((rol) => (
                      <SelectItem key={rol.id} value={rol.id}>
                        {rol.nombre}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Teléfono</Label>
                  <Input
                    value={nuevoUsuario.telefono}
                    onChange={(e) => setNuevoUsuario(prev => ({ ...prev, telefono: e.target.value }))}
                    placeholder="+56 9 1234 5678"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Departamento</Label>
                  <Input
                    value={nuevoUsuario.departamento}
                    onChange={(e) => setNuevoUsuario(prev => ({ ...prev, departamento: e.target.value }))}
                    placeholder="IT"
                  />
                </div>
              </div>
              <div className="flex space-x-2">
                <Button 
                  variant="outline" 
                  onClick={() => setMostrarFormularioUsuario(false)}
                  className="flex-1"
                >
                  Cancelar
                </Button>
                <Button 
                  onClick={crearUsuario}
                  disabled={procesando}
                  className="flex-1"
                >
                  {procesando ? 'Creando...' : 'Crear Usuario'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Modal de invitación */}
      {mostrarFormularioInvitacion && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Enviar Invitación</CardTitle>
              <CardDescription>
                Invite a un nuevo usuario a unirse a su organización
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Email</Label>
                <Input
                  type="email"
                  value={nuevaInvitacion.email}
                  onChange={(e) => setNuevaInvitacion(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="usuario@empresa.cl"
                />
              </div>
              <div className="space-y-2">
                <Label>Rol</Label>
                <Select 
                  value={nuevaInvitacion.rol} 
                  onValueChange={(value) => setNuevaInvitacion(prev => ({ ...prev, rol: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar rol" />
                  </SelectTrigger>
                  <SelectContent>
                    {roles.map((rol) => (
                      <SelectItem key={rol.id} value={rol.id}>
                        {rol.nombre}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Mensaje Personalizado (Opcional)</Label>
                <textarea
                  className="w-full p-3 border rounded-md resize-none"
                  rows={3}
                  value={nuevaInvitacion.mensaje}
                  onChange={(e) => setNuevaInvitacion(prev => ({ ...prev, mensaje: e.target.value }))}
                  placeholder="Mensaje personalizado para la invitación..."
                />
              </div>
              <div className="flex space-x-2">
                <Button 
                  variant="outline" 
                  onClick={() => setMostrarFormularioInvitacion(false)}
                  className="flex-1"
                >
                  Cancelar
                </Button>
                <Button 
                  onClick={enviarInvitacion}
                  disabled={procesando}
                  className="flex-1"
                >
                  {procesando ? 'Enviando...' : 'Enviar Invitación'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}