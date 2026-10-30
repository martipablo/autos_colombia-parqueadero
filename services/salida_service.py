"""Caso de uso: registrar la salida de un vehículo (RF-06)."""
from database.conexion import transaccion
from excepciones.errores import VehiculoNoEstaDentro
from models.entidades import Movimiento, Sesion
from repositories.movimiento_repository import MovimientoRepository
from services.utilidades import normalizar_placa


class SalidaService:
    def __init__(self, movimientos: MovimientoRepository):
        self._movimientos = movimientos

    def consultar_movimiento_activo(self, placa: str) -> Movimiento:
        """Paso 1 en pantalla: muestra celda y hora de ingreso del vehículo que va a salir."""
        placa = normalizar_placa(placa)
        with transaccion() as conn:
            movimiento = self._movimientos.buscar_activo(conn, placa)
        if movimiento is None:
            raise VehiculoNoEstaDentro(placa)
        return movimiento

    def registrar_salida(self, placa: str, sesion: Sesion) -> Movimiento:
        """Paso 2 en pantalla: cierra el movimiento. Al quedar con fecha de salida,
        su celda vuelve a estar disponible automáticamente (la ocupación se calcula).
        """
        placa = normalizar_placa(placa)
        with transaccion() as conn:
            activo = self._movimientos.buscar_activo(conn, placa)
            if activo is None:
                raise VehiculoNoEstaDentro(placa)
            cerrado = self._movimientos.cerrar(
                conn, activo.id_movimiento,
                sesion.puerta.id_puerta, sesion.operario.id_operario)
            if cerrado is None:  # otra puerta lo cerró en el mismo instante
                raise VehiculoNoEstaDentro(placa)
            cerrado.celda = activo.celda
            return cerrado
