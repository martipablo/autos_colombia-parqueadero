"""Entidades del dominio (las clases del diagrama de clases).

Son datos puros: no saben nada de PostgreSQL ni de la interfaz.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from models.enums import TipoVehiculo, Turno
from models.seguridad import comprobar_clave


@dataclass
class Propietario:
    id_propietario: int
    nombre: str
    documento: str
    telefono: Optional[str] = None


@dataclass
class Vehiculo:
    placa: str
    tipo: TipoVehiculo
    marca: str
    color: str
    id_propietario: int
    propietario: Optional[Propietario] = None  # se llena cuando la consulta lo trae


@dataclass
class Celda:
    id_celda: int
    codigo: str
    tipo: TipoVehiculo


@dataclass
class Puerta:
    id_puerta: int
    nombre: str


@dataclass
class Operario:
    id_operario: int
    nombre: str
    usuario: str
    clave_hash: str
    turno: Turno

    def verificar_clave(self, clave: str) -> bool:
        """True si la clave escrita corresponde al hash guardado."""
        return comprobar_clave(clave, self.clave_hash)


@dataclass
class Movimiento:
    """Una visita completa: nace al ingresar y se cierra al salir."""
    id_movimiento: int
    placa: str
    id_celda: int
    fecha_ingreso: datetime
    id_puerta_ingreso: int
    id_operario_ingreso: int
    fecha_salida: Optional[datetime] = None
    id_puerta_salida: Optional[int] = None
    id_operario_salida: Optional[int] = None
    celda: Optional[Celda] = None  # se llena cuando la consulta o el servicio la conoce

    def esta_activo(self) -> bool:
        """El vehículo sigue dentro mientras no tenga fecha de salida."""
        return self.fecha_salida is None


@dataclass
class Novedad:
    id_novedad: int
    id_movimiento: int
    id_operario: int
    descripcion: str
    fecha_hora: datetime


@dataclass
class Ocupacion:
    """Foto del estado del parqueadero: celdas libres y ocupadas por tipo."""
    motos_libres: int
    motos_ocupadas: int
    vehiculos_libres: int
    vehiculos_ocupados: int

    @property
    def total_dentro(self) -> int:
        return self.motos_ocupadas + self.vehiculos_ocupados


@dataclass
class Sesion:
    """Quién está trabajando y desde qué puerta; se crea al iniciar sesión."""
    operario: Operario
    puerta: Puerta
