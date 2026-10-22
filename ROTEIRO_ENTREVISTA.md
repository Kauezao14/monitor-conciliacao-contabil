# Demonstração de 3 minutos
## 0:00–0:40 — Contexto e resultado
“Construí um case fictício para a necessidade descrita na vaga. Concilio eventos do acadêmico, financeiro e folha contra registros-alvo do módulo contábil. Uma carga concluída não significa que seus dados estejam corretos.”
Abra Visão executiva. Explique denominador da taxa, diferença absoluta e diferença entre evento e linha.
## 0:40–1:50 — Investigue um caso
Abra Central de investigação e escolha um ID terminado em 006. Mostre que valor e centro estão incorretos simultaneamente.
“Preservei múltiplas falhas em vez de esconder uma por precedência. A evidência é esta comparação. A causa ainda precisa ser investigada com negócio e TI.”
Depois mostre 007: duplicidade pelo contrato 1:1. Explique que lançamentos reais podem ter múltiplas linhas legítimas.
## 1:50–2:40 — Processo e prevenção
Abra Qualidade e melhoria. Mostre Pareto por falha (não por documento), fila e ação preventiva.
“Meu Green Belt entra na validação da causa e na prevenção da recorrência. Não basta corrigir a planilha ou o gráfico.”
## 2:40–3:00 — Limites e adaptação
“É um protótipo sem integração real. Eu validaria as regras contábeis com a Controladoria e adaptaria as chaves e granularidade ao ERP. Em produção precisaria de auditoria, permissões, histórico real e aprovação de ajustes.”

# Perguntas técnicas para ensaiar
- Por que empresa + evento? IDs podem se repetir entre empresas.
- Por que centavos inteiros? Evitar ruído de ponto flutuante nos valores monetários.
- Por que agrupar destino antes de comparar? Evitar multiplicar origem no JOIN e preservar soma/contagem.
- Duplicado é sempre erro? Não. É suspeita sob o contrato simplificado deste case.
- De onde vem o aging? Primeira detecção sintética; não vencimento de cobrança.
- Este projeto prova domínio de Power BI? Não; demonstra lógica e raciocínio em Python. Seja honesto sobre experiência em cada ferramenta.
- Qual ganho financeiro? Não medido. Proponha medir esforço de conciliação, recorrência e tempo de resolução num piloto real.
