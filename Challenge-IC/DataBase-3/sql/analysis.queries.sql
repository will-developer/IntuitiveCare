SET @latest_quarter = (SELECT MAX(quarter_reference_date) FROM accounting);

SELECT
    op.Razao_Social AS OperatorName,
    FORMAT(SUM(acc.final_balance), 2, 'de_DE') AS TotalExpense_LastQuarter
FROM
    accounting acc
JOIN
    operators op ON acc.reg_ans = op.Registro_ANS
WHERE
    acc.account_description = 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR'
    AND acc.quarter_reference_date = @latest_quarter
    AND acc.final_balance IS NOT NULL
GROUP BY
    op.Registro_ANS, op.Razao_Social
ORDER BY
    SUM(acc.final_balance) DESC
LIMIT 10;