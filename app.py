from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
st.set_page_config(page_title="Conciliação Contábil",layout="wide")
base=Path(__file__).resolve().parent
a=pd.read_csv(base/'origem.csv')
c=pd.read_csv(base/'destino.csv')
g=c.groupby('id_documento').agg(valor_contabilizado=('valor_contabilizado','sum'),quantidade=('id_documento','size'),data_contabilizacao=('data_contabilizacao','min')).reset_index()
m=a.merge(g,on='id_documento',how='left')
m['valor_contabilizado']=m.valor_contabilizado.fillna(0)
m['diferenca']=m.valor_contabilizado-m.valor_mensalidade
m['categoria']='Conciliado'
m.loc[pd.to_datetime(m.data_contabilizacao).dt.strftime('%Y-%m').ne(m.competencia),'categoria']='Diferença de competência'
m.loc[m.diferenca.abs().gt(0.01),'categoria']='Valor divergente'
m.loc[m.quantidade.gt(1),'categoria']='Duplicado'
m.loc[m.quantidade.isna(),'categoria']='Não integrado'
st.title('Monitor de Conciliação Contábil')
st.caption('Projeto de portfólio • Dados 100% sintéticos • Não representa dados de nenhuma instituição real')
for col in ['competencia','polo','curso']:
 options=sorted(m[col].unique())
 selected=st.sidebar.multiselect(col,options,default=options)
 m=m[m[col].isin(selected)]
e=m[m.categoria.ne('Conciliado')]
x,y,z=st.columns(3)
x.metric('Documentos',len(m));y.metric('Exceções',len(e));z.metric('Diferença absoluta',f'R$ {e.diferenca.abs().sum():,.2f}')
if len(e):
 counts=e.groupby(['polo','categoria']).size().reset_index(name='quantidade')
 st.plotly_chart(px.bar(counts,x='polo',y='quantidade',color='categoria'),use_container_width=True)
st.dataframe(e,hide_index=True,use_container_width=True)
st.download_button('Exportar exceções',e.to_csv(index=False).encode('utf-8-sig'),'excecoes.csv')
with st.expander('Regras de conciliação'):
 st.write('Destino agregado por documento; tolerância R$ 0,01. Precedência: não integrado, duplicado, divergência de valor, diferença de competência, conciliado. Diferença de competência requer investigação, não comprova erro. Diferença monetária não equivale a perda financeira. Não substitui revisão contábil.')
