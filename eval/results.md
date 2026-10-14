# Resultados: RAG simples vs RAG agêntico vs RAG híbrido (jev)

## Por pergunta

| id | categoria | simples | agêntico | híbrido (jev) |
|---|---|:-:|:-:|:-:|
| q24 | multi_hop | ❌ | ✅ | ✅ |
| q28 | agregacao | ✅ | ✅ | ✅ |
| q30 | agregacao | ✅ | ✅ | ✅ |
| q32 | agregacao | ✅ | ✅ | ✅ |
| q33 | distrator | ✅ | ✅ | ✅ |
| q38 | referencia_secao | ✅ | ✅ | ✅ |
| q41 | resposta_parcial | ❌ | ✅ | ✅ |
| q42 | resposta_parcial | ❌ | ✅ | ✅ |

## Agregado por categoria

Médias por pergunta, exceto custo total. Latência = tempo gasto nas chamadas à API (LLM + embeddings), medido pelo `Usage`.

Decisões = chamadas ao decider do híbrido; com o Jev elas NÃO aparecem em chamadas LLM.

| categoria | sistema | n | acurácia | chamadas LLM (méd.) | decisões (méd.) | tokens (méd.) | custo US$ (méd.) | custo US$ (total) | latência s (méd.) |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| agregacao | simples | 3 | 100% | 1.0 | 0.0 | 1552 | 0.00031 | 0.00092 | 6.6 |
| agregacao | agêntico | 3 | 100% | 3.0 | 0.0 | 11297 | 0.00079 | 0.00237 | 11.4 |
| agregacao | híbrido (jev) | 3 | 100% | 3.3 | 2.0 | 13379 | 0.00112 | 0.00337 | 13.6 |
| distrator | simples | 1 | 100% | 1.0 | 0.0 | 1427 | 0.00026 | 0.00026 | 4.4 |
| distrator | agêntico | 1 | 100% | 2.0 | 0.0 | 4456 | 0.00031 | 0.00031 | 8.4 |
| distrator | híbrido (jev) | 1 | 100% | 3.0 | 2.0 | 7870 | 0.00063 | 0.00063 | 12.2 |
| multi_hop | simples | 1 | 0% | 1.0 | 0.0 | 1429 | 0.00027 | 0.00027 | 5.7 |
| multi_hop | agêntico | 1 | 100% | 3.0 | 0.0 | 11315 | 0.00106 | 0.00106 | 12.5 |
| multi_hop | híbrido (jev) | 1 | 100% | 3.0 | 2.0 | 10314 | 0.00106 | 0.00106 | 11.6 |
| referencia_secao | simples | 1 | 100% | 1.0 | 0.0 | 1340 | 0.00024 | 0.00024 | 4.1 |
| referencia_secao | agêntico | 1 | 100% | 3.0 | 0.0 | 7572 | 0.00043 | 0.00043 | 8.8 |
| referencia_secao | híbrido (jev) | 1 | 100% | 3.0 | 2.0 | 7574 | 0.00068 | 0.00068 | 9.0 |
| resposta_parcial | simples | 2 | 0% | 1.0 | 0.0 | 1437 | 0.00027 | 0.00055 | 5.4 |
| resposta_parcial | agêntico | 2 | 100% | 4.5 | 0.0 | 26806 | 0.00136 | 0.00271 | 17.9 |
| resposta_parcial | híbrido (jev) | 2 | 100% | 6.0 | 1.5 | 48662 | 0.00255 | 0.00511 | 26.7 |
| **TOTAL** | simples | 8 | 62% | 1.0 | 0.0 | 1466 | 0.00028 | 0.00224 | 5.6 |
| **TOTAL** | agêntico | 8 | 100% | 3.2 | 0.0 | 13856 | 0.00086 | 0.00687 | 12.5 |
| **TOTAL** | híbrido (jev) | 8 | 100% | 3.9 | 1.9 | 20402 | 0.00135 | 0.01084 | 15.9 |


## Roteamento do híbrido

| id | categoria real | rota | confiança | caminho |
|---|---|---|--:|---|
| q24 | multi_hop | agregacao | 0.37 | RAG agêntico |
| q28 | agregacao | agregacao | 0.8 | RAG agêntico |
| q30 | agregacao | agregacao | 0.89 | RAG agêntico |
| q32 | agregacao | agregacao | 0.92 | RAG agêntico |
| q33 | distrator | agregacao | 0.9 | RAG agêntico |
| q38 | referencia_secao | multi_hop | 0.6 | RAG agêntico |
| q41 | resposta_parcial | multi_hop | 0.79 | RAG agêntico |
| q42 | resposta_parcial | agregacao | 0.94 | RAG agêntico |

## Erros (motivo do juiz)

- **q24 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: Embora informe corretamente o código, a capacidade e a exigência de certificação, nega a ligação da unidade NB-CD-04 com Joinville e omite o nome da gerente responsável: Mariana Teixeira Lopes.
- **q41 / simples**: faltam termos ['Beatriz Moura Saldanha', '2210']; juiz: A resposta omite a responsável e o ramal, que são Beatriz Moura Saldanha e 2210. Acerta ao dizer que o manual não informa a tarifa por quilômetro nem permite calcular o reembolso.
- **q42 / simples**: faltam termos ['amônia']; juiz: Acerta que o total anual não pode ser calculado, mas não identifica o incidente grave descrito como vazamento de amônia em 14 de março de 2025.
