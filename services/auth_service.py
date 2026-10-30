"""Caso de uso: iniciar sesión."""
from typing import List

from database.conexion import transaccion
from excepciones.errores import CredencialesInvalidas, DatosInvalidos
from models.entidades import Operario, Puerta
from repositories.operario_repository import OperarioRepository
from repositories.puerta_repository import PuertaRepository


class AuthService:
    def __init__(self, operarios: OperarioRepository, puertas: PuertaRepository):
        self._operarios = operarios
        self._puertas = puertas

    def listar_puertas(self) -> List[Puerta]:
        """Puertas disponibles para elegir en la pantalla de inicio de sesión."""
        with transaccion() as conn:
            return self._puertas.listar(conn)

    def iniciar_sesion(self, usuario: str, clave: str) -> Operario:
        """Valida usuario y contraseña. Devuelve el operario o lanza CredencialesInvalidas."""
        usuario = (usuario or "").strip()
        if not usuario or not clave:
            raise DatosInvalidos("Escribe tu usuario y tu contraseña.")
        with transaccion() as conn:
            operario = self._operarios.buscar_por_usuario(conn, usuario)
        if operario is None or not operario.verificar_clave(clave):
            raise CredencialesInvalidas()
        return operario
