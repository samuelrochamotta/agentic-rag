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
| q37 | referencia_secao | ❌ | ✅ | ✅ |
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
| agregacao | simples | 8 | 88% | 1.0 | 0.0 | 2481 | 0.00064 | 0.00514 | 8.9 | 100% | 0 |
| agregacao | agêntico | 8 | 100% | 4.5 | 0.0 | 23282 | 0.00108 | 0.00860 | 11.9 | 100% | 0 |
| agregacao | híbrido (jev) | 8 | 100% | 4.8 | 1.9 | 25197 | 0.00141 | 0.01129 | 11.0 | 100% | 0 |
| codigo_exato | simples | 6 | 100% | 1.0 | 0.0 | 2027 | 0.00031 | 0.00186 | 4.6 | 100% | 0 |
| codigo_exato | agêntico | 6 | 100% | 3.0 | 0.0 | 13782 | 0.00066 | 0.00396 | 9.5 | 85% | 4 |
| codigo_exato | híbrido (jev) | 6 | 100% | 3.0 | 2.0 | 12523 | 0.00086 | 0.00514 | 13.6 | 97% | 1 |
| distrator | simples | 7 | 86% | 1.0 | 0.0 | 2035 | 0.00047 | 0.00331 | 5.7 | 100% | 0 |
| distrator | agêntico | 7 | 100% | 3.4 | 0.0 | 17124 | 0.00139 | 0.00976 | 8.9 | 100% | 0 |
| distrator | híbrido (jev) | 7 | 100% | 2.9 | 1.7 | 14047 | 0.00123 | 0.00858 | 8.5 | 100% | 0 |
| multi_hop | simples | 7 | 43% | 1.0 | 0.0 | 2067 | 0.00058 | 0.00405 | 5.3 | 100% | 0 |
| multi_hop | agêntico | 7 | 100% | 2.7 | 0.0 | 11823 | 0.00040 | 0.00278 | 7.5 | 100% | 0 |
| multi_hop | híbrido (jev) | 7 | 100% | 3.0 | 2.0 | 14253 | 0.00071 | 0.00495 | 7.5 | 100% | 0 |
| referencia_secao | simples | 4 | 25% | 1.0 | 0.0 | 2016 | 0.00072 | 0.00289 | 5.5 | 100% | 0 |
| referencia_secao | agêntico | 4 | 100% | 3.0 | 0.0 | 12329 | 0.00099 | 0.00397 | 4.9 | 100% | 0 |
| referencia_secao | híbrido (jev) | 4 | 100% | 2.8 | 2.0 | 10592 | 0.00106 | 0.00424 | 6.0 | 100% | 0 |
| resposta_parcial | simples | 2 | 0% | 1.0 | 0.0 | 2902 | 0.00035 | 0.00070 | 16.0 | 100% | 0 |
| resposta_parcial | agêntico | 2 | 100% | 7.5 | 0.0 | 57236 | 0.00254 | 0.00507 | 21.1 | 100% | 0 |
| resposta_parcial | híbrido (jev) | 2 | 100% | 7.5 | 1.0 | 59998 | 0.00255 | 0.00511 | 15.2 | 100% | 0 |
| sem_resposta | simples | 4 | 100% | 1.0 | 0.0 | 1471 | 0.00008 | 0.00034 | 2.6 | 100% | 0 |
| sem_resposta | agêntico | 4 | 100% | 5.8 | 0.0 | 34732 | 0.00230 | 0.00920 | 11.6 | 100% | 0 |
| sem_resposta | híbrido (jev) | 4 | 100% | 2.2 | 1.0 | 10826 | 0.00154 | 0.00615 | 5.8 | 100% | 0 |
| simples | simples | 4 | 100% | 1.0 | 0.0 | 1464 | 0.00006 | 0.00026 | 2.8 | 100% | 0 |
| simples | agêntico | 4 | 100% | 2.2 | 0.0 | 8417 | 0.00085 | 0.00341 | 5.4 | 100% | 0 |
| simples | híbrido (jev) | 4 | 100% | 1.5 | 1.2 | 4165 | 0.00025 | 0.00099 | 4.4 | 100% | 0 |
| **TOTAL** | simples | 42 | 74% | 1.0 | 0.0 | 2056 | 0.00044 | 0.01855 | 6.0 | 100% | 0 |
| **TOTAL** | agêntico | 42 | 100% | 3.7 | 0.0 | 19237 | 0.00111 | 0.04675 | 9.4 | 98% | 4 |
| **TOTAL** | híbrido (jev) | 42 | 100% | 3.3 | 1.7 | 16599 | 0.00111 | 0.04644 | 9.0 | 100% | 1 |

Precisão de citação: das âncoras verificáveis (códigos, números, nomes) de frases com [p. N], quantas estão na página citada; "citações erradas" estão em outra página. Valores calculados pelo modelo não aparecem no texto e ficam fora da conta.


## Roteamento do híbrido

| id | categoria real | rota | confiança | caminho |
|---|---|---|--:|---|
| q01 | simples | simples | 0.87 | RAG simples |
| q02 | simples | simples | 1.0 | RAG simples |
| q03 | multi_hop | multi_hop | 0.99 | RAG agêntico |
| q04 | multi_hop | multi_hop | 0.51 | RAG agêntico |
| q05 | multi_hop | multi_hop | 0.44 | RAG agêntico |
| q06 | codigo_exato | simples | 0.71 | RAG agêntico |
| q07 | codigo_exato | codigo_exato | 0.97 | RAG agêntico |
| q08 | codigo_exato | referencia_secao | 0.54 | RAG agêntico |
| q09 | agregacao | agregacao | 1.0 | RAG agêntico |
| q10 | agregacao | agregacao | 1.0 | RAG agêntico |
| q11 | agregacao | agregacao | 0.89 | RAG agêntico |
| q12 | distrator | simples | 1.0 | RAG simples |
| q13 | distrator | simples | 0.54 | RAG agêntico |
| q14 | distrator | simples | 0.96 | RAG simples |
| q15 | referencia_secao | referencia_secao | 1.0 | RAG agêntico |
| q16 | referencia_secao | referencia_secao | 0.82 | RAG agêntico |
| q17 | sem_resposta | simples | 1.0 | RAG simples |
| q18 | sem_resposta | simples | 0.94 | RAG simples |
| q19 | simples | simples | 0.91 | RAG simples |
| q20 | simples | simples | 0.75 | RAG agêntico |
| q21 | multi_hop | multi_hop | 0.95 | RAG agêntico |
| q22 | multi_hop | simples | 0.62 | RAG agêntico |
| q23 | multi_hop | multi_hop | 0.57 | RAG agêntico |
| q24 | multi_hop | agregacao | 0.39 | RAG agêntico |
| q25 | codigo_exato | agregacao | 0.87 | RAG agêntico |
| q26 | codigo_exato | agregacao | 0.45 | RAG agêntico |
| q27 | codigo_exato | agregacao | 0.96 | RAG agêntico |
| q28 | agregacao | agregacao | 0.62 | RAG agêntico |
| q29 | agregacao | agregacao | 1.0 | RAG agêntico |
| q30 | agregacao | agregacao | 0.89 | RAG agêntico |
| q31 | agregacao | agregacao | 0.99 | RAG agêntico |
| q32 | agregacao | agregacao | 0.96 | RAG agêntico |
| q33 | distrator | agregacao | 0.86 | RAG agêntico |
| q34 | distrator | agregacao | 0.42 | RAG agêntico |
| q35 | distrator | agregacao | 0.4 | RAG agêntico |
| q36 | distrator | agregacao | 0.64 | RAG agêntico |
| q37 | referencia_secao | multi_hop | 0.81 | RAG agêntico |
| q38 | referencia_secao | multi_hop | 0.49 | RAG agêntico |
| q39 | sem_resposta | codigo_exato | 0.46 | RAG agêntico |
| q40 | sem_resposta | simples | 0.99 | RAG simples |
| q41 | resposta_parcial | multi_hop | 0.54 | RAG agêntico |
| q42 | resposta_parcial | agregacao | 0.92 | RAG agêntico |

## Erros (motivo do juiz)

- **q04 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: A referência identifica Mariana Teixeira Lopes como gerente responsável pelo NB-CD-04; a resposta não informa esse nome.
- **q09 / simples**: faltam termos ['12']; juiz: A resposta soma apenas Sul e Sudeste (6) e omite outras áreas; o total de todas as áreas em 2024 é 12 incidentes.
- **q15 / simples**: faltam termos ['75']; juiz: A resposta não informa o conteúdo da seção 7.3, que trata do descredenciamento e de seus critérios, prazos e consequências.
- **q16 / simples**: faltam termos ['Nordeste']; juiz: Omitiu o capítulo 12, sobre a expansão no Nordeste, que também é tratado na página 15.
- **q21 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: A resposta afirma que não é possível determinar, mas a referência identifica a unidade como Joinville, com orçamento de R$ 3.210.000, e Mariana Teixeira Lopes como responsável pela execução local.
- **q22 / simples**: faltam termos ['Silvana Torres Aguiar', '3302']; juiz: Identifica a área correta, mas omite a responsável, Silvana Torres Aguiar, e o ramal 3302, que são partes centrais da pergunta.
- **q24 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: Informa corretamente o código, a capacidade e a exigência de certificação, mas omite o nome central pedido: a gerente responsável é Mariana Teixeira Lopes.
- **q35 / simples**: Informou corretamente o prazo geral de 54 horas, mas não respondeu que prevalecem as 60 horas previstas no contrato aprovado pela Diretoria Jurídica.
- **q37 / simples**: A resposta omite que o limite se aplica especificamente a avarias em manuseio interno, condição central do limite descrito na referência.
- **q41 / simples**: faltam termos ['Beatriz Moura Saldanha', '2210']; juiz: A resposta omite a responsável e o ramal, que a referência identifica como Beatriz Moura Saldanha e 2210. Está correta ao dizer que não há tarifa por quilômetro para calcular o reembolso.
- **q42 / simples**: Acerta que o manual não permite calcular o total anual, mas não identifica explicitamente o incidente grave como um vazamento de amônia; esse é o fato central pedido.

## Citações em página errada

- **q06 / agêntico**: 'ACX-7714' citado em p. [14], mas está em p. [7]
- **q06 / agêntico**: 'ACX-7417' citado em p. [14], mas está em p. [7]
- **q06 / agêntico**: 'ACX-7147' citado em p. [14], mas está em p. [7]
- **q06 / agêntico**: 'ACX-7471' citado em p. [14], mas está em p. [7]
- **q26 / híbrido (jev)**: 'ACX-7741' citado em p. [7], mas está em p. [14]
