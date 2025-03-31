-- Query 1: Top 10 Operadoras com Maiores Despesas (Saldo Final)

SET @ultimo_trimestre = (SELECT MAX(trimestre_referencia) FROM accounting);

SELECT
    op.Razao_Social AS OperatorName,
    FORMAT(SUM(acc.vl_saldo_final), 2, 'de_DE') AS TotalExpense_LastQuarter
FROM
    accounting acc
JOIN
    operators op ON acc.reg_ans = op.Registro_ANS
WHERE
    acc.cd_conta_contabil LIKE '411%'
    AND acc.trimestre_referencia = @ultimo_trimestre
    AND acc.vl_saldo_final IS NOT NULL
GROUP BY
    op.Registro_ANS, op.Razao_Social
ORDER BY
    SUM(acc.vl_saldo_final) DESC
LIMIT 10;

-- Query 2: Top 10 Operadoras com Maiores Despesas No Ultimo Ano

DROP TEMPORARY TABLE IF EXISTS last_4_quarters;
CREATE TEMPORARY TABLE last_4_quarters AS (
    SELECT DISTINCT trimestre_referencia
    FROM accounting
    ORDER BY trimestre_referencia DESC
    LIMIT 4
);

SELECT
    op.Razao_Social AS OperatorName,
    FORMAT(SUM(acc.vl_saldo_final), 2, 'de_DE') AS TotalExpense_LastYear
FROM
    accounting acc
JOIN
    operators op ON acc.reg_ans = op.Registro_ANS
JOIN
    last_4_quarters l4q ON acc.trimestre_referencia = l4q.trimestre_referencia
WHERE
    acc.cd_conta_contabil LIKE '411%'
    AND acc.vl_saldo_final IS NOT NULL
GROUP BY
    op.Registro_ANS, op.Razao_Social
ORDER BY
    SUM(acc.vl_saldo_final) DESC
LIMIT 10;

DROP TEMPORARY TABLE IF EXISTS last_4_quarters;

