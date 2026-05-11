-- ============================================================
-- Banco de Dados: Sistema de Estoque - Cantina Escolar
-- Projeto PIM - ADS 1º Semestre
-- ============================================================

-- Cria o banco de dados se ainda não existir
CREATE DATABASE IF NOT EXISTS cantina_escolar
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Seleciona o banco de dados para uso
USE cantina_escolar;

-- ============================================================
-- TABELA: produtos
-- Armazena todos os produtos cadastrados na cantina
-- ============================================================
CREATE TABLE IF NOT EXISTS produtos (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(100)   NOT NULL                COMMENT 'Nome do produto',
    quantidade      INT            NOT NULL DEFAULT 0      COMMENT 'Quantidade atual em estoque',
    preco           DECIMAL(10, 2) NOT NULL                COMMENT 'Preço unitário do produto',
    estoque_minimo  INT            NOT NULL DEFAULT 5      COMMENT 'Quantidade mínima antes do alerta',
    data_cadastro   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP COMMENT 'Data de cadastro'
);

-- ============================================================
-- TABELA: vendas
-- Registra todas as vendas realizadas na cantina
-- ============================================================
CREATE TABLE IF NOT EXISTS vendas (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    produto_id  INT         NOT NULL              COMMENT 'ID do produto vendido',
    quantidade  INT         NOT NULL              COMMENT 'Quantidade vendida',
    data_venda  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP COMMENT 'Data e hora da venda',
    dia_semana  VARCHAR(20)                       COMMENT 'Dia da semana em português',
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

-- ============================================================
-- DADOS INICIAIS PARA TESTE
-- ============================================================
INSERT INTO produtos (nome, quantidade, preco, estoque_minimo) VALUES
    ('Refrigerante Lata',   24,  4.50,  5),
    ('Suco de Caixinha',    30,  3.00,  8),
    ('Biscoito Recheado',   20,  2.50,  5),
    ('Pão de Queijo',       15,  5.00, 10),
    ('Água Mineral 500ml',  48,  2.00, 10),
    ('Barra de Cereal',      4,  3.50,  5),
    ('Iogurte',              2,  4.00,  5),
    ('Salgadinho 50g',      25,  3.00,  8);

-- Os últimos 2 produtos (Barra de Cereal e Iogurte) já estão
-- abaixo do estoque mínimo para demonstrar o alerta visual
