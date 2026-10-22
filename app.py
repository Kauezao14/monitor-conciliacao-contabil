from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
from motor import carregar,conciliar,ocorrencias,REGRAS,ACOES
st.set_page_config(page_title='Central de Integridade Contábil',page_icon='🔎',layout='wide')
st.markdown("""<style>.block-container{padding-top:2rem;max-width:1400px} [data-testid=stMetric]{border:1px solid #31435a;border-radius:12px;padding:14px}h1{letter-spacing:-1px} </style>""",unsafe_allow_html=True)
@st.cache_data
def preparar():
 o,d,l=carregar();m=conciliar(o,d);h=ocorrencias(m);return o,d,l,m.merge(h,on=['empresa','id_evento'],how='left')
o,d,l,full=preparar()
st.title('Central de Integridade Contábil')
st.caption('PORTFÓLIO • Instituição fictícia • Sem conexão a ERP • Sem IA • Snapshot demonstrativo: 22/10/2026')
st.sidebar.title('Navegação')
page=st.sidebar.radio('Área',['Visão executiva','Central de investigação','Qualidade e melhoria','Arquitetura e regras'])
reference=pd.Timestamp(st.sidebar.date_input('Data de análise',value=pd.Timestamp('2026-10-22').date(),min_value=pd.Timestamp('2026-10-10').date()))
m=full.copy()
for col,label in [('competencia','Competência esperada'),('sistema','Sistema de origem'),('polo','Polo')]:
 opts=sorted(m[col].dropna().unique());sel=st.sidebar.multiselect(label,opts,default=opts);m=m[m[col].isin(sel)]
m.loc[m.resolucao.gt(reference),'status']='Em análise'
m.loc[m.resolucao.gt(reference),'resolucao']=pd.NaT
m['dias_pendencia']=(reference-m.primeira_deteccao).dt.days.clip(lower=0)
m['prazo_vencido']=(m.dias_pendencia>m.sla_dias)&m.status.ne('Resolvida')&~m.conciliado
exc=m[~m.conciliado].copy()
open_exc=exc[exc.status.ne('Resolvida')]
def money(c):return ('R$ '+f'{c/100:,.2f}').replace(',','X').replace('.',',').replace('X','.')
def show_counts(frame,group,title):
 if frame.empty:st.info('Sem dados nos filtros atuais.');return
 counts=frame.groupby(group).size().reset_index(name='Quantidade')
 st.plotly_chart(px.bar(counts,x=group[0],y='Quantidade',color=group[1] if len(group)>1 else None,title=title,color_discrete_sequence=px.colors.qualitative.Safe),use_container_width=True)
if page=='Visão executiva':
 st.subheader('Integração concluída não significa dado conciliado')
 cols=st.columns(4)
 cols[0].metric('Eventos esperados',int(m.valor_centavos.notna().sum()))
 cols[1].metric('Eventos com destino',int(m.qtd_lancamentos.gt(0).sum()))
 cols[2].metric('Taxa de conciliação',f'{m.conciliado.mean()*100:.1f}%' if len(m) else '—')
 cols[3].metric('Eventos com exceção',len(exc))
 st.caption('Taxa de conciliação: eventos sem falha ÷ união de chaves origem/destino. Eventos com destino incluem os sem origem; não equivalem à contagem de linhas.')
 cols=st.columns(3)
 cols[0].metric('Valor esperado',money(m.valor_origem.sum()))
 cols[1].metric('Valor contabilizado',money(m.valor_destino.sum()))
 cols[2].metric('Diferença absoluta',money(m.diferenca.abs().sum()))
 st.caption('Diferença absoluta não é perda financeira. Falhas de conta, centro e competência podem ter diferença monetária zero. Valores referentes ao snapshot, inclusive ocorrências tratadas no histórico simulado.')
 a,b=st.columns(2)
 with a:show_counts(exc,['competencia','sistema'],'Eventos com exceção por competência')
 with b:show_counts(exc,['prioridade','sistema'],'Criticidade das exceções')
 st.subheader('Saúde dos lotes — logs sintéticos')
 st.dataframe(l[l.sistema.isin(m.sistema.unique())&l.competencia.isin(m.competencia.unique())],hide_index=True,use_container_width=True)
 st.info('Snapshot da carga e histórico de tratamento são demonstrações distintas. Resolver uma ocorrência no histórico não altera retroativamente os lançamentos deste snapshot.')
elif page=='Central de investigação':
 st.subheader('Da exceção até a evidência')
 if exc.empty:st.success('Nenhuma exceção selecionada.');st.stop()
 priorities=st.multiselect('Prioridade',sorted(exc.prioridade.unique()),default=sorted(exc.prioridade.unique()))
 e=exc[exc.prioridade.isin(priorities)].copy()
 e['regras_texto']=e.regras.apply(lambda x:', '.join(x))
 st.dataframe(e[['id_evento','sistema','prioridade','regras_texto','status','responsavel','dias_pendencia']],hide_index=True,use_container_width=True)
 if e.empty:st.stop()
 doc=st.selectbox('Investigar evento',e.id_evento)
 x=e[e.id_evento.eq(doc)].iloc[0]
 left,right=st.columns(2)
 with left:
  st.markdown('### Origem / expectativa')
  st.dataframe(o[o.id_evento.eq(doc)].T.astype(str),use_container_width=True)
 with right:
  st.markdown('### Destino / lançamentos recebidos')
  st.dataframe(d[d.id_evento.eq(doc)],hide_index=True,use_container_width=True)
 st.metric('Destino − origem',money(x.diferenca))
 for flag in x.regras:
  st.warning(f'{flag}: {REGRAS[flag]}')
  st.write('Próximo passo: '+ACOES[flag])
 st.markdown('### Tratamento demonstrativo')
 st.write(f'Responsável: {x.responsavel} | Status: {x.status}')
 st.write(f'Primeira detecção: {x.primeira_deteccao:%d/%m/%Y} | SLA proposto: {x.sla_dias:.0f} dias corridos')
 st.caption('SLA e priorização são premissas do case, não políticas da empresa. A idade é contada da primeira detecção, não do vencimento da mensalidade.')
 st.text_area('Resumo automático por regras (não é IA)',value=f'Evento {doc}, sistema {x.sistema}. Regras acionadas: {", ".join(x.regras)}. Valor esperado {money(x.valor_origem)}; destino {money(x.valor_destino)}. Encaminhar para {x.responsavel}. Hipóteses exigem validação.',height=140)
 st.download_button('Exportar eventos filtrados',e.drop(columns='regras').to_csv(index=False).encode('utf-8-sig'),'excecoes.csv')
elif page=='Qualidade e melhoria':
 st.subheader('Detectar, tratar e prevenir recorrência')
 cols=st.columns(3)
 cols[0].metric('Pendências abertas',len(open_exc))
 cols[1].metric('SLA vencido',int(m.prazo_vencido.sum()))
 closed=exc[exc.resolucao.notna()]
 days=(closed.resolucao-closed.primeira_deteccao).dt.days
 cols[2].metric('Tempo médio de resolução',f'{days.mean():.1f} dias' if len(days) else '—')
 st.caption('Indicadores calculados a partir de histórico sintético; não são resultados obtidos em uma empresa. Contagem de prazo em dias corridos.')
 flags=exc.explode('regras')
 if not flags.empty:
  pareto=flags.groupby('regras').size().sort_values(ascending=False).reset_index(name='Falhas');pareto['Acumulado %']=pareto.Falhas.cumsum()/pareto.Falhas.sum()*100
  st.plotly_chart(px.bar(pareto,x='regras',y='Falhas',title='Pareto de falhas — um evento pode ter múltiplas falhas'),use_container_width=True)
  st.dataframe(pareto,hide_index=True,use_container_width=True)
 show_counts(exc,['responsavel','status'],'Fila de tratamento')
 st.markdown('### Plano de prevenção proposto')
 st.dataframe(pd.DataFrame([
 ['DUPLICADO','Reenvio sem controle (hipótese)','Validar estorno autorizado','Chave de idempotência + teste de reprocessamento','TI'],
 ['CONTA / CENTRO','De/para desatualizado (hipótese)','Revisar com Contabilidade','Versionar mapeamento e validar cadastro','Controladoria + TI'],
 ['AUSENTE','Rejeição ou fila parada (hipótese)','Rastrear lote e reprocessar autorizado','Alertar rejeições e eventos esperados ausentes','TI + negócio'],
 ['COMPETENCIA','Corte ou regra divergente (hipótese)','Validar reconhecimento','Calendário de corte e testes de competência','Contabilidade']],columns=['Falha','Hipótese','Corretiva','Preventiva','Responsável']),hide_index=True,use_container_width=True)
 st.info('Categorias de falha não são causas-raiz comprovadas. Recorrência por regra indica onde investigar; DMAIC exige medir, validar hipótese e acompanhar eficácia.')
else:
 st.subheader('Contrato de dados e limitações')
 st.code('Origem + destino → validação de chaves → agregação por evento → regras independentes → tabela de exceções → investigação e melhoria')
 st.markdown("""
- Chave: empresa + id_evento. Não conciliamos por valor isolado.
- Contrato demonstrativo: um evento gera um registro-alvo. Mais de um é suspeita de duplicidade neste case.
- Não modelamos o lançamento completo de partidas dobradas. Em ERP real, várias linhas de débito e crédito por evento são normais.
- Valores em centavos inteiros; tolerância de 1 centavo.
- Regras independentes: o mesmo documento pode falhar em valor e centro simultaneamente.
- Origem é referência operacional, mas não é verdade contábil absoluta: deve ser validada pela Contabilidade.
- Sem estornos automáticos, alterações em ERP, autenticação ou IA.
- Sem garantia de integridade total do balancete: são controles específicos.
- Em produção: permissões, trilha de auditoria persistente, histórico real, regras versionadas, ambientes separados e aprovação de ajustes.
""")
 st.dataframe(pd.DataFrame(list(REGRAS.items()),columns=['Regra','Descrição']),hide_index=True,use_container_width=True)
