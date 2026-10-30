"""Caso de uso: registrar novedades sobre un vehículo (RF-08)."""
from typing import List

from database.conexion import transaccion
from excepciones.errores import DatosInvalidos, VehiculoNoEstaDentro
from models.entidades import Movimiento, Novedad, Sesion
from repositories.movimiento_repository import MovimientoRepository
from repositories.novedad_repository import NovedadRepository
from services.utilidades import normalizar_placa


class NovedadService:
    def __init__(self, movimientos: MovimientoRepository, novedades: NovedadRepository):
        self._movimientos = movimientos
        self._novedades = novedades

    def listar_vehiculos_dentro(self) -> List[Movimiento]:
        """Vehículos que están dentro ahora; alimenta la lista de la pantalla de novedades."""
        with transaccion() as conn:
            return self._movimientos.listar_activos(conn)

    def registrar_novedad(self, placa: str, descripcion: str, sesion: Sesion) -> Novedad:
        """Guarda una novedad ligada al ingreso activo del vehículo."""
        placa = normalizar_placa(placa)
        descripcion = (descripcion or "").strip()
        if not descripcion:
            raise DatosInvalidos("Escribe la descripción de la novedad.")
        with transaccion() as conn:
            activo = self._movimientos.buscar_activo(conn, placa)
            if activo is None:
                raise VehiculoNoEstaDentro(placa)
            return self._novedades.crear(
                conn, activo.id_movimiento, sesion.operario.id_operario, descripcion)
