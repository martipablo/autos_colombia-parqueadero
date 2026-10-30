"""Conexión a PostgreSQL y manejo de transacciones.

Cada operación del sistema abre su propia conexión con `transaccion()`:
si todo sale bien se confirma (commit); si algo falla se deshace (rollback).
Los datos de conexión salen de variables de entorno, con valores por defecto para desarrollo.
"""
import os
from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg.rows import dict_row

from excepciones.errores import ErrorBaseDatos


def _abrir_conexion() -> psycopg.Connection:
    """Abre una conexión nueva. Las filas llegan como diccionarios (columna -> valor)."""
    return psycopg.connect(
        host=os.getenv("PARQ_DB_HOST", "127.0.0.1"),
        port=os.getenv("PARQ_DB_PORT", "5432"),
        dbname=os.getenv("PARQ_DB_NAME", "parqueadero"),
        user=os.getenv("PARQ_DB_USER", "parq_app"),
        password=os.getenv("PARQ_DB_PASSWORD", "Parq_app123"),
        row_factory=dict_row,
        connect_timeout=5,
    )


@contextmanager
def transaccion() -> Iterator[psycopg.Connection]:
    """Entrega una conexión dentro de una transacción.

    Uso:
        with transaccion() as conn:
            ...consultas...
    Al salir del bloque sin errores hace commit; con cualquier error hace rollback.
    Los fallos de comunicación se traducen a ErrorBaseDatos para que la interfaz
    no necesite conocer psycopg.
    """
    try:
        conexion = _abrir_conexion()
    except psycopg.OperationalError as error:
        raise ErrorBaseDatos("No se pudo conectar con la base de datos.") from error
    try:
        with conexion:  # commit / rollback / cierre automáticos
            yield conexion
    except psycopg.OperationalError as error:
        raise ErrorBaseDatos("Falló la comunicación con la base de datos.") from error
