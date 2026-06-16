CREATE DATABASE IF NOT EXISTS lava_jato
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE lava_jato;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS ordem_servico_itens;
DROP TABLE IF EXISTS ordens_servico;
DROP TABLE IF EXISTS servicos;
DROP TABLE IF EXISTS carros;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS usuarios;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(120) NOT NULL,
    usuario VARCHAR(80) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    perfil VARCHAR(60) NOT NULL DEFAULT 'Administrador',
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE clientes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(160) NOT NULL,
    cpf_cnpj VARCHAR(30),
    telefone VARCHAR(30),
    email VARCHAR(140),
    endereco TEXT,
    observacoes TEXT,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_clientes_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE carros (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cliente_id INT NOT NULL,
    marca VARCHAR(80),
    modelo VARCHAR(100),
    ano INT,
    placa VARCHAR(20) NOT NULL UNIQUE,
    cor VARCHAR(50),
    tipo VARCHAR(60),
    observacoes TEXT,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_carros_placa (placa),
    CONSTRAINT fk_carros_clientes
        FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE servicos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(140) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL DEFAULT 0,
    tempo_estimado_minutos INT NOT NULL DEFAULT 0,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ordens_servico (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cliente_id INT NOT NULL,
    carro_id INT NOT NULL,
    data_abertura DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_finalizacao DATETIME,
    status VARCHAR(40) NOT NULL DEFAULT 'Aberta',
    valor_total DECIMAL(10,2) NOT NULL DEFAULT 0,
    forma_pagamento VARCHAR(60),
    observacoes TEXT,
    INDEX idx_ordens_status (status),
    INDEX idx_ordens_data_abertura (data_abertura),
    CONSTRAINT fk_ordens_clientes
        FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
    CONSTRAINT fk_ordens_carros
        FOREIGN KEY (carro_id) REFERENCES carros(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ordem_servico_itens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ordem_id INT NOT NULL,
    servico_id INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    valor_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_itens_ordens
        FOREIGN KEY (ordem_id) REFERENCES ordens_servico(id) ON DELETE CASCADE,
    CONSTRAINT fk_itens_servicos
        FOREIGN KEY (servico_id) REFERENCES servicos(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO usuarios (nome, usuario, senha_hash, perfil) VALUES
('Administrador', 'admin', 'pbkdf2_sha256$180000$6c6176616a61746f3230323664656d6f$f40bf9d492a9e7f34c3d7384b8f83b35cb135aed846a032174b1213563cd32de', 'Administrador');

INSERT INTO clientes (nome, cpf_cnpj, telefone, email, endereco, observacoes) VALUES
('Joao Pereira', '123.456.789-00', '(65) 99999-1001', 'joao@email.com', 'Rua das Flores, 120', 'Cliente mensalista.'),
('Maria Souza', '987.654.321-00', '(65) 99999-2002', 'maria@email.com', 'Av. Brasil, 450', 'Prefere lavagem completa.'),
('Auto Pecas Centro', '12.345.678/0001-99', '(65) 3322-7788', 'contato@autopecas.com', 'Centro Comercial, loja 8', 'Cliente PJ.');

INSERT INTO carros (cliente_id, marca, modelo, ano, placa, cor, tipo, observacoes) VALUES
(1, 'Toyota', 'Corolla', 2021, 'ABC1D23', 'Prata', 'Sedan', 'Interior claro.'),
(1, 'Honda', 'CG 160', 2022, 'MOT2A22', 'Vermelha', 'Moto', ''),
(2, 'Jeep', 'Renegade', 2020, 'JKL4M56', 'Branco', 'SUV', ''),
(3, 'Fiat', 'Strada', 2019, 'PJL8T90', 'Preto', 'Pickup', 'Uso comercial.');

INSERT INTO servicos (nome, descricao, preco, tempo_estimado_minutos, ativo) VALUES
('Lavagem simples', 'Lavagem externa com secagem manual.', 35.00, 35, 1),
('Lavagem completa', 'Lavagem externa, aspiracao e painel.', 65.00, 70, 1),
('Higienizacao interna', 'Limpeza detalhada de bancos, carpete e teto.', 180.00, 180, 1),
('Polimento', 'Polimento tecnico de pintura.', 250.00, 240, 1),
('Cera cristalizadora', 'Aplicacao de cera de protecao.', 90.00, 90, 1);

INSERT INTO ordens_servico
    (cliente_id, carro_id, status, valor_total, forma_pagamento, observacoes, data_finalizacao)
VALUES
(1, 1, 'Aberta', 100.00, 'Pix', 'Retirar ate 17h', NULL),
(2, 3, 'Concluida', 245.00, 'Cartao de credito', 'Cliente aprovou adicional.', '2026-06-09 10:40:00');

INSERT INTO ordem_servico_itens
    (ordem_id, servico_id, quantidade, valor_unitario, subtotal)
VALUES
(1, 1, 1, 35.00, 35.00),
(1, 2, 1, 65.00, 65.00),
(2, 2, 1, 65.00, 65.00),
(2, 3, 1, 180.00, 180.00);
