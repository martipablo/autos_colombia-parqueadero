"""Ventana de registro de salida (HU-05).

Flujo en dos pasos:
  1. Buscar: con la placa se muestra la celda y la hora de ingreso del vehículo.
  2. Confirmar: registra la salida y la celda queda libre otra vez.
"""
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QVBoxLayout)

from models.entidades import Sesion
from services.salida_service import SalidaService
from ui.comun import ejecutar, mostrar_info, mostrar_ok


class SalidaView(QDialog):
    def __init__(self, sesion: Sesion, servicio: SalidaService, parent=None):
        super().__init__(parent)
        self._sesion = sesion
        self._servicio = servicio

        self.setWindowTitle("Registrar salida")
        self.setMinimumWidth(440)

        # --- Controles ---
        titulo = QLabel("Registrar salida")
        titulo.setObjectName("titulo")
        self.txt_placa = QLineEdit()
        self.txt_placa.setPlaceholderText("Placa, por ejemplo ABC123")
        self.txt_placa.setMaxLength(10)
        self.btn_buscar = QPushButton("Buscar")
        self.lbl_datos = QLabel("")
        self.lbl_mensaje = QLabel("")
        self.btn_confirmar = QPushButton("Confirmar salida")
        self.btn_confirmar.setEnabled(False)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setObjectName("secundario")

        # --- Distribución ---
        fila_placa = QHBoxLayout()
        fila_placa.addWidget(self.txt_placa)
        fila_placa.addWidget(self.btn_buscar)
        layout = QVBoxLayout(self)
        layout.addWidget(titulo)
        layout.addLayout(fila_placa)
        layout.addWidget(self.lbl_datos)
        layout.addWidget(self.lbl_mensaje)
        layout.addWidget(self.btn_confirmar)
        layout.addWidget(btn_cerrar)

        # --- Eventos ---
        self.txt_placa.textEdited.connect(self._al_editar_placa)
        self.txt_placa.returnPressed.connect(self._buscar)
        self.btn_buscar.clicked.connect(self._buscar)
        self.btn_confirmar.clicked.connect(self._confirmar)
        btn_cerrar.clicked.connect(self.accept)

    def _al_editar_placa(self, texto: str) -> None:
        if texto != texto.upper():
            self.txt_placa.setText(texto.upper())
        self._reiniciar()

    def _reiniciar(self) -> None:
        self.btn_confirmar.setEnabled(False)
        self.lbl_datos.setText("")
        mostrar_info(self.lbl_mensaje, "")

    def _buscar(self) -> None:
        """Paso 1: busca el ingreso activo y muestra celda y hora."""
        self._reiniciar()
        ok, movimiento = ejecutar(
            self.lbl_mensaje,
            lambda: self._servicio.consultar_movimiento_activo(self.txt_placa.text()))
        if not ok:
            return
        self.lbl_datos.setText(
            f"Celda: {movimiento.celda.codigo}\n"
            f"Ingresó: {movimiento.fecha_ingreso:%d/%m/%Y %H:%M}")
        mostrar_info(self.lbl_mensaje, "Confirma la salida del vehículo.")
        self.btn_confirmar.setEnabled(True)

    def _confirmar(self) -> None:
        """Paso 2: registra la salida y libera la celda."""
        ok, movimiento = ejecutar(
            self.lbl_mensaje,
            lambda: self._servicio.registrar_salida(self.txt_placa.text(), self._sesion))
        self.btn_confirmar.setEnabled(False)
        if ok:
            mostrar_ok(self.lbl_mensaje,
                       f"Salida registrada. La celda {movimiento.celda.codigo} quedó libre.")
