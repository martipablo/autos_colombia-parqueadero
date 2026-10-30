"""Punto de entrada de la aplicación de escritorio de Autos Colombia.

Flujo de ejecución:
  1. Se crea la aplicación Qt y los servicios (capa de negocio).
  2. Se muestra el login; si el operario entra, se abre el panel.
  3. En el panel el operario trabaja todo el turno. Con "Cerrar sesión" se vuelve
     al login (cambio de turno); cerrando la ventana con la X se termina el programa.
"""
import logging
import sys

from PySide6.QtWidgets import QApplication

from services.contenedor import crear_servicios
from ui.comun import HOJA_ESTILOS
from ui.login_view import LoginView
from ui.panel_view import PanelView


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    app = QApplication(sys.argv)
    app.setStyleSheet(HOJA_ESTILOS)
    servicios = crear_servicios()

    while True:
        login = LoginView(servicios.auth)
        # exec() abre la ventana y espera: devuelve 1 si se aceptó y 0 si se cerró con la X
        if not login.exec():
            break
        panel = PanelView(login.sesion, servicios)
        if not panel.exec():  # 0 = cerró con la X -> salir; 1 = "Cerrar sesión" -> otro login
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
