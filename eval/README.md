# Conjunto de avaliação

`questions.json` traz 18 perguntas sobre `data/manual_simulado.pdf`, o manual de uma empresa
fictícia (Nébula Logística S.A.), com 16 páginas. O PDF é gerado por `data/gerar_pdf.py`, e o
conteúdo foi escrito de propósito para expor os pontos fracos do RAG simples, que embeda a
pergunta, pega os 5 chunks mais próximos por cosseno e responde numa única chamada.

| Categoria | Qtd. | O que testa | Por que o RAG simples sofre |
|---|---|---|---|
| `simples` | 2 | Fato direto, num único trecho. | Não sofre. É o grupo de controle: os dois modos devem acertar. |
| `multi_hop` | 3 | A resposta só sai juntando duas páginas distantes (ex.: o gerente aparece na p. 3 e o orçamento da unidade, identificado só pelo nome da cidade, na p. 13). | A busca acontece uma vez, com a pergunta original. O elo intermediário (o nome da cidade, o código do CD) não está na pergunta, então o segundo trecho dificilmente fica entre os top-5. |
| `codigo_exato` | 3 | Códigos como `ACX-7741`, `PRT-0093` e `Anexo C-3`, cercados de códigos quase iguais (`ACX-7714`, `PRT-0039`, `Anexo C-2`...). | Embeddings capturam o significado, não a string exata. Uma tabela cheia de códigos parecidos "parece" mais relevante que o trecho certo. Busca por palavra-chave (BM25/grep) acha o código na hora. |
| `agregacao` | 3 | Contar ou somar itens espalhados por 3 a 5 seções (incidentes classe 3 de 2024, multas internas, caminhões por região). O total não aparece escrito em lugar nenhum. | O top-5 traz só uma parte das ocorrências, e o modelo soma o que vê. Para enumerar tudo é preciso varrer o documento (grep) e conferir a conta (calculadora). |
| `distrator` | 3 | Seções quase duplicadas com números diferentes: reembolso 2023 (revogada) x 2025 (vigente), prazos de entrega 2024 x 2025, frota Sul x Sudeste. | Os dois trechos têm embeddings quase idênticos, e o errado pode vir na frente. Sem ler o contexto ("revogada", "vigente"), o modelo escolhe o número errado. |
| `referencia_secao` | 2 | "O que diz a seção 7.3?" e "o que está na página 15?". | O número de seção ou de página quase não tem peso semântico, então a similaridade não leva até o trecho. Ferramentas como sumário (`list_outline`) e leitura de página (`read_page`) resolvem direto. |
| `sem_resposta` | 2 | Perguntas plausíveis (home office, PLR) sobre temas que o manual não cobre. | O top-5 sempre devolve *algum* trecho, e o modelo tende a responder com base nele. O certo é dizer "Não encontrei essa informação no documento". |

## Como a nota é dada

Veja o `SPEC.md`. Em resumo, uma resposta está correta quando o juiz (LLM) a considera equivalente
ao `gold` **e** todos os termos de `must_contain` aparecem nela. A comparação ignora maiúsculas e
acentos. Em `sem_resposta`, a resposta precisa declarar que a informação não está no documento.

Os termos de `must_contain` copiam o formato do PDF (ex.: `4.870.000`, `15.850`, `2,7`). Se o modelo
reescrever um valor ("R$ 4,87 milhões"), a checagem determinística falha mesmo com a resposta certa.
Nesses casos, consulte o veredito do juiz.
