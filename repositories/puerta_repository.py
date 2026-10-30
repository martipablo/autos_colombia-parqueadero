"""Acceso a la tabla puerta."""
from typing import List

from models.entidades import Puerta


class PuertaRepository:
    def listar(self, conn) -> List[Puerta]:
        """Todas las puertas, para que el operario elija desde cuál trabaja."""
        filas = conn.execute(
            "SELECT id_puerta, nombre FROM puerta ORDER BY id_puerta"
        ).fetchall()
        return [Puerta(f["id_puerta"], f["nombre"]) for f in filas]
