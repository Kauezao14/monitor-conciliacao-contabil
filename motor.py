from pathlib import Path
import pandas as pd
BASE=Path(__file__).resolve().parent
REGRAS={
 'AUSENTE':'Evento da origem sem lançamento no destino.',
 'SEM_ORIGEM':'Lançamento sem evento correspondente na origem.',
 'DUPLICADO':'Mais de um lançamento para o evento, contrariando o contrato 1:1 desta simulação.',
 'VALOR':'Diferença monetária superior a 1 centavo.',
 'COMPETENCIA':'Competência contabilizada diferente da esperada.',
 'CONTA':'Conta utilizada diferente da regra esperada.',
 'CENTRO':'Centro de custo diferente do esperado.'}
ACOES={
 'AUSENTE':'Verificar rejeições, fila e elegibilidade do evento antes de reprocessar.',
 'SEM_ORIGEM':'Rastrear documento e sistema de origem; não excluir sem validação.',
 'DUPLICADO':'Verificar reenvio e chave de idempotência; avaliar estorno com a Contabilidade.',
 'VALOR':'Conferir descontos, arredondamentos e transformação do valor.',
 'COMPETENCIA':'Validar regra de reconhecimento e corte com a Contabilidade.',
 'CONTA':'Revisar o de/para vigente e a classificação com a Contabilidade.',
 'CENTRO':'Conferir cadastro, regra de alocação e vigência do centro de custo.'}
def carregar():
 return tuple(pd.read_csv(BASE/'dados'/f'{x}.csv',dtype={'empresa':str,'id_evento':str}) for x in ['origem','destino','cargas'])
def conciliar(o,d):
 keys=['empresa','id_evento']
 if o.duplicated(keys).any(): raise ValueError('Chave duplicada na origem; corrigir antes da conciliação.')
 if d.id_lancamento.duplicated().any(): raise ValueError('ID de lançamento repetido na carga.')
 for x in [o,d]:
  if x[keys].isna().any().any(): raise ValueError('Chave nula na carga.')
  if x.valor_centavos.isna().any() or (x.valor_centavos%1!=0).any(): raise ValueError('Valor deve ser inteiro em centavos.')
 grouped=d.groupby(keys).agg(valor_destino=('valor_centavos','sum'),qtd_lancamentos=('id_lancamento','size')).reset_index()
 m=o.merge(grouped,on=keys,how='outer',indicator=True)
 rows=[]
 for _,row in m.iterrows():
  k=(row.empresa,row.id_evento)
  lines=d[(d.empresa==k[0])&(d.id_evento==k[1])]
  has_o=row['_merge']!='right_only';has_d=len(lines)>0
  rec={str(key):value for key,value in row.items() if key!='_merge'}
  if not has_o:
   for field in ['sistema','lote','competencia']:rec[field]=lines.iloc[0][field]
   rec['polo']='Sem origem';rec['tipo_evento']='Não identificado'
  rec['valor_origem']=int(row.valor_centavos) if has_o else 0
  rec['valor_destino']=int(lines.valor_centavos.sum()) if has_d else 0
  rec['diferenca']=rec['valor_destino']-rec['valor_origem']
  rec['qtd_lancamentos']=len(lines)
  flags=[]
  if not has_d:flags.append('AUSENTE')
  if not has_o:flags.append('SEM_ORIGEM')
  if has_o and has_d:
   if len(lines)>1: flags.append('DUPLICADO')
   if abs(rec['diferenca'])>1:flags.append('VALOR')
   for field,expected,code in [('competencia','competencia','COMPETENCIA'),('conta','conta_esperada','CONTA'),('centro','centro_esperado','CENTRO')]:
    if lines[field].ne(row[expected]).any():flags.append(code)
  rec['regras']=flags;rec['conciliado']=not flags
  rec['prioridade']='Alta' if any(f in flags for f in ['DUPLICADO','SEM_ORIGEM']) or abs(rec['diferenca'])>=100000 else ('Média' if flags else 'Sem pendência')
  rows.append(rec)
 return pd.DataFrame(rows)
def ocorrencias(m):
 rows=[]
 for _,x in m[~m.conciliado].iterrows():
  seed=sum(x.id_evento.encode())
  first=pd.Timestamp('2026-10-01')+pd.Timedelta(days=seed%10)
  resolved=seed%5==0
  closed=first+pd.Timedelta(days=2+seed%4) if resolved else pd.NaT
  status='Resolvida' if resolved else ('Em análise' if seed%2 else 'Aberta')
  rows.append(dict(empresa=x.empresa,id_evento=x.id_evento,status=status,responsavel={'Acadêmico':'Equipe acadêmica + TI','Financeiro':'Tesouraria + TI','Folha':'RH + Contabilidade'}[x.sistema],primeira_deteccao=first,resolucao=closed,sla_dias=3 if x.prioridade=='Alta' else 7))
 return pd.DataFrame(rows)
