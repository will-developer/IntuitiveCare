-- Tabela operadoras
CREATE TABLE operators (
    Registro_ANS INT PRIMARY KEY,
    CNPJ VARCHAR(18) NULL,
    Razao_Social VARCHAR(255) NOT NULL,
    Nome_Fantasia VARCHAR(255) NULL,
    Modalidade VARCHAR(100) NULL,
    Logradouro VARCHAR(255) NULL,
    Numero VARCHAR(50) NULL,
    Complemento VARCHAR(100) NULL,
    Bairro VARCHAR(100) NULL,
    Cidade VARCHAR(100) NULL,
    UF CHAR(2) NULL,
    CEP VARCHAR(9) NULL,
    DDD VARCHAR(3) NULL,
    Telefone VARCHAR(50) NULL,
    Fax VARCHAR(50) NULL,
    Endereco_eletronico VARCHAR(255) NULL,
    Representante VARCHAR(255) NULL,
    Cargo_Representante VARCHAR(100) NULL,
    Regiao_de_Comercializacao VARCHAR(100) NULL,
    Data_Registro_ANS DATE NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela accounting
CREATE TABLE accounting (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    trimestre_referencia DATE NOT NULL,
    reg_ans INT NOT NULL,
    cd_conta_contabil VARCHAR(50) NOT NULL,
    descricao VARCHAR(500) NOT NULL,
    vl_saldo_inicial DECIMAL(18, 2) NULL,
    vl_saldo_final DECIMAL(18, 2) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE accounting
ADD CONSTRAINT fk_accounting_operadoras
FOREIGN KEY (reg_ans) REFERENCES operators(Registro_ANS)
ON DELETE RESTRICT ON UPDATE CASCADE;