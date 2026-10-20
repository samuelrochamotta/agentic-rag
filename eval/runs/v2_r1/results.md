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
| q11 | agregacao | ✅ | ✅ | ✅ |
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
| q32 | agregacao | ✅ | ✅ | ✅ |
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
| agregacao | simples | 8 | 88% | 1.0 | 0.0 | 2292 | 0.00071 | 0.00567 | 6.5 | 100% | 0 |
| agregacao | agêntico | 8 | 100% | 4.9 | 0.0 | 26629 | 0.00103 | 0.00822 | 10.3 | 100% | 0 |
| agregacao | híbrido (jev) | 8 | 100% | 5.5 | 1.9 | 31134 | 0.00146 | 0.01167 | 11.0 | 100% | 0 |
| codigo_exato | simples | 6 | 100% | 1.0 | 0.0 | 1968 | 0.00035 | 0.00209 | 3.6 | 100% | 0 |
| codigo_exato | agêntico | 6 | 100% | 3.0 | 0.0 | 13063 | 0.00067 | 0.00400 | 9.4 | 88% | 4 |
| codigo_exato | híbrido (jev) | 6 | 100% | 3.0 | 2.0 | 13228 | 0.00085 | 0.00510 | 9.9 | 100% | 0 |
| distrator | simples | 7 | 86% | 1.0 | 0.0 | 2046 | 0.00029 | 0.00202 | 5.0 | 100% | 0 |
| distrator | agêntico | 7 | 100% | 2.7 | 0.0 | 12360 | 0.00141 | 0.00985 | 5.9 | 100% | 0 |
| distrator | híbrido (jev) | 7 | 100% | 2.9 | 1.7 | 13306 | 0.00157 | 0.01097 | 7.2 | 100% | 0 |
| multi_hop | simples | 7 | 43% | 1.0 | 0.0 | 2184 | 0.00031 | 0.00219 | 6.1 | 100% | 0 |
| multi_hop | agêntico | 7 | 100% | 3.9 | 0.0 | 20939 | 0.00073 | 0.00514 | 7.7 | 100% | 0 |
| multi_hop | híbrido (jev) | 7 | 100% | 2.9 | 2.0 | 13802 | 0.00073 | 0.00509 | 8.1 | 100% | 0 |
| referencia_secao | simples | 4 | 50% | 1.0 | 0.0 | 2114 | 0.00065 | 0.00261 | 6.5 | 100% | 0 |
| referencia_secao | agêntico | 4 | 100% | 2.8 | 0.0 | 9396 | 0.00072 | 0.00287 | 4.2 | 100% | 0 |
| referencia_secao | híbrido (jev) | 4 | 100% | 2.8 | 2.0 | 9758 | 0.00097 | 0.00386 | 5.0 | 100% | 0 |
| resposta_parcial | simples | 2 | 0% | 1.0 | 0.0 | 2602 | 0.00137 | 0.00273 | 10.1 | 100% | 0 |
| resposta_parcial | agêntico | 2 | 100% | 9.0 | 0.0 | 85084 | 0.00354 | 0.00707 | 23.3 | 100% | 0 |
| resposta_parcial | híbrido (jev) | 2 | 100% | 8.0 | 1.0 | 66280 | 0.00303 | 0.00607 | 40.1 | 100% | 0 |
| sem_resposta | simples | 4 | 100% | 1.0 | 0.0 | 1742 | 0.00028 | 0.00113 | 3.2 | 100% | 0 |
| sem_resposta | agêntico | 4 | 100% | 7.0 | 0.0 | 50428 | 0.00418 | 0.01674 | 14.3 | 100% | 0 |
| sem_resposta | híbrido (jev) | 4 | 100% | 2.0 | 1.2 | 10501 | 0.00170 | 0.00680 | 5.4 | 100% | 0 |
| simples | simples | 4 | 100% | 1.0 | 0.0 | 1606 | 0.00041 | 0.00164 | 2.2 | 100% | 0 |
| simples | agêntico | 4 | 100% | 2.2 | 0.0 | 8583 | 0.00082 | 0.00330 | 4.1 | 100% | 0 |
| simples | híbrido (jev) | 4 | 100% | 1.5 | 1.2 | 3912 | 0.00030 | 0.00121 | 3.7 | 100% | 0 |
| **TOTAL** | simples | 42 | 76% | 1.0 | 0.0 | 2067 | 0.00048 | 0.02008 | 5.2 | 100% | 0 |
| **TOTAL** | agêntico | 42 | 100% | 4.0 | 0.0 | 23055 | 0.00136 | 0.05718 | 8.8 | 98% | 4 |
| **TOTAL** | híbrido (jev) | 42 | 100% | 3.4 | 1.7 | 17796 | 0.00121 | 0.05076 | 9.3 | 100% | 0 |

Precisão de citação: das âncoras verificáveis (códigos, números, nomes) de frases com [p. N], quantas estão na página citada; "citações erradas" estão em outra página. Valores calculados pelo modelo não aparecem no texto e ficam fora da conta.


## Roteamento do híbrido

| id | categoria real | rota | confiança | caminho |
|---|---|---|--:|---|
| q01 | simples | simples | 0.82 | RAG simples |
| q02 | simples | simples | 1.0 | RAG simples |
| q03 | multi_hop | multi_hop | 0.99 | RAG agêntico |
| q04 | multi_hop | multi_hop | 0.5 | RAG agêntico |
| q05 | multi_hop | multi_hop | 0.45 | RAG agêntico |
| q06 | codigo_exato | simples | 0.75 | RAG agêntico |
| q07 | codigo_exato | codigo_exato | 0.95 | RAG agêntico |
| q08 | codigo_exato | referencia_secao | 0.5 | RAG agêntico |
| q09 | agregacao | agregacao | 1.0 | RAG agêntico |
| q10 | agregacao | agregacao | 1.0 | RAG agêntico |
| q11 | agregacao | agregacao | 0.87 | RAG agêntico |
| q12 | distrator | simples | 1.0 | RAG simples |
| q13 | distrator | simples | 0.61 | RAG agêntico |
| q14 | distrator | simples | 0.92 | RAG simples |
| q15 | referencia_secao | referencia_secao | 1.0 | RAG agêntico |
| q16 | referencia_secao | referencia_secao | 0.81 | RAG agêntico |
| q17 | sem_resposta | simples | 1.0 | RAG simples |
| q18 | sem_resposta | simples | 0.94 | RAG simples |
| q19 | simples | simples | 0.92 | RAG simples |
| q20 | simples | simples | 0.76 | RAG agêntico |
| q21 | multi_hop | multi_hop | 0.95 | RAG agêntico |
| q22 | multi_hop | simples | 0.59 | RAG agêntico |
| q23 | multi_hop | multi_hop | 0.59 | RAG agêntico |
| q24 | multi_hop | agregacao | 0.39 | RAG agêntico |
| q25 | codigo_exato | agregacao | 0.86 | RAG agêntico |
| q26 | codigo_exato | agregacao | 0.54 | RAG agêntico |
| q27 | codigo_exato | agregacao | 0.96 | RAG agêntico |
| q28 | agregacao | agregacao | 0.61 | RAG agêntico |
| q29 | agregacao | agregacao | 1.0 | RAG agêntico |
| q30 | agregacao | agregacao | 0.94 | RAG agêntico |
| q31 | agregacao | agregacao | 0.99 | RAG agêntico |
| q32 | agregacao | agregacao | 0.96 | RAG agêntico |
| q33 | distrator | agregacao | 0.87 | RAG agêntico |
| q34 | distrator | agregacao | 0.42 | RAG agêntico |
| q35 | distrator | agregacao | 0.41 | RAG agêntico |
| q36 | distrator | agregacao | 0.69 | RAG agêntico |
| q37 | referencia_secao | multi_hop | 0.76 | RAG agêntico |
| q38 | referencia_secao | multi_hop | 0.52 | RAG agêntico |
| q39 | sem_resposta | codigo_exato | 0.49 | RAG agêntico |
| q40 | sem_resposta | simples | 0.99 | RAG simples |
| q41 | resposta_parcial | multi_hop | 0.51 | RAG agêntico |
| q42 | resposta_parcial | agregacao | 0.95 | RAG agêntico |

## Erros (motivo do juiz)

- **q04 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: A referência identifica o NB-CD-04 como o CD de Joinville, gerido por Mariana Teixeira Lopes; a resposta afirma que não é possível identificar a gerente.
- **q09 / simples**: faltam termos ['12']; juiz: A referência informa 12 incidentes classe 3 no total, somando todas as áreas; a resposta apresenta apenas 6.
- **q15 / simples**: faltam termos ['75']; juiz: A resposta não informa o conteúdo da seção 7.3, que trata do descredenciamento e de suas condições.
- **q16 / simples**: faltam termos ['Nordeste']; juiz: A resposta omite o capítulo 12, Expansão Nordeste, que também é tratado na página 15.
- **q21 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: A referência identifica a unidade como Joinville, informa orçamento de R$ 3.210.000 e atribui a execução local à gerente Mariana Teixeira Lopes. A resposta afirma que esses dados não podem ser identificados.
- **q22 / simples**: faltam termos ['Silvana Torres Aguiar', '3302']; juiz: Identifica a área correta, mas omite a responsável (Silvana Torres Aguiar) e o ramal 3302, que foram pedidos.
- **q24 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: A referência identifica NB-CD-04 como a unidade de Joinville, gerida por Mariana Teixeira Lopes. A resposta contesta essa identificação e omite o nome da gerente solicitado.
- **q35 / simples**: Acerta o prazo geral de 54 horas, mas contradiz a referência ao dizer que não há regra sobre prevalência: no caso, prevalecem as 60 horas do contrato aprovado pela Diretoria Jurídica.
- **q41 / simples**: faltam termos ['Beatriz Moura Saldanha', '2210']; juiz: A resposta acerta ao dizer que não há tarifa para calcular o reembolso, mas erra ao afirmar que o documento não informa a responsável e o ramal: são Beatriz Moura Saldanha e 2210.
- **q42 / simples**: Acerta que o total anual não pode ser calculado, mas não identifica explicitamente o incidente grave como um vazamento de amônia em 14 de março de 2025 no NB-CD-04, em Joinville.

## Citações em página errada

- **q06 / agêntico**: 'ACX-7714' citado em p. [14], mas está em p. [7]
- **q06 / agêntico**: 'ACX-7417' citado em p. [14], mas está em p. [7]
- **q06 / agêntico**: 'ACX-7147' citado em p. [14], mas está em p. [7]
- **q06 / agêntico**: 'ACX-7471' citado em p. [14], mas está em p. [7]
