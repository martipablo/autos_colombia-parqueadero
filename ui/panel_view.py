"""Panel principal: es la ventana de trabajo del operario durante todo su turno.

Muestra la ocupación en vivo y ofrece los accesos a las demás ventanas
(ingreso, salida, novedad), que se abren como diálogos modales encima del panel.
"""
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton, QVBoxLayout

from models.entidades import Sesion
from services.contenedor import Servicios
from ui.comun import ejecutar, mostrar_info
from ui.ingreso_view import IngresoView
from ui.novedad_view import NovedadView
from ui.salida_view import SalidaView

_REFRESCO_MS = 5000  # cada 5 s se actualizan los contadores (refleja lo que hace la otra puerta)


class PanelView(QDialog):
    def __init__(self, sesion: Sesion, servicios: Servicios, parent=None):
        super().__init__(parent)
        self._sesion = sesion
        self._servicios = servicios

        self.setWindowTitle("Autos Colombia - Panel")
        self.setMinimumWidth(480)

        # --- Encabezado: quién y desde dónde ---
        titulo = QLabel("Panel de operación")
        titulo.setObjectName("titulo")
        quien = QLabel(f"Operario: {sesion.operario.nombre}   |   {sesion.puerta.nombre}")

        # --- Sección de ocupación (se rellena en _refrescar_ocupacion) ---
        self.lbl_motos = QLabel()
        self.lbl_vehiculos = QLabel()
        self.lbl_total = QLabel()
        self.lbl_mensaje = QLabel("")

        # --- Sección de accesos ---
        btn_ingreso = QPushButton("Registrar ingreso")
        btn_salida = QPushButton("Registrar salida")
        btn_novedad = QPushButton("Registrar novedad")
        btn_cerrar = QPushButton("Cerrar sesión")
        for boton in (btn_ingreso, btn_salida, btn_novedad):
            boton.setObjectName("grande")
        btn_cerrar.setObjectName("secundario")

        acciones = QGridLayout()
        acciones.addWidget(btn_ingreso, 0, 0)
        acciones.addWidget(btn_salida, 0, 1)
        acciones.addWidget(btn_novedad, 1, 0, 1, 2)

        layout = QVBoxLayout(self)
        layout.addWidget(titulo)
        layout.addWidget(quien)
        layout.addWidget(self.lbl_motos)
        layout.addWidget(self.lbl_vehiculos)
        layout.addWidget(self.lbl_total)
        layout.addWidget(self.lbl_mensaje)
        layout.addLayout(acciones)
        layout.addWidget(btn_cerrar)

        # --- Eventos ---
        btn_ingreso.clicked.connect(self._abrir_ingreso)
        btn_salida.clicked.connect(self._abrir_salida)
        btn_novedad.clicked.connect(self._abrir_novedad)
        btn_cerrar.clicked.connect(self.accept)  # "aceptado" = volver al login (ver main.py)

        # Actualización periódica de los contadores
        self._temporizador = QTimer(self)
        self._temporizador.timeout.connect(self._refrescar_ocupacion)
        self._temporizador.start(_REFRESCO_MS)
        self._refrescar_ocupacion()

    def _refrescar_ocupacion(self) -> None:
        """Consulta la ocupación y actualiza los contadores de la pantalla."""
        ok, o = ejecutar(self.lbl_mensaje, self._servicios.ocupacion.consultar_ocupacion)
        if not ok:
            return
        self.lbl_motos.setText(
            f"Motos: {o.motos_ocupadas} ocupadas, {o.motos_libres} libres")
        self.lbl_vehiculos.setText(
            f"Vehículos: {o.vehiculos_ocupados} ocupados, {o.vehiculos_libres} libres")
        self.lbl_total.setText(f"Dentro del parqueadero ahora: {o.total_dentro}")
        mostrar_info(self.lbl_mensaje, "")

    # Cada método abre su ventana de forma modal; al cerrarla se refresca el panel.
    def _abrir_ingreso(self) -> None:
        IngresoView(self._sesion, self._servicios.ingreso, self).exec()
        self._refrescar_ocupacion()

    def _abrir_salida(self) -> None:
        SalidaView(self._sesion, self._servicios.salida, self).exec()
        self._refrescar_ocupacion()

    def _abrir_novedad(self) -> None:
        NovedadView(self._sesion, self._servicios.novedad, self).exec()
