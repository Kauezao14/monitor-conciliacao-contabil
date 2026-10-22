# Central de Integridade Contábil
Case de portfólio em Python e Streamlit. Dados 100% fictícios, sem relação com dados reais da UniCesumar ou de outra instituição. Sem IA.

## Comece aqui
1. Extraia o ZIP.
2. Envie o conteúdo extraído para a raiz do repositório, preservando as pastas `dados`, `consultas` e `.streamlit`.
3. Não misture bases antigas com esta versão. Os CSVs usados estão exclusivamente em `dados/`.
4. No Streamlit Cloud: selecione o repositório, a branch existente e `app.py`.
5. Atualize/reinicie o app se já existir um deploy.
Se subir tudo em uma subpasta, ajuste o caminho principal para `nome-da-pasta/app.py`.

## Rodar localmente
Python 3.11 ou 3.12 recomendado.
```
pip install -r requirements.txt
python testes.py
streamlit run app.py
```

## Escopo
Três áreas: visão executiva, investigação transacional e melhoria contínua; aba extra com contrato e limitações.
540 eventos na origem, 549 linhas no destino, 549 chaves na união. 477 conciliados e 72 eventos com exceção. 90 falhas independentes: 27 VALOR, 18 CENTRO e 9 de cada uma das outras cinco regras. Duplicidade também dispara VALOR pelo total dobrado.

## Modelo
- origem: expectativa operacional por empresa/evento, competência, valor em centavos, conta e centro esperados.
- destino: linhas recebidas, ID de lançamento, conta e centro efetivos.
- cargas: logs sintéticos por sistema e competência.
- motor: validação e regras independentes, sem depender da interface.
- histórico: gerado deterministicamente para demonstrar fila, responsáveis e SLA.

## Limitações que devem ser explicadas
Não há pares completos de débito/crédito: é uma visão de registro-alvo para ensinar conciliação de integração. O contrato 1:1 é uma simplificação explícita; múltiplas linhas são normais em lançamentos reais.
Datas de evento e cargas são sintéticas. Sistemas e centros são fictícios.
Os tratamentos históricos não corrigem o snapshot da carga. Resolvida significa um status demonstrativo, não alteração efetiva dos registros mostrados.
SLA é hipótese didática (3 ou 7 dias corridos), não compromisso real. Diferença monetária não é perda financeira. Classificações não comprovam causa-raiz.
Não há conexão ERP, autenticação, persistência de workflow ou correção automática.
Testes do motor não equivalem a testes de UI ou deploy.

## Arquivos SQL
`consultas/conciliacao.sql` contém exemplos SQLite para explicar JOIN, anti-join, agregação e regras de mapeamento. Não é executado pela interface.
