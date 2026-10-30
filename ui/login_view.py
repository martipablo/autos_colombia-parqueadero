"""Ventana de inicio de sesión.

Flujo: el operario escribe usuario y clave, elige la puerta desde la que trabaja
y pulsa Entrar. Si las credenciales son válidas se cierra con éxito y deja la
Sesion (operario + puerta) disponible en `self.sesion`.
"""
from typing import Optional

from PySide6.QtWidgets import (QComboBox, QDialog, QFormLayout, QLabel, QLineEdit,
                               QPushButton, QVBoxLayout)

from models.entidades import Sesion
from services.auth_service import AuthService
from ui.comun import ejecutar, mostrar_error


class LoginView(QDialog):
    def __init__(self, auth: AuthService, parent=None):
        super().__init__(parent)
        self._auth = auth
        self.sesion: Optional[Sesion] = None

        self.setWindowTitle("Autos Colombia - Inicio de sesión")
        self.setMinimumWidth(380)

        # --- Controles ---
        titulo = QLabel("Autos Colombia")
        titulo.setObjectName("titulo")
        self.txt_usuario = QLineEdit()
        self.txt_clave = QLineEdit()
        self.txt_clave.setEchoMode(QLineEdit.EchoMode.Password)
        self.cmb_puerta = QComboBox()
        self.lbl_mensaje = QLabel("")
        self.btn_entrar = QPushButton("Entrar")
        self.btn_entrar.setDefault(True)

        # --- Distribución ---
        formulario = QFormLayout()
        formulario.addRow("Usuario", self.txt_usuario)
        formulario.addRow("Contraseña", self.txt_clave)
        formulario.addRow("Puerta", self.cmb_puerta)
        layout = QVBoxLayout(self)
        layout.addWidget(titulo)
        layout.addLayout(formulario)
        layout.addWidget(self.lbl_mensaje)
        layout.addWidget(self.btn_entrar)

        # --- Eventos: clic en Entrar o Enter en la clave disparan el mismo método ---
        self.btn_entrar.clicked.connect(self._entrar)
        self.txt_clave.returnPressed.connect(self._entrar)

        self._cargar_puertas()

    def _cargar_puertas(self) -> None:
        """Llena la lista de puertas desde la base al abrir la ventana."""
        ok, puertas = ejecutar(self.lbl_mensaje, self._auth.listar_puertas)
        if ok:
            for puerta in puertas:
                self.cmb_puerta.addItem(puerta.nombre, puerta)  # el objeto viaja como dato

    def _entrar(self) -> None:
        """Valida las credenciales; si son correctas, crea la Sesion y cierra la ventana."""
        puerta = self.cmb_puerta.currentData()
        if puerta is None:
            mostrar_error(self.lbl_mensaje, "No hay puertas configuradas en el sistema.")
            return
        ok, operario = ejecutar(
            self.lbl_mensaje,
            lambda: self._auth.iniciar_sesion(self.txt_usuario.text(), self.txt_clave.text()),
        )
        if ok:
            self.sesion = Sesion(operario=operario, puerta=puerta)
            self.accept()  # exec() devuelve "aceptado" y main.py abre el panel
        else:
            self.txt_clave.clear()
            self.txt_clave.setFocus()
