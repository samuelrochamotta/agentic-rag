# Resultados: RAG simples vs RAG agêntico vs RAG híbrido (jev)

## Por pergunta

| id | categoria | simples | agêntico | híbrido (jev) |
|---|---|:-:|:-:|:-:|
| q01 | simples | ✅ | ✅ | ✅ |
| q02 | simples | ✅ | ✅ | ✅ |
| q03 | multi_hop | ✅ | ✅ | ✅ |
| q04 | multi_hop | ❌ | ✅ | ✅ |
| q05 | multi_hop | ✅ | ✅ | ✅ |
| q06 | codigo_exato | ✅ | ✅ | ✅ |
| q07 | codigo_exato | ✅ | ✅ | ✅ |
| q08 | codigo_exato | ✅ | ✅ | ✅ |
| q09 | agregacao | ❌ | ✅ | ✅ |
| q10 | agregacao | ✅ | ✅ | ✅ |
| q11 | agregacao | ❌ | ✅ | ✅ |
| q12 | distrator | ✅ | ✅ | ✅ |
| q13 | distrator | ✅ | ✅ | ✅ |
| q14 | distrator | ✅ | ✅ | ✅ |
| q15 | referencia_secao | ❌ | ✅ | ✅ |
| q16 | referencia_secao | ❌ | ✅ | ✅ |
| q17 | sem_resposta | ✅ | ✅ | ✅ |
| q18 | sem_resposta | ✅ | ✅ | ✅ |
| q19 | simples | ✅ | ✅ | ✅ |
| q20 | simples | ✅ | ✅ | ✅ |
| q21 | multi_hop | ❌ | ✅ | ✅ |
| q22 | multi_hop | ❌ | ✅ | ✅ |
| q23 | multi_hop | ✅ | ✅ | ✅ |
| q24 | multi_hop | ❌ | ✅ | ✅ |
| q25 | codigo_exato | ✅ | ✅ | ✅ |
| q26 | codigo_exato | ✅ | ✅ | ✅ |
| q27 | codigo_exato | ✅ | ✅ | ✅ |
| q28 | agregacao | ✅ | ✅ | ✅ |
| q29 | agregacao | ✅ | ✅ | ✅ |
| q30 | agregacao | ✅ | ✅ | ✅ |
| q31 | agregacao | ✅ | ✅ | ✅ |
| q32 | agregacao | ❌ | ✅ | ✅ |
| q33 | distrator | ✅ | ✅ | ✅ |
| q34 | distrator | ✅ | ✅ | ✅ |
| q35 | distrator | ❌ | ✅ | ✅ |
| q36 | distrator | ✅ | ✅ | ✅ |
| q37 | referencia_secao | ✅ | ✅ | ✅ |
| q38 | referencia_secao | ✅ | ✅ | ✅ |
| q39 | sem_resposta | ✅ | ✅ | ✅ |
| q40 | sem_resposta | ✅ | ✅ | ✅ |
| q41 | resposta_parcial | ❌ | ✅ | ✅ |
| q42 | resposta_parcial | ❌ | ✅ | ✅ |

## Agregado por categoria

Médias por pergunta, exceto custo total. Latência = tempo gasto nas chamadas à API (LLM + embeddings), medido pelo `Usage`.

Decisões = chamadas ao decider do híbrido; com o Jev elas NÃO aparecem em chamadas LLM.

| categoria | sistema | n | acurácia | chamadas LLM (méd.) | decisões (méd.) | tokens (méd.) | custo US$ (méd.) | custo US$ (total) | latência s (méd.) | precisão de citação | citações erradas |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| agregacao | simples | 8 | 62% | 1.0 | 0.0 | 18976 | 0.00084 | 0.00671 | 74.2 | 100% | 0 |
| agregacao | agêntico | 8 | 100% | 4.8 | 0.0 | 26214 | 0.00089 | 0.00715 | 11.6 | 100% | 0 |
| agregacao | híbrido (jev) | 8 | 100% | 4.8 | 1.8 | 26334 | 0.00114 | 0.00910 | 11.3 | 100% | 0 |
| codigo_exato | simples | 6 | 100% | 1.0 | 0.0 | 1848 | 0.00021 | 0.00125 | 103.9 | 100% | 0 |
| codigo_exato | agêntico | 6 | 100% | 3.0 | 0.0 | 13683 | 0.00058 | 0.00349 | 8.6 | 88% | 4 |
| codigo_exato | híbrido (jev) | 6 | 100% | 3.5 | 2.0 | 18108 | 0.00080 | 0.00480 | 9.4 | 95% | 2 |
| distrator | simples | 7 | 86% | 1.0 | 0.0 | 1970 | 0.00041 | 0.00286 | 5.5 | 100% | 0 |
| distrator | agêntico | 7 | 100% | 3.0 | 0.0 | 14092 | 0.00090 | 0.00632 | 8.1 | 100% | 0 |
| distrator | híbrido (jev) | 7 | 100% | 2.9 | 1.7 | 13581 | 0.00142 | 0.00995 | 7.7 | 100% | 0 |
| multi_hop | simples | 7 | 43% | 1.0 | 0.0 | 2009 | 0.00049 | 0.00342 | 4.9 | 95% | 1 |
| multi_hop | agêntico | 7 | 100% | 3.1 | 0.0 | 14147 | 0.00039 | 0.00274 | 6.8 | 100% | 0 |
| multi_hop | híbrido (jev) | 7 | 100% | 3.0 | 2.0 | 14249 | 0.00068 | 0.00473 | 7.1 | 100% | 0 |
| referencia_secao | simples | 4 | 50% | 1.0 | 0.0 | 1855 | 0.00055 | 0.00219 | 5.6 | 100% | 0 |
| referencia_secao | agêntico | 4 | 100% | 3.0 | 0.0 | 10638 | 0.00077 | 0.00307 | 5.3 | 100% | 0 |
| referencia_secao | híbrido (jev) | 4 | 100% | 3.5 | 2.0 | 21016 | 0.00214 | 0.00858 | 9.2 | 100% | 0 |
| resposta_parcial | simples | 2 | 0% | 1.0 | 0.0 | 3018 | 0.00039 | 0.00077 | 12.7 | 100% | 0 |
| resposta_parcial | agêntico | 2 | 100% | 6.5 | 0.0 | 52357 | 0.00179 | 0.00359 | 16.9 | 100% | 0 |
| resposta_parcial | híbrido (jev) | 2 | 100% | 7.5 | 1.0 | 57200 | 0.00278 | 0.00557 | 22.3 | 100% | 0 |
| sem_resposta | simples | 4 | 100% | 1.0 | 0.0 | 1506 | 0.00016 | 0.00063 | 3.4 | 100% | 0 |
| sem_resposta | agêntico | 4 | 100% | 6.0 | 0.0 | 38114 | 0.00333 | 0.01331 | 11.5 | 100% | 0 |
| sem_resposta | híbrido (jev) | 4 | 100% | 2.2 | 1.0 | 9633 | 0.00121 | 0.00486 | 155.3 | 100% | 0 |
| simples | simples | 4 | 100% | 1.0 | 0.0 | 1464 | 0.00006 | 0.00024 | 3.0 | 100% | 0 |
| simples | agêntico | 4 | 100% | 3.0 | 0.0 | 13231 | 0.00075 | 0.00299 | 5.4 | 100% | 0 |
| simples | híbrido (jev) | 4 | 100% | 1.5 | 1.2 | 4120 | 0.00014 | 0.00058 | 4.6 | 100% | 0 |
| **TOTAL** | simples | 42 | 71% | 1.0 | 0.0 | 5145 | 0.00043 | 0.01808 | 32.5 | 99% | 1 |
| **TOTAL** | agêntico | 42 | 100% | 3.8 | 0.0 | 20051 | 0.00102 | 0.04267 | 8.8 | 98% | 4 |
| **TOTAL** | híbrido (jev) | 42 | 100% | 3.4 | 1.7 | 18276 | 0.00115 | 0.04816 | 23.1 | 99% | 2 |

Precisão de citação: das âncoras verificáveis (códigos, números, nomes) de frases com [p. N], quantas estão na página citada; "citações erradas" estão em outra página. Valores calculados pelo modelo não aparecem no texto e ficam fora da conta.


## Roteamento do híbrido

| id | categoria real | rota | confiança | caminho |
|---|---|---|--:|---|
| q01 | simples | simples | 0.91 | RAG simples |
| q02 | simples | simples | 1.0 | RAG simples |
| q03 | multi_hop | multi_hop | 0.99 | RAG agêntico |
| q04 | multi_hop | multi_hop | 0.41 | RAG agêntico |
| q05 | multi_hop | multi_hop | 0.4 | RAG agêntico |
| q06 | codigo_exato | simples | 0.75 | RAG agêntico |
| q07 | codigo_exato | codigo_exato | 0.95 | RAG agêntico |
| q08 | codigo_exato | referencia_secao | 0.49 | RAG agêntico |
| q09 | agregacao | agregacao | 1.0 | RAG agêntico |
| q10 | agregacao | agregacao | 1.0 | RAG agêntico |
| q11 | agregacao | agregacao | 0.84 | RAG agêntico |
| q12 | distrator | simples | 1.0 | RAG simples |
| q13 | distrator | simples | 0.56 | RAG agêntico |
| q14 | distrator | simples | 0.96 | RAG simples |
| q15 | referencia_secao | referencia_secao | 1.0 | RAG agêntico |
| q16 | referencia_secao | referencia_secao | 0.84 | RAG agêntico |
| q17 | sem_resposta | simples | 1.0 | RAG simples |
| q18 | sem_resposta | simples | 0.92 | RAG simples |
| q19 | simples | simples | 0.92 | RAG simples |
| q20 | simples | simples | 0.79 | RAG agêntico |
| q21 | multi_hop | multi_hop | 0.95 | RAG agêntico |
| q22 | multi_hop | simples | 0.59 | RAG agêntico |
| q23 | multi_hop | multi_hop | 0.56 | RAG agêntico |
| q24 | multi_hop | agregacao | 0.41 | RAG agêntico |
| q25 | codigo_exato | agregacao | 0.89 | RAG agêntico |
| q26 | codigo_exato | agregacao | 0.52 | RAG agêntico |
| q27 | codigo_exato | agregacao | 0.96 | RAG agêntico |
| q28 | agregacao | agregacao | 0.52 | RAG agêntico |
| q29 | agregacao | agregacao | 1.0 | RAG agêntico |
| q30 | agregacao | agregacao | 0.9 | RAG agêntico |
| q31 | agregacao | agregacao | 0.99 | RAG agêntico |
| q32 | agregacao | agregacao | 0.96 | RAG agêntico |
| q33 | distrator | agregacao | 0.89 | RAG agêntico |
| q34 | distrator | agregacao | 0.49 | RAG agêntico |
| q35 | distrator | agregacao | 0.4 | RAG agêntico |
| q36 | distrator | agregacao | 0.69 | RAG agêntico |
| q37 | referencia_secao | multi_hop | 0.8 | RAG agêntico |
| q38 | referencia_secao | multi_hop | 0.46 | RAG agêntico |
| q39 | sem_resposta | codigo_exato | 0.44 | RAG agêntico |
| q40 | sem_resposta | simples | 0.97 | RAG simples |
| q41 | resposta_parcial | multi_hop | 0.52 | RAG agêntico |
| q42 | resposta_parcial | agregacao | 0.94 | RAG agêntico |

## Erros (motivo do juiz)

- **q04 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: A referência identifica a unidade como o CD de Joinville e informa que sua gerente é Mariana Teixeira Lopes; a resposta afirma que esses dados não constam no documento.
- **q09 / simples**: faltam termos ['12']; juiz: A resposta considera apenas as frotas Sul e Sudeste e não informa o total. Somando todas as áreas, foram 12 incidentes classe 3 em 2024.
- **q11 / simples**: faltam termos ['150']; juiz: A resposta lista as três parcelas, mas não informa o total pedido: 150 caminhões.
- **q15 / simples**: faltam termos ['75']; juiz: A resposta não informa o conteúdo da seção 7.3, que trata do descredenciamento e de seus critérios e prazos.
- **q16 / simples**: faltam termos ['Nordeste']; juiz: A resposta menciona apenas o capítulo 11 e omite o capítulo 12, Expansão Nordeste, também tratado na página 15.
- **q21 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: Não informa o orçamento de R$ 3.210.000 nem que Mariana Teixeira Lopes responde pela execução local; além disso, afirma que esses dados não foram encontrados.
- **q22 / simples**: faltam termos ['Silvana Torres Aguiar', '3302']; juiz: Identifica a área, mas omite a responsável, Silvana Torres Aguiar, e o ramal 3302.
- **q24 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: A resposta omite o nome pedido: a referência identifica Mariana Teixeira Lopes como gerente responsável.
- **q32 / simples**: faltam termos ['Recife', 'Tiago Falcão Medeiros']; juiz: A resposta está em branco; não informa as razões por unidade nem identifica Recife e seu gerente, Tiago Falcão Medeiros.
- **q35 / simples**: faltam termos ['60']; juiz: Informa corretamente o prazo geral de 54 horas, mas não reconhece que, conforme a referência, prevalecem as 60 horas do contrato específico aprovado pela Diretoria Jurídica.
- **q41 / simples**: faltam termos ['Beatriz Moura Saldanha', '2210']; juiz: Identifica corretamente a Controladoria e a ausência da tarifa por quilômetro, mas afirma que o documento não informa a responsável nem o ramal. A referência informa Beatriz Moura Saldanha, ramal 2210.
- **q42 / simples**: Acerta que o total anual não pode ser calculado, mas não identifica explicitamente o incidente grave descrito: o vazamento de amônia classe 3. Também omite a data e o local.

## Citações em página errada

- **q06 / agêntico**: 'ACX-7714' citado em p. [14], mas está em p. [7]
- **q06 / agêntico**: 'ACX-7417' citado em p. [14], mas está em p. [7]
- **q06 / agêntico**: 'ACX-7147' citado em p. [14], mas está em p. [7]
- **q06 / agêntico**: 'ACX-7471' citado em p. [14], mas está em p. [7]
- **q06 / híbrido (jev)**: 'ACX-7741' citado em p. [7, 7], mas está em p. [14]
- **q21 / simples**: 'NB-CD-04' citado em p. [13], mas está em p. [3, 6]
- **q26 / híbrido (jev)**: 'ACX-7741' citado em p. [7], mas está em p. [14]
