"""Funciones de apoyo compartidas por los servicios."""
import re

from excepciones.errores import DatosInvalidos

_PATRON_PLACA = re.compile(r"^[A-Z0-9]{5,7}$")


def normalizar_placa(texto: str) -> str:
    """Deja la placa en mayúsculas y sin espacios ni guiones ('abc-123' -> 'ABC123').

    Lanza DatosInvalidos si el resultado no parece una placa.
    """
    placa = (texto or "").strip().upper().replace("-", "").replace(" ", "")
    if not _PATRON_PLACA.match(placa):
        raise DatosInvalidos("Escribe una placa válida (de 5 a 7 letras o números).")
    return placa
