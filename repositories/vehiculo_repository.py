"""Acceso a las tablas vehiculo y propietario (solo lectura en esta iteración)."""
from typing import Optional

from models.entidades import Propietario, Vehiculo
from models.enums import TipoVehiculo


class VehiculoRepository:
    def buscar_por_placa(self, conn, placa: str) -> Optional[Vehiculo]:
        """Busca el vehículo junto con su propietario. None si la placa no está registrada."""
        fila = conn.execute(
            "SELECT v.placa, v.tipo, v.marca, v.color, v.id_propietario, "
            "       p.nombre, p.documento, p.telefono "
            "FROM vehiculo v JOIN propietario p ON p.id_propietario = v.id_propietario "
            "WHERE v.placa = %s",
            (placa,),
        ).fetchone()
        if fila is None:
            return None
        propietario = Propietario(
            id_propietario=fila["id_propietario"],
            nombre=fila["nombre"],
            documento=fila["documento"],
            telefono=fila["telefono"],
        )
        return Vehiculo(
            placa=fila["placa"],
            tipo=TipoVehiculo(fila["tipo"]),
            marca=fila["marca"],
            color=fila["color"],
            id_propietario=fila["id_propietario"],
            propietario=propietario,
        )
