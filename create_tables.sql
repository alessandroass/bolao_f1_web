-- Primeiro, remove as tabelas existentes
DROP TABLE IF EXISTS palpites;
DROP TABLE IF EXISTS respostas;
DROP TABLE IF EXISTS config_votacao;
DROP TABLE IF EXISTS pontuacao;
DROP TABLE IF EXISTS gps;
DROP TABLE IF EXISTS pilotos;
DROP TABLE IF EXISTS usuarios;

-- Tabela usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    first_name VARCHAR(80) NOT NULL,
    password VARCHAR(500) NOT NULL,  -- Aumentado para 500 caracteres
    is_admin BOOLEAN DEFAULT FALSE,
    primeiro_login BOOLEAN DEFAULT TRUE
);

-- Tabela pilotos
CREATE TABLE IF NOT EXISTS pilotos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(80) NOT NULL
);

-- Tabela palpites
CREATE TABLE IF NOT EXISTS palpites (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    gp_slug VARCHAR(80) NOT NULL,
    pos_1 VARCHAR(80),
    pos_2 VARCHAR(80),
    pos_3 VARCHAR(80),
    pos_4 VARCHAR(80),
    pos_5 VARCHAR(80),
    pos_6 VARCHAR(80),
    pos_7 VARCHAR(80),
    pos_8 VARCHAR(80),
    pos_9 VARCHAR(80),
    pos_10 VARCHAR(80),
    pole VARCHAR(80),
    UNIQUE(usuario_id, gp_slug)
);

-- Tabela respostas
CREATE TABLE IF NOT EXISTS respostas (
    id SERIAL PRIMARY KEY,
    gp_slug VARCHAR(80) UNIQUE NOT NULL,
    pos_1 VARCHAR(80),
    pos_2 VARCHAR(80),
    pos_3 VARCHAR(80),
    pos_4 VARCHAR(80),
    pos_5 VARCHAR(80),
    pos_6 VARCHAR(80),
    pos_7 VARCHAR(80),
    pos_8 VARCHAR(80),
    pos_9 VARCHAR(80),
    pos_10 VARCHAR(80),
    pole VARCHAR(80)
);

-- Tabela pontuacao
CREATE TABLE IF NOT EXISTS pontuacao (
    id SERIAL PRIMARY KEY,
    posicao INTEGER UNIQUE NOT NULL,
    pontos INTEGER NOT NULL
);

-- Tabela config_votacao
CREATE TABLE IF NOT EXISTS config_votacao (
    id SERIAL PRIMARY KEY,
    gp_slug VARCHAR(80) UNIQUE NOT NULL,
    pole_habilitado BOOLEAN DEFAULT TRUE,
    posicoes_habilitado BOOLEAN DEFAULT TRUE
);

-- Tabela gps
CREATE TABLE IF NOT EXISTS gps (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(80) UNIQUE NOT NULL,
    nome VARCHAR(80) NOT NULL,
    data_corrida VARCHAR(10) NOT NULL,
    hora_corrida VARCHAR(5) NOT NULL,
    data_classificacao VARCHAR(10) NOT NULL,
    hora_classificacao VARCHAR(5) NOT NULL
); 