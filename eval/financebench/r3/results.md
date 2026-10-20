# FinanceBench (open source) · chat `deepseek/deepseek-v4.1-flash` · juiz `openai/gpt-6-luna`

Um índice por documento (configuração *single store* do artigo). `recall de evidência` = a página anotada pelos autores está entre as que o sistema viu. "Erros com evidência em mãos" exclui as perguntas em que o read_page da página de evidência foi truncado (contadas à parte).

| sistema | grupo | n | erros do juiz | acurácia | recall de evidência | erros com evidência em mãos | página de evidência truncada | precisão de citação | US$/pergunta | US$ total | latência s | chamadas LLM |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| agentic | **TOTAL** | 150 | 0 | 89.3% | 94% | 12 | 0 | 97% | 0.00238 | 0.3570 | 13.9 | 4.8 |
| agentic | domain-relevant | 50 | 0 | 88.0% | 94% | 6 | 0 | 97% | 0.00350 | 0.1751 | 21.2 | 6.0 |
| agentic | metrics-generated | 50 | 0 | 96.0% | 100% | 2 | 0 | 95% | 0.00172 | 0.0861 | 8.7 | 4.4 |
| agentic | novel-generated | 50 | 0 | 84.0% | 88% | 4 | 0 | 100% | 0.00192 | 0.0958 | 12.0 | 3.9 |

## Erros

- **financebench_id_00540** (agentic, AES_2022_10K, evidência vista): The system answer calculates about 12.1 turns, which conflicts with the gold answer of 9.5 turns.
- **financebench_id_10420** (agentic, AES_2022_10K, evidência vista): The system answer gives −1.42%, while the gold answer is −0.02 when ROA is rounded to two decimal places.
- **financebench_id_00799** (agentic, AMCOR_2023_10K, evidência vista): Although both answers say the ratio improved, the system answer reports 0.57 and 0.53, materially different from the gold answer’s 0.67 and 0.69.
- **financebench_id_05718** (agentic, AMERICANWATERWORKS_2020_10K, evidência vista): The system gives $0.389 billion, about 2.75% below the gold answer of $0.40 billion—outside the stated rounding tolerance.
- **financebench_id_01902** (agentic, BESTBUY_2024Q2_10Q, evidência NÃO vista): The gold answer identifies Entertainment as the best-performing category by growth (up 9%), while the system answer names Computing and Mobile Phones based on absolute revenue.
- **financebench_id_00585** (agentic, BOEING_2022_10K, evidência NÃO vista): The system answer gives FY2021 as positive 14.8% and FY2022 as negative 0.6%, while the gold answer gives FY2021 as negative 14.76% and FY2022 as positive 0.62%.
- **financebench_id_00005** (agentic, CORNING_2022_10K, evidência vista): It correctly concludes that working capital was positive, but gives $2.278 million rather than the gold answer’s $831 million operating working capital.
- **financebench_id_00790** (agentic, CVSHEALTH_2022_10K, evidência vista): The gold answer concludes CVS Health is capital-intensive, citing its low ROA and extensive asset base. The system answer concludes it is not capital-intensive.
- **financebench_id_00651** (agentic, JOHNSON_JOHNSON_2022Q4_EARNINGS, evidência vista): The gold answer says adjusted EPS growth is expected to decelerate slightly, from 3.6% to 3.5%; the system answer concludes it will accelerate to 4.0%.
- **financebench_id_00299** (agentic, JPMORGAN_2021Q1_10Q, evidência NÃO vista): The gold answer identifies Corporate as the lowest, with net revenue of -$473 million. The system answer instead concludes Commercial Banking, despite noting Corporate’s negative revenue.
- **financebench_id_02119** (agentic, JPMORGAN_2021Q1_10Q, evidência NÃO vista): The system answer gives approximately $82.31 per common share, not the gold answer of $66.56 per share.
- **financebench_id_01911** (agentic, MGMRESORTS_2022Q4_EARNINGS, evidência vista): The gold answer says Adjusted EBIT is negative, so the interest coverage ratio is zero. The system instead uses Adjusted EBITDAR and reports 5.88x.
- **financebench_id_00080** (agentic, PAYPAL_2022_10K, evidência vista): It correctly concludes that working capital is positive, but gives $12.416 billion rather than the gold answer’s $1.6 billion—a material numerical contradiction.
- **financebench_id_01328** (agentic, PEPSICO_2022_10K, evidência vista): The gold answer is $411 million; the system answer gives $0.
- **financebench_id_00283** (agentic, Pfizer_2023Q2_10Q, evidência vista): The answer gives approximately $700 million in total separation costs, not the expected future payment of $77.78 million.
- **financebench_id_02419** (agentic, Pfizer_2023Q2_10Q, evidência vista): The gold answer says yes—Pfizer is spinning off Upjohn. The system answer says no and characterizes the Upjohn spin-off as already completed.
