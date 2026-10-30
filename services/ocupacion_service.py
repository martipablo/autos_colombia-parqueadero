"""Caso de uso: consultar la ocupación del parqueadero (RF-07)."""
from database.conexion import transaccion
from models.entidades import Ocupacion
from repositories.celda_repository import CeldaRepository


class OcupacionService:
    def __init__(self, celdas: CeldaRepository):
        self._celdas = celdas

    def consultar_ocupacion(self) -> Ocupacion:
        """Celdas libres y ocupadas por tipo, siempre calculadas al momento."""
        with transaccion() as conn:
            return self._celdas.contar_por_estado(conn)
