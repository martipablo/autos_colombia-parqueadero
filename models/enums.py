"""Enumeraciones del dominio."""
from enum import Enum


class TipoVehiculo(str, Enum):
    """Categoría que decide en qué bloque de celdas se parquea (10 de motos, 70 de vehículos)."""
    MOTO = "MOTO"
    VEHICULO = "VEHICULO"

    @property
    def etiqueta(self) -> str:
        """Texto legible para mostrar en pantalla."""
        return "moto" if self is TipoVehiculo.MOTO else "vehículo"


class Turno(str, Enum):
    DIA = "DIA"
    NOCHE = "NOCHE"
