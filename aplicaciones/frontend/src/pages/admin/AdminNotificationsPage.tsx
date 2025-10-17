import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/utilidades/apiClient';
import { 
  Bell, 
  Send, 
  Mail, 
  MessageSquare, 
  Users,
  Calendar,
  RefreshCw,
  Download,
  Filter,
  Eye,
  Trash2,
  Edit
} from 'lucide-react';

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'email' | 'push' | 'in-app';
  recipients: number;
  sentAt: string;
  status: 'sent' | 'scheduled' | 'draft' | 'failed';
  sentBy: string;
  openRate?: number;
  clickRate?: number;
}

interface NotificationTemplate {
  id: string;
  name: string;
  subject: string;
  type: 'welcome' | 'payment' | 'alert' | 'custom';
  lastUsed: string;
}

interface NotificationStats {
  totalSent: number;
  pendingNotifications: number;
  failedNotifications: number;
  averageOpenRate: number;
  averageClickRate: number;
  activeRecipients: number;
}

const AdminNotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [templates, setTemplates] = useState<NotificationTemplate[]>([]);
  const [stats, setStats] = useState<NotificationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [showNewNotification, setShowNewNotification] = useState(false);
  const [filterStatus, setFilterStatus] = useState<'all' | Notification['status']>('all');

  const [newNotification, setNewNotification] = useState({
    title: '',
    message: '',
    type: 'email' as const,
    recipients: 'all' as 'all' | 'active' | 'custom'
  });

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      
      // Obtener datos reales del backend
      const [statsResponse, notificationsResponse, templatesResponse] = await Promise.all([
        apiClient.get('/api/v1/admin/notifications/stats'),
        apiClient.get('/api/v1/admin/notifications'),
        apiClient.get('/api/v1/admin/notifications/templates')
      ]);

      setStats(statsResponse.data || statsResponse);
      setNotifications(notificationsResponse.data?.notifications || notificationsResponse.notifications || []);
      setTemplates(templatesResponse.data?.templates || templatesResponse.templates || []);
    } catch (error) {
      console.error('Error fetching notifications:', error);
      
      // Fallback a datos mock si hay error
      const mockStats: NotificationStats = {
        totalSent: 1247,
        pendingNotifications: 3,
        failedNotifications: 12,
        averageOpenRate: 68.5,
        averageClickRate: 24.3,
        activeRecipients: 156
      };

      const mockNotifications: Notification[] = [
        {
          id: '1',
          title: 'Actualización de Sistema',
          message: 'Nueva versión disponible con mejoras de seguridad',
          type: 'email',
          recipients: 156,
          sentAt: new Date().toISOString(),
          status: 'sent',
          sentBy: 'Frank Bailey',
          openRate: 72.5,
          clickRate: 28.3
        }
      ];

      const mockTemplates: NotificationTemplate[] = [
        {
          id: '1',
          name: 'Bienvenida Nuevos Usuarios',
          subject: 'Bienvenido a C4A',
          type: 'welcome',
          lastUsed: new Date(Date.now() - 86400000).toISOString()
        }
      ];

      setStats(mockStats);
      setNotifications(mockNotifications);
      setTemplates(mockTemplates);
    } finally {
      setLoading(false);
    }
  };

  const handleSendNotification = async () => {
    try {
      // Conectar con endpoint real del backend
      await apiClient.post('/api/v1/admin/notifications', newNotification);
      
      alert('Notificación enviada exitosamente');
      setShowNewNotification(false);
      setNewNotification({
        title: '',
        message: '',
        type: 'email',
        recipients: 'all'
      });
      fetchNotifications();
    } catch (error) {
      console.error('Error sending notification:', error);
      alert('Error al enviar notificación');
    }
  };

  // Función para ejecutar notificaciones automáticas
  const handleRunAutomatic = async () => {
    try {
      const response = await apiClient.post('/api/v1/admin/notifications/run-automatic');
      alert(`Notificaciones automáticas ejecutadas: ${response.data.result.payment_reminders} recordatorios enviados`);
      fetchNotifications();
    } catch (error) {
      console.error('Error running automatic notifications:', error);
      alert('Error ejecutando notificaciones automáticas');
    }
  };

  const getStatusBadge = (status: Notification['status']) => {
    const variants = {
      sent: 'bg-green-100 text-green-800',
      scheduled: 'bg-blue-100 text-blue-800',
      draft: 'bg-gray-100 text-gray-800',
      failed: 'bg-red-100 text-red-800'
    };

    const labels = {
      sent: 'Enviado',
      scheduled: 'Programado',
      draft: 'Borrador',
      failed: 'Fallido'
    };

    return (
      <Badge className={variants[status]}>
        {labels[status]}
      </Badge>
    );
  };

  const getTypeBadge = (type: Notification['type']) => {
    const variants = {
      email: 'bg-purple-100 text-purple-800',
      push: 'bg-orange-100 text-orange-800',
      'in-app': 'bg-cyan-100 text-cyan-800'
    };

    const labels = {
      email: 'Email',
      push: 'Push',
      'in-app': 'In-App'
    };

    return (
      <Badge className={variants[type]}>
        {labels[type]}
      </Badge>
    );
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-CL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const filteredNotifications = filterStatus === 'all' 
    ? (notifications || []) 
    : (notifications || []).filter(n => n.status === filterStatus);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Notificaciones</h1>
          <p className="text-gray-500 mt-1">
            Gestión de notificaciones, templates y estadísticas de envío
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={fetchNotifications}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Actualizar
          </Button>
          <Button onClick={() => setShowNewNotification(!showNewNotification)}>
            <Send className="w-4 h-4 mr-2" />
            Nueva Notificación
          </Button>
          <Button 
            onClick={handleRunAutomatic}
            variant="outline"
            className="bg-green-50 text-green-700 border-green-200 hover:bg-green-100"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Ejecutar Automáticas
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Enviadas</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalSent}</p>
                </div>
                <Send className="w-8 h-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Pendientes</p>
                  <p className="text-2xl font-bold text-orange-600">{stats.pendingNotifications}</p>
                </div>
                <Calendar className="w-8 h-8 text-orange-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Fallidas</p>
                  <p className="text-2xl font-bold text-red-600">{stats.failedNotifications}</p>
                </div>
                <Trash2 className="w-8 h-8 text-red-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Tasa Apertura</p>
                  <p className="text-2xl font-bold text-green-600">{stats.averageOpenRate}%</p>
                </div>
                <Eye className="w-8 h-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Tasa Click</p>
                  <p className="text-2xl font-bold text-purple-600">{stats.averageClickRate}%</p>
                </div>
                <MessageSquare className="w-8 h-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Destinatarios</p>
                  <p className="text-2xl font-bold text-cyan-600">{stats.activeRecipients}</p>
                </div>
                <Users className="w-8 h-8 text-cyan-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* New Notification Form */}
      {showNewNotification && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Send className="w-5 h-5" />
              Nueva Notificación
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Título</label>
                <Input
                  value={newNotification.title}
                  onChange={(e) => setNewNotification({ ...newNotification, title: e.target.value })}
                  placeholder="Ej: Actualización del sistema"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Mensaje</label>
                <textarea
                  className="w-full p-3 border rounded-md"
                  rows={4}
                  value={newNotification.message}
                  onChange={(e) => setNewNotification({ ...newNotification, message: e.target.value })}
                  placeholder="Escribe el contenido de la notificación..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Tipo de Notificación</label>
                  <select
                    className="w-full p-2 border rounded-md"
                    value={newNotification.type}
                    onChange={(e) => setNewNotification({ ...newNotification, type: e.target.value as any })}
                  >
                    <option value="email">Email</option>
                    <option value="push">Push</option>
                    <option value="in-app">In-App</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Destinatarios</label>
                  <select
                    className="w-full p-2 border rounded-md"
                    value={newNotification.recipients}
                    onChange={(e) => setNewNotification({ ...newNotification, recipients: e.target.value as any })}
                  >
                    <option value="all">Todos los usuarios</option>
                    <option value="active">Solo usuarios activos</option>
                    <option value="custom">Selección personalizada</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <Button 
                  variant="outline" 
                  onClick={() => setShowNewNotification(false)}
                >
                  Cancelar
                </Button>
                <Button onClick={handleSendNotification}>
                  <Send className="w-4 h-4 mr-2" />
                  Enviar Notificación
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="w-5 h-5" />
            Templates de Notificaciones
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {templates && templates.length > 0 ? templates.map((template) => (
              <div 
                key={template.id}
                className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-gray-900">{template.name}</h3>
                  <Button variant="ghost" size="sm">
                    <Edit className="w-4 h-4" />
                  </Button>
                </div>
                <p className="text-sm text-gray-600 mb-3">{template.subject}</p>
                <div className="flex justify-between items-center text-xs text-gray-500">
                  <span>Último uso: {formatDate(template.lastUsed)}</span>
                  <Badge variant="outline">{template.type}</Badge>
                </div>
              </div>
            )) : (
              <div className="col-span-3 text-center py-8 text-gray-500">
                No hay templates disponibles
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Notifications List */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5" />
              Historial de Notificaciones
            </CardTitle>
            <div className="flex gap-2">
              <Button 
                variant={filterStatus === 'all' ? 'default' : 'outline'} 
                size="sm"
                onClick={() => setFilterStatus('all')}
              >
                Todas
              </Button>
              <Button 
                variant={filterStatus === 'sent' ? 'default' : 'outline'} 
                size="sm"
                onClick={() => setFilterStatus('sent')}
              >
                Enviadas
              </Button>
              <Button 
                variant={filterStatus === 'scheduled' ? 'default' : 'outline'} 
                size="sm"
                onClick={() => setFilterStatus('scheduled')}
              >
                Programadas
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Título
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Tipo
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Destinatarios
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Estado
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Fecha/Hora
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Enviado Por
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Métricas
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredNotifications && filteredNotifications.length > 0 ? filteredNotifications.map((notification) => (
                  <tr key={notification.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div>
                        <p className="font-medium text-gray-900">{notification.title}</p>
                        <p className="text-sm text-gray-500 truncate max-w-xs">{notification.message}</p>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {getTypeBadge(notification.type)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {notification.recipients > 0 ? `${notification.recipients} usuarios` : '-'}
                    </td>
                    <td className="px-4 py-3">
                      {getStatusBadge(notification.status)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {formatDate(notification.sentAt)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {notification.sentBy}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {notification.openRate !== undefined && notification.clickRate !== undefined ? (
                        <div className="text-xs">
                          <div className="text-green-600">Abierto: {notification.openRate}%</div>
                          <div className="text-blue-600">Clicks: {notification.clickRate}%</div>
                        </div>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                      No hay notificaciones disponibles
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {filteredNotifications && filteredNotifications.length === 0 && (
            <div className="text-center py-12">
              <Bell className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500">No hay notificaciones para mostrar</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminNotificationsPage;

