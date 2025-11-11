# app/api/v1/endpoints/__init__.py
"""
Endpoints de la API v1
"""

from . import auth, usuarios, organizaciones, evaluaciones, reportes, suscripciones, admin, dashboard, cuestionarios, pdf_profesional

__all__ = [
    "auth",
    "usuarios", 
    "organizaciones",
    "evaluaciones",
    "reportes",
    "suscripciones",
    "admin",
    "dashboard",
    "cuestionarios",
    "pdf_profesional"
] 