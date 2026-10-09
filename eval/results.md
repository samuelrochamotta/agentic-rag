# Resultados: RAG simples vs RAG agêntico

## Por pergunta

| id | categoria | simples | agêntico |
|---|---|:-:|:-:|
| q01 | simples | ✅ | ✅ |
| q02 | simples | ✅ | ✅ |
| q03 | multi_hop | ✅ | ✅ |
| q04 | multi_hop | ❌ | ✅ |
| q05 | multi_hop | ✅ | ✅ |
| q06 | codigo_exato | ✅ | ✅ |
| q07 | codigo_exato | ✅ | ✅ |
| q08 | codigo_exato | ✅ | ✅ |
| q09 | agregacao | ❌ | ❌ |
| q10 | agregacao | ✅ | ✅ |
| q11 | agregacao | ✅ | ✅ |
| q12 | distrator | ✅ | ✅ |
| q13 | distrator | ✅ | ✅ |
| q14 | distrator | ✅ | ✅ |
| q15 | referencia_secao | ❌ | ✅ |
| q16 | referencia_secao | ❌ | ❌ |
| q17 | sem_resposta | ✅ | ✅ |
| q18 | sem_resposta | ✅ | ✅ |

## Agregado por categoria

Médias por pergunta, exceto custo total. Latência = tempo gasto nas chamadas à API (LLM + embeddings), medido pelo `Usage`.

| categoria | sistema | n | acurácia | chamadas LLM (méd.) | tokens (méd.) | custo US$ (méd.) | custo US$ (total) | latência s (méd.) |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| agregacao | simples | 3 | 67% | 1.0 | 1148 | 0.00018 | 0.00053 | 4.4 |
| agregacao | agêntico | 3 | 67% | 5.3 | 16736 | 0.00062 | 0.00187 | 15.7 |
| codigo_exato | simples | 3 | 100% | 1.0 | 1189 | 0.00017 | 0.00050 | 3.7 |
| codigo_exato | agêntico | 3 | 100% | 2.0 | 3566 | 0.00016 | 0.00047 | 3.6 |
| distrator | simples | 3 | 100% | 1.0 | 1159 | 0.00016 | 0.00047 | 3.2 |
| distrator | agêntico | 3 | 100% | 2.0 | 3944 | 0.00020 | 0.00061 | 4.5 |
| multi_hop | simples | 3 | 67% | 1.0 | 1264 | 0.00018 | 0.00055 | 4.1 |
| multi_hop | agêntico | 3 | 100% | 2.3 | 5061 | 0.00027 | 0.00082 | 6.2 |
| referencia_secao | simples | 2 | 0% | 1.0 | 1128 | 0.00016 | 0.00033 | 4.2 |
| referencia_secao | agêntico | 2 | 50% | 2.5 | 4978 | 0.00022 | 0.00044 | 5.4 |
| sem_resposta | simples | 2 | 100% | 1.0 | 1096 | 0.00013 | 0.00025 | 2.7 |
| sem_resposta | agêntico | 2 | 100% | 4.5 | 13488 | 0.00062 | 0.00125 | 12.3 |
| simples | simples | 2 | 100% | 1.0 | 1084 | 0.00013 | 0.00026 | 3.6 |
| simples | agêntico | 2 | 100% | 2.0 | 4524 | 0.00028 | 0.00056 | 5.1 |
| **TOTAL** | simples | 18 | 78% | 1.0 | 1161 | 0.00016 | 0.00289 | 3.7 |
| **TOTAL** | agêntico | 18 | 89% | 2.9 | 7439 | 0.00033 | 0.00601 | 7.5 |

## Erros (motivo do juiz)

- **q04 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: A resposta omite o nome do gerente responsável, que é Mariana Teixeira Lopes.
- **q09 / simples**: faltam termos ['12']; juiz: A resposta de referência informa um total de 12 incidentes classe 3 em 2024; a resposta não fornece esse total.
- **q09 / agêntico**: faltam termos ['12']; juiz: O total correto é 12; a resposta omite 1 incidente da cadeia fria.
- **q15 / simples**: faltam termos ['75']; juiz: A resposta não apresenta as regras da seção 7.3 descritas na referência.
- **q16 / simples**: faltam termos ['Nordeste']; juiz: Menciona apenas conformidade fiscal e documental, omitindo a expansão no Nordeste e seus dados essenciais; também não informa a multa de R$ 1.350 por documento.
- **q16 / agêntico**: Omitiu fatos essenciais da referência: a multa de R$ 1.350 por documento, a frota de 29 caminhões e 8 VUCs e os 2 incidentes classe 3 em 2024.
