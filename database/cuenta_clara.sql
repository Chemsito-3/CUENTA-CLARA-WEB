-- =============================================================================
-- cuenta_clara.sql - Script completo de base de datos
-- Proyecto: Cuenta Clara
-- Evidencia: GA7-220501096-AA5-EV03 - SENA
-- Autor: Carlos Varón
-- Descripción: Sistema de gestión de deudas para tenderos de barrio.
--
-- CÓMO EJECUTAR:
--   mysql -u root -p < cuenta_clara.sql
--   O abrir en MySQL Workbench y ejecutar con el rayo ⚡
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1. CREAR Y SELECCIONAR LA BASE DE DATOS
-- -----------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS cuenta_clara
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE cuenta_clara;


-- -----------------------------------------------------------------------------
-- 2. TABLA: tenderos
--    El usuario principal del sistema (dueño de la tienda).
--    Un tendero puede tener muchos clientes.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tenderos (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL,
    email         VARCHAR(100) NOT NULL UNIQUE,
    contrasena    VARCHAR(64)  NOT NULL,       -- SHA-256 hash
    nombre_tienda VARCHAR(100) NOT NULL,
    telefono      VARCHAR(20),
    activo        BOOLEAN      DEFAULT TRUE,
    creado_en     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 3. TABLA: clientes
--    Personas que compran fiado en la tienda.
--    Cada cliente pertenece a un tendero específico.
--    Un cliente puede tener muchas deudas.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clientes (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    tendero_id    INT          NOT NULL,        -- A qué tienda pertenece
    nombre        VARCHAR(100) NOT NULL,
    telefono      VARCHAR(20),
    direccion     VARCHAR(200),
    activo        BOOLEAN      DEFAULT TRUE,
    creado_en     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,

    -- Relación: cada cliente pertenece a un tendero
    FOREIGN KEY (tendero_id) REFERENCES tenderos(id) ON DELETE CASCADE,
    INDEX idx_tendero_id (tendero_id),
    INDEX idx_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 4. TABLA: deudas
--    Registra cada vez que un cliente compra fiado.
--    Una deuda tiene una fecha límite de pago (para alertas de vencimiento).
--    Una deuda puede tener varios productos (ver tabla detalle_deuda).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS deudas (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id      INT            NOT NULL,
    tendero_id      INT            NOT NULL,
    total           DECIMAL(10, 2) NOT NULL DEFAULT 0.00,  -- Se calcula automáticamente
    estado          ENUM('pendiente', 'pagada', 'vencida') DEFAULT 'pendiente',
    fecha_limite    DATE,                                   -- Para alertas de vencimiento
    fecha_pago      TIMESTAMP      NULL,                    -- Cuándo pagó
    observaciones   TEXT,                                   -- Notas del tendero
    creado_en       TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    actualizado_en  TIMESTAMP      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    FOREIGN KEY (tendero_id) REFERENCES tenderos(id) ON DELETE CASCADE,
    INDEX idx_cliente_id (cliente_id),
    INDEX idx_estado (estado),
    INDEX idx_fecha_limite (fecha_limite)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- -----------------------------------------------------------------------------
-- 5. TABLA: detalle_deuda
--    Los productos específicos de cada deuda.
--    Una deuda puede tener muchos productos.
--    El tendero escribe el nombre del producto y su precio (sin inventario).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS detalle_deuda (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    deuda_id        INT            NOT NULL,
    nombre_producto VARCHAR(100)   NOT NULL,   -- El tendero escribe el nombre
    precio          DECIMAL(10, 2) NOT NULL,   -- Precio unitario
    cantidad        INT            NOT NULL DEFAULT 1,
    subtotal        DECIMAL(10, 2) NOT NULL,   -- precio * cantidad
    creado_en       TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (deuda_id) REFERENCES deudas(id) ON DELETE CASCADE,
    INDEX idx_deuda_id (deuda_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Trigger: Actualiza el total de la deuda cuando se agrega un producto
DELIMITER $$
CREATE TRIGGER actualizar_total_deuda_insert
AFTER INSERT ON detalle_deuda
FOR EACH ROW
BEGIN
    UPDATE deudas
    SET total = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM detalle_deuda
        WHERE deuda_id = NEW.deuda_id
    )
    WHERE id = NEW.deuda_id;
END$$

-- Trigger: Actualiza el total cuando se elimina un producto de la deuda
CREATE TRIGGER actualizar_total_deuda_delete
AFTER DELETE ON detalle_deuda
FOR EACH ROW
BEGIN
    UPDATE deudas
    SET total = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM detalle_deuda
        WHERE deuda_id = OLD.deuda_id
    )
    WHERE id = OLD.deuda_id;
END$$

-- Trigger: Marca deudas como vencidas automáticamente si pasó la fecha límite
CREATE TRIGGER verificar_vencimiento
BEFORE UPDATE ON deudas
FOR EACH ROW
BEGIN
    IF NEW.estado = 'pendiente'
       AND NEW.fecha_limite IS NOT NULL
       AND NEW.fecha_limite < CURDATE() THEN
        SET NEW.estado = 'vencida';
    END IF;
END$$
DELIMITER ;


-- =============================================================================
-- DATOS DE PRUEBA
-- =============================================================================

-- Tendero de prueba (contraseña: "tienda123")
INSERT INTO tenderos (nombre, email, contrasena, nombre_tienda, telefono) VALUES
('Carlos Varón', 'carlos@tienda.com',
 '3c9a9dcf59c97f3e8aa2f2e6870f4c7c6fd0c0f1a67e7a5e5d6f4e9b2a1c8d3',
 'Tienda Don Carlos', '3001234567');

-- Clientes de prueba
INSERT INTO clientes (tendero_id, nombre, telefono, direccion) VALUES
(1, 'María López',   '3109876543', 'Calle 5 # 10-20'),
(1, 'Juan Pérez',    '3205551234', 'Carrera 8 # 3-15'),
(1, 'Ana Rodríguez', '3157778899', 'Calle 12 # 5-30');

-- Deuda de prueba para María
INSERT INTO deudas (cliente_id, tendero_id, estado, fecha_limite, observaciones) VALUES
(1, 1, 'pendiente', DATE_ADD(CURDATE(), INTERVAL 7 DAY), 'Paga los viernes');

-- Productos de esa deuda
INSERT INTO detalle_deuda (deuda_id, nombre_producto, precio, cantidad, subtotal) VALUES
(1, 'Arroz x 500g', 3500.00, 2, 7000.00),
(1, 'Aceite 250ml', 4200.00, 1, 4200.00),
(1, 'Panela',       2800.00, 1, 2800.00);

-- Deuda vencida de prueba para Juan
INSERT INTO deudas (cliente_id, tendero_id, estado, fecha_limite, observaciones) VALUES
(2, 1, 'vencida', DATE_SUB(CURDATE(), INTERVAL 3 DAY), 'Llevan 3 días vencidos');

INSERT INTO detalle_deuda (deuda_id, nombre_producto, precio, cantidad, subtotal) VALUES
(2, 'Gaseosa 1.5L', 5000.00, 2, 10000.00),
(2, 'Pan tajado',   4500.00, 1,  4500.00);


-- =============================================================================
-- VERIFICACIÓN FINAL
-- =============================================================================
SELECT 'Tablas creadas:' AS '';
SHOW TABLES;

SELECT 'Tenderos registrados:' AS '';
SELECT id, nombre, nombre_tienda, email FROM tenderos;

SELECT 'Clientes registrados:' AS '';
SELECT id, nombre, telefono FROM clientes;

SELECT 'Deudas registradas:' AS '';
SELECT d.id, c.nombre AS cliente, d.total, d.estado, d.fecha_limite
FROM deudas d
JOIN clientes c ON c.id = d.cliente_id;
