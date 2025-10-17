import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/utilidades/apiClient';
import { 
  Search, 
  Filter, 
  Download, 
  CreditCard,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Calendar,
  Eye,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';

interface Payment {
  id: string;
  organizacion: string;
  suscripcion: string;
  monto: number;
  moneda: string;
  estado: 'active' | 'canceled' | 'past_due' | 'incomplete';
  metodo_pago: string;
  fecha_creacion: string;
  proxima_facturacion: string;
  ciclo: string;
}

interface PaymentStats {
  totalRevenue: number;
  monthlyRevenue: number;
  activeSubscriptions: number;
  canceledSubscriptions: number;
  averageRevenue: number;
  growthRate: number;
}

const AdminPaymentsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [payments, setPayments] = useState<Payment[]>([]);
  const [stats, setStats] = useState<PaymentStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const [paymentsResponse, statsResponse] = await Promise.all([
          apiClient.get('/api/v1/admin/payments'),
          apiClient.get('/api/v1/admin/payments/stats')
        ]);
        
        setPayments(paymentsResponse.data.payments);
        setStats(statsResponse.data);
        setError(null);
      } catch (err: any) {
        console.error('Error fetching payments:', err);
        
        // Fallback a datos mock si hay error (valores realistas)
        const mockPayments: Payment[] = [
          {
            id: '1',
            organizacion: 'Empresa ABC',
            suscripcion: 'pro',
            monto: 24990, // $24,990 CLP
            moneda: 'CLP',
            estado: 'active',
            metodo_pago: 'Tarjeta terminada en 4242',
            fecha_creacion: '2025-09-15T08:00:00Z',
            proxima_facturacion: '2025-11-15T08:00:00Z',
            ciclo: 'mensual'
          },
          {
            id: '2',
            organizacion: 'TechCorp Chile',
            suscripcion: 'empresarial',
            monto: 79990, // $79,990 CLP
            moneda: 'CLP',
            estado: 'active',
            metodo_pago: 'Transferencia bancaria',
            fecha_creacion: '2025-09-10T14:30:00Z',
            proxima_facturacion: '2025-11-10T14:30:00Z',
            ciclo: 'mensual'
          },
          {
            id: '3',
            organizacion: 'Consultora Digital',
            suscripcion: 'pro',
            monto: 24990, // $24,990 CLP
            moneda: 'CLP',
            estado: 'active',
            metodo_pago: 'Tarjeta terminada en 5555',
            fecha_creacion: '2025-09-05T09:15:00Z',
            proxima_facturacion: '2025-11-05T09:15:00Z',
            ciclo: 'mensual'
          },
          {
            id: '4',
            organizacion: 'Startup Innovadora',
            suscripcion: 'gratuito',
            monto: 0,
            moneda: 'CLP',
            estado: 'active',
            metodo_pago: 'Sin método de pago',
            fecha_creacion: '2025-08-20T11:00:00Z',
            proxima_facturacion: 'N/A',
            ciclo: 'gratuito'
          }
        ];

        const mockStats: PaymentStats = {
          totalRevenue: 129970, // $129,970 CLP (24,990 + 79,990 + 24,990)
          monthlyRevenue: 129970,
          activeSubscriptions: 4,
          canceledSubscriptions: 0,
          averageRevenue: 43323, // Promedio realista
          growthRate: 8.7 // Crecimiento más realista
        };

        setPayments(mockPayments);
        setStats(mockStats);
        setError(err.response?.data?.detail || 'Error al cargar datos de pagos');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatCurrency = (amount: number, currency: string = 'CLP') => {
    if (amount === 0) return 'Gratuito';
    
    // Formatear con separadores de miles para CLP
    return `$${Math.round(amount).toLocaleString('es-CL')} CLP`;
  };

  const formatDate = (dateString: string) => {
    if (dateString === 'N/A') return 'N/A';
    return new Date(dateString).toLocaleDateString('es-CL', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      active: 'bg-green-100 text-green-800',
      canceled: 'bg-red-100 text-red-800',
      past_due: 'bg-orange-100 text-orange-800',
      incomplete: 'bg-yellow-100 text-yellow-800',
    };
    
    const labels = {
      active: 'Activa',
      canceled: 'Cancelada',
      past_due: 'Vencida',
      incomplete: 'Incompleta',
    };
    
    return (
      <Badge className={variants[status as keyof typeof variants]}>
        {labels[status as keyof typeof labels]}
      </Badge>
    );
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'canceled':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      case 'past_due':
        return <Clock className="h-4 w-4 text-orange-600" />;
      case 'incomplete':
        return <RefreshCw className="h-4 w-4 text-yellow-600" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-600" />;
    }
  };

  const filteredPayments = payments.filter(payment => {
    const matchesSearch = payment.organizacion.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         payment.suscripcion.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterStatus === 'all' || payment.estado === filterStatus;
    
    return matchesSearch && matchesFilter;
  });

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
    trend?: 'up' | 'down' | 'neutral';
  }) => {
    const colorClasses = {
      blue: 'bg-blue-50 text-blue-600',
      green: 'bg-green-50 text-green-600',
      orange: 'bg-orange-50 text-orange-600',
      red: 'bg-red-50 text-red-600',
      purple: 'bg-purple-50 text-purple-600',
    };

    const trendIcon = trend === 'up' ? <TrendingUp className="h-4 w-4 text-green-600" /> : 
                     trend === 'down' ? <TrendingDown className="h-4 w-4 text-red-600" /> : null;

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
          <div className="flex items-center space-x-2">
            <div className="text-2xl font-bold text-gray-900">{value}</div>
            {trendIcon}
          </div>
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
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Pagos</h1>
          <p className="text-gray-600 mt-2">Cargando datos de pagos...</p>
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
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Pagos</h1>
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
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Pagos</h1>
          <p className="text-gray-600 mt-2">
            Administra suscripciones, pagos y facturación
          </p>
        </div>
        
        <div className="flex space-x-3">
          <Button variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Sincronizar
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Ingresos Totales"
              value={formatCurrency(stats.totalRevenue)}
              icon={DollarSign}
              color="green"
              subtitle="Este mes"
            />
          
          <StatCard
            title="Suscripciones Activas"
            value={stats.activeSubscriptions}
            icon={CreditCard}
            color="blue"
            subtitle={`${stats.canceledSubscriptions} canceladas`}
          />
          
          <StatCard
            title="Ingreso Promedio"
            value={formatCurrency(stats.averageRevenue)}
            icon={TrendingUp}
            color="purple"
            subtitle="Por suscripción"
          />
          
          <StatCard
            title="Crecimiento"
            value={`+${stats.growthRate}%`}
            icon={TrendingUp}
            color="green"
            subtitle="vs mes anterior"
            trend="up"
          />
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex items-center space-x-2 flex-1">
              <Search className="h-4 w-4 text-gray-400" />
              <Input
                placeholder="Buscar por organización o suscripción..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="border-gray-300"
              />
            </div>
            
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm"
              >
                <option value="all">Todos los estados</option>
                <option value="active">Activas</option>
                <option value="canceled">Canceladas</option>
                <option value="past_due">Vencidas</option>
                <option value="incomplete">Incompletas</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Payments Table */}
      <Card>
        <CardHeader>
          <CardTitle>
            Suscripciones ({filteredPayments.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Organización</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Suscripción</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Monto</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Estado</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Método de Pago</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Próxima Facturación</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredPayments.map((payment) => (
                  <tr key={payment.id} className="border-b hover:bg-gray-50">
                    <td className="py-4 px-4">
                      <div className="font-medium text-gray-900">{payment.organizacion}</div>
                    </td>
                    <td className="py-4 px-4">
                      <Badge variant="outline">{payment.suscripcion}</Badge>
                    </td>
                    <td className="py-4 px-4 text-gray-900">
                      {formatCurrency(payment.monto, payment.moneda)}
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(payment.estado)}
                        {getStatusBadge(payment.estado)}
                      </div>
                    </td>
                    <td className="py-4 px-4 text-sm text-gray-600">
                      {payment.metodo_pago}
                    </td>
                    <td className="py-4 px-4 text-sm text-gray-600">
                      {formatDate(payment.proxima_facturacion)}
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center space-x-2">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <RefreshCw className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminPaymentsPage;
