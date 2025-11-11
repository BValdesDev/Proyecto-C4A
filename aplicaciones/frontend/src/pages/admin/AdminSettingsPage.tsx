import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { 
  Settings, 
  Save, 
  Shield, 
  Mail, 
  Globe,
  Database,
  Bell,
  Palette
} from 'lucide-react';

interface SystemSettings {
  // General
  siteName: string;
  siteDescription: string;
  supportEmail: string;
  contactPhone: string;
  
  // Security
  passwordMinLength: number;
  sessionTimeout: number;
  maxLoginAttempts: number;
  enableTwoFactor: boolean;
  requireEmailVerification: boolean;
  
  // Email
  smtpHost: string;
  smtpPort: number;
  smtpUser: string;
  smtpPassword: string;
  emailFromName: string;
  
  // Features
  enableRegistration: boolean;
  enablePublicDiagnostics: boolean;
  enableNotifications: boolean;
  maintenanceMode: boolean;
  
  // Appearance
  primaryColor: string;
  logoUrl: string;
  faviconUrl: string;
}

const AdminSettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState<SystemSettings>({
    // General
    siteName: 'C4A SaaS',
    siteDescription: 'Plataforma de evaluación de ciberseguridad para PyMEs',
    supportEmail: 'soporte@c4a.cl',
    contactPhone: '+56 9 1234 5678',
    
    // Security
    passwordMinLength: 8,
    sessionTimeout: 30,
    maxLoginAttempts: 5,
    enableTwoFactor: true,
    requireEmailVerification: true,
    
    // Email
    smtpHost: 'smtp.gmail.com',
    smtpPort: 587,
    smtpUser: 'noreply@c4a.cl',
    smtpPassword: '********',
    emailFromName: 'C4A Soporte',
    
    // Features
    enableRegistration: true,
    enablePublicDiagnostics: false,
    enableNotifications: true,
    maintenanceMode: false,
    
    // Appearance
    primaryColor: '#3B82F6',
    logoUrl: '/logo.png',
    faviconUrl: '/favicon.ico',
  });

  const [hasChanges, setHasChanges] = useState(false);

  const handleSettingChange = (key: keyof SystemSettings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSave = () => {
    // TODO: Implementar guardado en API
    setHasChanges(false);
    // Mostrar toast de éxito
  };

  const tabs = [
    { id: 'general', label: 'General', icon: Settings },
    { id: 'security', label: 'Seguridad', icon: Shield },
    { id: 'email', label: 'Email', icon: Mail },
    { id: 'features', label: 'Funciones', icon: Globe },
    { id: 'appearance', label: 'Apariencia', icon: Palette },
  ];

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            Configuración General
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre del Sitio
            </label>
            <Input
              value={settings.siteName}
              onChange={(e) => handleSettingChange('siteName', e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descripción del Sitio
            </label>
            <Input
              value={settings.siteDescription}
              onChange={(e) => handleSettingChange('siteDescription', e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email de Soporte
            </label>
            <Input
              type="email"
              value={settings.supportEmail}
              onChange={(e) => handleSettingChange('supportEmail', e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Teléfono de Contacto
            </label>
            <Input
              value={settings.contactPhone}
              onChange={(e) => handleSettingChange('contactPhone', e.target.value)}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Shield className="h-5 w-5 mr-2" />
            Configuración de Seguridad
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Longitud Mínima de Contraseña
            </label>
            <Input
              type="number"
              value={settings.passwordMinLength}
              onChange={(e) => handleSettingChange('passwordMinLength', parseInt(e.target.value))}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tiempo de Expiración de Sesión (minutos)
            </label>
            <Input
              type="number"
              value={settings.sessionTimeout}
              onChange={(e) => handleSettingChange('sessionTimeout', parseInt(e.target.value))}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Máximo Intentos de Login
            </label>
            <Input
              type="number"
              value={settings.maxLoginAttempts}
              onChange={(e) => handleSettingChange('maxLoginAttempts', parseInt(e.target.value))}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Habilitar Autenticación de Dos Factores
              </label>
              <p className="text-sm text-gray-500">Requerir 2FA para todos los usuarios</p>
            </div>
            <Switch
              checked={settings.enableTwoFactor}
              onCheckedChange={(checked) => handleSettingChange('enableTwoFactor', checked)}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Requerir Verificación de Email
              </label>
              <p className="text-sm text-gray-500">Los usuarios deben verificar su email</p>
            </div>
            <Switch
              checked={settings.requireEmailVerification}
              onCheckedChange={(checked) => handleSettingChange('requireEmailVerification', checked)}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderEmailSettings = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Mail className="h-5 w-5 mr-2" />
            Configuración de Email
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Servidor SMTP
              </label>
              <Input
                value={settings.smtpHost}
                onChange={(e) => handleSettingChange('smtpHost', e.target.value)}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Puerto SMTP
              </label>
              <Input
                type="number"
                value={settings.smtpPort}
                onChange={(e) => handleSettingChange('smtpPort', parseInt(e.target.value))}
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Usuario SMTP
            </label>
            <Input
              value={settings.smtpUser}
              onChange={(e) => handleSettingChange('smtpUser', e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contraseña SMTP
            </label>
            <Input
              type="password"
              value={settings.smtpPassword}
              onChange={(e) => handleSettingChange('smtpPassword', e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre del Remitente
            </label>
            <Input
              value={settings.emailFromName}
              onChange={(e) => handleSettingChange('emailFromName', e.target.value)}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderFeaturesSettings = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Globe className="h-5 w-5 mr-2" />
            Funciones del Sistema
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Habilitar Registro de Usuarios
              </label>
              <p className="text-sm text-gray-500">Permitir nuevos registros</p>
            </div>
            <Switch
              checked={settings.enableRegistration}
              onCheckedChange={(checked) => handleSettingChange('enableRegistration', checked)}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Habilitar Diagnósticos Públicos
              </label>
              <p className="text-sm text-gray-500">Permitir diagnósticos sin registro</p>
            </div>
            <Switch
              checked={settings.enablePublicDiagnostics}
              onCheckedChange={(checked) => handleSettingChange('enablePublicDiagnostics', checked)}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Habilitar Notificaciones
              </label>
              <p className="text-sm text-gray-500">Enviar notificaciones por email</p>
            </div>
            <Switch
              checked={settings.enableNotifications}
              onCheckedChange={(checked) => handleSettingChange('enableNotifications', checked)}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Modo de Mantenimiento
              </label>
              <p className="text-sm text-gray-500">Mostrar página de mantenimiento</p>
            </div>
            <Switch
              checked={settings.maintenanceMode}
              onCheckedChange={(checked) => handleSettingChange('maintenanceMode', checked)}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderAppearanceSettings = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Palette className="h-5 w-5 mr-2" />
            Apariencia
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Color Primario
            </label>
            <div className="flex items-center space-x-3">
              <Input
                type="color"
                value={settings.primaryColor}
                onChange={(e) => handleSettingChange('primaryColor', e.target.value)}
                className="w-16 h-10"
              />
              <Input
                value={settings.primaryColor}
                onChange={(e) => handleSettingChange('primaryColor', e.target.value)}
                className="flex-1"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              URL del Logo
            </label>
            <Input
              value={settings.logoUrl}
              onChange={(e) => handleSettingChange('logoUrl', e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              URL del Favicon
            </label>
            <Input
              value={settings.faviconUrl}
              onChange={(e) => handleSettingChange('faviconUrl', e.target.value)}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return renderGeneralSettings();
      case 'security':
        return renderSecuritySettings();
      case 'email':
        return renderEmailSettings();
      case 'features':
        return renderFeaturesSettings();
      case 'appearance':
        return renderAppearanceSettings();
      default:
        return renderGeneralSettings();
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Configuración del Sistema</h1>
          <p className="text-gray-600 mt-2">
            Administra la configuración general de la plataforma
          </p>
        </div>
        
        {hasChanges && (
          <Button onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" />
            Guardar Cambios
          </Button>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {renderTabContent()}
    </div>
  );
};

export default AdminSettingsPage;

