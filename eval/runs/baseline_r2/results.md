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
| q40 | sem_resposta | ❌ | ✅ | ✅ |
| q41 | resposta_parcial | ❌ | ✅ | ✅ |
| q42 | resposta_parcial | ❌ | ✅ | ✅ |

## Agregado por categoria

Médias por pergunta, exceto custo total. Latência = tempo gasto nas chamadas à API (LLM + embeddings), medido pelo `Usage`.

Decisões = chamadas ao decider do híbrido; com o Jev elas NÃO aparecem em chamadas LLM.

| categoria | sistema | n | acurácia | chamadas LLM (méd.) | decisões (méd.) | tokens (méd.) | custo US$ (méd.) | custo US$ (total) | latência s (méd.) | precisão de citação | citações erradas |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| agregacao | simples | 8 | 88% | 1.0 | 0.0 | 2461 | 0.00035 | 0.00276 | 7.8 | 100% | 0 |
| agregacao | agêntico | 8 | 100% | 4.4 | 0.0 | 21199 | 0.00076 | 0.00605 | 9.2 | 100% | 0 |
| agregacao | híbrido (jev) | 8 | 100% | 4.2 | 2.0 | 21054 | 0.00102 | 0.00815 | 9.4 | 100% | 0 |
| codigo_exato | simples | 6 | 100% | 1.0 | 0.0 | 1982 | 0.00030 | 0.00179 | 4.0 | 100% | 0 |
| codigo_exato | agêntico | 6 | 100% | 2.8 | 0.0 | 12291 | 0.00049 | 0.00296 | 7.5 | 86% | 4 |
| codigo_exato | híbrido (jev) | 6 | 100% | 3.2 | 2.0 | 13759 | 0.00075 | 0.00449 | 8.4 | 100% | 0 |
| distrator | simples | 7 | 86% | 1.0 | 0.0 | 1899 | 0.00036 | 0.00251 | 5.1 | 96% | 1 |
| distrator | agêntico | 7 | 100% | 3.3 | 0.0 | 15657 | 0.00120 | 0.00838 | 9.9 | 100% | 0 |
| distrator | híbrido (jev) | 7 | 100% | 3.0 | 1.7 | 14391 | 0.00148 | 0.01037 | 12.2 | 100% | 0 |
| multi_hop | simples | 7 | 43% | 1.0 | 0.0 | 2002 | 0.00046 | 0.00320 | 4.7 | 96% | 1 |
| multi_hop | agêntico | 7 | 100% | 2.9 | 0.0 | 13125 | 0.00040 | 0.00283 | 7.0 | 100% | 0 |
| multi_hop | híbrido (jev) | 7 | 100% | 3.4 | 2.0 | 17789 | 0.00091 | 0.00637 | 8.3 | 100% | 0 |
| referencia_secao | simples | 4 | 50% | 1.0 | 0.0 | 1903 | 0.00051 | 0.00205 | 4.7 | 100% | 0 |
| referencia_secao | agêntico | 4 | 100% | 3.0 | 0.0 | 11746 | 0.00094 | 0.00378 | 5.1 | 100% | 0 |
| referencia_secao | híbrido (jev) | 4 | 100% | 2.8 | 2.0 | 11042 | 0.00111 | 0.00445 | 6.8 | 100% | 0 |
| resposta_parcial | simples | 2 | 0% | 1.0 | 0.0 | 2508 | 0.00035 | 0.00070 | 9.0 | 100% | 0 |
| resposta_parcial | agêntico | 2 | 100% | 7.0 | 0.0 | 55444 | 0.00169 | 0.00338 | 17.2 | 100% | 0 |
| resposta_parcial | híbrido (jev) | 2 | 100% | 8.0 | 1.0 | 68814 | 0.00295 | 0.00590 | 20.6 | 100% | 0 |
| sem_resposta | simples | 4 | 75% | 1.0 | 0.0 | 1561 | 0.00020 | 0.00081 | 3.4 | 100% | 0 |
| sem_resposta | agêntico | 4 | 100% | 5.2 | 0.0 | 29651 | 0.00192 | 0.00767 | 10.5 | 100% | 0 |
| sem_resposta | híbrido (jev) | 4 | 100% | 2.2 | 1.0 | 10623 | 0.00137 | 0.00547 | 6.1 | 100% | 0 |
| simples | simples | 4 | 100% | 1.0 | 0.0 | 1478 | 0.00004 | 0.00016 | 2.5 | 100% | 0 |
| simples | agêntico | 4 | 100% | 2.2 | 0.0 | 8835 | 0.00064 | 0.00255 | 5.0 | 100% | 0 |
| simples | híbrido (jev) | 4 | 100% | 1.8 | 1.2 | 5384 | 0.00026 | 0.00104 | 4.1 | 100% | 0 |
| **TOTAL** | simples | 42 | 74% | 1.0 | 0.0 | 1992 | 0.00033 | 0.01398 | 5.2 | 99% | 2 |
| **TOTAL** | agêntico | 42 | 100% | 3.6 | 0.0 | 18015 | 0.00090 | 0.03759 | 8.4 | 98% | 4 |
| **TOTAL** | híbrido (jev) | 42 | 100% | 3.4 | 1.7 | 17192 | 0.00110 | 0.04625 | 9.0 | 100% | 0 |

Precisão de citação: das âncoras verificáveis (códigos, números, nomes) de frases com [p. N], quantas estão na página citada; "citações erradas" estão em outra página. Valores calculados pelo modelo não aparecem no texto e ficam fora da conta.


## Roteamento do híbrido

| id | categoria real | rota | confiança | caminho |
|---|---|---|--:|---|
| q01 | simples | simples | 0.86 | RAG simples |
| q02 | simples | simples | 1.0 | RAG simples |
| q03 | multi_hop | multi_hop | 0.99 | RAG agêntico |
| q04 | multi_hop | multi_hop | 0.57 | RAG agêntico |
| q05 | multi_hop | multi_hop | 0.39 | RAG agêntico |
| q06 | codigo_exato | simples | 0.76 | RAG agêntico |
| q07 | codigo_exato | codigo_exato | 0.95 | RAG agêntico |
| q08 | codigo_exato | referencia_secao | 0.49 | RAG agêntico |
| q09 | agregacao | agregacao | 1.0 | RAG agêntico |
| q10 | agregacao | agregacao | 1.0 | RAG agêntico |
| q11 | agregacao | agregacao | 0.9 | RAG agêntico |
| q12 | distrator | simples | 1.0 | RAG simples |
| q13 | distrator | simples | 0.62 | RAG agêntico |
| q14 | distrator | simples | 0.96 | RAG simples |
| q15 | referencia_secao | referencia_secao | 1.0 | RAG agêntico |
| q16 | referencia_secao | referencia_secao | 0.82 | RAG agêntico |
| q17 | sem_resposta | simples | 1.0 | RAG simples |
| q18 | sem_resposta | simples | 0.94 | RAG simples |
| q19 | simples | simples | 0.94 | RAG simples |
| q20 | simples | simples | 0.75 | RAG agêntico |
| q21 | multi_hop | multi_hop | 0.96 | RAG agêntico |
| q22 | multi_hop | simples | 0.62 | RAG agêntico |
| q23 | multi_hop | multi_hop | 0.57 | RAG agêntico |
| q24 | multi_hop | agregacao | 0.36 | RAG agêntico |
| q25 | codigo_exato | agregacao | 0.87 | RAG agêntico |
| q26 | codigo_exato | agregacao | 0.54 | RAG agêntico |
| q27 | codigo_exato | agregacao | 0.96 | RAG agêntico |
| q28 | agregacao | agregacao | 0.56 | RAG agêntico |
| q29 | agregacao | agregacao | 1.0 | RAG agêntico |
| q30 | agregacao | agregacao | 0.91 | RAG agêntico |
| q31 | agregacao | agregacao | 0.99 | RAG agêntico |
| q32 | agregacao | agregacao | 0.96 | RAG agêntico |
| q33 | distrator | agregacao | 0.87 | RAG agêntico |
| q34 | distrator | agregacao | 0.51 | RAG agêntico |
| q35 | distrator | agregacao | 0.4 | RAG agêntico |
| q36 | distrator | agregacao | 0.64 | RAG agêntico |
| q37 | referencia_secao | multi_hop | 0.76 | RAG agêntico |
| q38 | referencia_secao | multi_hop | 0.5 | RAG agêntico |
| q39 | sem_resposta | codigo_exato | 0.49 | RAG agêntico |
| q40 | sem_resposta | simples | 0.99 | RAG simples |
| q41 | resposta_parcial | multi_hop | 0.52 | RAG agêntico |
| q42 | resposta_parcial | agregacao | 0.94 | RAG agêntico |

## Erros (motivo do juiz)

- **q04 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: A referência identifica a unidade NB-CD-04 como o CD de Joinville, gerido por Mariana Teixeira Lopes; a resposta afirma que essa associação não consta no documento.
- **q09 / simples**: faltam termos ['12']; juiz: A resposta soma apenas Sul e Sudeste e informa 6, mas o total de todas as áreas é 12, incluindo cadeia fria, armazenagem e operação Nordeste.
- **q15 / simples**: faltam termos ['75']; juiz: A resposta não informa o conteúdo da seção 7.3, que trata do descredenciamento e suas condições.
- **q16 / simples**: faltam termos ['Nordeste']; juiz: A resposta aborda apenas o capítulo 11 e omite o capítulo 12, sobre a expansão no Nordeste, também tratado na página 15.
- **q21 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: A resposta nega a associação do NB-CD-04 a Joinville e omite o orçamento de R$ 3.210.000 e a responsável pela execução local, Mariana Teixeira Lopes.
- **q22 / simples**: faltam termos ['Silvana Torres Aguiar', '3302']; juiz: Identifica corretamente a área, mas omite a responsável Silvana Torres Aguiar e o ramal 3302, afirmando que não constam no documento.
- **q24 / simples**: faltam termos ['Mariana Teixeira Lopes']; juiz: Embora informe corretamente o código, a capacidade e a exigência de certificação, omite e nega a identificação da gerente: a referência informa Mariana Teixeira Lopes, responsável pela unidade NB-CD-04 em Joinville.
- **q35 / simples**: Acerta o prazo geral de 54 horas, mas omite a regra central: o contrato específico aprovado pela Diretoria Jurídica prevalece, portanto valem as 60 horas.
- **q40 / simples**: não declarou que a informação não está no documento
- **q41 / simples**: faltam termos ['Beatriz Moura Saldanha', '2210']; juiz: A resposta acerta que a tarifa por quilômetro não está informada e que não é possível calcular o reembolso, mas omite a responsável Beatriz Moura Saldanha e o ramal 2210, que são dados pedidos e disponíveis.
- **q42 / simples**: Embora acerte que o total anual não pode ser calculado, não identifica o vazamento de amônia de 14 de março de 2025 e afirma que houve 3 incidentes classe 3 em 2024, enquanto a referência informa 12.

## Citações em página errada

- **q06 / agêntico**: 'ACX-7714' citado em p. [14], mas está em p. [7]
- **q06 / agêntico**: 'ACX-7417' citado em p. [14], mas está em p. [7]
- **q06 / agêntico**: 'ACX-7147' citado em p. [14], mas está em p. [7]
- **q06 / agêntico**: 'ACX-7471' citado em p. [14], mas está em p. [7]
- **q21 / simples**: 'NB-CD-04' citado em p. [13], mas está em p. [3, 6]
- **q35 / simples**: 'Diretoria Jurídica' citado em p. [10], mas está em p. [1, 6]
