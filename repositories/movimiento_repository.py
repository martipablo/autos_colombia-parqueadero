"""Acceso a la tabla movimiento (ingresos y salidas)."""
from typing import List, Optional

import psycopg

from excepciones.errores import CeldaOcupada, VehiculoYaDentro
from models.entidades import Celda, Movimiento
from models.enums import TipoVehiculo

# Consulta base que trae el movimiento junto con los datos de su celda.
_SELECT_CON_CELDA = (
    "SELECT m.*, c.codigo AS celda_codigo, c.tipo AS celda_tipo "
    "FROM movimiento m JOIN celda c ON c.id_celda = m.id_celda "
)


def _a_movimiento(fila: dict) -> Movimiento:
    """Convierte una fila de la base en un Movimiento (con su Celda si la fila la trae)."""
    celda = None
    if "celda_codigo" in fila:
        celda = Celda(fila["id_celda"], fila["celda_codigo"], TipoVehiculo(fila["celda_tipo"]))
    return Movimiento(
        id_movimiento=fila["id_movimiento"],
        placa=fila["placa"],
        id_celda=fila["id_celda"],
        fecha_ingreso=fila["fecha_ingreso"],
        id_puerta_ingreso=fila["id_puerta_ingreso"],
        id_operario_ingreso=fila["id_operario_ingreso"],
        fecha_salida=fila["fecha_salida"],
        id_puerta_salida=fila["id_puerta_salida"],
        id_operario_salida=fila["id_operario_salida"],
        celda=celda,
    )


class MovimientoRepository:
    def crear(self, conn, placa: str, id_celda: int, id_puerta: int, id_operario: int) -> Movimiento:
        """Registra un ingreso. Los índices únicos de la base son la última barrera:
        si chocan, se traducen a errores del dominio.
        """
        try:
            fila = conn.execute(
                "INSERT INTO movimiento (placa, id_celda, id_puerta_ingreso, id_operario_ingreso) "
                "VALUES (%s, %s, %s, %s) RETURNING *",
                (placa, id_celda, id_puerta, id_operario),
            ).fetchone()
        except psycopg.errors.UniqueViolation as error:
            restriccion = error.diag.constraint_name
            if restriccion == "uq_celda_activa":
                raise CeldaOcupada() from error
            if restriccion == "uq_vehiculo_activo":
                raise VehiculoYaDentro(placa) from error
            raise
        return _a_movimiento(fila)

    def buscar_activo(self, conn, placa: str) -> Optional[Movimiento]:
        """El movimiento abierto de una placa (con su celda), o None si no está dentro."""
        fila = conn.execute(
            _SELECT_CON_CELDA + "WHERE m.placa = %s AND m.fecha_salida IS NULL", (placa,)
        ).fetchone()
        return _a_movimiento(fila) if fila else None

    def cerrar(self, conn, id_movimiento: int, id_puerta: int, id_operario: int) -> Optional[Movimiento]:
        """Registra la salida. La condición fecha_salida IS NULL evita cerrar dos veces
        el mismo movimiento; devuelve None si alguien ya lo había cerrado.
        """
        fila = conn.execute(
            "UPDATE movimiento SET fecha_salida = now(), id_puerta_salida = %s, "
            "id_operario_salida = %s "
            "WHERE id_movimiento = %s AND fecha_salida IS NULL RETURNING *",
            (id_puerta, id_operario, id_movimiento),
        ).fetchone()
        return _a_movimiento(fila) if fila else None

    def listar_activos(self, conn) -> List[Movimiento]:
        """Todos los vehículos que están dentro ahora, del más reciente al más antiguo."""
        filas = conn.execute(
            _SELECT_CON_CELDA + "WHERE m.fecha_salida IS NULL ORDER BY m.fecha_ingreso DESC"
        ).fetchall()
        return [_a_movimiento(f) for f in filas]
