import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Users, FileText, CreditCard, TrendingUp, AlertCircle, CheckCircle, Download, Plus, RefreshCw } from 'lucide-react';
import { apiClient } from '@/utilidades/apiClient';

interface DashboardStats {
  totalUsers: number;
  activeUsers: number;
  totalDiagnostics: number;
  completedDiagnostics: number;
  pendingDiagnostics: number;
  monthlyRevenue: number;
  completionRate: number;
  growthRate: number;
}

const AdminDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 0,
    activeUsers: 0,
    totalDiagnostics: 0,
    completedDiagnostics: 0,
    pendingDiagnostics: 0,
    monthlyRevenue: 0,
    completionRate: 0,
    growthRate: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get('/api/v1/admin/dashboard/stats');
        setStats(response.data);
        setError(null);
      } catch (err: any) {
        console.error('Error fetching dashboard stats:', err);
        setError(err.response?.data?.detail || 'Error al cargar estadísticas');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
    }).format(amount);
  };

  // Funciones para acciones rápidas
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
      console.error('Error al exportar usuarios:', error);
      alert('Error al exportar usuarios. Inténtalo de nuevo.');
    }
  };

  const handleExportDiagnostics = async () => {
    try {
      const response = await apiClient.get('/api/v1/admin/diagnostics/export', {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `diagnosticos_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error al exportar diagnósticos:', error);
      alert('Error al exportar diagnósticos. Inténtalo de nuevo.');
    }
  };

  const handleSyncPayments = async () => {
    try {
      await apiClient.post('/api/v1/admin/payments/sync');
      alert('Sincronización de pagos completada exitosamente');
    } catch (error) {
      console.error('Error al sincronizar pagos:', error);
      alert('Error al sincronizar pagos. Inténtalo de nuevo.');
    }
  };

  const handleExportPayments = async () => {
    try {
      const response = await apiClient.get('/api/v1/admin/payments/export', {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `pagos_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error al exportar pagos:', error);
      alert('Error al exportar pagos. Inténtalo de nuevo.');
    }
  };

  const handleExportAnalytics = async () => {
    try {
      const response = await apiClient.get('/api/v1/admin/analytics/export', {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `analytics_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error al exportar analytics:', error);
      alert('Error al exportar analytics. Inténtalo de nuevo.');
    }
  };

  const StatCard = ({ 
    title, 
    value, 
    icon: Icon, 
    color = 'blue',
    subtitle 
  }: {
    title: string;
    value: string | number;
    icon: React.ElementType;
    color?: 'blue' | 'green' | 'orange' | 'red' | 'purple';
    subtitle?: string;
  }) => {
    const colorClasses = {
      blue: 'bg-blue-50 text-blue-600',
      green: 'bg-green-50 text-green-600',
      orange: 'bg-orange-50 text-orange-600',
      red: 'bg-red-50 text-red-600',
      purple: 'bg-purple-50 text-purple-600',
    };

    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">
            {title}
          </CardTitle>
          <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
            <Icon className="h-4 w-4" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-gray-900">{value}</div>
          {subtitle && (
            <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
          )}
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Panel de Administración</h1>
          <p className="text-gray-600 mt-2">Cargando estadísticas...</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </CardHeader>
              <CardContent className="animate-pulse">
                <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
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
          <h1 className="text-3xl font-bold text-gray-900">Panel de Administración</h1>
          <p className="text-red-600 mt-2">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Panel de Administración</h1>
        <p className="text-gray-600 mt-2">
          Vista general de la plataforma C4A SaaS
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard
          title="Total de Usuarios"
          value={stats.totalUsers.toLocaleString('es-CL')}
          icon={Users}
          color="blue"
          subtitle={`${stats.activeUsers} usuarios activos`}
        />
        
        <StatCard
          title="Diagnósticos Totales"
          value={stats.totalDiagnostics.toLocaleString('es-CL')}
          icon={FileText}
          color="green"
          subtitle={`${stats.completedDiagnostics} completados`}
        />
        
        <StatCard
          title="Ingresos Mensuales"
          value={formatCurrency(stats.monthlyRevenue)}
          icon={CreditCard}
          color="purple"
          subtitle="Octubre 2025"
        />
        
        <StatCard
          title="Diagnósticos Pendientes"
          value={stats.pendingDiagnostics}
          icon={AlertCircle}
          color="orange"
          subtitle="Requieren atención"
        />
        
        <StatCard
          title="Tasa de Completación"
          value={`${stats.completionRate}%`}
          icon={CheckCircle}
          color="green"
          subtitle="Diagnósticos completados"
        />
        
        <StatCard
          title="Crecimiento Mensual"
          value={`${stats.growthRate > 0 ? '+' : ''}${stats.growthRate}%`}
          icon={TrendingUp}
          color="blue"
          subtitle="Usuarios nuevos"
        />
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Acciones Rápidas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Gestionar Usuarios */}
            <div className="space-y-2">
              <Button 
                onClick={() => navigate('/admin/users')}
                className="w-full flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                variant="outline"
              >
                <Users className="h-5 w-5 mr-2 text-blue-600" />
                <span className="text-sm font-medium">Gestionar Usuarios</span>
              </Button>
              <div className="flex gap-2">
                <Button 
                  onClick={handleExportUsers}
                  size="sm" 
                  variant="outline"
                  className="flex-1"
                >
                  <Download className="h-4 w-4 mr-1" />
                  Exportar
                </Button>
                <Button 
                  onClick={() => navigate('/admin/users')}
                  size="sm" 
                  variant="outline"
                  className="flex-1"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Nuevo
                </Button>
              </div>
            </div>
            
            {/* Ver Diagnósticos */}
            <div className="space-y-2">
              <Button 
                onClick={() => navigate('/admin/diagnostics')}
                className="w-full flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                variant="outline"
              >
                <FileText className="h-5 w-5 mr-2 text-green-600" />
                <span className="text-sm font-medium">Ver Diagnósticos</span>
              </Button>
              <Button 
                onClick={handleExportDiagnostics}
                size="sm" 
                variant="outline"
                className="w-full"
              >
                <Download className="h-4 w-4 mr-1" />
                Exportar Datos
              </Button>
            </div>
            
            {/* Gestión de Pagos */}
            <div className="space-y-2">
              <Button 
                onClick={() => navigate('/admin/payments')}
                className="w-full flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                variant="outline"
              >
                <CreditCard className="h-5 w-5 mr-2 text-purple-600" />
                <span className="text-sm font-medium">Gestión de Pagos</span>
              </Button>
              <div className="flex gap-2">
                <Button 
                  onClick={handleSyncPayments}
                  size="sm" 
                  variant="outline"
                  className="flex-1"
                >
                  <RefreshCw className="h-4 w-4 mr-1" />
                  Sincronizar
                </Button>
                <Button 
                  onClick={handleExportPayments}
                  size="sm" 
                  variant="outline"
                  className="flex-1"
                >
                  <Download className="h-4 w-4 mr-1" />
                  Exportar
                </Button>
              </div>
            </div>
            
            {/* Ver Analytics */}
            <div className="space-y-2">
              <Button 
                onClick={() => navigate('/admin/analytics')}
                className="w-full flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                variant="outline"
              >
                <TrendingUp className="h-5 w-5 mr-2 text-orange-600" />
                <span className="text-sm font-medium">Ver Analytics</span>
              </Button>
              <Button 
                onClick={handleExportAnalytics}
                size="sm" 
                variant="outline"
                className="w-full"
              >
                <Download className="h-4 w-4 mr-1" />
                Exportar Reporte
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Actividad Reciente</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Nuevo usuario registrado</p>
                <p className="text-xs text-gray-500">Empresa ABC se registró hace 5 minutos</p>
              </div>
              <span className="text-xs text-gray-500">Hace 5 min</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Diagnóstico completado</p>
                <p className="text-xs text-gray-500">Empresa XYZ completó evaluación NIST</p>
              </div>
              <span className="text-xs text-gray-500">Hace 15 min</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Pago procesado</p>
                <p className="text-xs text-gray-500">Suscripción Pro activada - $29.990 CLP</p>
              </div>
              <span className="text-xs text-gray-500">Hace 1 hora</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminDashboardPage;

