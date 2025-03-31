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