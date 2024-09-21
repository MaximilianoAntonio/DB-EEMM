# DB EEMM
 
CREATE DATABASE equipos_medicos;
USE equipos_medicos;


CREATE TABLE inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(255),
    marca VARCHAR(100),
    modelo VARCHAR(100),
    numero_serie VARCHAR(100),
    ubicacion VARCHAR(100),
    estado VARCHAR(50),
    valor DECIMAL(10,2),
    fecha_adquisicion DATE
);


CREATE TABLE ficha_tecnica (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipo_id INT,
    especificaciones TEXT,
    FOREIGN KEY (equipo_id) REFERENCES inventario(id) ON DELETE CASCADE
);


CREATE TABLE historial_equipo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipo_id INT,
    fecha_evento DATE,
    descripcion_evento TEXT,
    FOREIGN KEY (equipo_id) REFERENCES inventario(id) ON DELETE CASCADE
);


