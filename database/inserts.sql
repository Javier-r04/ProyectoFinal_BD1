-- =====================================================================
-- Proyecto Final - Base de Datos I
-- Datos de prueba (Inserts) - Sistema de Tarjetas de Circulación
-- =====================================================================

-- ---------------------------------------------------------------------
-- MARCAS
-- ---------------------------------------------------------------------
INSERT INTO marca (nombre_marca) VALUES
('Toyota'), ('Honda'), ('Nissan'), ('Mazda'), ('Hyundai'),
('Kia'), ('Ford'), ('Chevrolet'), ('Mitsubishi'), ('Suzuki');

-- ---------------------------------------------------------------------
-- MODELOS
-- ---------------------------------------------------------------------
INSERT INTO modelo (nombre_modelo, id_marca) VALUES
('Corolla', 1), ('Hilux', 1), ('Yaris', 1), ('RAV4', 1),
('Civic', 2), ('CR-V', 2), ('Accord', 2),
('Sentra', 3), ('Frontier', 3), ('Versa', 3),
('Mazda 3', 4), ('CX-5', 4),
('Tucson', 5), ('Elantra', 5), ('Accent', 5),
('Sportage', 6), ('Rio', 6),
('F-150', 7), ('Escape', 7),
('Spark', 8), ('Aveo', 8),
('Lancer', 9), ('Outlander', 9),
('Swift', 10), ('Grand Vitara', 10);

-- ---------------------------------------------------------------------
-- TIPOS DE USO
-- ---------------------------------------------------------------------
INSERT INTO tipo_uso (descripcion) VALUES
('Particular'),
('Comercial'),
('Público'),
('Oficial'),
('Transporte de carga'),
('Transporte de pasajeros');

-- ---------------------------------------------------------------------
-- PROPIETARIOS
-- ---------------------------------------------------------------------
INSERT INTO propietario (nombre, dpi, direccion, telefono) VALUES
('Carlos Roberto López Méndez',     '2547896301013', 'Zona 1, Ciudad de Guatemala',     '50123456'),
('María Fernanda Pérez García',     '1985632147012', 'Zona 10, Ciudad de Guatemala',    '55896321'),
('Juan Pablo Ramírez Hernández',    '3654789210114', 'Zona 5, Quetzaltenango',          '42587896'),
('Ana Lucía Morales Castillo',      '2014785632101', 'Huehuetenango Centro',            '58741236'),
('Pedro Antonio González Cifuentes','1547896325101', 'San Marcos, Cabecera',            '47896325'),
('Luisa María Hernández Ortíz',     '2589632147010', 'Zona 14, Ciudad de Guatemala',    '52369874'),
('Roberto Carlos Méndez Soto',      '3014785621011', 'Antigua Guatemala',               '41258963'),
('Daniela Sofía Castillo Ruiz',     '2789632015411', 'Zona 11, Ciudad de Guatemala',    '54125896'),
('Jorge Estuardo Sánchez Pérez',    '1985632710104', 'Mixco, Guatemala',                '53698741'),
('Sofía Alejandra Vásquez León',    '2658974102031', 'Zona 7, Quetzaltenango',          '42589632'),
('Andrés Felipe Cordón Reyes',      '1478965230114', 'Cobán, Alta Verapaz',             '57896325'),
('Patricia Eugenia Solís Argueta',  '2369874152011', 'Escuintla Centro',                '52369874');

-- ---------------------------------------------------------------------
-- USUARIOS (los que realizan trámites en SAT)
-- ---------------------------------------------------------------------
INSERT INTO usuario (nombre, dpi, licencia) VALUES
('Carlos Roberto López Méndez',     '2547896301013', 'A-2547896'),
('María Fernanda Pérez García',     '1985632147012', 'B-1985632'),
('Juan Pablo Ramírez Hernández',    '3654789210114', 'A-3654789'),
('Ana Lucía Morales Castillo',      '2014785632101', 'C-2014785'),
('Pedro Antonio González Cifuentes','1547896325101', 'A-1547896'),
('Luisa María Hernández Ortíz',     '2589632147010', 'B-2589632'),
('Roberto Carlos Méndez Soto',      '3014785621011', 'A-3014785'),
('Daniela Sofía Castillo Ruiz',     '2789632015411', 'B-2789632'),
('Jorge Estuardo Sánchez Pérez',    '1985632710104', 'A-1985632'),
('Sofía Alejandra Vásquez León',    '2658974102031', 'C-2658974'),
('Andrés Felipe Cordón Reyes',      '1478965230114', 'A-1478965'),
('Patricia Eugenia Solís Argueta',  '2369874152011', 'B-2369874');

-- ---------------------------------------------------------------------
-- VEHÍCULOS (placa integrada como atributo)
-- ---------------------------------------------------------------------
INSERT INTO vehiculo (anio, color, numero_motor, numero_chasis, numero_placa, tipo_placa, id_modelo, id_tipo_uso) VALUES
(2020, 'Blanco',  'MOT-TOY-001', 'CHAS-TOY-001', 'P-123ABC', 'Particular', 1, 1),
(2018, 'Negro',   'MOT-TOY-002', 'CHAS-TOY-002', 'P-456DEF', 'Particular', 2, 5),
(2022, 'Rojo',    'MOT-HON-001', 'CHAS-HON-001', 'P-789GHI', 'Particular', 5, 1),
(2019, 'Gris',    'MOT-NIS-001', 'CHAS-NIS-001', 'P-321JKL', 'Particular', 8, 1),
(2021, 'Azul',    'MOT-MAZ-001', 'CHAS-MAZ-001', 'P-654MNO', 'Particular', 11, 1),
(2017, 'Plateado','MOT-HYU-001', 'CHAS-HYU-001', 'C-987PQR', 'Comercial',  13, 2),
(2023, 'Blanco',  'MOT-KIA-001', 'CHAS-KIA-001', 'P-147STU', 'Particular', 16, 1),
(2015, 'Verde',   'MOT-FOR-001', 'CHAS-FOR-001', 'C-258VWX', 'Comercial',  18, 5),
(2020, 'Negro',   'MOT-CHE-001', 'CHAS-CHE-001', 'P-369YZA', 'Particular', 20, 1),
(2016, 'Amarillo','MOT-MIT-001', 'CHAS-MIT-001', 'A-741BCD', 'Alquiler',   22, 6),
(2022, 'Rojo',    'MOT-SUZ-001', 'CHAS-SUZ-001', 'P-852EFG', 'Particular', 24, 1),
(2019, 'Azul',    'MOT-TOY-003', 'CHAS-TOY-003', 'P-963HIJ', 'Particular', 3, 1),
(2021, 'Gris',    'MOT-HON-002', 'CHAS-HON-002', 'M-159KLM', 'Mercantil',  6, 2),
(2014, 'Blanco',  'MOT-NIS-002', 'CHAS-NIS-002', 'P-357NOP', 'Particular', 10, 1),
(2024, 'Negro',   'MOT-TOY-004', 'CHAS-TOY-004', 'O-468QRS', 'Oficial',    4, 4);

-- ---------------------------------------------------------------------
-- RELACIÓN PROPIETARIO - VEHÍCULO (muchos a muchos)
-- Cada vehículo tiene un propietario actual.
-- También se registran cambios de dueño en el histórico.
-- ---------------------------------------------------------------------
-- Propietarios actuales
INSERT INTO vehiculo_propietario (id_vehiculo, id_propietario, fecha_inicio, fecha_fin, es_actual) VALUES
(1,  1,  '2020-03-15', NULL, TRUE),
(2,  2,  '2018-07-22', NULL, TRUE),
(3,  3,  '2022-01-10', NULL, TRUE),
(4,  4,  '2019-05-18', NULL, TRUE),
(5,  5,  '2021-08-30', NULL, TRUE),
(6,  6,  '2017-11-12', NULL, TRUE),
(7,  7,  '2023-02-25', NULL, TRUE),
(8,  8,  '2015-09-14', NULL, TRUE),
(9,  9,  '2020-06-08', NULL, TRUE),
(10, 10, '2016-04-19', NULL, TRUE),
(11, 11, '2022-10-05', NULL, TRUE),
(12, 12, '2019-12-20', NULL, TRUE),
(13, 1,  '2021-03-11', NULL, TRUE),
(14, 2,  '2014-08-26', NULL, TRUE),
(15, 7,  '2024-01-15', NULL, TRUE);

-- Casos de cambio de dueño (registros históricos)
-- Vehículo 1 perteneció antes a María Fernanda
INSERT INTO vehiculo_propietario (id_vehiculo, id_propietario, fecha_inicio, fecha_fin, es_actual) VALUES
(1, 2,  '2018-01-10', '2020-03-14', FALSE),
(4, 11, '2017-06-01', '2019-05-17', FALSE),
(8, 3,  '2013-05-20', '2015-09-13', FALSE);

-- ---------------------------------------------------------------------
-- TARJETAS DE CIRCULACIÓN
-- Incluye casos: ACTIVA, VENCIDA, DESACTIVADA por impago
-- ---------------------------------------------------------------------
INSERT INTO tarjeta_circulacion (fecha_emision, fecha_vencimiento, estado, motivo_desactivacion, id_vehiculo, id_usuario) VALUES
('2024-03-15', '2027-03-15', 'ACTIVA',      NULL, 1, 1),
('2024-07-22', '2027-07-22', 'ACTIVA',      NULL, 2, 2),
('2025-01-10', '2028-01-10', 'ACTIVA',      NULL, 3, 3),
('2023-05-18', '2026-05-18', 'ACTIVA',      NULL, 4, 4),
('2024-08-30', '2027-08-30', 'ACTIVA',      NULL, 5, 5),
('2020-11-12', '2023-11-12', 'VENCIDA',     'Vencimiento natural', 6, 6),
('2025-02-25', '2028-02-25', 'ACTIVA',      NULL, 7, 7),
('2018-09-14', '2021-09-14', 'VENCIDA',     'Vencimiento natural', 8, 8),
('2024-06-08', '2027-06-08', 'ACTIVA',      NULL, 9, 9),
('2022-04-19', '2024-04-19', 'DESACTIVADA', 'Desactivada por impago de impuestos', 10, 10),
('2024-10-05', '2027-10-05', 'ACTIVA',      NULL, 11, 11),
('2023-12-20', '2026-12-20', 'ACTIVA',      NULL, 12, 12),
('2024-03-11', '2027-03-11', 'ACTIVA',      NULL, 13, 1),
('2019-08-26', '2022-08-26', 'IMPAGO',      'Desactivada por impago acumulado de 3 años', 14, 2),
('2025-01-15', '2028-01-15', 'ACTIVA',      NULL, 15, 7);

-- ---------------------------------------------------------------------
-- CALCOMANÍAS
-- ---------------------------------------------------------------------
INSERT INTO calcomania (anio, estado, id_vehiculo) VALUES
(2026, 'VIGENTE', 1),
(2026, 'VIGENTE', 2),
(2026, 'VIGENTE', 3),
(2026, 'VIGENTE', 4),
(2026, 'VIGENTE', 5),
(2023, 'VENCIDA', 6),
(2026, 'VIGENTE', 7),
(2021, 'VENCIDA', 8),
(2026, 'VIGENTE', 9),
(2024, 'ANULADA', 10),
(2026, 'VIGENTE', 11),
(2026, 'VIGENTE', 12),
(2026, 'VIGENTE', 13),
(2022, 'VENCIDA', 14),
(2026, 'VIGENTE', 15);

-- ---------------------------------------------------------------------
-- HISTORIAL DE CAMBIOS DE COLOR
-- ---------------------------------------------------------------------
INSERT INTO historial_cambio_color (id_vehiculo, color_anterior, color_nuevo, observaciones) VALUES
(1, 'Negro',  'Blanco',  'Cambio solicitado por el propietario'),
(5, 'Verde',  'Azul',    'Repintado completo del vehículo'),
(8, 'Rojo',   'Verde',   'Cambio tras reparación de daños');

-- ---------------------------------------------------------------------
-- HISTORIAL DE CAMBIOS DE MOTOR
-- ---------------------------------------------------------------------
INSERT INTO historial_cambio_motor (id_vehiculo, motor_anterior, motor_nuevo, observaciones) VALUES
(2, 'MOT-TOY-002-OLD', 'MOT-TOY-002', 'Cambio por daño irreparable del motor original'),
(6, 'MOT-HYU-001-OLD', 'MOT-HYU-001', 'Reemplazo planificado por alto kilometraje');

-- =====================================================================
-- Verificación rápida
-- =====================================================================
-- SELECT 'propietarios' AS tabla, COUNT(*) FROM propietario
-- UNION ALL SELECT 'vehiculos',  COUNT(*) FROM vehiculo
-- UNION ALL SELECT 'tarjetas',   COUNT(*) FROM tarjeta_circulacion;
