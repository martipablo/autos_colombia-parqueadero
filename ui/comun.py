"""Piezas compartidas por todas las ventanas: estilos y manejo uniforme de errores."""
import logging
from typing import Callable, Tuple, TypeVar

from PySide6.QtWidgets import QLabel

from excepciones.errores import ParqueaderoError

T = TypeVar("T")

# Hoja de estilos global (se aplica una sola vez en main.py).
HOJA_ESTILOS = """
QDialog { background: #000000; }
QLabel { font-size: 14px; color: #f2f2f2; }
QLabel#titulo { font-size: 20px; font-weight: 700; color: #ffffff; }
QLabel#celda { font-size: 28px; font-weight: 700; color: #4ade80; }
QLineEdit, QComboBox, QPlainTextEdit { font-size: 15px; padding: 6px; background: #1c1c1e;
    color: #ffffff; border: 1px solid #555555; border-radius: 4px; selection-background-color: #2f5fd0; }
QComboBox QAbstractItemView { background: #1c1c1e; color: #ffffff; selection-background-color: #2f5fd0; }
QPushButton { font-size: 15px; padding: 8px 14px; border-radius: 6px;
              background: #2f5fd0; color: #ffffff; }
QPushButton:hover { background: #4573e0; }
QPushButton:disabled { background: #2a2a2e; color: #777777; }
QPushButton#secundario { background: #2a2a2e; color: #f2f2f2; }
QPushButton#secundario:hover { background: #3a3a40; }
QPushButton#grande { font-size: 18px; padding: 16px; }
"""

_ESTILO_ERROR = "color: #ff6b6b; font-weight: 600;"
_ESTILO_OK = "color: #4ade80; font-weight: 600;"
_ESTILO_NEUTRO = "color: #d0d0d0;"

def mostrar_error(etiqueta: QLabel, texto: str) -> None:
    """Pinta un mensaje de error (rojo) en la etiqueta de mensajes de la ventana."""
    etiqueta.setStyleSheet(_ESTILO_ERROR)
    etiqueta.setText(texto)


def mostrar_ok(etiqueta: QLabel, texto: str) -> None:
    """Pinta un mensaje de éxito (verde)."""
    etiqueta.setStyleSheet(_ESTILO_OK)
    etiqueta.setText(texto)


def mostrar_info(etiqueta: QLabel, texto: str) -> None:
    """Pinta un mensaje informativo (gris)."""
    etiqueta.setStyleSheet(_ESTILO_NEUTRO)
    etiqueta.setText(texto)


def ejecutar(etiqueta: QLabel, funcion: Callable[[], T]) -> Tuple[bool, T]:
    """Ejecuta una acción de negocio y muestra cualquier error en `etiqueta`.

    Devuelve (True, resultado) si funcionó o (False, None) si falló. Así las ventanas
    no repiten try/except: los errores controlados se muestran tal cual y los
    inesperados se registran en el log con un mensaje genérico para el operario.
    """
    try:
        return True, funcion()
    except ParqueaderoError as error:
        mostrar_error(etiqueta, str(error))
    except Exception:  # noqa: BLE001 - último recurso para que la ventana no se cierre
        logging.exception("Error inesperado")
        mostrar_error(etiqueta, "Ocurrió un error inesperado. Avisa al administrador.")
    return False, None
