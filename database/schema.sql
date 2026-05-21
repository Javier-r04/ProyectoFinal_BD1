-- =====================================================================
-- Proyecto Final - Base de Datos I
-- Sistema de Tarjetas de Circulación Vehicular (SAT - Guatemala)
-- Autor: José Javier Rodríguez Alvarado - 1535524
-- =====================================================================
-- Correcciones aplicadas respecto a la Fase 1:
--   1. Se eliminó la entidad "Placa" y sus atributos (numero_placa, 
--      tipo_placa) se trasladaron como columnas de la entidad Vehículo.
--   2. La relación Propietario - Vehículo pasó a ser de muchos a muchos
--      mediante la tabla intermedia "Vehiculo_Propietario", la cual
--      también permite registrar el histórico de cambios de dueño.
--   3. Se agregaron timestamps de auditoría y campos para registrar los
--      casos de cambio de color y cambio de motor.
-- =====================================================================

-- Eliminar tablas si existen (en orden inverso por FK)
DROP TABLE IF EXISTS historial_cambio_motor CASCADE;
DROP TABLE IF EXISTS historial_cambio_color CASCADE;
DROP TABLE IF EXISTS vehiculo_propietario CASCADE;
DROP TABLE IF EXISTS calcomania CASCADE;
DROP TABLE IF EXISTS tarjeta_circulacion CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;
DROP TABLE IF EXISTS vehiculo CASCADE;
DROP TABLE IF EXISTS modelo CASCADE;
DROP TABLE IF EXISTS marca CASCADE;
DROP TABLE IF EXISTS tipo_uso CASCADE;
DROP TABLE IF EXISTS propietario CASCADE;

-- =====================================================================
-- TABLA: propietario
-- Representa a la persona legalmente dueña del vehículo.
-- =====================================================================
CREATE TABLE propietario (
    id_propietario  SERIAL PRIMARY KEY,
    nombre          VARCHAR(150) NOT NULL,
    dpi             VARCHAR(13)  NOT NULL UNIQUE,
    direccion       TEXT,
    telefono        VARCHAR(15),
    fecha_registro  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_dpi_length CHECK (LENGTH(dpi) = 13)
);

-- =====================================================================
-- TABLA: marca
-- Representa la empresa encargada de fabricar el vehículo.
-- =====================================================================
CREATE TABLE marca (
    id_marca     SERIAL PRIMARY KEY,
    nombre_marca VARCHAR(50) NOT NULL UNIQUE
);

-- =====================================================================
-- TABLA: modelo
-- Representa la línea del vehículo según su marca.
-- =====================================================================
CREATE TABLE modelo (
    id_modelo     SERIAL PRIMARY KEY,
    nombre_modelo VARCHAR(50) NOT NULL,
    id_marca      INT NOT NULL,
    CONSTRAINT fk_modelo_marca FOREIGN KEY (id_marca)
        REFERENCES marca(id_marca) ON DELETE RESTRICT,
    CONSTRAINT uk_modelo_marca UNIQUE (nombre_modelo, id_marca)
);

-- =====================================================================
-- TABLA: tipo_uso
-- Clasificación del vehículo: particular, comercial, público, oficial...
-- =====================================================================
CREATE TABLE tipo_uso (
    id_tipo_uso SERIAL PRIMARY KEY,
    descripcion VARCHAR(50) NOT NULL UNIQUE
);

-- =====================================================================
-- TABLA: vehiculo
-- Representa el vehículo registrado en el sistema.
-- Incluye los atributos numero_placa y tipo_placa (antes en tabla Placa).
-- =====================================================================
CREATE TABLE vehiculo (
    id_vehiculo    SERIAL PRIMARY KEY,
    anio           INT NOT NULL,
    color          VARCHAR(30) NOT NULL,
    numero_motor   VARCHAR(50) NOT NULL UNIQUE,
    numero_chasis  VARCHAR(50) NOT NULL UNIQUE,
    numero_placa   VARCHAR(10) NOT NULL UNIQUE,
    tipo_placa     VARCHAR(20) NOT NULL,
    id_modelo      INT NOT NULL,
    id_tipo_uso    INT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_anio CHECK (anio BETWEEN 1900 AND 2100),
    CONSTRAINT chk_tipo_placa CHECK (
        tipo_placa IN ('Particular','Comercial','Mercantil','Oficial',
                       'Diplomática','Alquiler','Moto','Remolque')
    ),
    CONSTRAINT fk_vehiculo_modelo FOREIGN KEY (id_modelo)
        REFERENCES modelo(id_modelo) ON DELETE RESTRICT,
    CONSTRAINT fk_vehiculo_tipo_uso FOREIGN KEY (id_tipo_uso)
        REFERENCES tipo_uso(id_tipo_uso) ON DELETE RESTRICT
);

-- =====================================================================
-- TABLA: vehiculo_propietario  (Relación muchos a muchos)
-- Registra qué propietario(s) tiene un vehículo en el tiempo.
-- Permite además mantener el historial de cambios de dueño.
-- =====================================================================
CREATE TABLE vehiculo_propietario (
    id_vehiculo_propietario SERIAL PRIMARY KEY,
    id_vehiculo     INT NOT NULL,
    id_propietario  INT NOT NULL,
    fecha_inicio    DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_fin       DATE,             -- NULL = propietario actual
    es_actual       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_vp_vehiculo FOREIGN KEY (id_vehiculo)
        REFERENCES vehiculo(id_vehiculo) ON DELETE CASCADE,
    CONSTRAINT fk_vp_propietario FOREIGN KEY (id_propietario)
        REFERENCES propietario(id_propietario) ON DELETE RESTRICT
);

CREATE INDEX idx_vp_actual ON vehiculo_propietario(id_vehiculo, es_actual);

-- =====================================================================
-- TABLA: usuario
-- Representa al usuario en la red de la SAT que registra un vehículo.
-- =====================================================================
CREATE TABLE usuario (
    id_usuario  SERIAL PRIMARY KEY,
    nombre      VARCHAR(150) NOT NULL,
    dpi         VARCHAR(13)  NOT NULL UNIQUE,
    licencia    VARCHAR(20)  NOT NULL,
    CONSTRAINT chk_usuario_dpi CHECK (LENGTH(dpi) = 13)
);

-- =====================================================================
-- TABLA: tarjeta_circulacion
-- Documento legal que permite al vehículo circular.
-- Estados: ACTIVA, VENCIDA, DESACTIVADA, IMPAGO
-- =====================================================================
CREATE TABLE tarjeta_circulacion (
    id_tarjeta        SERIAL PRIMARY KEY,
    fecha_emision     DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    estado            VARCHAR(20) NOT NULL DEFAULT 'ACTIVA',
    motivo_desactivacion VARCHAR(100),
    id_vehiculo       INT NOT NULL,
    id_usuario        INT NOT NULL,
    CONSTRAINT chk_estado_tarjeta CHECK (
        estado IN ('ACTIVA','VENCIDA','DESACTIVADA','IMPAGO')
    ),
    CONSTRAINT chk_fechas_tarjeta CHECK (fecha_vencimiento > fecha_emision),
    CONSTRAINT fk_tarjeta_vehiculo FOREIGN KEY (id_vehiculo)
        REFERENCES vehiculo(id_vehiculo) ON DELETE CASCADE,
    CONSTRAINT fk_tarjeta_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario) ON DELETE RESTRICT
);

-- =====================================================================
-- TABLA: calcomania
-- Control que se posee en el vehículo para su circulación legal.
-- =====================================================================
CREATE TABLE calcomania (
    id_calcomania SERIAL PRIMARY KEY,
    anio          INT NOT NULL,
    estado        VARCHAR(20) NOT NULL DEFAULT 'VIGENTE',
    id_vehiculo   INT NOT NULL,
    CONSTRAINT chk_estado_calc CHECK (estado IN ('VIGENTE','VENCIDA','ANULADA')),
    CONSTRAINT fk_calc_vehiculo FOREIGN KEY (id_vehiculo)
        REFERENCES vehiculo(id_vehiculo) ON DELETE CASCADE
);

-- =====================================================================
-- TABLA: historial_cambio_color
-- Registra cada trámite de cambio de color del vehículo.
-- =====================================================================
CREATE TABLE historial_cambio_color (
    id_cambio_color SERIAL PRIMARY KEY,
    id_vehiculo     INT NOT NULL,
    color_anterior  VARCHAR(30) NOT NULL,
    color_nuevo     VARCHAR(30) NOT NULL,
    fecha_cambio    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones   TEXT,
    CONSTRAINT fk_cc_vehiculo FOREIGN KEY (id_vehiculo)
        REFERENCES vehiculo(id_vehiculo) ON DELETE CASCADE
);

-- =====================================================================
-- TABLA: historial_cambio_motor
-- Registra cada trámite de cambio de motor del vehículo.
-- =====================================================================
CREATE TABLE historial_cambio_motor (
    id_cambio_motor SERIAL PRIMARY KEY,
    id_vehiculo     INT NOT NULL,
    motor_anterior  VARCHAR(50) NOT NULL,
    motor_nuevo     VARCHAR(50) NOT NULL,
    fecha_cambio    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones   TEXT,
    CONSTRAINT fk_cm_vehiculo FOREIGN KEY (id_vehiculo)
        REFERENCES vehiculo(id_vehiculo) ON DELETE CASCADE
);

-- =====================================================================
-- ÍNDICES adicionales para mejorar consultas
-- =====================================================================
CREATE INDEX idx_vehiculo_placa     ON vehiculo(numero_placa);
CREATE INDEX idx_tarjeta_estado     ON tarjeta_circulacion(estado);
CREATE INDEX idx_tarjeta_vehiculo   ON tarjeta_circulacion(id_vehiculo);
CREATE INDEX idx_propietario_dpi    ON propietario(dpi);

-- =====================================================================
-- VISTA: v_tarjeta_completa
-- Consulta unificada de información de tarjeta de circulación.
-- =====================================================================
CREATE OR REPLACE VIEW v_tarjeta_completa AS
SELECT
    t.id_tarjeta,
    t.fecha_emision,
    t.fecha_vencimiento,
    t.estado            AS estado_tarjeta,
    t.motivo_desactivacion,
    v.id_vehiculo,
    v.numero_placa,
    v.tipo_placa,
    v.anio,
    v.color,
    v.numero_motor,
    v.numero_chasis,
    ma.nombre_marca,
    mo.nombre_modelo,
    tu.descripcion      AS tipo_uso,
    p.id_propietario,
    p.nombre            AS nombre_propietario,
    p.dpi               AS dpi_propietario,
    p.direccion         AS direccion_propietario,
    p.telefono          AS telefono_propietario,
    u.nombre            AS nombre_usuario_sat,
    u.dpi               AS dpi_usuario_sat,
    u.licencia
FROM tarjeta_circulacion t
INNER JOIN vehiculo  v  ON t.id_vehiculo  = v.id_vehiculo
INNER JOIN modelo    mo ON v.id_modelo    = mo.id_modelo
INNER JOIN marca     ma ON mo.id_marca    = ma.id_marca
INNER JOIN tipo_uso  tu ON v.id_tipo_uso  = tu.id_tipo_uso
INNER JOIN usuario   u  ON t.id_usuario   = u.id_usuario
LEFT  JOIN vehiculo_propietario vp
       ON vp.id_vehiculo = v.id_vehiculo AND vp.es_actual = TRUE
LEFT  JOIN propietario p ON vp.id_propietario = p.id_propietario;
