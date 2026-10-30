"""Acceso a la tabla celda.

Una celda está ocupada cuando tiene un movimiento sin fecha de salida;
por eso el estado nunca se guarda aparte, siempre se calcula.
"""
from typing import Optional

from models.entidades import Celda, Ocupacion
from models.enums import TipoVehiculo


class CeldaRepository:
    def asignar_disponible(self, conn, tipo: TipoVehiculo) -> Optional[Celda]:
        """Elige una celda libre del tipo pedido y la bloquea para esta transacción.

        FOR UPDATE SKIP LOCKED es la clave contra los choques entre puertas: si otra
        transacción ya tiene bloqueada una celda, esta la salta y toma la siguiente
        libre, así dos operarios simultáneos nunca reciben la misma.
        Devuelve None si no queda ninguna.
        """
        fila = conn.execute(
            "SELECT c.id_celda, c.codigo, c.tipo FROM celda c "
            "WHERE c.tipo = %s AND NOT EXISTS ("
            "    SELECT 1 FROM movimiento m "
            "    WHERE m.id_celda = c.id_celda AND m.fecha_salida IS NULL) "
            "ORDER BY c.codigo LIMIT 1 "
            "FOR UPDATE OF c SKIP LOCKED",
            (tipo.value,),
        ).fetchone()
        if fila is None:
            return None
        return Celda(fila["id_celda"], fila["codigo"], TipoVehiculo(fila["tipo"]))

    def contar_libres(self, conn, tipo: TipoVehiculo) -> int:
        """Cantidad de celdas libres de un tipo (para avisar si no hay cupo)."""
        fila = conn.execute(
            "SELECT COUNT(*) AS libres FROM celda c "
            "WHERE c.tipo = %s AND NOT EXISTS ("
            "    SELECT 1 FROM movimiento m "
            "    WHERE m.id_celda = c.id_celda AND m.fecha_salida IS NULL)",
            (tipo.value,),
        ).fetchone()
        return fila["libres"]

    def contar_por_estado(self, conn) -> Ocupacion:
        """Celdas libres y ocupadas por tipo, en una sola consulta."""
        filas = conn.execute(
            "SELECT c.tipo, COUNT(*) AS total, COUNT(m.id_movimiento) AS ocupadas "
            "FROM celda c LEFT JOIN movimiento m "
            "  ON m.id_celda = c.id_celda AND m.fecha_salida IS NULL "
            "GROUP BY c.tipo"
        ).fetchall()
        datos = {f["tipo"]: (f["total"], f["ocupadas"]) for f in filas}
        motos_total, motos_ocup = datos.get(TipoVehiculo.MOTO.value, (0, 0))
        veh_total, veh_ocup = datos.get(TipoVehiculo.VEHICULO.value, (0, 0))
        return Ocupacion(
            motos_libres=motos_total - motos_ocup,
            motos_ocupadas=motos_ocup,
            vehiculos_libres=veh_total - veh_ocup,
            vehiculos_ocupados=veh_ocup,
        )
