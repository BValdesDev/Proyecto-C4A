"""
Sistema de auditoría para C4A SaaS
"""
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.modelos.log_auditoria import LogAuditoria
from app.modelos.usuario import Usuario
from app.modelos.organizacion import Organizacion

class AuditService:
    """Servicio de auditoría"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_event(
        self,
        usuario_id: Optional[str] = None,
        organizacion_id: Optional[str] = None,
        tipo_evento: str = "general",
        accion: str = "",
        tipo_recurso: Optional[str] = None,
        id_recurso: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        exitoso: bool = True,
        mensaje_error: Optional[str] = None,
        metadatos: Optional[Dict[str, Any]] = None
    ) -> LogAuditoria:
        """Registrar evento de auditoría"""
        
        # Crear suma de verificación
        suma_verificacion = self._create_checksum(
            usuario_id, organizacion_id, tipo_evento, accion,
            tipo_recurso, id_recurso, ip_address, user_agent,
            exitoso, mensaje_error, metadatos
        )
        
        # Crear log de auditoría
        log = LogAuditoria(
            usuario_id=usuario_id,
            organizacion_id=organizacion_id,
            tipo_evento=tipo_evento,
            accion=accion,
            tipo_recurso=tipo_recurso,
            id_recurso=id_recurso,
            ip_address=ip_address,
            user_agent=user_agent,
            exitoso=exitoso,
            mensaje_error=mensaje_error,
            metadatos=metadatos,
            suma_verificacion=suma_verificacion
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def _create_checksum(
        self,
        usuario_id: Optional[str],
        organizacion_id: Optional[str],
        tipo_evento: str,
        accion: str,
        tipo_recurso: Optional[str],
        id_recurso: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str],
        exitoso: bool,
        mensaje_error: Optional[str],
        metadatos: Optional[Dict[str, Any]]
    ) -> str:
        """Crear suma de verificación SHA-256"""
        
        # Crear string para hash
        data_string = f"{usuario_id}|{organizacion_id}|{tipo_evento}|{accion}|{tipo_recurso}|{id_recurso}|{ip_address}|{user_agent}|{exitoso}|{mensaje_error}|{json.dumps(metadatos or {}, sort_keys=True)}"
        
        # Generar hash SHA-256
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def log_authentication(
        self,
        usuario_id: str,
        organizacion_id: str,
        accion: str,
        ip_address: str,
        user_agent: str,
        exitoso: bool = True,
        mensaje_error: Optional[str] = None
    ) -> LogAuditoria:
        """Registrar evento de autenticación"""
        return self.log_event(
            usuario_id=usuario_id,
            organizacion_id=organizacion_id,
            tipo_evento="autenticacion",
            accion=accion,
            ip_address=ip_address,
            user_agent=user_agent,
            exitoso=exitoso,
            mensaje_error=mensaje_error
        )
    
    def log_evaluation(
        self,
        usuario_id: str,
        organizacion_id: str,
        accion: str,
        evaluacion_id: str,
        ip_address: str,
        user_agent: str,
        exitoso: bool = True,
        mensaje_error: Optional[str] = None,
        metadatos: Optional[Dict[str, Any]] = None
    ) -> LogAuditoria:
        """Registrar evento de evaluación"""
        return self.log_event(
            usuario_id=usuario_id,
            organizacion_id=organizacion_id,
            tipo_evento="evaluacion",
            accion=accion,
            tipo_recurso="evaluacion",
            id_recurso=evaluacion_id,
            ip_address=ip_address,
            user_agent=user_agent,
            exitoso=exitoso,
            mensaje_error=mensaje_error,
            metadatos=metadatos
        )
    
    def log_report(
        self,
        usuario_id: str,
        organizacion_id: str,
        accion: str,
        reporte_id: str,
        ip_address: str,
        user_agent: str,
        exitoso: bool = True,
        mensaje_error: Optional[str] = None,
        metadatos: Optional[Dict[str, Any]] = None
    ) -> LogAuditoria:
        """Registrar evento de reporte"""
        return self.log_event(
            usuario_id=usuario_id,
            organizacion_id=organizacion_id,
            tipo_evento="reporte",
            accion=accion,
            tipo_recurso="reporte",
            id_recurso=reporte_id,
            ip_address=ip_address,
            user_agent=user_agent,
            exitoso=exitoso,
            mensaje_error=mensaje_error,
            metadatos=metadatos
        )
    
    def log_subscription(
        self,
        usuario_id: str,
        organizacion_id: str,
        accion: str,
        suscripcion_id: str,
        ip_address: str,
        user_agent: str,
        exitoso: bool = True,
        mensaje_error: Optional[str] = None,
        metadatos: Optional[Dict[str, Any]] = None
    ) -> LogAuditoria:
        """Registrar evento de suscripción"""
        return self.log_event(
            usuario_id=usuario_id,
            organizacion_id=organizacion_id,
            tipo_evento="suscripcion",
            accion=accion,
            tipo_recurso="suscripcion",
            id_recurso=suscripcion_id,
            ip_address=ip_address,
            user_agent=user_agent,
            exitoso=exitoso,
            mensaje_error=mensaje_error,
            metadatos=metadatos
        )
    
    def log_data_access(
        self,
        usuario_id: str,
        organizacion_id: str,
        accion: str,
        tipo_recurso: str,
        id_recurso: str,
        ip_address: str,
        user_agent: str,
        exitoso: bool = True,
        mensaje_error: Optional[str] = None,
        metadatos: Optional[Dict[str, Any]] = None
    ) -> LogAuditoria:
        """Registrar acceso a datos"""
        return self.log_event(
            usuario_id=usuario_id,
            organizacion_id=organizacion_id,
            tipo_evento="acceso_datos",
            accion=accion,
            tipo_recurso=tipo_recurso,
            id_recurso=id_recurso,
            ip_address=ip_address,
            user_agent=user_agent,
            exitoso=exitoso,
            mensaje_error=mensaje_error,
            metadatos=metadatos
        )
    
    def get_audit_logs(
        self,
        usuario_id: Optional[str] = None,
        organizacion_id: Optional[str] = None,
        tipo_evento: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[LogAuditoria]:
        """Obtener logs de auditoría con filtros"""
        
        query = self.db.query(LogAuditoria)
        
        if usuario_id:
            query = query.filter(LogAuditoria.usuario_id == usuario_id)
        
        if organizacion_id:
            query = query.filter(LogAuditoria.organizacion_id == organizacion_id)
        
        if tipo_evento:
            query = query.filter(LogAuditoria.tipo_evento == tipo_evento)
        
        if fecha_desde:
            query = query.filter(LogAuditoria.creado_en >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(LogAuditoria.creado_en <= fecha_hasta)
        
        return query.order_by(LogAuditoria.creado_en.desc()).offset(offset).limit(limit).all()
    
    def verify_audit_integrity(self, log_id: str) -> bool:
        """Verificar integridad de un log de auditoría"""
        
        log = self.db.query(LogAuditoria).filter(LogAuditoria.id == log_id).first()
        
        if not log:
            return False
        
        # Recalcular suma de verificación
        expected_checksum = self._create_checksum(
            log.usuario_id,
            log.organizacion_id,
            log.tipo_evento,
            log.accion,
            log.tipo_recurso,
            log.id_recurso,
            log.ip_address,
            log.user_agent,
            log.exitoso,
            log.mensaje_error,
            log.metadatos
        )
        
        return log.suma_verificacion == expected_checksum
    
    def get_audit_summary(
        self,
        organizacion_id: str,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Obtener resumen de auditoría para una organización"""
        
        query = self.db.query(LogAuditoria).filter(
            LogAuditoria.organizacion_id == organizacion_id
        )
        
        if fecha_desde:
            query = query.filter(LogAuditoria.creado_en >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(LogAuditoria.creado_en <= fecha_hasta)
        
        logs = query.all()
        
        # Contar eventos por tipo
        eventos_por_tipo = {}
        eventos_exitosos = 0
        eventos_fallidos = 0
        
        for log in logs:
            if log.tipo_evento not in eventos_por_tipo:
                eventos_por_tipo[log.tipo_evento] = 0
            eventos_por_tipo[log.tipo_evento] += 1
            
            if log.exitoso:
                eventos_exitosos += 1
            else:
                eventos_fallidos += 1
        
        return {
            "total_eventos": len(logs),
            "eventos_exitosos": eventos_exitosos,
            "eventos_fallidos": eventos_fallidos,
            "eventos_por_tipo": eventos_por_tipo,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        }

def get_audit_service(db: Session) -> AuditService:
    """Obtener instancia del servicio de auditoría"""
    return AuditService(db)
















