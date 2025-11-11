import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  Filter, 
  Download,
  Eye,
  FileText,
  Calendar,
  Building,
  User
} from 'lucide-react';
import { apiClient } from '@/utilidades/apiClient';

interface Diagnostic {
  id: string;
  companyName: string;
  userName: string;
  framework: 'NIST' | 'COBIT' | 'ISO 27001';
  status: 'completado' | 'en_progreso' | 'pendiente' | 'cancelado';
  score: number;
  maxScore: number;
  createdAt: string;
  completedAt?: string;
  progress: number;
}

const AdminDiagnosticsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterFramework, setFilterFramework] = useState<string>('all');
  const [diagnostics, setDiagnostics] = useState<Diagnostic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar datos reales de la API
  useEffect(() => {
    const fetchDiagnostics = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get('/api/v1/admin/diagnostics');
        setDiagnostics(response.data.diagnostics || []);
        setError(null);
      } catch (err: any) {
        console.error('Error fetching diagnostics:', err);
        setError(err.response?.data?.detail || 'Error al cargar diagnósticos');
      } finally {
        setLoading(false);
      }
    };

    fetchDiagnostics();
  }, []);

  const getStatusBadge = (status: string) => {
    const variants = {
      completada: 'bg-green-100 text-green-800',
      completado: 'bg-green-100 text-green-800', // Para compatibilidad
      en_progreso: 'bg-blue-100 text-blue-800',
      pendiente: 'bg-yellow-100 text-yellow-800',
      cancelado: 'bg-red-100 text-red-800',
    };
    
    return (
      <Badge className={variants[status as keyof typeof variants] || 'bg-gray-100 text-gray-800'}>
        {status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
      </Badge>
    );
  };

  const getFrameworkBadge = (framework: string) => {
    const variants = {
      'NIST': 'bg-blue-100 text-blue-800',
      'COBIT': 'bg-purple-100 text-purple-800',
      'ISO 27001': 'bg-green-100 text-green-800',
    };
    
    return (
      <Badge className={variants[framework as keyof typeof variants]}>
        {framework}
      </Badge>
    );
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
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

  const filteredDiagnostics = diagnostics.filter(diagnostic => {
    const matchesSearch = diagnostic.companyName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         diagnostic.userName.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || diagnostic.status === filterStatus;
    const matchesFramework = filterFramework === 'all' || diagnostic.framework === filterFramework;
    
    return matchesSearch && matchesStatus && matchesFramework;
  });

  // Estadísticas calculadas dinámicamente
  const stats = {
    total: diagnostics.length,
    completed: diagnostics.filter(d => d.status === 'completada').length,
    inProgress: diagnostics.filter(d => d.status === 'en_progreso').length,
    pending: diagnostics.filter(d => d.status === 'pendiente').length,
    averageScore: diagnostics
      .filter(d => d.status === 'completada' && d.score > 0)
      .reduce((acc, d) => acc + d.score, 0) / 
      diagnostics.filter(d => d.status === 'completada' && d.score > 0).length || 0,
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Diagnósticos</h1>
          <p className="text-gray-600 mt-2">Cargando diagnósticos...</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => (
            <Card key={i}>
              <CardContent className="pt-6 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Diagnósticos</h1>
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
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Diagnósticos</h1>
          <p className="text-gray-600 mt-2">
            Monitorea y administra todos los diagnósticos de la plataforma
          </p>
        </div>
        
        <Button variant="outline">
          <Download className="h-4 w-4 mr-2" />
          Exportar Datos
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <FileText className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Completados</p>
                <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
              </div>
              <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                <div className="h-4 w-4 bg-green-600 rounded-full"></div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">En Progreso</p>
                <p className="text-2xl font-bold text-blue-600">{stats.inProgress}</p>
              </div>
              <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                <div className="h-4 w-4 bg-blue-600 rounded-full"></div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pendientes</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
              </div>
              <div className="h-8 w-8 bg-yellow-100 rounded-full flex items-center justify-center">
                <div className="h-4 w-4 bg-yellow-600 rounded-full"></div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Puntaje Promedio</p>
                <p className="text-2xl font-bold text-gray-900">{stats.averageScore.toFixed(1)}</p>
              </div>
              <div className="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center">
                <div className="h-4 w-4 bg-purple-600 rounded-full"></div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Buscar por empresa o usuario..."
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
                <option value="completada">Completados</option>
                <option value="en_progreso">En Progreso</option>
                <option value="pendiente">Pendientes</option>
                <option value="cancelado">Cancelados</option>
              </select>
            </div>
            
            <select
              value={filterFramework}
              onChange={(e) => setFilterFramework(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="all">Todos los frameworks</option>
              <option value="NIST">NIST</option>
              <option value="COBIT">COBIT</option>
              <option value="ISO 27001">ISO 27001</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Diagnostics Table */}
      <Card>
        <CardHeader>
          <CardTitle>
            Diagnósticos ({filteredDiagnostics.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Empresa</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Usuario</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Framework</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Estado</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Progreso</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Puntaje</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Creado</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredDiagnostics.map((diagnostic) => (
                  <tr key={diagnostic.id} className="border-b hover:bg-gray-50">
                    <td className="py-4 px-4">
                      <div className="flex items-center">
                        <Building className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="font-medium text-gray-900">{diagnostic.companyName}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center">
                        <User className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-gray-900">{diagnostic.userName}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      {getFrameworkBadge(diagnostic.framework)}
                    </td>
                    <td className="py-4 px-4">
                      {getStatusBadge(diagnostic.status)}
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${diagnostic.progress}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600">{diagnostic.progress}%</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      {diagnostic.status === 'completado' ? (
                        <span className={`font-semibold ${getScoreColor(diagnostic.score)}`}>
                          {diagnostic.score}/{diagnostic.maxScore}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="py-4 px-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 text-gray-400 mr-1" />
                        {formatDate(diagnostic.createdAt)}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center space-x-2">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <FileText className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {filteredDiagnostics.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500">No se encontraron diagnósticos</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminDiagnosticsPage;

