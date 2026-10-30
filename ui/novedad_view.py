"""Ventana de registro de novedades (HU-07).

El operario elige uno de los vehículos que están dentro, escribe qué ocurrió
y guarda. La novedad queda ligada al ingreso activo de ese vehículo.
"""
from PySide6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QLabel, QPlainTextEdit,
                               QPushButton, QVBoxLayout)

from models.entidades import Sesion
from services.novedad_service import NovedadService
from ui.comun import ejecutar, mostrar_info, mostrar_ok


class NovedadView(QDialog):
    def __init__(self, sesion: Sesion, servicio: NovedadService, parent=None):
        super().__init__(parent)
        self._sesion = sesion
        self._servicio = servicio

        self.setWindowTitle("Registrar novedad")
        self.setMinimumWidth(460)

        # --- Controles ---
        titulo = QLabel("Registrar novedad")
        titulo.setObjectName("titulo")
        self.cmb_vehiculos = QComboBox()
        btn_actualizar = QPushButton("Actualizar lista")
        btn_actualizar.setObjectName("secundario")
        self.txt_descripcion = QPlainTextEdit()
        self.txt_descripcion.setPlaceholderText("Describe lo ocurrido (rayón, objeto olvidado...)")
        self.lbl_mensaje = QLabel("")
        self.btn_guardar = QPushButton("Guardar novedad")
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setObjectName("secundario")

        # --- Distribución ---
        fila_lista = QHBoxLayout()
        fila_lista.addWidget(self.cmb_vehiculos, 1)
        fila_lista.addWidget(btn_actualizar)
        layout = QVBoxLayout(self)
        layout.addWidget(titulo)
        layout.addWidget(QLabel("Vehículo (dentro del parqueadero)"))
        layout.addLayout(fila_lista)
        layout.addWidget(self.txt_descripcion)
        layout.addWidget(self.lbl_mensaje)
        layout.addWidget(self.btn_guardar)
        layout.addWidget(btn_cerrar)

        # --- Eventos ---
        btn_actualizar.clicked.connect(self._cargar_vehiculos)
        self.btn_guardar.clicked.connect(self._guardar)
        btn_cerrar.clicked.connect(self.accept)

        self._cargar_vehiculos()

    def _cargar_vehiculos(self) -> None:
        """Llena la lista con los vehículos que están dentro (placa y celda)."""
        self.cmb_vehiculos.clear()
        ok, movimientos = ejecutar(self.lbl_mensaje, self._servicio.listar_vehiculos_dentro)
        if not ok:
            return
        for m in movimientos:
            self.cmb_vehiculos.addItem(f"{m.placa}  -  celda {m.celda.codigo}", m.placa)
        hay = bool(movimientos)
        self.btn_guardar.setEnabled(hay)
        if not hay:
            mostrar_info(self.lbl_mensaje, "No hay vehículos dentro del parqueadero.")
        else:
            mostrar_info(self.lbl_mensaje, "")

    def _guardar(self) -> None:
        """Guarda la novedad del vehículo seleccionado."""
        placa = self.cmb_vehiculos.currentData()
        ok, _ = ejecutar(
            self.lbl_mensaje,
            lambda: self._servicio.registrar_novedad(
                placa, self.txt_descripcion.toPlainText(), self._sesion))
        if ok:
            self.txt_descripcion.clear()
            mostrar_ok(self.lbl_mensaje, f"Novedad registrada para {placa}.")
