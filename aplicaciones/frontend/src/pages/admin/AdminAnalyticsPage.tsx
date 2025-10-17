import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/utilidades/apiClient';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts';
import { 
  TrendingUp, 
  Users, 
  FileText, 
  DollarSign,
  Calendar,
  Download,
  RefreshCw,
  Eye
} from 'lucide-react';

interface AnalyticsData {
  userGrowth: Array<{
    month: string;
    users: number;
    newUsers: number;
  }>;
  revenueData: Array<{
    month: string;
    revenue: number;
    subscriptions: number;
  }>;
  subscriptionDistribution: Array<{
    name: string;
    value: number;
    color: string;
  }>;
  diagnosticStats: Array<{
    framework: string;
    completed: number;
    inProgress: number;
    total: number;
  }>;
  monthlyMetrics: {
    totalRevenue: number;
    newUsers: number;
    completedDiagnostics: number;
    activeSubscriptions: number;
    growthRate: number;
    conversionRate: number;
  };
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

const AdminAnalyticsPage: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        
        // Obtener datos reales de los endpoints
        const [overviewResponse, userGrowthResponse, revenueResponse, subscriptionResponse, diagnosticResponse] = await Promise.all([
          apiClient.get('/api/v1/admin/analytics/overview'),
          apiClient.get(`/api/v1/admin/analytics/user-growth?period=${timeRange}`),
          apiClient.get(`/api/v1/admin/analytics/revenue?period=${timeRange}`),
          apiClient.get('/api/v1/admin/analytics/subscription-distribution'),
          apiClient.get('/api/v1/admin/analytics/diagnostic-stats')
        ]);

        const realData: AnalyticsData = {
          userGrowth: userGrowthResponse.data.userGrowth,
          revenueData: revenueResponse.data.revenueData,
          subscriptionDistribution: subscriptionResponse.data.subscriptionDistribution,
          diagnosticStats: diagnosticResponse.data.diagnosticStats,
          monthlyMetrics: {
            totalRevenue: overviewResponse.data.totalRevenue,
            newUsers: overviewResponse.data.activeUsers,
            completedDiagnostics: overviewResponse.data.completedDiagnostics,
            activeSubscriptions: overviewResponse.data.activeSubscriptions,
            growthRate: overviewResponse.data.growthRate,
            conversionRate: overviewResponse.data.conversionRate
          }
        };

        setAnalyticsData(realData);
        setError(null);
      } catch (err: any) {
        console.error('Error fetching analytics:', err);
        
        // Fallback a datos mock si hay error
        const mockData: AnalyticsData = {
          userGrowth: [
            { month: 'Oct', users: 8, newUsers: 8 },
            { month: 'Nov', users: 8, newUsers: 0 },
            { month: 'Dic', users: 8, newUsers: 0 }
          ],
          revenueData: [
            { month: 'Oct', revenue: 154960, subscriptions: 5 },
            { month: 'Nov', revenue: 154960, subscriptions: 5 },
            { month: 'Dic', revenue: 154960, subscriptions: 5 }
          ],
          subscriptionDistribution: [
            { name: 'Gratuito', value: 37.5, color: '#94A3B8' },
            { name: 'Pro', value: 50, color: '#3B82F6' },
            { name: 'Empresarial', value: 12.5, color: '#8B5CF6' }
          ],
          diagnosticStats: [
            { framework: 'NIST', completed: 0, inProgress: 0, total: 0 },
            { framework: 'ISO 27001', completed: 0, inProgress: 0, total: 0 },
            { framework: 'CIS Controls', completed: 0, inProgress: 0, total: 0 },
            { framework: 'COBIT', completed: 0, inProgress: 0, total: 0 }
          ],
          monthlyMetrics: {
            totalRevenue: 154960,
            newUsers: 8,
            completedDiagnostics: 0,
            activeSubscriptions: 5,
            growthRate: 0,
            conversionRate: 62.5
          }
        };

        setAnalyticsData(mockData);
        setError(err.response?.data?.detail || 'Error al cargar analytics');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [timeRange]);

  const formatCurrency = (amount: number) => {
    // Formatear con separadores de miles para CLP
    return `$${Math.round(amount).toLocaleString('es-CL')} CLP`;
  };

  const StatCard = ({ 
    title, 
    value, 
    icon: Icon, 
    color = 'blue',
    subtitle,
    trend
  }: {
    title: string;
    value: string | number;
    icon: React.ElementType;
    color?: 'blue' | 'green' | 'orange' | 'red' | 'purple';
    subtitle?: string;
    trend?: {
      value: number;
      isPositive: boolean;
    };
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
          {trend && (
            <div className={`flex items-center text-xs mt-1 ${
              trend.isPositive ? 'text-green-600' : 'text-red-600'
            }`}>
              <TrendingUp className={`h-3 w-3 mr-1 ${
                trend.isPositive ? '' : 'rotate-180'
              }`} />
              {trend.isPositive ? '+' : ''}{trend.value}%
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-2">Cargando analytics...</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
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
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
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
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-2">
            Análisis y estadísticas avanzadas de la plataforma
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Calendar className="h-4 w-4 text-gray-400" />
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as any)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="7d">Últimos 7 días</option>
              <option value="30d">Últimos 30 días</option>
              <option value="90d">Últimos 90 días</option>
              <option value="1y">Último año</option>
            </select>
          </div>
          
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Actualizar
          </Button>
          
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      {analyticsData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Ingresos Totales"
            value={formatCurrency(analyticsData.monthlyMetrics.totalRevenue)}
            icon={DollarSign}
            color="green"
            subtitle="Este mes"
            trend={{
              value: analyticsData.monthlyMetrics.growthRate,
              isPositive: analyticsData.monthlyMetrics.growthRate > 0
            }}
          />
          
          <StatCard
            title="Nuevos Usuarios"
            value={analyticsData.monthlyMetrics.newUsers}
            icon={Users}
            color="blue"
            subtitle="Último mes"
            trend={{
              value: 12.5,
              isPositive: true
            }}
          />
          
          <StatCard
            title="Diagnósticos Completados"
            value={analyticsData.monthlyMetrics.completedDiagnostics}
            icon={FileText}
            color="purple"
            subtitle="Este mes"
            trend={{
              value: 8.3,
              isPositive: true
            }}
          />
          
          <StatCard
            title="Tasa de Conversión"
            value={`${analyticsData.monthlyMetrics.conversionRate}%`}
            icon={TrendingUp}
            color="orange"
            subtitle="Gratuito a Pro"
            trend={{
              value: 2.1,
              isPositive: true
            }}
          />
        </div>
      )}

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Growth Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Crecimiento de Usuarios</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={analyticsData?.userGrowth || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'users' ? `${value} usuarios` : `${value} nuevos`,
                    name === 'users' ? 'Total' : 'Nuevos'
                  ]}
                />
                <Area 
                  type="monotone" 
                  dataKey="users" 
                  stackId="1" 
                  stroke="#3B82F6" 
                  fill="#3B82F6" 
                  fillOpacity={0.6}
                />
                <Area 
                  type="monotone" 
                  dataKey="newUsers" 
                  stackId="2" 
                  stroke="#10B981" 
                  fill="#10B981" 
                  fillOpacity={0.6}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Revenue Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Ingresos Mensuales</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analyticsData?.revenueData || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`} />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'revenue' ? formatCurrency(value as number) : `${value} suscripciones`,
                    name === 'revenue' ? 'Ingresos' : 'Suscripciones'
                  ]}
                />
                <Line 
                  type="monotone" 
                  dataKey="revenue" 
                  stroke="#10B981" 
                  strokeWidth={3}
                  dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Subscription Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Distribución de Suscripciones</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analyticsData?.subscriptionDistribution || []}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {(analyticsData?.subscriptionDistribution || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value}%`, 'Porcentaje']} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Diagnostic Stats */}
        <Card>
          <CardHeader>
            <CardTitle>Diagnósticos por Framework</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {(analyticsData?.diagnosticStats || []).map((stat, index) => (
                <div key={stat.framework} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div 
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    ></div>
                    <span className="text-sm font-medium">{stat.framework}</span>
                  </div>
                  <div className="flex items-center space-x-4">
                    <Badge variant="outline" className="text-green-600 border-green-200">
                      {stat.completed} completados
                    </Badge>
                    <Badge variant="outline" className="text-orange-600 border-orange-200">
                      {stat.inProgress} en progreso
                    </Badge>
                    <span className="text-sm text-gray-500">
                      {stat.total} total
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Actividad Reciente</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Nueva suscripción Pro activada</p>
                <p className="text-xs text-gray-500">Empresa ABC - hace 2 horas</p>
              </div>
              <Button variant="ghost" size="sm">
                <Eye className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Diagnóstico NIST completado</p>
                <p className="text-xs text-gray-500">TechCorp Chile - hace 4 horas</p>
              </div>
              <Button variant="ghost" size="sm">
                <Eye className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Usuario registrado</p>
                <p className="text-xs text-gray-500">Startup Innovadora - hace 6 horas</p>
              </div>
              <Button variant="ghost" size="sm">
                <Eye className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminAnalyticsPage;
