"""Manejo de contraseñas: nunca se guarda la clave, solo su hash con sal (PBKDF2-SHA256)."""
import hashlib
import hmac
import secrets

_ITERACIONES = 200_000


def generar_hash(clave: str) -> str:
    """Devuelve 'sal$hash' en hexadecimal. Cada clave lleva una sal aleatoria distinta."""
    sal = secrets.token_bytes(16)
    derivada = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), sal, _ITERACIONES)
    return f"{sal.hex()}${derivada.hex()}"


def comprobar_clave(clave: str, almacenado: str) -> bool:
    """Recalcula el hash con la sal guardada y lo compara en tiempo constante."""
    try:
        sal_hex, hash_hex = almacenado.split("$")
        sal = bytes.fromhex(sal_hex)
    except ValueError:
        return False
    derivada = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), sal, _ITERACIONES)
    return hmac.compare_digest(derivada.hex(), hash_hex)
