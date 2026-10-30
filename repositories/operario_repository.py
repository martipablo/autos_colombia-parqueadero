"""Acceso a la tabla operario."""
from typing import Optional

from models.entidades import Operario
from models.enums import Turno


class OperarioRepository:
    def buscar_por_usuario(self, conn, usuario: str) -> Optional[Operario]:
        """Devuelve el operario con ese nombre de usuario, o None si no existe."""
        fila = conn.execute(
            "SELECT id_operario, nombre, usuario, clave_hash, turno "
            "FROM operario WHERE usuario = %s",
            (usuario,),
        ).fetchone()
        if fila is None:
            return None
        return Operario(
            id_operario=fila["id_operario"],
            nombre=fila["nombre"],
            usuario=fila["usuario"],
            clave_hash=fila["clave_hash"],
            turno=Turno(fila["turno"]),
        )
