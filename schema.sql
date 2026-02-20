CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    nombre_completo VARCHAR(255),
    telefono_whatsapp VARCHAR(50),
    email VARCHAR(255),
    edad INTEGER,
    status_legal BOOLEAN DEFAULT FALSE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tanque_gasolina NUMERIC(5,2) DEFAULT 100.00,
    tier_suscripcion VARCHAR(50) DEFAULT 'TRIAL'
);

CREATE TABLE adn_negocios (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE UNIQUE,
    nombre_empresa VARCHAR(255),
    modelo_negocio TEXT,
    tipo_ayuda_esperada TEXT,
    liderazgo_rutinas TEXT
);

CREATE TABLE memoria_vectorial (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    agente_emisor VARCHAR(100),
    contenido_texto TEXT,
    vector_embedding vector(768),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
