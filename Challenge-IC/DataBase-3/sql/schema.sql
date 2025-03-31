-- Create operators table
CREATE TABLE operators (
    Registro_ANS INT PRIMARY KEY,
    CNPJ VARCHAR(18) NULL, -- Formato XX.XXX.XXX/XXXX-XX
    Razao_Social VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    Nome_Fantasia VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
    Modalidade VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
    Logradouro VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
    Numero VARCHAR(50) NULL,
    Complemento VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
    Bairro VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
    Cidade VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
    UF CHAR(2) NULL,
    CEP VARCHAR(9) NULL,
    DDD VARCHAR(3) NULL,
    Telefone VARCHAR(50) NULL,
    Fax VARCHAR(50) NULL,
    Endereco_eletronico VARCHAR(255) NULL,
    Representante VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
    Cargo_Representante VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
    Regiao_de_Comercializacao VARCHAR(100) NULL,
    Data_Registro_ANS DATE NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create accounting table
CREATE TABLE accounting (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    trimestre_referencia DATE NOT NULL COMMENT
    reg_ans INT NOT NULL COMMENT
    cd_conta_contabil VARCHAR(50) NOT NULL COMMENT
    descricao VARCHAR(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 
    vl_saldo_inicial DECIMAL(18, 2) NULL COMMENT 
    vl_saldo_final DECIMAL(18, 2) NULL COMMENT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;