-- Esquema físico de "Autos Colombia" (PostgreSQL) - Iteración 1.
-- Se puede ejecutar varias veces: todo usa IF NOT EXISTS.

CREATE TABLE IF NOT EXISTS propietario (
  id_propietario SERIAL PRIMARY KEY,
  nombre    VARCHAR(100) NOT NULL,
  documento VARCHAR(20)  NOT NULL UNIQUE,
  telefono  VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS vehiculo (
  placa          VARCHAR(10) PRIMARY KEY,
  id_propietario INT NOT NULL REFERENCES propietario,
  tipo   VARCHAR(10) NOT NULL CHECK (tipo IN ('MOTO','VEHICULO')),
  marca  VARCHAR(50) NOT NULL,
  color  VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS celda (
  id_celda SERIAL PRIMARY KEY,
  codigo   VARCHAR(10) NOT NULL UNIQUE,
  tipo     VARCHAR(10) NOT NULL CHECK (tipo IN ('MOTO','VEHICULO'))
);

CREATE TABLE IF NOT EXISTS operario (
  id_operario SERIAL PRIMARY KEY,
  nombre     VARCHAR(100) NOT NULL,
  usuario    VARCHAR(30)  NOT NULL UNIQUE,
  clave_hash VARCHAR(255) NOT NULL,
  turno      VARCHAR(10)  NOT NULL CHECK (turno IN ('DIA','NOCHE'))
);

CREATE TABLE IF NOT EXISTS puerta (
  id_puerta SERIAL PRIMARY KEY,
  nombre    VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS movimiento (
  id_movimiento       SERIAL PRIMARY KEY,
  placa               VARCHAR(10) NOT NULL REFERENCES vehiculo,
  id_celda            INT NOT NULL REFERENCES celda,
  fecha_ingreso       TIMESTAMP NOT NULL DEFAULT now(),
  id_puerta_ingreso   INT NOT NULL REFERENCES puerta,
  id_operario_ingreso INT NOT NULL REFERENCES operario,
  fecha_salida        TIMESTAMP,
  id_puerta_salida    INT REFERENCES puerta,
  id_operario_salida  INT REFERENCES operario,
  CHECK (fecha_salida IS NULL OR fecha_salida >= fecha_ingreso)
);

-- Anti-duplicados: una celda y un vehículo solo pueden tener UN movimiento abierto
-- (sin fecha de salida). Es la última barrera si dos puertas chocan al mismo tiempo.
CREATE UNIQUE INDEX IF NOT EXISTS uq_celda_activa    ON movimiento (id_celda) WHERE fecha_salida IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_vehiculo_activo ON movimiento (placa)    WHERE fecha_salida IS NULL;

CREATE TABLE IF NOT EXISTS novedad (
  id_novedad    SERIAL PRIMARY KEY,
  id_movimiento INT NOT NULL REFERENCES movimiento,
  id_operario   INT NOT NULL REFERENCES operario,
  descripcion   TEXT NOT NULL,
  fecha_hora    TIMESTAMP NOT NULL DEFAULT now()
);
