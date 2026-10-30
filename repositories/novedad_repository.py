"""Acceso a la tabla novedad."""
from models.entidades import Novedad


class NovedadRepository:
    def crear(self, conn, id_movimiento: int, id_operario: int, descripcion: str) -> Novedad:
        """Guarda una novedad ligada a un movimiento activo."""
        fila = conn.execute(
            "INSERT INTO novedad (id_movimiento, id_operario, descripcion) "
            "VALUES (%s, %s, %s) RETURNING *",
            (id_movimiento, id_operario, descripcion),
        ).fetchone()
        return Novedad(
            id_novedad=fila["id_novedad"],
            id_movimiento=fila["id_movimiento"],
            id_operario=fila["id_operario"],
            descripcion=fila["descripcion"],
            fecha_hora=fila["fecha_hora"],
        )
