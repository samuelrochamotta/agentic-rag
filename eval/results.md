# Resultados: RAG simples vs RAG agêntico

## Por pergunta

| id | categoria | simples | agêntico |
|---|---|:-:|:-:|
| q01 | simples | ✅ | ✅ |
| q02 | simples | ✅ | ✅ |
| q03 | multi_hop | ✅ | ✅ |
| q04 | multi_hop | ❌ | ✅ |
| q05 | multi_hop | ✅ | ✅ |
| q06 | codigo_exato | ❌ | ✅ |
| q07 | codigo_exato | ✅ | ✅ |
| q08 | codigo_exato | ✅ | ✅ |
| q09 | agregacao | ❌ | ❌ |
| q10 | agregacao | ❌ | ✅ |
| q11 | agregacao | ✅ | ✅ |
| q12 | distrator | ✅ | ✅ |
| q13 | distrator | ✅ | ✅ |
| q14 | distrator | ✅ | ✅ |
| q15 | referencia_secao | ❌ | ✅ |
| q16 | referencia_secao | ❌ | ✅ |
| q17 | sem_resposta | ✅ | ✅ |
| q18 | sem_resposta | ✅ | ✅ |

## Agregado por categoria

Médias por pergunta, exceto custo total. Latência = tempo gasto nas chamadas à API (LLM + embeddings), medido pelo `Usage`.

| categoria | sistema | n | acurácia | chamadas LLM (méd.) | tokens (méd.) | custo US$ (méd.) | custo US$ (total) | latência s (méd.) |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| agregacao | simples | 3 | 33% | 1.0 | 1151 | 0.00057 | 0.00170 | 2.7 |
| agregacao | agêntico | 3 | 67% | 3.0 | 6472 | 0.00178 | 0.00535 | 4.6 |
| codigo_exato | simples | 3 | 67% | 1.0 | 1193 | 0.00053 | 0.00158 | 2.4 |
| codigo_exato | agêntico | 3 | 100% | 2.0 | 3767 | 0.00136 | 0.00409 | 3.4 |
| distrator | simples | 3 | 100% | 1.0 | 1092 | 0.00048 | 0.00145 | 2.5 |
| distrator | agêntico | 3 | 100% | 2.0 | 3899 | 0.00128 | 0.00384 | 3.8 |
| multi_hop | simples | 3 | 67% | 1.0 | 1180 | 0.00056 | 0.00167 | 2.9 |
| multi_hop | agêntico | 3 | 100% | 3.3 | 8228 | 0.00210 | 0.00629 | 5.4 |
| referencia_secao | simples | 2 | 0% | 1.0 | 1100 | 0.00045 | 0.00089 | 2.1 |
| referencia_secao | agêntico | 2 | 100% | 2.5 | 5004 | 0.00166 | 0.00333 | 5.4 |
| sem_resposta | simples | 2 | 100% | 1.0 | 1242 | 0.00050 | 0.00100 | 2.2 |
| sem_resposta | agêntico | 2 | 100% | 4.5 | 12598 | 0.00271 | 0.00542 | 7.7 |
| simples | simples | 2 | 100% | 1.0 | 1096 | 0.00047 | 0.00093 | 3.2 |
| simples | agêntico | 2 | 100% | 2.0 | 3425 | 0.00107 | 0.00215 | 3.4 |
| **TOTAL** | simples | 18 | 67% | 1.0 | 1151 | 0.00051 | 0.00923 | 2.6 |
| **TOTAL** | agêntico | 18 | 94% | 2.7 | 6064 | 0.00169 | 0.03046 | 4.7 |

## Erros (motivo do juiz)

- **q04 / simples**: A resposta de referência identifica claramente que NB-CD-04 é o CD de Joinville, gerido por Mariana Teixeira Lopes, informação essencial omitida na resposta.
- **q06 / simples**: faltam termos ['2,7']; juiz: A resposta não apresenta a capacidade nominal de carga que está claramente indicada na referência como 2,7 t.
- **q09 / simples**: faltam termos ['12']; juiz: A resposta não apresenta o número total de incidentes classe 3 em 2024, que é 12 conforme a referência.
- **q09 / agêntico**: faltam termos ['12']; juiz: A resposta omite o incidente da cadeia fria, que é essencial para o total correto de 12 incidentes.
- **q10 / simples**: faltam termos ['4.200']; juiz: omitiu a multa de descarte irregular de R$ 4.200, que é essencial para o total correto de R$ 15.850
- **q15 / simples**: faltam termos ['75']; juiz: A resposta não apresenta os fatos essenciais da seção 7.3, que estão claramente descritos na referência.
- **q16 / simples**: faltam termos ['Nordeste', 'fiscal']; juiz: omissão da informação essencial presente na referência
