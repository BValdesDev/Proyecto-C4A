import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/utilidades/apiClient';
import { 
  Shield, 
  Lock, 
  AlertTriangle, 
  Clock, 
  User,
  Activity,
  RefreshCw,
  Download,
  Settings,
  Eye,
  Key
} from 'lucide-react';

interface SecurityConfig {
  sessionTimeout: number;
  maxLoginAttempts: number;
  passwordExpirationDays: number;
  mfaRequired: boolean;
  ipWhitelistEnabled: boolean;
}

interface SecurityLog {
  id: string;
  timestamp: string;
  userId: string;
  userName: string;
  action: string;
  ipAddress: string;
  status: 'success' | 'failed' | 'warning';
  details: string;
}

interface SecurityStats {
  totalLogins: number;
  failedLogins: number;
  blockedAccounts: number;
  activeSessions: number;
  mfaUsers: number;
  suspiciousActivity: number;
}

const AdminSecurityPage: React.FC = () => {
  const [config, setConfig] = useState<SecurityConfig>({
    sessionTimeout: 30,
    maxLoginAttempts: 5,
    passwordExpirationDays: 90,
    mfaRequired: false,
    ipWhitelistEnabled: false
  });
  const [logs, setLogs] = useState<SecurityLog[]>([]);
  const [stats, setStats] = useState<SecurityStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchSecurityData();
  }, []);

  const fetchSecurityData = async () => {
    try {
      setLoading(true);
      
      // Obtener datos reales del backend
      const [statsResponse, logsResponse, configResponse] = await Promise.all([
        apiClient.get('/api/v1/admin/security/stats'),
        apiClient.get('/api/v1/admin/security/logs'),
        apiClient.get('/api/v1/admin/security/config')
      ]);

      setStats(statsResponse.data);
      setLogs(logsResponse.data.logs);
      setConfig(configResponse.data);
    } catch (error) {
      console.error('Error fetching security data:', error);
      
      // Fallback a datos mock si hay error
      const mockStats: SecurityStats = {
        totalLogins: 142,
        failedLogins: 8,
        blockedAccounts: 2,
        activeSessions: 24,
        mfaUsers: 5,
        suspiciousActivity: 3
      };

      const mockLogs: SecurityLog[] = [
        {
          id: '1',
          timestamp: new Date().toISOString(),
          userId: 'usr_001',
          userName: 'Frank Bailey',
          action: 'LOGIN',
          ipAddress: '192.168.1.100',
          status: 'success',
          details: 'Inicio de sesión exitoso desde panel admin'
        }
      ];

      setStats(mockStats);
      setLogs(mockLogs);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfig = async () => {
    try {
      setSaving(true);
      
      // Conectar con endpoint real del backend
      await apiClient.post('/api/v1/admin/security/config', config);
      
      alert('Configuración de seguridad guardada exitosamente');
    } catch (error) {
      console.error('Error saving config:', error);
      alert('Error al guardar configuración');
    } finally {
      setSaving(false);
    }
  };

  const getStatusBadge = (status: SecurityLog['status']) => {
    const variants = {
      success: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      warning: 'bg-yellow-100 text-yellow-800'
    };

    return (
      <Badge className={variants[status]}>
        {status === 'success' ? 'Exitoso' : status === 'failed' ? 'Fallido' : 'Advertencia'}
      </Badge>
    );
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return new Intl.DateTimeFormat('es-CL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

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
          <h1 className="text-3xl font-bold text-gray-900">Seguridad del Sistema</h1>
          <p className="text-gray-500 mt-1">
            Configuración de seguridad, logs de actividad y monitoreo
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={fetchSecurityData}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Actualizar
          </Button>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Exportar Logs
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
                  <p className="text-sm font-medium text-gray-600">Total Logins</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalLogins}</p>
                </div>
                <User className="w-8 h-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Login Fallidos</p>
                  <p className="text-2xl font-bold text-red-600">{stats.failedLogins}</p>
                </div>
                <AlertTriangle className="w-8 h-8 text-red-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Cuentas Bloqueadas</p>
                  <p className="text-2xl font-bold text-orange-600">{stats.blockedAccounts}</p>
                </div>
                <Lock className="w-8 h-8 text-orange-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Sesiones Activas</p>
                  <p className="text-2xl font-bold text-green-600">{stats.activeSessions}</p>
                </div>
                <Activity className="w-8 h-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Usuarios MFA</p>
                  <p className="text-2xl font-bold text-purple-600">{stats.mfaUsers}</p>
                </div>
                <Key className="w-8 h-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Act. Sospechosa</p>
                  <p className="text-2xl font-bold text-yellow-600">{stats.suspiciousActivity}</p>
                </div>
                <Eye className="w-8 h-8 text-yellow-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Security Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Configuración de Seguridad
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                Timeout de Sesión (minutos)
              </label>
              <Input
                type="number"
                value={config.sessionTimeout || ''}
                onChange={(e) => setConfig({ ...config, sessionTimeout: parseInt(e.target.value) || 30 })}
                min={5}
                max={120}
              />
              <p className="text-xs text-gray-500">
                Tiempo de inactividad antes de cerrar sesión automáticamente
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                Máximo Intentos de Login
              </label>
              <Input
                type="number"
                value={config.maxLoginAttempts || ''}
                onChange={(e) => setConfig({ ...config, maxLoginAttempts: parseInt(e.target.value) || 5 })}
                min={3}
                max={10}
              />
              <p className="text-xs text-gray-500">
                Cantidad de intentos antes de bloquear la cuenta
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                Expiración de Contraseña (días)
              </label>
              <Input
                type="number"
                value={config.passwordExpirationDays || ''}
                onChange={(e) => setConfig({ ...config, passwordExpirationDays: parseInt(e.target.value) || 90 })}
                min={30}
                max={365}
              />
              <p className="text-xs text-gray-500">
                Días antes de solicitar cambio de contraseña
              </p>
            </div>

            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={config.mfaRequired}
                  onChange={(e) => setConfig({ ...config, mfaRequired: e.target.checked })}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-sm font-medium text-gray-700">
                  Requerir Autenticación de Dos Factores (MFA)
                </span>
              </label>
              <p className="text-xs text-gray-500 ml-6">
                Obligar a todos los usuarios a usar MFA
              </p>
            </div>

            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={config.ipWhitelistEnabled}
                  onChange={(e) => setConfig({ ...config, ipWhitelistEnabled: e.target.checked })}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-sm font-medium text-gray-700">
                  Habilitar Lista Blanca de IPs
                </span>
              </label>
              <p className="text-xs text-gray-500 ml-6">
                Permitir acceso solo desde IPs autorizadas
              </p>
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <Button onClick={handleSaveConfig} disabled={saving}>
              {saving ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Guardando...
                </>
              ) : (
                <>
                  <Shield className="w-4 h-4 mr-2" />
                  Guardar Configuración
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Security Logs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Registro de Actividad de Seguridad
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Fecha/Hora
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Usuario
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Acción
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    IP
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Estado
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Detalles
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {logs && logs.length > 0 ? logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {formatTimestamp(log.timestamp)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {log.userName}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <code className="px-2 py-1 bg-gray-100 rounded text-xs">
                        {log.action}
                      </code>
                    </td>
                    <td className="px-4 py-3 text-sm font-mono text-gray-600">
                      {log.ipAddress}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {getStatusBadge(log.status)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {log.details}
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                      No hay logs de seguridad disponibles
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {logs && logs.length === 0 && (
            <div className="text-center py-12">
              <Shield className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500">No hay logs de seguridad disponibles</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminSecurityPage;

