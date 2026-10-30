"""Ventana de registro de ingreso (HU-01 a HU-04).

Flujo en dos pasos:
  1. Verificar: se escribe la placa y el sistema comprueba que esté registrada,
     que no esté ya dentro y que haya cupo. Muestra los datos del vehículo.
  2. Confirmar: asigna la celda y registra el ingreso. Se muestra la celda asignada.
Cualquier cambio en la placa reinicia el proceso.
"""
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QVBoxLayout)

from models.entidades import Sesion
from services.ingreso_service import IngresoService
from ui.comun import ejecutar, mostrar_info, mostrar_ok


class IngresoView(QDialog):
    def __init__(self, sesion: Sesion, servicio: IngresoService, parent=None):
        super().__init__(parent)
        self._sesion = sesion
        self._servicio = servicio

        self.setWindowTitle("Registrar ingreso")
        self.setMinimumWidth(440)

        # --- Controles ---
        titulo = QLabel("Registrar ingreso")
        titulo.setObjectName("titulo")
        self.txt_placa = QLineEdit()
        self.txt_placa.setPlaceholderText("Placa, por ejemplo ABC123")
        self.txt_placa.setMaxLength(10)
        self.btn_verificar = QPushButton("Verificar")
        self.lbl_datos = QLabel("")      # propietario, tipo, marca y color
        self.lbl_celda = QLabel("")      # celda asignada tras confirmar
        self.lbl_celda.setObjectName("celda")
        self.lbl_mensaje = QLabel("")
        self.btn_confirmar = QPushButton("Confirmar ingreso")
        self.btn_confirmar.setEnabled(False)  # solo se habilita tras verificar con éxito
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setObjectName("secundario")

        # --- Distribución ---
        fila_placa = QHBoxLayout()
        fila_placa.addWidget(self.txt_placa)
        fila_placa.addWidget(self.btn_verificar)
        layout = QVBoxLayout(self)
        layout.addWidget(titulo)
        layout.addLayout(fila_placa)
        layout.addWidget(self.lbl_datos)
        layout.addWidget(self.lbl_celda)
        layout.addWidget(self.lbl_mensaje)
        layout.addWidget(self.btn_confirmar)
        layout.addWidget(btn_cerrar)

        # --- Eventos ---
        self.txt_placa.textEdited.connect(self._al_editar_placa)
        self.txt_placa.returnPressed.connect(self._verificar)
        self.btn_verificar.clicked.connect(self._verificar)
        self.btn_confirmar.clicked.connect(self._confirmar)
        btn_cerrar.clicked.connect(self.accept)

    def _al_editar_placa(self, texto: str) -> None:
        """Pone la placa en mayúsculas y borra resultados anteriores."""
        if texto != texto.upper():
            self.txt_placa.setText(texto.upper())
        self._reiniciar()

    def _reiniciar(self) -> None:
        self.btn_confirmar.setEnabled(False)
        self.lbl_datos.setText("")
        self.lbl_celda.setText("")
        mostrar_info(self.lbl_mensaje, "")

    def _verificar(self) -> None:
        """Paso 1: valida el vehículo y muestra sus datos."""
        self._reiniciar()
        ok, vehiculo = ejecutar(
            self.lbl_mensaje, lambda: self._servicio.verificar_ingreso(self.txt_placa.text()))
        if not ok:
            return
        self.lbl_datos.setText(
            f"Propietario: {vehiculo.propietario.nombre}\n"
            f"Tipo: {vehiculo.tipo.etiqueta}   Marca: {vehiculo.marca}   Color: {vehiculo.color}")
        mostrar_info(self.lbl_mensaje, "Vehículo verificado. Confirma el ingreso.")
        self.btn_confirmar.setEnabled(True)

    def _confirmar(self) -> None:
        """Paso 2: asigna la celda y registra el ingreso."""
        ok, movimiento = ejecutar(
            self.lbl_mensaje,
            lambda: self._servicio.registrar_ingreso(self.txt_placa.text(), self._sesion))
        self.btn_confirmar.setEnabled(False)  # evita registrar dos veces con doble clic
        if ok:
            self.lbl_celda.setText(f"Celda asignada: {movimiento.celda.codigo}")
            mostrar_ok(self.lbl_mensaje, "Ingreso registrado.")
