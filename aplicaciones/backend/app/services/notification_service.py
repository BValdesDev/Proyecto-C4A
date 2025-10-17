"""
Servicio de Notificaciones Automáticas
Maneja el envío automático de notificaciones basado en eventos
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
from sqlalchemy.orm import Session
from app.modelos.usuario import Usuario
from app.modelos.organizacion import Organizacion
from app.modelos.suscripcion import Suscripcion
from app.core.config import ConfiguracionSeguridad

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = "c4a.notifications@gmail.com"
        self.email_password = "c4a_notifications_2024"
    
    def send_welcome_notification(self, usuario: Usuario):
        """Enviar notificación de bienvenida a nuevo usuario"""
        try:
            template = {
                "subject": "¡Bienvenido a C4A!",
                "body": f"""
                <h2>¡Bienvenido a C4A, {usuario.nombres}!</h2>
                <p>Tu cuenta ha sido creada exitosamente.</p>
                <p>Puedes comenzar a usar la plataforma inmediatamente.</p>
                <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                <br>
                <p>Saludos,<br>El equipo de C4A</p>
                """
            }
            
            self._send_email(usuario.email, template["subject"], template["body"])
            self._log_notification("welcome", usuario.id, "sent")
            
            logger.info(f"Notificación de bienvenida enviada a {usuario.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando bienvenida a {usuario.email}: {e}")
            self._log_notification("welcome", usuario.id, "failed")
            return False
    
    def send_payment_reminder(self, suscripcion: Suscripcion):
        """Enviar recordatorio de pago"""
        try:
            usuario = suscripcion.organizacion.usuarios[0] if suscripcion.organizacion.usuarios else None
            if not usuario:
                return False
                
            template = {
                "subject": "Recordatorio de Pago - C4A",
                "body": f"""
                <h2>Recordatorio de Pago</h2>
                <p>Hola {usuario.nombres},</p>
                <p>Tu suscripción {suscripcion.nivel.value} está próxima a vencer.</p>
                <p>Fecha de vencimiento: {suscripcion.fin_periodo_actual.strftime('%d/%m/%Y') if suscripcion.fin_periodo_actual else 'Próximamente'}</p>
                <p>Monto: ${(suscripcion.monto_centavos or 0) / 100:,.0f} CLP</p>
                <p>Para continuar disfrutando de nuestros servicios, por favor renueva tu suscripción.</p>
                <br>
                <p>Saludos,<br>El equipo de C4A</p>
                """
            }
            
            self._send_email(usuario.email, template["subject"], template["body"])
            self._log_notification("payment_reminder", usuario.id, "sent")
            
            logger.info(f"Recordatorio de pago enviado a {usuario.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando recordatorio a {usuario.email}: {e}")
            self._log_notification("payment_reminder", usuario.id, "failed")
            return False
    
    def send_security_alert(self, usuario: Usuario, alert_type: str, details: str = ""):
        """Enviar alerta de seguridad"""
        try:
            template = {
                "subject": "Alerta de Seguridad - C4A",
                "body": f"""
                <h2>Alerta de Seguridad</h2>
                <p>Hola {usuario.nombres},</p>
                <p>Hemos detectado actividad inusual en tu cuenta:</p>
                <p><strong>Tipo de alerta:</strong> {alert_type}</p>
                <p><strong>Detalles:</strong> {details}</p>
                <p><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                <p>Si no reconoces esta actividad, por favor contacta a soporte inmediatamente.</p>
                <br>
                <p>Saludos,<br>El equipo de C4A</p>
                """
            }
            
            self._send_email(usuario.email, template["subject"], template["body"])
            self._log_notification("security_alert", usuario.id, "sent")
            
            logger.info(f"Alerta de seguridad enviada a {usuario.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando alerta a {usuario.email}: {e}")
            self._log_notification("security_alert", usuario.id, "failed")
            return False
    
    def check_payment_reminders(self):
        """Verificar suscripciones próximas a vencer"""
        try:
            # Buscar suscripciones que vencen en 3 días
            three_days_from_now = datetime.utcnow() + timedelta(days=3)
            
            suscripciones = self.db.query(Suscripcion).filter(
                Suscripcion.fin_periodo_actual <= three_days_from_now,
                Suscripcion.estado == 'active'
            ).all()
            
            sent_count = 0
            for suscripcion in suscripciones:
                if self.send_payment_reminder(suscripcion):
                    sent_count += 1
            
            logger.info(f"Enviados {sent_count} recordatorios de pago")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error verificando recordatorios: {e}")
            return 0
    
    def _send_email(self, to_email: str, subject: str, body: str):
        """Enviar email usando SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {e}")
            return False
    
    def _log_notification(self, notification_type: str, user_id: str, status: str):
        """Registrar notificación en la base de datos"""
        try:
            # Aquí podrías guardar en una tabla de notificaciones
            # Por ahora solo log
            logger.info(f"Notificación {notification_type} para usuario {user_id}: {status}")
        except Exception as e:
            logger.error(f"Error registrando notificación: {e}")

# Función para ejecutar tareas automáticas
def run_automatic_notifications(db: Session):
    """Ejecutar todas las notificaciones automáticas"""
    service = NotificationService(db)
    
    try:
        # Verificar recordatorios de pago
        payment_reminders = service.check_payment_reminders()
        
        logger.info(f"Tarea automática completada: {payment_reminders} recordatorios enviados")
        return {
            "payment_reminders": payment_reminders,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error en tareas automáticas: {e}")
        return {"error": str(e)}
