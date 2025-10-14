import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, FileText, CreditCard, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';

interface DashboardStats {
  totalUsers: number;
  activeUsers: number;
  totalDiagnostics: number;
  monthlyRevenue: number;
  pendingDiagnostics: number;
  completedDiagnostics: number;
}

const AdminDashboardPage: React.FC = () => {
  // TODO: Conectar con API real
  const stats: DashboardStats = {
    totalUsers: 1247,
    activeUsers: 892,
    totalDiagnostics: 3456,
    monthlyRevenue: 2845000, // CLP
    pendingDiagnostics: 23,
    completedDiagnostics: 3433,
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
    }).format(amount);
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
          value="99.3%"
          icon={CheckCircle}
          color="green"
          subtitle="Diagnósticos completados"
        />
        
        <StatCard
          title="Crecimiento Mensual"
          value="+12.5%"
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
            <button className="flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <Users className="h-5 w-5 mr-2 text-blue-600" />
              <span className="text-sm font-medium">Gestionar Usuarios</span>
            </button>
            
            <button className="flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <FileText className="h-5 w-5 mr-2 text-green-600" />
              <span className="text-sm font-medium">Ver Diagnósticos</span>
            </button>
            
            <button className="flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <CreditCard className="h-5 w-5 mr-2 text-purple-600" />
              <span className="text-sm font-medium">Gestión de Pagos</span>
            </button>
            
            <button className="flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <TrendingUp className="h-5 w-5 mr-2 text-orange-600" />
              <span className="text-sm font-medium">Ver Analytics</span>
            </button>
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
