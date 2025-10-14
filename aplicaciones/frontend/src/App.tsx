import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'sonner'

// Contextos y providers
import { AuthProvider } from './hooks/useAuth'
import { ThemeProvider } from './hooks/useTheme'

// Componentes de layout
import { Layout } from './components/layout/Layout'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import AdminLayout from './components/admin/AdminLayout'
import ProtectedAdminRoute from './components/admin/ProtectedAdminRoute'

// Páginas
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/auth/LoginPage'
import { RegistroPage } from './pages/auth/RegistroPage'
import { DashboardPage } from './pages/dashboard/DashboardPage'
import { EvaluacionesPage } from './pages/evaluaciones/EvaluacionesPage'
import { EvaluacionPage } from './pages/evaluaciones/EvaluacionPage'
import CrearEvaluacionPage from './pages/evaluaciones/CrearEvaluacionPage'
import { ReportesPage } from './pages/reportes/ReportesPage'
import { SuscripcionesPage } from './pages/suscripciones/SuscripcionesPage'
import { PerfilPage } from './pages/perfil/PerfilPage'
import { NotFoundPage } from './pages/NotFoundPage'

// Admin Pages
import AdminDashboardPage from './pages/admin/AdminDashboardPage'
import AdminUsersPage from './pages/admin/AdminUsersPage'
import AdminDiagnosticsPage from './pages/admin/AdminDiagnosticsPage'
import AdminSettingsPage from './pages/admin/AdminSettingsPage'

// Estilos
import './App.css'

function App() {
  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <div className="min-h-screen bg-background">
            <Routes>
              {/* Ruta pública - Página de inicio */}
              <Route path="/" element={<HomePage />} />
              
              {/* Rutas públicas de autenticación */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/registro" element={<RegistroPage />} />
              
              {/* Rutas protegidas */}
              <Route path="/app" element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }>
                <Route index element={<Navigate to="/app/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="evaluaciones" element={<EvaluacionesPage />} />
                <Route path="evaluaciones/crear" element={<CrearEvaluacionPage />} />
                <Route path="evaluaciones/:id" element={<EvaluacionPage />} />
                <Route path="reportes" element={<ReportesPage />} />
                <Route path="suscripciones" element={<SuscripcionesPage />} />
                <Route path="perfil" element={<PerfilPage />} />
              </Route>

              {/* Admin Routes */}
              <Route path="/admin" element={
                <ProtectedAdminRoute>
                  <AdminLayout>
                    <AdminDashboardPage />
                  </AdminLayout>
                </ProtectedAdminRoute>
              } />
              
              <Route path="/admin/users" element={
                <ProtectedAdminRoute>
                  <AdminLayout>
                    <AdminUsersPage />
                  </AdminLayout>
                </ProtectedAdminRoute>
              } />
              
              <Route path="/admin/diagnostics" element={
                <ProtectedAdminRoute>
                  <AdminLayout>
                    <AdminDiagnosticsPage />
                  </AdminLayout>
                </ProtectedAdminRoute>
              } />
              
              <Route path="/admin/settings" element={
                <ProtectedAdminRoute>
                  <AdminLayout>
                    <AdminSettingsPage />
                  </AdminLayout>
                </ProtectedAdminRoute>
              } />
              
              {/* Ruta 404 */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
            
            {/* Toast notifications */}
            <Toaster 
              position="top-right"
              expand={true}
              richColors={true}
              closeButton={true}
            />
          </div>
        </AuthProvider>
      </ThemeProvider>
    </Router>
  )
}

export default App