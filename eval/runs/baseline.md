# 3 rodadas · chat `deepseek/deepseek-v4.1-flash` · juiz `openai/gpt-6-luna`

| sistema | acurácia (média) | mín–máx | custo US$/pergunta | latência s | precisão de citação |
|---|--:|--:|--:|--:|--:|
| simples | 73.0% | 71%–74% | 0.00040 | 14.5 | 99% |
| agêntico | 100.0% | 100%–100% | 0.00101 | 8.9 | 98% |
| híbrido (jev) | 100.0% | 100%–100% | 0.00112 | 13.7 | 100% |

## Acertos por pergunta (rodadas certas / total)

| id | categoria | simples | agêntico | híbrido (jev) |
|---|---|:-:|:-:|:-:|
| q01 | simples | 3/3 | 3/3 | 3/3 |
| q02 | simples | 3/3 | 3/3 | 3/3 |
| q03 | multi_hop | 3/3 | 3/3 | 3/3 |
| q04 | multi_hop | 0/3 | 3/3 | 3/3 |
| q05 | multi_hop | 3/3 | 3/3 | 3/3 |
| q06 | codigo_exato | 3/3 | 3/3 | 3/3 |
| q07 | codigo_exato | 3/3 | 3/3 | 3/3 |
| q08 | codigo_exato | 3/3 | 3/3 | 3/3 |
| q09 | agregacao | 0/3 | 3/3 | 3/3 |
| q10 | agregacao | 3/3 | 3/3 | 3/3 |
| q11 | agregacao | 2/3 ⚠️ | 3/3 | 3/3 |
| q12 | distrator | 3/3 | 3/3 | 3/3 |
| q13 | distrator | 3/3 | 3/3 | 3/3 |
| q14 | distrator | 3/3 | 3/3 | 3/3 |
| q15 | referencia_secao | 0/3 | 3/3 | 3/3 |
| q16 | referencia_secao | 0/3 | 3/3 | 3/3 |
| q17 | sem_resposta | 3/3 | 3/3 | 3/3 |
| q18 | sem_resposta | 3/3 | 3/3 | 3/3 |
| q19 | simples | 3/3 | 3/3 | 3/3 |
| q20 | simples | 3/3 | 3/3 | 3/3 |
| q21 | multi_hop | 0/3 | 3/3 | 3/3 |
| q22 | multi_hop | 0/3 | 3/3 | 3/3 |
| q23 | multi_hop | 3/3 | 3/3 | 3/3 |
| q24 | multi_hop | 0/3 | 3/3 | 3/3 |
| q25 | codigo_exato | 3/3 | 3/3 | 3/3 |
| q26 | codigo_exato | 3/3 | 3/3 | 3/3 |
| q27 | codigo_exato | 3/3 | 3/3 | 3/3 |
| q28 | agregacao | 3/3 | 3/3 | 3/3 |
| q29 | agregacao | 3/3 | 3/3 | 3/3 |
| q30 | agregacao | 3/3 | 3/3 | 3/3 |
| q31 | agregacao | 3/3 | 3/3 | 3/3 |
| q32 | agregacao | 2/3 ⚠️ | 3/3 | 3/3 |
| q33 | distrator | 3/3 | 3/3 | 3/3 |
| q34 | distrator | 3/3 | 3/3 | 3/3 |
| q35 | distrator | 0/3 | 3/3 | 3/3 |
| q36 | distrator | 3/3 | 3/3 | 3/3 |
| q37 | referencia_secao | 2/3 ⚠️ | 3/3 | 3/3 |
| q38 | referencia_secao | 3/3 | 3/3 | 3/3 |
| q39 | sem_resposta | 3/3 | 3/3 | 3/3 |
| q40 | sem_resposta | 2/3 ⚠️ | 3/3 | 3/3 |
| q41 | resposta_parcial | 0/3 | 3/3 | 3/3 |
| q42 | resposta_parcial | 0/3 | 3/3 | 3/3 |

⚠️ = instável entre rodadas.
