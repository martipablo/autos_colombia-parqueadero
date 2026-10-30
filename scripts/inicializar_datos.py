"""Crea las tablas y carga los datos iniciales. Se puede ejecutar varias veces.

Uso (desde la carpeta del proyecto):
    python -m scripts.inicializar_datos

Carga: 2 puertas, 80 celdas (10 de motos y 70 de vehículos), 3 operarios de prueba
(clave 1234) y algunos propietarios y vehículos de ejemplo.
"""
from pathlib import Path

from database.conexion import transaccion
from models.seguridad import generar_hash

RUTA_ESQUEMA = Path(__file__).resolve().parent.parent / "sql" / "esquema.sql"

OPERARIOS = [  # (nombre, usuario, turno)
    ("Operario Día 1", "dia1", "DIA"),
    ("Operario Día 2", "dia2", "DIA"),
    ("Operario Noche", "noche1", "NOCHE"),
]
PROPIETARIOS = [  # (nombre, documento, teléfono)
    ("Laura Gómez", "1000000001", "3001112233"),
    ("Carlos Ruiz", "1000000002", "3004445566"),
    ("Marta Pérez", "1000000003", "3007778899"),
]
VEHICULOS = [  # (placa, tipo, marca, color, documento del propietario)
    ("ABC123", "VEHICULO", "Mazda", "Rojo", "1000000001"),
    ("XYZ789", "VEHICULO", "Renault", "Gris", "1000000001"),  # un dueño con 2 vehículos
    ("MOT12A", "MOTO", "Yamaha", "Negro", "1000000002"),
    ("DEF456", "VEHICULO", "Chevrolet", "Azul", "1000000003"),
]


def main() -> None:
    with transaccion() as conn:
        # 1. Tablas e índices
        conn.execute(RUTA_ESQUEMA.read_text(encoding="utf-8"))

        with conn.cursor() as cur:
            # 2. Puertas
            cur.executemany(
                "INSERT INTO puerta (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING",
                [("Puerta 1",), ("Puerta 2",)])

            # 3. Celdas: M01-M10 para motos y V01-V70 para vehículos
            celdas = [(f"M{i:02d}", "MOTO") for i in range(1, 11)]
            celdas += [(f"V{i:02d}", "VEHICULO") for i in range(1, 71)]
            cur.executemany(
                "INSERT INTO celda (codigo, tipo) VALUES (%s, %s) ON CONFLICT (codigo) DO NOTHING",
                celdas)

            # 4. Operarios de prueba (la clave se guarda con hash, nunca en claro)
            cur.executemany(
                "INSERT INTO operario (nombre, usuario, clave_hash, turno) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (usuario) DO NOTHING",
                [(n, u, generar_hash("1234"), t) for n, u, t in OPERARIOS])

            # 5. Propietarios y vehículos de ejemplo
            cur.executemany(
                "INSERT INTO propietario (nombre, documento, telefono) "
                "VALUES (%s, %s, %s) ON CONFLICT (documento) DO NOTHING",
                PROPIETARIOS)
            cur.executemany(
                "INSERT INTO vehiculo (placa, tipo, marca, color, id_propietario) "
                "SELECT %s, %s, %s, %s, id_propietario FROM propietario WHERE documento = %s "
                "ON CONFLICT (placa) DO NOTHING",
                VEHICULOS)
    print("Base de datos lista: esquema, 2 puertas, 80 celdas y datos de prueba.")


if __name__ == "__main__":
    main()
