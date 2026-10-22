from motor import carregar,conciliar,ocorrencias
import pandas as pd

def executar():
 o,d,_=carregar();m=conciliar(o,d)
 assert len(o)==540 and len(d)==549 and len(m)==549
 assert int(m.conciliado.sum())==477
 counts=m.explode('regras').regras.value_counts().to_dict()
 assert counts=={'VALOR':27,'CENTRO':18,'AUSENTE':9,'SEM_ORIGEM':9,'DUPLICADO':9,'COMPETENCIA':9,'CONTA':9},counts
 assert int(m.diferenca.sum())==sum(d.valor_centavos)-sum(o.valor_centavos)
 multi=m[m.id_evento.str.endswith('-006')]
 assert all(set(x)=={'VALOR','CENTRO'} for x in multi.regras)
 # tolerância, isolamento entre empresas e origem sem duplicação
 oo=o.iloc[:1].copy();dd=d.iloc[:1].copy()
 dd['id_evento']=oo.iloc[0].id_evento;dd['competencia']=oo.iloc[0].competencia
 dd['conta']=oo.iloc[0].conta_esperada;dd['centro']=oo.iloc[0].centro_esperado
 dd['valor_centavos']=int(oo.iloc[0].valor_centavos)+1
 assert conciliar(oo,dd).iloc[0].conciliado
 dd['valor_centavos']+=1
 assert 'VALOR' in conciliar(oo,dd).iloc[0].regras
 dd['empresa']='OUTRA'
 assert len(conciliar(oo,dd))==2
 try:conciliar(pd.concat([o,o.iloc[:1]]),d)
 except ValueError:pass
 else:raise AssertionError('Duplicidade na origem não bloqueada')
 assert len(ocorrencias(m))==72
 print('Testes aprovados: contagens, múltiplas falhas, tolerância, chave por empresa, duplicação e totais.')
if __name__=='__main__':executar()
