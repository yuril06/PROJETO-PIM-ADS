-- banco de dados cantina amadeu olivério
-- projeto PIM - ADS 1 semestre

CREATE TABLE IF NOT EXISTS produtos (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    nome           VARCHAR(100)   NOT NULL,
    quantidade     INT            NOT NULL DEFAULT 0,
    preco          DECIMAL(10, 2) NOT NULL,
    estoque_minimo INT            NOT NULL DEFAULT 5,
    data_cadastro  TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vendas (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT         NOT NULL,
    quantidade INT         NOT NULL,
    data_venda TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    dia_semana VARCHAR(20),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

-- produtos de exemplo
INSERT INTO produtos (nome, quantidade, preco, estoque_minimo) VALUES
    ('Refrigerante Lata',   24,  4.50,  5),
    ('Suco de Caixinha',    30,  3.00,  8),
    ('Biscoito Recheado',   20,  2.50,  5),
    ('Pao de Queijo',       15,  5.00, 10),
    ('Agua Mineral 500ml',  48,  2.00, 10),
    ('Barra de Cereal',      4,  3.50,  5),
    ('Iogurte',              2,  4.00,  5),
    ('Salgadinho 50g',      25,  3.00,  8);
