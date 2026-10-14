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
| q07 | codigo_exato | ✅ | ✅ | ❌ |
| q08 | codigo_exato | ✅ | ✅ | ✅ |
| q09 | agregacao | ❌ | ✅ | ✅ |
| q10 | agregacao | ✅ | ✅ | ✅ |
| q11 | agregacao | ✅ | ✅ | ✅ |
| q12 | distrator | ✅ | ✅ | ✅ |
| q13 | distrator | ✅ | ✅ | ✅ |
| q14 | distrator | ✅ | ✅ | ✅ |
| q15 | referencia_secao | ❌ | ✅ | ✅ |
| q16 | referencia_secao | ❌ | ❌ | ❌ |
| q17 | sem_resposta | ✅ | ✅ | ✅ |
| q18 | sem_resposta | ✅ | ✅ | ✅ |

## Agregado por categoria

Médias por pergunta, exceto custo total. Latência = tempo gasto nas chamadas à API (LLM + embeddings), medido pelo `Usage`.

Decisões = chamadas ao decider do híbrido; com o Jev elas NÃO aparecem em chamadas LLM.

| categoria | sistema | n | acurácia | chamadas LLM (méd.) | decisões (méd.) | tokens (méd.) | custo US$ (méd.) | custo US$ (total) | latência s (méd.) |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| agregacao | simples | 3 | 67% | 1.0 | 0.0 | 1147 | 0.00017 | 0.00052 | 4.5 |
| agregacao | agêntico | 3 | 100% | 4.3 | 0.0 | 12868 | 0.00055 | 0.00166 | 11.5 |
| agregacao | híbrido (jev) | 3 | 100% | 5.0 | 2.0 | 15487 | 0.00075 | 0.00225 | 13.4 |
| codigo_exato | simples | 3 | 100% | 1.0 | 0.0 | 1187 | 0.00017 | 0.00050 | 4.5 |
| codigo_exato | agêntico | 3 | 100% | 2.0 | 0.0 | 3564 | 0.00015 | 0.00046 | 5.0 |
| codigo_exato | híbrido (jev) | 3 | 67% | 2.7 | 2.0 | 5621 | 0.00039 | 0.00118 | 8.2 |
| distrator | simples | 3 | 100% | 1.0 | 0.0 | 1174 | 0.00016 | 0.00049 | 3.2 |
| distrator | agêntico | 3 | 100% | 2.0 | 0.0 | 4004 | 0.00021 | 0.00062 | 5.4 |
| distrator | híbrido (jev) | 3 | 100% | 1.3 | 1.3 | 2097 | 0.00014 | 0.00041 | 4.4 |
| multi_hop | simples | 3 | 67% | 1.0 | 0.0 | 1271 | 0.00019 | 0.00056 | 6.3 |
| multi_hop | agêntico | 3 | 100% | 2.7 | 0.0 | 6116 | 0.00031 | 0.00094 | 7.3 |
| multi_hop | híbrido (jev) | 3 | 100% | 2.7 | 2.0 | 6418 | 0.00056 | 0.00169 | 11.2 |
| referencia_secao | simples | 2 | 0% | 1.0 | 0.0 | 1131 | 0.00017 | 0.00033 | 3.1 |
| referencia_secao | agêntico | 2 | 50% | 2.5 | 0.0 | 4956 | 0.00021 | 0.00042 | 4.7 |
| referencia_secao | híbrido (jev) | 2 | 50% | 3.0 | 2.0 | 6772 | 0.00043 | 0.00085 | 10.1 |
| sem_resposta | simples | 2 | 100% | 1.0 | 0.0 | 1096 | 0.00013 | 0.00025 | 2.8 |
| sem_resposta | agêntico | 2 | 100% | 5.0 | 0.0 | 14737 | 0.00058 | 0.00116 | 12.2 |
| sem_resposta | híbrido (jev) | 2 | 100% | 1.0 | 1.0 | 1096 | 0.00009 | 0.00017 | 3.6 |
| simples | simples | 2 | 100% | 1.0 | 0.0 | 1084 | 0.00013 | 0.00026 | 6.7 |
| simples | agêntico | 2 | 100% | 2.0 | 0.0 | 4510 | 0.00036 | 0.00071 | 4.7 |
| simples | híbrido (jev) | 2 | 100% | 1.5 | 1.5 | 3030 | 0.00031 | 0.00063 | 5.3 |
| **TOTAL** | simples | 18 | 78% | 1.0 | 0.0 | 1164 | 0.00016 | 0.00293 | 4.5 |
| **TOTAL** | agêntico | 18 | 94% | 2.9 | 0.0 | 7114 | 0.00033 | 0.00598 | 7.3 |
| **TOTAL** | híbrido (jev) | 18 | 89% | 2.6 | 1.7 | 6148 | 0.00040 | 0.00718 | 8.3 |


## Roteamento do híbrido

| id | categoria real | rota | confiança | caminho |
|---|---|---|--:|---|
| q01 | simples | simples | 0.77 | RAG agêntico |
| q02 | simples | simples | 1.0 | RAG simples |
| q03 | multi_hop | multi_hop | 0.99 | RAG agêntico |
| q04 | multi_hop | multi_hop | 0.51 | RAG agêntico |
| q05 | multi_hop | multi_hop | 0.46 | RAG agêntico |
| q06 | codigo_exato | simples | 0.64 | RAG agêntico |
| q07 | codigo_exato | codigo_exato | 0.99 | RAG agêntico |
| q08 | codigo_exato | referencia_secao | 0.68 | RAG agêntico |
| q09 | agregacao | agregacao | 1.0 | RAG agêntico |
| q10 | agregacao | agregacao | 1.0 | RAG agêntico |
| q11 | agregacao | agregacao | 0.95 | RAG agêntico |
| q12 | distrator | simples | 1.0 | RAG simples |
| q13 | distrator | simples | 0.47 | RAG agêntico |
| q14 | distrator | simples | 0.96 | RAG simples |
| q15 | referencia_secao | referencia_secao | 1.0 | RAG agêntico |
| q16 | referencia_secao | referencia_secao | 0.85 | RAG agêntico |
| q17 | sem_resposta | simples | 1.0 | RAG simples |
| q18 | sem_resposta | simples | 0.89 | RAG simples |

## Erros (motivo do juiz)

- **q04 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: A resposta não identifica a gerente responsável. A unidade era o CD de Joinville, gerido por Mariana Teixeira Lopes.
- **q07 / híbrido (jev)**: A resposta omite que a carga deve ficar especificamente na doca de retenção.
- **q09 / simples**: faltam termos ['12']; juiz: A resposta não informa o total de 12 incidentes classe 3 registrados em 2024.
- **q15 / simples**: faltam termos ['75']; juiz: A resposta não informa nenhum dos critérios ou prazos da seção 7.3 descritos na referência.
- **q16 / simples**: faltam termos ['Nordeste']; juiz: A resposta omite o capítulo 12, sobre a expansão no Nordeste e seus dados operacionais, e não informa a multa de R$ 1.350 por documento.
- **q16 / agêntico**: A resposta omite dados essenciais: a multa de R$ 1.350 por documento, a frota de 29 caminhões e 8 VUCs e os 2 incidentes classe 3 em 2024.
- **q16 / híbrido (jev)**: A resposta omite dados essenciais da referência: multa de R$ 1.350 por documento, operação regional a partir de Recife, frota de 29 caminhões e 8 VUCs e 2 incidentes classe 3 em 2024.
