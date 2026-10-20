# FinanceBench (open source) · chat `deepseek/deepseek-v4.1-flash` · juiz `openai/gpt-6-luna`

Um índice por documento (configuração *single store* do artigo). `recall de evidência` = a página anotada pelos autores está entre as que o sistema viu. "Erros com evidência em mãos" exclui as perguntas em que o read_page da página de evidência foi truncado (contadas à parte).

| sistema | grupo | n | erros do juiz | acurácia | recall de evidência | erros com evidência em mãos | página de evidência truncada | precisão de citação | US$/pergunta | US$ total | latência s | chamadas LLM |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| agentic | **TOTAL** | 150 | 0 | 87.3% | 93% | 15 | 0 | 98% | 0.00241 | 0.3614 | 13.9 | 4.8 |
| agentic | domain-relevant | 50 | 0 | 86.0% | 94% | 7 | 0 | 97% | 0.00346 | 0.1729 | 20.3 | 6.1 |
| agentic | metrics-generated | 50 | 0 | 98.0% | 100% | 1 | 0 | 98% | 0.00182 | 0.0909 | 9.5 | 4.6 |
| agentic | novel-generated | 50 | 0 | 78.0% | 86% | 7 | 0 | 99% | 0.00195 | 0.0975 | 12.0 | 3.8 |

## Erros

- **financebench_id_00499** (agentic, 3M_2022_10K, evidência vista): The gold answer concludes that 3M is not capital-intensive, while the system answer says it is moderately capital-intensive.
- **financebench_id_00540** (agentic, AES_2022_10K, evidência vista): The system answer gives an inventory turnover of about 12.1 times, which differs materially from the gold answer of 9.5 times.
- **financebench_id_10420** (agentic, AES_2022_10K, evidência vista): The gold answer is −0.02 as a decimal ROA (about −2%), while the system answer’s main result is −1.42% (−0.0142), which does not match.
- **financebench_id_01935** (agentic, AMCOR_2022_8K_dated-2022-07-01, evidência vista): The answer reverses the issuer substitution in its detailed description: the Substitute Issuer replaced the Former Issuer, not vice versa.
- **financebench_id_00799** (agentic, AMCOR_2023_10K, evidência vista): It correctly says the quick ratio improved, but reports 0.57 and 0.53 instead of the gold figures of 0.69 and 0.67.
- **financebench_id_00460** (agentic, BESTBUY_2024Q2_10Q, evidência vista): The system says Best Buy-branded stores fell from 1,057 to 1,035, whereas the gold answer gives 982 to 969. It mentions 982 to 969 only as the domestic total across store formats, not as its Best Buy store count.
- **financebench_id_01902** (agentic, BESTBUY_2024Q2_10Q, evidência NÃO vista): The gold answer identifies Entertainment as the best-performing category by its 9% growth. The system answer instead names Computing and Mobile Phones based on highest revenue.
- **financebench_id_00585** (agentic, BOEING_2022_10K, evidência NÃO vista): The answer reverses the signs of both rates: FY2022 was 0.62%, while FY2021 was -14.76%.
- **financebench_id_00005** (agentic, CORNING_2022_10K, evidência vista): It reaches the same positive conclusion, but gives $2.278 billion rather than the gold answer’s $831 million operating working capital amount.
- **financebench_id_00790** (agentic, CVSHEALTH_2022_10K, evidência vista): The system answer concludes CVS is not capital-intensive, directly contradicting the gold answer’s conclusion that it is.
- **financebench_id_00651** (agentic, JOHNSON_JOHNSON_2022Q4_EARNINGS, evidência vista): The gold answer says adjusted EPS growth is expected to decelerate slightly, while the system answer concludes it will be stable to marginally higher and cites a 4.0% midpoint growth rate.
- **financebench_id_00299** (agentic, JPMORGAN_2021Q1_10Q, evidência NÃO vista): The gold answer identifies Corporate as the segment with the lowest net revenue (-$473 million), while the system answer names Commercial Banking.
- **financebench_id_02119** (agentic, JPMORGAN_2021Q1_10Q, evidência NÃO vista): The gold answer is $66.56 per share, but the system answer gives $82.31 per share.
- **financebench_id_01911** (agentic, MGMRESORTS_2022Q4_EARNINGS, evidência vista): The gold answer gives a zero coverage ratio because Adjusted EBIT is negative; the system answer says the ratio cannot be calculated.
- **financebench_id_01912** (agentic, MGMRESORTS_2022Q4_EARNINGS, evidência vista): It correctly identifies MGM China and its 44% decline, but its comparison says Management and other operations also declined, contradicting the gold answer that the other regions presented increased revenue.
- **financebench_id_00080** (agentic, PAYPAL_2022_10K, evidência vista): It says working capital is positive, but reports approximately $12.4 billion rather than the gold answer’s $1.6 billion.
- **financebench_id_01328** (agentic, PEPSICO_2022_10K, evidência vista): The gold answer is $411 million; the system answer gives $0.
- **financebench_id_00283** (agentic, Pfizer_2023Q2_10Q, evidência vista): The gold answer is USD 77.78 million, but the response states approximately USD 700 million.
- **financebench_id_02419** (agentic, Pfizer_2023Q2_10Q, evidência vista): The gold answer says Pfizer is spinning off Upjohn, while the system answer says no spin-off is occurring.
