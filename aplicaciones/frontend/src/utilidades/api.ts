import axios from 'axios';

// Configuración base de la API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Cliente de API configurado
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token de autenticación
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas y errores
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Funciones de API específicas
export const authAPI = {
  login: (email: string, password: string) =>
    apiClient.post('/api/v1/auth/iniciar-sesion', { email, password }),
  
  register: (userData: any) =>
    apiClient.post('/api/v1/usuarios/registrar', userData),
  
  refreshToken: (refreshToken: string) =>
    apiClient.post('/api/v1/auth/renovar-token', { refresh_token: refreshToken }),
  
  logout: () =>
    apiClient.post('/api/v1/auth/cerrar-sesion'),
};

export const userAPI = {
  getProfile: () =>
    apiClient.get('/api/v1/auth/mi-perfil'),
  
  updateProfile: (data: any) =>
    apiClient.put('/api/v1/usuarios/{usuario_id}', data),
  
  changePassword: (data: any) =>
    apiClient.post('/api/v1/auth/cambiar-password', data),
};

export const organizationAPI = {
  getOrganizations: () =>
    apiClient.get('/api/v1/organizaciones/'),
  
  createOrganization: (data: any) =>
    apiClient.post('/api/v1/organizaciones/', data),
  
  updateOrganization: (id: string, data: any) =>
    apiClient.put(`/api/v1/organizaciones/${id}`, data),
  
  getOrganization: (id: string) =>
    apiClient.get(`/api/v1/organizaciones/${id}`),
};

export const evaluationAPI = {
  getEvaluations: () =>
    apiClient.get('/api/v1/evaluaciones/'),
  
  createEvaluation: (data: any) =>
    apiClient.post('/api/v1/evaluaciones/', data),
  
  getEvaluation: (id: string) =>
    apiClient.get(`/api/v1/evaluaciones/${id}`),
  
  updateEvaluation: (id: string, data: any) =>
    apiClient.put(`/api/v1/evaluaciones/${id}`, data),
  
  submitAnswers: (evaluationId: string, answers: any[]) =>
    apiClient.post(`/api/v1/evaluaciones/${evaluationId}/respuestas`, { answers }),
};

export const reportAPI = {
  getReports: () =>
    apiClient.get('/api/v1/reportes/'),
  
  generateReport: (evaluationId: string) =>
    apiClient.post(`/api/v1/reportes/evaluacion/${evaluationId}/generar`),
  
  getReport: (id: string) =>
    apiClient.get(`/api/v1/reportes/evaluacion/${id}/puntuacion`),
  
  downloadReport: (id: string) =>
    apiClient.get(`/api/v1/reportes/evaluacion/${id}/exportar/excel`, { responseType: 'blob' }),
};

export const subscriptionAPI = {
  getSubscriptions: () =>
    apiClient.get('/api/v1/suscripciones/actual'),
  
  createSubscription: (data: any) =>
    apiClient.post('/api/v1/suscripciones/suscribirse', data),
  
  updateSubscription: (id: string, data: any) =>
    apiClient.put(`/api/v1/suscripciones/${id}`, data),
  
  cancelSubscription: (id: string) =>
    apiClient.post('/api/v1/suscripciones/cancelar'),
};

export default apiClient;