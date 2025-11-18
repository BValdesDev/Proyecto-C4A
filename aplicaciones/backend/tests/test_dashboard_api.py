"""
Pruebas del Dashboard usando TestClient para evitar dependencias externas.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modelos.base import obtener_sesion
from app.api.v1.dependencias import obtener_usuario_actual_dependencia
from app.core.config import NivelSuscripcion
from app.modelos.evaluacion import EstadoEvaluacion


def _auth_headers() -> Dict[str, str]:
    return {"Authorization": "Bearer fake-token"}


class FakeQuery:
    def __init__(self, data: List[Any]):
        self._data = list(data)
        self._limit = None
        self._order_desc = False

    def filter(self, *args: Any, **kwargs: Any) -> "FakeQuery":
        return self

    def order_by(self, *args: Any, **kwargs: Any) -> "FakeQuery":
        # Asumir que order_by siempre ordena por fecha_creacion descendente
        # (esto es suficiente para las pruebas del dashboard)
        self._order_desc = True
        return self

    def limit(self, value: int) -> "FakeQuery":
        self._limit = value
        return self

    def all(self) -> List[Any]:
        result = list(self._data)
        # Ordenar por fecha_creacion si se especificó order_by
        if self._order_desc:
            result.sort(key=lambda x: x.fecha_creacion, reverse=True)
        if self._limit is None:
            return result
        return result[: self._limit]

    def first(self) -> Any:
        data = self.all()
        return data[0] if data else None


class FakeSession:
    def __init__(self, evaluaciones: List[Any]):
        self._evaluaciones = evaluaciones

    def query(self, model: Any) -> FakeQuery:
        if model.__name__ != "Evaluacion":
            raise NotImplementedError("Solo se soporta el modelo Evaluacion en las pruebas")
        return FakeQuery(self._evaluaciones)

    @property
    def evaluaciones(self) -> List[Any]:
        return list(self._evaluaciones)


@dataclass
class FakeOrganizacion:
    id: uuid.UUID
    nombre: str
    nivel_suscripcion: NivelSuscripcion
    maximo_evaluaciones_por_mes: int
    puede_crear_evaluacion: bool = True

    def obtener_uso_mensual(self) -> int:
        return 4


class FakeUsuario:
    def __init__(self, organizacion: FakeOrganizacion):
        self.id = uuid.uuid4()
        self.organizacion = organizacion

    def puede_crear_evaluacion(self) -> bool:
        return True

    def puede_acceder_recurso(self, recurso: str, accion: str) -> bool:
        return True

    def obtener_estadisticas_uso(self) -> Dict[str, Any]:
        return {"diagnosticos_completados": 2, "horas": 5}


@dataclass
class FakeEvaluacion:
    id: uuid.UUID
    organizacion_id: uuid.UUID
    nombre: str
    estado: EstadoEvaluacion
    puntuacion_global: float | None
    porcentaje_completado: float
    fecha_creacion: datetime
    fecha_eliminacion: None = None


def _crear_evaluaciones(organizacion_id: uuid.UUID) -> List[FakeEvaluacion]:
    ahora = datetime.utcnow()
    return [
        FakeEvaluacion(
            id=uuid.uuid4(),
            organizacion_id=organizacion_id,
            nombre="Evaluación completada",
            estado=EstadoEvaluacion.COMPLETADA,
            puntuacion_global=92.5,
            porcentaje_completado=100.0,
            fecha_creacion=ahora - timedelta(days=15),
        ),
        FakeEvaluacion(
            id=uuid.uuid4(),
            organizacion_id=organizacion_id,
            nombre="Evaluación en progreso",
            estado=EstadoEvaluacion.EN_PROGRESO,
            puntuacion_global=None,
            porcentaje_completado=55.0,
            fecha_creacion=ahora - timedelta(days=3),
        ),
        FakeEvaluacion(
            id=uuid.uuid4(),
            organizacion_id=organizacion_id,
            nombre="Evaluación borrador",
            estado=EstadoEvaluacion.BORRADOR,
            puntuacion_global=None,
            porcentaje_completado=10.0,
            fecha_creacion=ahora - timedelta(days=1),
        ),
    ]


@pytest.fixture()
def test_context():
    organizacion = FakeOrganizacion(
        id=uuid.uuid4(),
        nombre="Organizacion QA",
        nivel_suscripcion=NivelSuscripcion.PRO,
        maximo_evaluaciones_por_mes=10,
    )
    fake_session = FakeSession(_crear_evaluaciones(organizacion.id))
    fake_usuario = FakeUsuario(organizacion)

    app.dependency_overrides[obtener_sesion] = lambda: fake_session
    app.dependency_overrides[obtener_usuario_actual_dependencia] = lambda: fake_usuario

    client = TestClient(app)
    yield {"client": client, "session": fake_session, "organizacion": organizacion}
    app.dependency_overrides = {}


def test_health_endpoint(test_context):
    response = test_context["client"].get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"


def test_dashboard_summary(test_context):
    response = test_context["client"].get(
        "/api/v1/dashboard/summary",
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_evaluaciones"] == len(test_context["session"].evaluaciones)
    assert payload["nivel_suscripcion"] == NivelSuscripcion.PRO.value


def test_dashboard_evaluaciones_recientes(test_context):
    response = test_context["client"].get(
        "/api/v1/dashboard/evaluaciones-recientes",
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) <= 5
    assert payload[0]["nombre"] == "Evaluación borrador" or payload[0]["nombre"] == "Evaluación en progreso"


def test_dashboard_acciones(test_context):
    response = test_context["client"].get(
        "/api/v1/dashboard/acciones",
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert any(accion["id"] == "crear_nueva_evaluacion" for accion in payload)


def test_dashboard_estadisticas(test_context):
    response = test_context["client"].get(
        "/api/v1/dashboard/estadisticas-uso",
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["organizacion"]["nombre"] == "Organizacion QA"
