"""Prueba del requisito anti-duplicados: muchas entradas simultáneas desde las dos puertas.

Crea vehículos temporales, los hace ingresar todos a la vez desde hilos que alternan
entre las dos puertas y verifica que ninguna celda se haya asignado dos veces.
Al final limpia todo lo que creó.

Uso:  python -m scripts.prueba_concurrencia
"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from database.conexion import transaccion
from excepciones.errores import SinCupo
from models.entidades import Sesion
from models.seguridad import generar_hash
from services.contenedor import crear_servicios

N_VEHICULOS = 70   # llegan 70 vehículos a la vez para 70 celdas
N_MOTOS = 13       # llegan 13 motos para solo 10 celdas: 3 deben ser rechazadas
DOC_PRUEBA = "TEST-CONCURRENCIA"


def preparar():
    """Crea el propietario y los vehículos de prueba; devuelve las dos sesiones y las placas."""
    with transaccion() as conn:
        operario = servicios.auth._operarios.buscar_por_usuario(conn, "dia1")
        puertas = servicios.auth._puertas.listar(conn)
        id_prop = conn.execute(
            "INSERT INTO propietario (nombre, documento) VALUES ('Prueba', %s) "
            "ON CONFLICT (documento) DO UPDATE SET nombre = 'Prueba' RETURNING id_propietario",
            (DOC_PRUEBA,)).fetchone()["id_propietario"]
        placas = []
        for i in range(N_VEHICULOS):
            placas.append((f"TV{i:04d}", "VEHICULO"))
        for i in range(N_MOTOS):
            placas.append((f"TM{i:04d}", "MOTO"))
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO vehiculo (placa, tipo, marca, color, id_propietario) "
                "VALUES (%s, %s, 'Prueba', 'Prueba', %s) ON CONFLICT (placa) DO NOTHING",
                [(p, t, id_prop) for p, t in placas])
    sesiones = [Sesion(operario, puertas[0]), Sesion(operario, puertas[1])]
    return sesiones, [p for p, _ in placas]


def limpiar(placas):
    """Borra movimientos, vehículos y propietario de prueba."""
    with transaccion() as conn:
        conn.execute("DELETE FROM movimiento WHERE placa = ANY(%s)", (placas,))
        conn.execute("DELETE FROM vehiculo WHERE placa = ANY(%s)", (placas,))
        conn.execute("DELETE FROM propietario WHERE documento = %s", (DOC_PRUEBA,))


def intentar_ingreso(args):
    placa, sesion = args
    try:
        return servicios.ingreso.registrar_ingreso(placa, sesion).celda.codigo
    except SinCupo:
        return "SIN_CUPO"


servicios = crear_servicios()

if __name__ == "__main__":
    sesiones, placas = preparar()
    try:
        tareas = [(p, sesiones[i % 2]) for i, p in enumerate(placas)]  # alterna puertas
        with ThreadPoolExecutor(max_workers=24) as pool:
            resultados = list(pool.map(intentar_ingreso, tareas))

        celdas = [r for r in resultados if r != "SIN_CUPO"]
        rechazados = resultados.count("SIN_CUPO")
        repetidas = [c for c, n in Counter(celdas).items() if n > 1]

        print(f"Intentos: {len(resultados)} | Ingresos: {len(celdas)} | Sin cupo: {rechazados}")
        print(f"Celdas repetidas: {repetidas or 'ninguna'}")
        assert not repetidas, "¡Se asignó la misma celda dos veces!"
        assert len(celdas) == 80, "Debían entrar exactamente 80 (70 vehículos + 10 motos)"
        assert rechazados == N_MOTOS - 10, "Las motos sobrantes debían ser rechazadas"
        print("OK: sin duplicados y con control de capacidad.")
    finally:
        limpiar(placas)
