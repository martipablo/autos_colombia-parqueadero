"""Caso de uso: registrar el ingreso de un vehículo (RF-01 a RF-05).

Es el servicio más delicado porque dos puertas pueden trabajar a la vez.
Defensa en dos niveles contra celdas duplicadas:
  1. CeldaRepository.asignar_disponible bloquea la celda elegida (SKIP LOCKED).
  2. Los índices únicos de la base rechazan cualquier duplicado que aun así se cuele;
     en ese caso se reintenta con otra celda.
"""
from excepciones.errores import (CeldaOcupada, ParqueaderoError, SinCupo,
                                 VehiculoNoRegistrado, VehiculoYaDentro)
from database.conexion import transaccion
from models.entidades import Movimiento, Sesion, Vehiculo
from repositories.celda_repository import CeldaRepository
from repositories.movimiento_repository import MovimientoRepository
from repositories.vehiculo_repository import VehiculoRepository
from services.utilidades import normalizar_placa

_MAX_REINTENTOS = 3


class IngresoService:
    def __init__(self, vehiculos: VehiculoRepository, celdas: CeldaRepository,
                 movimientos: MovimientoRepository):
        self._vehiculos = vehiculos
        self._celdas = celdas
        self._movimientos = movimientos

    def verificar_ingreso(self, placa: str) -> Vehiculo:
        """Paso 1 en pantalla: comprueba que el vehículo puede entrar, sin reservar nada.

        Valida (en orden) que esté registrado, que no esté ya dentro y que haya cupo.
        Devuelve el vehículo con su propietario para mostrarlo al operario.
        """
        placa = normalizar_placa(placa)
        with transaccion() as conn:
            vehiculo = self._vehiculos.buscar_por_placa(conn, placa)
            if vehiculo is None:
                raise VehiculoNoRegistrado(placa)
            if self._movimientos.buscar_activo(conn, placa) is not None:
                raise VehiculoYaDentro(placa)
            if self._celdas.contar_libres(conn, vehiculo.tipo) == 0:
                raise SinCupo(vehiculo.tipo.etiqueta)
            return vehiculo

    def registrar_ingreso(self, placa: str, sesion: Sesion) -> Movimiento:
        """Paso 2 en pantalla: asigna celda y registra el ingreso de forma atómica.

        Todo ocurre en una transacción: si algo falla, no queda nada a medias.
        Devuelve el movimiento con la celda asignada.
        """
        placa = normalizar_placa(placa)
        for _ in range(_MAX_REINTENTOS):
            try:
                with transaccion() as conn:
                    vehiculo = self._vehiculos.buscar_por_placa(conn, placa)
                    if vehiculo is None:
                        raise VehiculoNoRegistrado(placa)
                    if self._movimientos.buscar_activo(conn, placa) is not None:
                        raise VehiculoYaDentro(placa)

                    celda = self._celdas.asignar_disponible(conn, vehiculo.tipo)
                    if celda is None:
                        raise SinCupo(vehiculo.tipo.etiqueta)

                    movimiento = self._movimientos.crear(
                        conn, placa, celda.id_celda,
                        sesion.puerta.id_puerta, sesion.operario.id_operario)
                    movimiento.celda = celda
                    return movimiento  # al salir del bloque se confirma la transacción
            except CeldaOcupada:
                continue  # otra puerta tomó la misma celda justo ahora: se intenta con otra
        raise ParqueaderoError("No se pudo asignar una celda, intenta de nuevo.")
