# Resultados: RAG híbrido (llm)

## Por pergunta

| id | categoria | híbrido (llm) |
|---|---|:-:|
| q01 | simples | ✅ |
| q02 | simples | ✅ |
| q03 | multi_hop | ✅ |
| q04 | multi_hop | ✅ |
| q05 | multi_hop | ✅ |
| q06 | codigo_exato | ✅ |
| q07 | codigo_exato | ✅ |
| q08 | codigo_exato | ✅ |
| q09 | agregacao | ✅ |
| q10 | agregacao | ✅ |
| q11 | agregacao | ✅ |
| q12 | distrator | ✅ |
| q13 | distrator | ✅ |
| q14 | distrator | ✅ |
| q15 | referencia_secao | ✅ |
| q16 | referencia_secao | ✅ |
| q17 | sem_resposta | ✅ |
| q18 | sem_resposta | ✅ |

## Agregado por categoria

Médias por pergunta, exceto custo total. Latência = tempo gasto nas chamadas à API (LLM + embeddings), medido pelo `Usage`.

Decisões = chamadas ao decider do híbrido; com o Jev elas NÃO aparecem em chamadas LLM.

| categoria | sistema | n | acurácia | chamadas LLM (méd.) | decisões (méd.) | tokens (méd.) | custo US$ (méd.) | custo US$ (total) | latência s (méd.) |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| agregacao | híbrido (llm) | 3 | 100% | 8.0 | 2.0 | 25039 | 0.00164 | 0.00491 | 23.8 |
| codigo_exato | híbrido (llm) | 3 | 100% | 4.0 | 2.0 | 5274 | 0.00038 | 0.00113 | 9.6 |
| distrator | híbrido (llm) | 3 | 100% | 2.0 | 1.0 | 1599 | 0.00010 | 0.00029 | 6.0 |
| multi_hop | híbrido (llm) | 3 | 100% | 5.0 | 2.0 | 9709 | 0.00068 | 0.00204 | 15.0 |
| referencia_secao | híbrido (llm) | 2 | 100% | 5.0 | 2.0 | 8972 | 0.00047 | 0.00094 | 12.4 |
| sem_resposta | híbrido (llm) | 2 | 100% | 2.0 | 1.0 | 1544 | 0.00013 | 0.00027 | 6.2 |
| simples | híbrido (llm) | 2 | 100% | 2.0 | 1.0 | 1611 | 0.00018 | 0.00035 | 6.1 |
| **TOTAL** | híbrido (llm) | 18 | 100% | 4.2 | 1.6 | 8284 | 0.00055 | 0.00993 | 11.8 |


## Roteamento do híbrido

| id | categoria real | rota | confiança | caminho |
|---|---|---|--:|---|
| q01 | simples | simples | 0.92 | RAG simples |
| q02 | simples | simples | 0.99 | RAG simples |
| q03 | multi_hop | multi_hop | 0.99 | RAG agêntico |
| q04 | multi_hop | multi_hop | 0.99 | RAG agêntico |
| q05 | multi_hop | multi_hop | 0.98 | RAG agêntico |
| q06 | codigo_exato | codigo_exato | 0.99 | RAG agêntico |
| q07 | codigo_exato | codigo_exato | 1.0 | RAG agêntico |
| q08 | codigo_exato | codigo_exato | 0.98 | RAG agêntico |
| q09 | agregacao | agregacao | 0.99 | RAG agêntico |
| q10 | agregacao | agregacao | 0.99 | RAG agêntico |
| q11 | agregacao | agregacao | 0.98 | RAG agêntico |
| q12 | distrator | simples | 0.99 | RAG simples |
| q13 | distrator | simples | 0.99 | RAG simples |
| q14 | distrator | simples | 0.99 | RAG simples |
| q15 | referencia_secao | referencia_secao | 1.0 | RAG agêntico |
| q16 | referencia_secao | referencia_secao | 1.0 | RAG agêntico |
| q17 | sem_resposta | simples | 0.99 | RAG simples |
| q18 | sem_resposta | simples | 0.96 | RAG simples |

## Erros (motivo do juiz)

