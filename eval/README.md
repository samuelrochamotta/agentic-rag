# Conjunto de avaliação

`questions.json` traz 42 perguntas sobre `data/manual_simulado.pdf`, o manual de uma empresa
fictícia (Nébula Logística S.A.), com 16 páginas. O PDF é gerado por `data/gerar_pdf.py`, e o
conteúdo foi escrito de propósito para expor os pontos fracos do RAG simples, que embeda a
pergunta, pega os 5 chunks mais próximos por cosseno e responde numa única chamada.

| Categoria | Qtd. | O que testa | Por que o RAG simples sofre |
|---|---|---|---|
| `simples` | 4 | Fatos diretos, num único trecho. | É o grupo de controle: os sistemas devem acertar. |
| `multi_hop` | 7 | Encadear unidade, gerente, orçamento, responsável ou equipamento entre páginas distantes. | A busca única pode recuperar apenas um elo da cadeia. |
| `codigo_exato` | 6 | Distinguir códigos parecidos, comparar capacidades e corrigir uma premissa sobre anexos. | Similaridade semântica pode confundir identificadores ou recuperar só parte da comparação. |
| `agregacao` | 8 | Enumerar, somar, calcular proporções e comparar orçamento por área entre todas as unidades. | O top-5 pode trazer apenas parte dos dados; contas e seleção do máximo também podem falhar. |
| `distrator` | 7 | Separar versões, aplicar limites estritos e exceções, resolver precedência de contrato. | Recuperar a regra não garante aplicar suas condições corretamente. |
| `referencia_secao` | 4 | Encontrar seções e páginas, seguir remissões e conectar regras a um incidente. | Números de página/seção têm pouco peso semântico; o trecho inicial pode apenas remeter a outro. |
| `sem_resposta` | 4 | Reconhecer temas e detalhes ausentes, mesmo quando o evento relacionado está descrito. | Trechos próximos podem induzir a inventar um identificador ou valor. |
| `resposta_parcial` | 2 | Responder os fatos disponíveis e declarar quais dados faltam para completar a resposta. | Pode inventar a parte ausente ou desistir também da parte respondível. |

## Perguntas adicionais e dificuldade

As perguntas originais `q01`–`q18` foram preservadas. As 24 novas, `q19`–`q42`, têm
`difficulty` igual a `facil`, `dificil` ou `limite`. Essa classificação é uma estimativa
de complexidade, não um resultado medido; o avaliador atual agrupa por `category` e
não exibe nem filtra `difficulty`. Use `--only` para selecionar um grupo.

| IDs | Dificuldade | O que observar |
|---|---|---|
| q19–q20 | fácil | Controle: duas informações explícitas na mesma seção. |
| q21–q23 | difícil | Cadeias de busca e aprovação conjunta com nomes próprios. |
| q24 | limite | Incidente → unidade → equipamento especial → qualificação → gerente. |
| q25–q27 | difícil | Códigos permutados, comparação de capacidade e premissa falsa sobre C-3. |
| q28 | limite | Selecionar CDs pela região antes de somar seus orçamentos. |
| q29 | difícil | Incluir caminhões e VUCs de todas as regiões, sem confundir os subtotais. |
| q30 | limite | Aplicar condições e unidades de cobrança de quatro multas, depois somar. |
| q31 | difícil | Somar seis áreas e calcular uma participação percentual. |
| q32 | limite | Cruzar duas tabelas, calcular seis razões, selecionar o máximo e buscar o gerente. |
| q33 | limite | Distinguir atraso de exatamente 24 h de mais de 24 h e aplicar a exceção documentada. |
| q34–q36 | difícil | Nota exatamente no limiar, fraude, contrato aprovado e política revogada. |
| q37 | difícil | Seguir remissão do anexo para outra página e recuperar a providência aplicável. |
| q38 | limite | Classificação, gatilho, prazo, destinatários e comunicação externa em três seções. |
| q39–q40 | difícil | Não confundir equipamento com válvula nem multa com valor de prejuízo. |
| q41–q42 | limite | Responder a parte conhecida sem inventar tarifa nem extrapolar um total anual. |

No híbrido, observe especialmente se `q21`–`q24` vão para o agente e se `q33`–`q36`
recebem evidências suficientes sobre condições e exceções. O roteador só vê a pergunta;
uma rota barata equivocada pode comprometer o resultado. Nos casos `q41`–`q42`, confira
também o trace: o verificador atual é dispensado quando o rascunho declara ausência,
mesmo que a pergunta tenha uma parte respondível. O agente pode falhar por parar cedo,
deixar de enumerar candidatos ou consumir seus passos antes de completar a cadeia.

## Como comparar as abordagens

```bash
# Conjunto completo: simples, agêntico e híbrido com Jev
uv run rag eval --systems simple,agentic,hybrid --decider jev
cp eval/results.json eval/runs/results_extended_jev.json
cp eval/results.md eval/runs/results_extended_jev.md

# Mesmas perguntas e sistemas, agora com o LLM como decisor
uv run rag eval --systems simple,agentic,hybrid --decider llm
cp eval/results.json eval/runs/results_extended_llm.json
cp eval/results.md eval/runs/results_extended_llm.md

# Rodada curta com os oito casos de limite
uv run rag eval --only q24,q28,q30,q32,q33,q38,q41,q42 --decider jev
```

Cada execução sobrescreve `eval/results.json` e `eval/results.md`; as cópias acima
guardam as rodadas completas antes da seguinte. Repetir os comandos de cópia também
substitui essas cópias; use nomes diferentes para preservar repetições. Mantenha PDF,
modelos, chunks, limiares e `--max-steps` iguais entre comparações. Compare acurácia,
custo, latência e trace por pergunta, além da média geral. Repita as rodadas para
observar variação; compare Jev e LLM na coluna do híbrido.

Os relatórios anteriores cobrem apenas as 18 perguntas originais. Para comparar com
eles, selecione `q01`–`q18` explicitamente em `--only`. O conjunto foi construído para
explorar limitações conhecidas e não representa a distribuição de perguntas reais.

## Juiz independente, citações e várias rodadas

- O juiz usa `JUDGE_MODEL` (padrão `openai/gpt-6-luna`), diferente do `CHAT_MODEL`
  (padrão `deepseek/deepseek-v4.1-flash`). Antes, o mesmo modelo respondia e corrigia.
- `sem_resposta` agora exige declarar a ausência **e** passar pelo juiz: "não encontrei,
  mas o valor é X" deixou de contar como acerto.
- Cada resposta recebe uma **checagem de citações** sem API: as âncoras de cada frase com
  `[p. N]` (códigos, números com 2+ dígitos, nomes próprios) precisam estar na página citada.
  O relatório mostra a precisão de citação e lista as citações em página errada. Valores
  calculados pelo modelo não aparecem no texto e ficam fora da conta; frases sem citação
  própria também.
- `temperature=0` não torna o OpenRouter determinístico. Rode várias vezes e resuma:

```bash
for i in 1 2 3; do uv run rag eval --out eval/runs/baseline_r$i; done
uv run rag summarize eval/runs/baseline_r*/results.json --out eval/runs/baseline.md
```

## Benchmark externo: FinanceBench

`uv run rag financebench --systems simple,agentic` roda as 150 perguntas abertas do
[FinanceBench](https://github.com/patronus-ai/financebench) (relatórios da SEC em PDF, gabarito
humano), com um índice por documento, como na configuração *single store* do artigo. Além da
acurácia, o relatório mede o **recall de evidência**: se a página anotada pelos autores está entre
as que o sistema viu. Isso separa erro de busca de erro de leitura ou cálculo. Veja em
`src/agentic_rag/financebench.py` como baixar os dados para `data/financebench/` (fora do git).

## Como a nota é dada

O critério está em `src/agentic_rag/evaluate.py`. Uma resposta está correta quando o juiz (LLM) a considera equivalente
ao `gold` **e** todos os termos de `must_contain` aparecem nela. A comparação ignora maiúsculas e
acentos.

Os termos de `must_contain` copiam o formato do PDF (ex.: `4.870.000`, `15.850`, `2,7`). Se o modelo
reescrever um valor ("R$ 4,87 milhões"), a checagem determinística falha mesmo com a resposta certa.
Nesses casos, consulte o veredito do juiz. Nas novas perguntas, contas derivadas e
valores sujeitos a reformatação são avaliados pelo gabarito do juiz; `must_contain`
prioriza identificadores, nomes e termos estáveis.

`resposta_parcial` usa a avaliação normal pelo juiz e pelos termos obrigatórios:
admitir ausência sem responder a parte conhecida deve ser considerado incorreto.
Em `sem_resposta`, a resposta precisa declarar a ausência e o juiz precisa confirmar que
ela não inventou o dado.
