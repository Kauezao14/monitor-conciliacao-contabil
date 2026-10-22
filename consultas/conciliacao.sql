-- SQLite; valores em centavos; contrato 1 registro-alvo por evento.
-- Crie tabelas origem e destino a partir dos CSVs para executar.
WITH d AS (
 SELECT empresa,id_evento,COUNT(*) AS quantidade,SUM(valor_centavos) AS valor_destino
 FROM destino GROUP BY empresa,id_evento
)
SELECT o.empresa,o.id_evento,o.valor_centavos AS esperado,
 COALESCE(d.valor_destino,0) AS recebido,
 COALESCE(d.valor_destino,0)-o.valor_centavos AS diferenca,
 CASE WHEN d.id_evento IS NULL THEN 1 ELSE 0 END AS ausente,
 CASE WHEN d.quantidade>1 THEN 1 ELSE 0 END AS duplicado
FROM origem o LEFT JOIN d ON d.empresa=o.empresa AND d.id_evento=o.id_evento;

-- Destino sem origem
SELECT d.* FROM destino d WHERE NOT EXISTS (
 SELECT 1 FROM origem o WHERE o.empresa=d.empresa AND o.id_evento=d.id_evento
);

-- Evidências de mapeamento/competência; preserve múltiplas falhas.
SELECT o.id_evento,d.id_lancamento,
 CASE WHEN o.conta_esperada<>d.conta THEN 1 ELSE 0 END AS falha_conta,
 CASE WHEN o.centro_esperado<>d.centro THEN 1 ELSE 0 END AS falha_centro,
 CASE WHEN o.competencia<>d.competencia THEN 1 ELSE 0 END AS falha_competencia
FROM origem o JOIN destino d ON d.empresa=o.empresa AND d.id_evento=o.id_evento;
