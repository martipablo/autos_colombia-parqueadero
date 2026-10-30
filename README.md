# Autos Colombia - Gestión de entrada y salida de vehículos (Iteración 1)

Aplicación de escritorio en Python (PySide6) con base de datos PostgreSQL.

## Cómo ejecutarlo

1. Crea la base de datos: `createdb parqueadero` (o desde pgAdmin), no olvides crear las tablas (`sql/esquema.sql`).
2. Instala las dependencias: `pip install -r requirements.txt`
3. Si tu PostgreSQL no usa los datos por defecto, define las variables de `.env.example`
   en tu terminal (`PARQ_DB_HOST`, `PARQ_DB_PORT`, `PARQ_DB_NAME`, `PARQ_DB_USER`, `PARQ_DB_PASSWORD`).
4. Crea las tablas y los datos iniciales: `python -m scripts.inicializar_datos`
5. Abre la aplicación: `python main.py`

Usuarios de prueba: `dia1`, `dia2` y `noche1`, todos con clave `1234`.
Placas de prueba: `ABC123`, `XYZ789`, `DEF456` (vehículos) y `MOT12A` (moto).

## Estructura

| Carpeta | Qué contiene |
|---|---|
| `ui/` | Ventanas PySide6: login, panel, ingreso, salida y novedad. |
| `services/` | Reglas de negocio, un archivo por caso de uso. |
| `repositories/` | Consultas SQL, una clase por tabla. |
| `models/` | Entidades, enumeraciones y manejo de contraseñas. |
| `database/` | Conexión y transacciones. |
| `excepciones/` | Errores controlados con mensajes para el operario. |
| `sql/` | Esquema físico de la base de datos. |
| `scripts/` | Carga de datos iniciales y prueba de concurrencia. |

Regla de capas: `ui` solo habla con `services`; `services` con `repositories`; `repositories` con la base.

## Flujo de un ingreso

`main.py` -> `LoginView` -> `PanelView` -> `IngresoView` -> `IngresoService.verificar_ingreso` (¿registrado?, ¿ya dentro?, ¿hay cupo?)
-> `IngresoService.registrar_ingreso` -> `CeldaRepository.asignar_disponible` (bloquea la celda) -> `MovimientoRepository.crear`.

## Anti-duplicados

Dos defensas: la celda se bloquea al asignarla (`FOR UPDATE SKIP LOCKED`) y la base tiene índices únicos
que impiden dos movimientos abiertos sobre la misma celda o el mismo vehículo.
Para comprobarlo: `python -m scripts.prueba_concurrencia`
