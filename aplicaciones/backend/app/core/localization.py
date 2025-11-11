"""
Sistema de localización para Chile
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import locale
import pytz
from decimal import Decimal
import re

class ChileLocalization:
    """Servicio de localización para Chile"""
    
    def __init__(self):
        self.timezone = pytz.timezone('America/Santiago')
        self.locale = 'es_CL.UTF-8'
        self.currency = 'CLP'
        
        # Configurar locale
        try:
            locale.setlocale(locale.LC_ALL, self.locale)
        except locale.Error:
            # Fallback a locale genérico
            try:
                locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
            except locale.Error:
                locale.setlocale(locale.LC_ALL, 'C')
    
    def format_currency(self, amount: float, show_symbol: bool = True) -> str:
        """Formatear moneda chilena"""
        if show_symbol:
            return f"${amount:,.0f} CLP"
        else:
            return f"{amount:,.0f}"
    
    def format_number(self, number: float, decimals: int = 0) -> str:
        """Formatear número con separadores de miles chilenos"""
        if decimals > 0:
            return f"{number:,.{decimals}f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        else:
            return f"{number:,.0f}".replace(',', '.')
    
    def format_date(self, date: datetime, format_type: str = "short") -> str:
        """Formatear fecha en formato chileno"""
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        
        # Convertir a zona horaria de Chile
        chile_date = date.astimezone(self.timezone)
        
        if format_type == "short":
            return chile_date.strftime("%d/%m/%Y")
        elif format_type == "long":
            return chile_date.strftime("%d de %B de %Y")
        elif format_type == "datetime":
            return chile_date.strftime("%d/%m/%Y %H:%M")
        elif format_type == "datetime_long":
            return chile_date.strftime("%d de %B de %Y a las %H:%M")
        else:
            return chile_date.strftime(format_type)
    
    def format_rut(self, rut: str) -> str:
        """Formatear RUT chileno"""
        if not rut:
            return rut
        
        # Limpiar RUT
        rut_clean = re.sub(r'[^0-9kK]', '', rut)
        
        if len(rut_clean) < 2:
            return rut
        
        # Separar número y dígito verificador
        numero = rut_clean[:-1]
        dv = rut_clean[-1].upper()
        
        # Formatear con puntos
        numero_formateado = self._format_number_with_dots(numero)
        
        return f"{numero_formateado}-{dv}"
    
    def _format_number_with_dots(self, number: str) -> str:
        """Formatear número con puntos cada 3 dígitos"""
        if len(number) <= 3:
            return number
        
        result = ""
        for i, digit in enumerate(reversed(number)):
            if i > 0 and i % 3 == 0:
                result = "." + result
            result = digit + result
        
        return result
    
    def validate_rut(self, rut: str) -> bool:
        """Validar RUT chileno"""
        if not rut:
            return False
        
        # Limpiar RUT
        rut_clean = re.sub(r'[^0-9kK]', '', rut)
        
        if len(rut_clean) < 2:
            return False
        
        # Separar número y dígito verificador
        numero = rut_clean[:-1]
        dv = rut_clean[-1].upper()
        
        # Validar que el número sea válido
        try:
            int(numero)
        except ValueError:
            return False
        
        # Calcular dígito verificador
        dv_calculado = self._calculate_rut_dv(numero)
        
        return dv == dv_calculado
    
    def _calculate_rut_dv(self, numero: str) -> str:
        """Calcular dígito verificador de RUT"""
        suma = 0
        multiplicador = 2
        
        for digit in reversed(numero):
            suma += int(digit) * multiplicador
            multiplicador += 1
            if multiplicador > 7:
                multiplicador = 2
        
        resto = suma % 11
        dv = 11 - resto
        
        if dv == 11:
            return "0"
        elif dv == 10:
            return "K"
        else:
            return str(dv)
    
    def get_chilean_timezone(self) -> pytz.timezone:
        """Obtener zona horaria de Chile"""
        return self.timezone
    
    def get_current_chilean_time(self) -> datetime:
        """Obtener hora actual de Chile"""
        return datetime.now(self.timezone)
    
    def parse_chilean_date(self, date_string: str, format_type: str = "short") -> Optional[datetime]:
        """Parsear fecha en formato chileno"""
        try:
            if format_type == "short":
                # DD/MM/YYYY
                return datetime.strptime(date_string, "%d/%m/%Y").replace(tzinfo=self.timezone)
            elif format_type == "long":
                # DD de MMMM de YYYY
                return datetime.strptime(date_string, "%d de %B de %Y").replace(tzinfo=self.timezone)
            elif format_type == "datetime":
                # DD/MM/YYYY HH:MM
                return datetime.strptime(date_string, "%d/%m/%Y %H:%M").replace(tzinfo=self.timezone)
            else:
                return datetime.strptime(date_string, format_type).replace(tzinfo=self.timezone)
        except ValueError:
            return None
    
    def get_month_names(self) -> Dict[int, str]:
        """Obtener nombres de meses en español"""
        return {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
    
    def get_weekday_names(self) -> Dict[int, str]:
        """Obtener nombres de días de la semana en español"""
        return {
            0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
            4: "Viernes", 5: "Sábado", 6: "Domingo"
        }
    
    def format_phone(self, phone: str) -> str:
        """Formatear número de teléfono chileno"""
        if not phone:
            return phone
        
        # Limpiar número
        phone_clean = re.sub(r'[^0-9]', '', phone)
        
        if len(phone_clean) == 9:
            # Móvil: 9 1234 5678
            return f"{phone_clean[0]} {phone_clean[1:5]} {phone_clean[5:]}"
        elif len(phone_clean) == 8:
            # Fijo: 2 1234 5678
            return f"{phone_clean[0]} {phone_clean[1:5]} {phone_clean[5:]}"
        else:
            return phone
    
    def get_chilean_sectors(self) -> Dict[str, str]:
        """Obtener sectores económicos chilenos"""
        return {
            "agricultura": "Agricultura, Silvicultura y Pesca",
            "mineria": "Minería",
            "manufactura": "Manufactura",
            "construccion": "Construcción",
            "comercio": "Comercio",
            "transporte": "Transporte y Almacenamiento",
            "alojamiento": "Alojamiento y Servicios de Comida",
            "informacion": "Información y Comunicaciones",
            "financiero": "Actividades Financieras y de Seguros",
            "inmobiliario": "Actividades Inmobiliarias",
            "profesional": "Actividades Profesionales, Científicas y Técnicas",
            "administrativo": "Actividades de Servicios Administrativos",
            "publico": "Administración Pública",
            "educacion": "Educación",
            "salud": "Actividades de Atención de la Salud",
            "arte": "Artes, Entretenimiento y Recreación",
            "otro": "Otras Actividades de Servicios",
            "hogares": "Actividades de los Hogares",
            "organizaciones": "Organizaciones y Órganos Extraterritoriales"
        }
    
    def get_company_sizes(self) -> Dict[str, str]:
        """Obtener tamaños de empresa chilenos"""
        return {
            "micro": "Microempresa (1-9 empleados)",
            "pequena": "Pequeña empresa (10-49 empleados)",
            "mediana": "Mediana empresa (50-199 empleados)",
            "grande": "Gran empresa (200+ empleados)"
        }
    
    def get_chilean_regions(self) -> Dict[str, str]:
        """Obtener regiones de Chile"""
        return {
            "arica": "Región de Arica y Parinacota",
            "tarapaca": "Región de Tarapacá",
            "antofagasta": "Región de Antofagasta",
            "atacama": "Región de Atacama",
            "coquimbo": "Región de Coquimbo",
            "valparaiso": "Región de Valparaíso",
            "metropolitana": "Región Metropolitana",
            "ohiggins": "Región del Libertador General Bernardo O'Higgins",
            "maule": "Región del Maule",
            "nuble": "Región de Ñuble",
            "biobio": "Región del Biobío",
            "araucania": "Región de La Araucanía",
            "rios": "Región de Los Ríos",
            "lagos": "Región de Los Lagos",
            "aysen": "Región Aysén del General Carlos Ibáñez del Campo",
            "magallanes": "Región de Magallanes y de la Antártica Chilena"
        }

# Instancia global del servicio de localización
chile_localization = ChileLocalization()

def get_chile_localization() -> ChileLocalization:
    """Obtener instancia del servicio de localización"""
    return chile_localization

# Funciones de conveniencia
def format_clp(amount: float, show_symbol: bool = True) -> str:
    """Formatear moneda chilena"""
    return chile_localization.format_currency(amount, show_symbol)

def format_chilean_date(date: datetime, format_type: str = "short") -> str:
    """Formatear fecha en formato chileno"""
    return chile_localization.format_date(date, format_type)

def format_rut(rut: str) -> str:
    """Formatear RUT chileno"""
    return chile_localization.format_rut(rut)

def validate_rut(rut: str) -> bool:
    """Validar RUT chileno"""
    return chile_localization.validate_rut(rut)

def get_chilean_time() -> datetime:
    """Obtener hora actual de Chile"""
    return chile_localization.get_current_chilean_time()

