import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/utilidades/apiClient';
import { 
  Search, 
  Filter, 
  MoreHorizontal, 
  UserPlus, 
  Download,
  Edit,
  Trash2,
  Eye
} from 'lucide-react';

interface User {
  id: string;
  nombre: string;
  email: string;
  empresa: string;
  suscripcion: string;
  estado: 'activo' | 'inactivo' | 'suspendido';
  ultimoLogin: string | null;
  fechaRegistro: string;
  activo: boolean;
}

const AdminUsersPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get('/api/v1/admin/users');
        setUsers(response.data.users);
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Error al cargar usuarios');
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const getStatusBadge = (status: string) => {
    const variants = {
      activo: 'bg-green-100 text-green-800',
      inactivo: 'bg-yellow-100 text-yellow-800',
      suspendido: 'bg-red-100 text-red-800',
    };
    
    return (
      <Badge className={variants[status as keyof typeof variants]}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  // Función para exportar usuarios
  const handleExportUsers = async () => {
    try {
      const response = await apiClient.get('/api/v1/admin/users/export', {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `usuarios_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert('Error al exportar usuarios. Inténtalo de nuevo.');
    }
  };

  // Función para crear nuevo usuario
  const handleCreateUser = () => {
    setShowCreateModal(true);
  };

  const getSubscriptionBadge = (subscription: string) => {
    const variants = {
      'gratuito': 'bg-gray-100 text-gray-800',
      'pro': 'bg-blue-100 text-blue-800',
      'empresarial': 'bg-purple-100 text-purple-800',
    };
    
    return (
      <Badge className={variants[subscription.toLowerCase() as keyof typeof variants] || 'bg-gray-100 text-gray-800'}>
        {subscription.charAt(0).toUpperCase() + subscription.slice(1)}
      </Badge>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-CL', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.empresa.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterStatus === 'all' || user.estado === filterStatus;
    
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Usuarios</h1>
          <p className="text-gray-600 mt-2">Cargando usuarios...</p>
        </div>
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Usuarios</h1>
          <p className="text-red-600 mt-2">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Usuarios</h1>
          <p className="text-gray-600 mt-2">
            Administra usuarios, suscripciones y permisos
          </p>
        </div>
        
        <div className="flex space-x-3">
          <Button variant="outline" onClick={handleExportUsers}>
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
          <Button onClick={handleCreateUser}>
            <UserPlus className="h-4 w-4 mr-2" />
            Nuevo Usuario
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Buscar por nombre, email o empresa..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm"
              >
                <option value="all">Todos los estados</option>
                <option value="activo">Activos</option>
                <option value="inactivo">Inactivos</option>
                <option value="suspendido">Suspendidos</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>
            Usuarios ({filteredUsers.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Usuario</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Empresa</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Suscripción</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Estado</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Último Login</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Registro</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="border-b hover:bg-gray-50">
                    <td className="py-4 px-4">
                      <div>
                        <div className="font-medium text-gray-900">{user.nombre}</div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-gray-900">{user.empresa}</td>
                    <td className="py-4 px-4">
                      {getSubscriptionBadge(user.suscripcion)}
                    </td>
                    <td className="py-4 px-4">
                      {getStatusBadge(user.estado)}
                    </td>
                    <td className="py-4 px-4 text-sm text-gray-600">
                      {user.ultimoLogin ? formatDate(user.ultimoLogin) : 'Nunca'}
                    </td>
                    <td className="py-4 px-4 text-sm text-gray-600">
                      {formatDate(user.fechaRegistro)}
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center space-x-2">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {filteredUsers.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500">No se encontraron usuarios</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal para crear usuario */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Crear Nuevo Usuario</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre completo
                </label>
                <Input placeholder="Ej: Juan Pérez" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <Input type="email" placeholder="juan@empresa.com" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Empresa
                </label>
                <Input placeholder="Nombre de la empresa" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rol
                </label>
                <select className="w-full p-2 border border-gray-300 rounded-md">
                  <option value="evaluador">Evaluador</option>
                  <option value="admin_empresa">Admin Empresa</option>
                  <option value="admin_sistema">Admin Sistema</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <Button 
                variant="outline" 
                onClick={() => setShowCreateModal(false)}
              >
                Cancelar
              </Button>
              <Button onClick={() => {
                alert('Usuario creado exitosamente (simulado)');
                setShowCreateModal(false);
              }}>
                Crear Usuario
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminUsersPage;

