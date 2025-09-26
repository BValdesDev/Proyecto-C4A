// Tipos principales para C4A SaaS Frontend

// ===========================================
// TIPOS DE USUARIO Y AUTENTICACIÓN
// ===========================================

export interface Usuario {
  id: string
  email: string
  nombres: string
  apellidos: string
  organizacion: Organizacion
  rol: Rol
  nivel_suscripcion: string
  mfa_habilitado: boolean
  estado_cuenta: string
  fecha_ultimo_acceso: string | null
}

export interface Organizacion {
  id: string
  nombre: string
  rut?: string
  sector: string
  tamaño: string
  region?: string
  comuna?: string
  nivel_suscripcion: string
  fecha_inicio_suscripcion?: string
  fecha_vencimiento_suscripcion?: string
  maximo_usuarios: number
  maximo_evaluaciones_por_mes: number
  maximo_dias_retencion_datos: number
  descripcion?: string
  sitio_web?: string
  telefono?: string
  email_facturacion?: string
  fecha_creacion: string
}

export interface Rol {
  id: string
  nombre: string
  nombre_mostrar: string
  descripcion?: string
  permisos: string[]
  niveles_disponibles: string[]
  esta_activo: boolean
}

// ===========================================
// TIPOS DE EVALUACIÓN
// ===========================================

export interface Evaluacion {
  id: string
  nombre: string
  framework: Framework
  nivel_usado: string
  estado: string
  total_preguntas: number
  preguntas_completadas: number
  porcentaje_completado: number
  puntuacion_global?: number
  fecha_inicio?: string
  fecha_completada?: string
  fecha_creacion: string
}

export interface Framework {
  id: string
  nombre: string
  version: string
  nombre_mostrar: string
  descripcion?: string
  niveles_disponibles: string[]
  esta_activo: boolean
}

export interface Pregunta {
  id: string
  codigo: string
  texto_pregunta: string
  texto_ayuda?: string
  categoria?: string
  peso: number
  tipo_respuesta: string
  orden: number
}

export interface Respuesta {
  id: string
  pregunta_id: string
  valor: number
  texto_evidencia?: string
  comentarios?: string
  nivel_confianza?: number
  fecha_respuesta: string
}

// ===========================================
// TIPOS DE REPORTES
// ===========================================

export interface Reporte {
  id: string
  titulo: string
  tipo_reporte: string
  nivel_generado: string
  puntuacion_global: number
  total_fortalezas: number
  total_debilidades: number
  total_recomendaciones: number
  tiene_marca_agua: boolean
  fecha_generacion: string
  url_pdf?: string
}

export interface Recomendacion {
  id: string
  titulo: string
  descripcion: string
  esfuerzo: 'bajo' | 'medio' | 'alto'
  impacto: 'bajo' | 'medio' | 'alto'
  plazo: string
  referencias_nist?: string[]
  estimacion_costo?: string
  pasos_implementacion?: string[]
  prioridad: 'baja' | 'media' | 'alta' | 'critica'
}

// ===========================================
// TIPOS DE SUSCRIPCIÓN
// ===========================================

export interface NivelSuscripcion {
  nivel: string
  nombre_mostrar: string
  precio_mensual_clp: number
  precio_anual_clp: number
  caracteristicas: string[]
  limites: {
    max_usuarios: number
    max_evaluaciones_mes: number
    max_preguntas: number
    dias_retencion: number
    max_recomendaciones: number
    limite_velocidad: number
  }
}

export interface Suscripcion {
  id: string
  nivel: string
  estado: string
  monto_clp: number
  ciclo_facturacion: string
  inicio_periodo_actual: string
  fin_periodo_actual: string
  uso_evaluaciones: number
  uso_usuarios: number
  fecha_creacion: string
}

export interface UsoOrganizacion {
  evaluaciones_usadas: number
  evaluaciones_limite: number
  usuarios_activos: number
  usuarios_limite: number
  porcentaje_uso_evaluaciones: number
  porcentaje_uso_usuarios: number
}

// ===========================================
// TIPOS DE DASHBOARD Y ANALYTICS
// ===========================================

export interface EstadisticasDashboard {
  total_evaluaciones: number
  evaluaciones_completadas: number
  evaluaciones_en_progreso: number
  puntuacion_promedio: number
  ultima_evaluacion?: Evaluacion
  proxima_vencimiento?: string
  uso_mensual: UsoOrganizacion
}

export interface GraficoDatos {
  name: string
  value: number
  color?: string
}

export interface BenchmarkData {
  organizacion: number
  industria: number
  promedio: number
  percentil: number
}

// ===========================================
// TIPOS DE FORMULARIOS
// ===========================================

export interface LoginForm {
  email: string
  password: string
}

export interface RegistroForm {
  email: string
  nombres: string
  apellidos: string
  password: string
  confirmar_password: string
  organizacion: {
    nombre: string
    rut?: string
    sector: string
    tamaño: string
    region?: string
    comuna?: string
  }
}

export interface EvaluacionForm {
  nombre: string
  framework_id: string
}

export interface RespuestaForm {
  pregunta_id: string
  valor: number
  texto_evidencia?: string
  comentarios?: string
  nivel_confianza?: number
}

// ===========================================
// TIPOS DE NAVEGACIÓN
// ===========================================

export interface MenuItem {
  id: string
  label: string
  icon: string
  path: string
  nivel_requerido?: string
  children?: MenuItem[]
}

export interface BreadcrumbItem {
  label: string
  path?: string
}

// ===========================================
// TIPOS DE ESTADO Y UI
// ===========================================

export interface LoadingState {
  isLoading: boolean
  error?: string
}

export interface PaginationState {
  pagina: number
  por_pagina: number
  total: number
}

export interface FilterState {
  [key: string]: any
}

export interface SortState {
  campo: string
  direccion: 'asc' | 'desc'
}

// ===========================================
// TIPOS DE NOTIFICACIONES
// ===========================================

export interface Notificacion {
  id: string
  tipo: 'info' | 'success' | 'warning' | 'error'
  titulo: string
  mensaje: string
  fecha: string
  leida: boolean
}

// ===========================================
// TIPOS DE CONFIGURACIÓN
// ===========================================

export interface ConfiguracionApp {
  nombre: string
  version: string
  api_url: string
  moneda: string
  idioma: string
  zona_horaria: string
}

// ===========================================
// TIPOS DE ERRORES
// ===========================================

export interface ApiError {
  mensaje: string
  codigo_error: string
  detalles?: any
}

export interface ValidationError {
  campo: string
  mensaje: string
}

// ===========================================
// TIPOS DE UTILIDADES
// ===========================================

export type NivelSuscripcionType = 'gratuito' | 'pro' | 'empresarial'
export type EstadoEvaluacionType = 'borrador' | 'en_progreso' | 'completada' | 'archivada'
export type TipoRolType = 'admin_sistema' | 'admin_empresa' | 'evaluador' | 'usuario_basico' | 'auditor'
export type SectorType = 'financiero' | 'salud' | 'retail' | 'gobierno' | 'educacion' | 'tecnologia' | 'manufactura' | 'servicios' | 'construccion' | 'mineria'
export type TamañoEmpresaType = 'micro' | 'pequeña' | 'mediana' | 'grande'