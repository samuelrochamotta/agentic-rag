# FinanceBench (open source) · chat `deepseek/deepseek-v4.1-flash` · juiz `openai/gpt-6-luna`

Um índice por documento (configuração *single store* do artigo). `recall de evidência` = a página anotada pelos autores está entre as que o sistema viu. "Erros com evidência em mãos" exclui as perguntas em que o read_page da página de evidência foi truncado (contadas à parte).

| sistema | grupo | n | erros do juiz | acurácia | recall de evidência | erros com evidência em mãos | página de evidência truncada | precisão de citação | US$/pergunta | US$ total | latência s | chamadas LLM |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| agentic | **TOTAL** | 150 | 0 | 87.3% | 95% | 15 | 0 | 97% | 0.00271 | 0.4060 | 27.1 | 4.9 |
| agentic | domain-relevant | 50 | 0 | 82.0% | 96% | 9 | 0 | 95% | 0.00375 | 0.1874 | 32.1 | 6.2 |
| agentic | metrics-generated | 50 | 0 | 98.0% | 98% | 1 | 0 | 98% | 0.00198 | 0.0988 | 35.5 | 4.2 |
| agentic | novel-generated | 50 | 0 | 82.0% | 92% | 5 | 0 | 99% | 0.00240 | 0.1199 | 13.6 | 4.2 |
| simple | **TOTAL** | 150 | 0 | 56.7% | 69% | 32 | 0 | 99% | 0.00126 | 0.1893 | 26.6 | 1.0 |
| simple | domain-relevant | 50 | 0 | 50.0% | 56% | 11 | 0 | 98% | 0.00070 | 0.0349 | 7.2 | 1.0 |
| simple | metrics-generated | 50 | 0 | 56.0% | 74% | 12 | 0 | 99% | 0.00260 | 0.1301 | 65.9 | 1.0 |
| simple | novel-generated | 50 | 0 | 64.0% | 78% | 9 | 0 | 100% | 0.00049 | 0.0243 | 6.6 | 1.0 |

## Erros

- **financebench_id_00499** (agentic, 3M_2022_10K, evidência vista): The gold answer concludes that 3M is not capital-intensive, while the system answer characterizes it as moderately capital-intensive, even though both cite similar metrics.
- **financebench_id_00499** (simple, 3M_2022_10K, evidência NÃO vista): The gold answer concludes that 3M is not capital-intensive based on its FY2022 metrics, while the system answer says this cannot be determined.
- **financebench_id_01226** (simple, 3M_2022_10K, evidência vista): The answer does not state the 1.7% operating-margin decrease or identify the principal one-off charges cited in the gold answer, including Combat Arms litigation, PFAS-exit impairment, Russia-exit costs, and divestiture-related restructuring.
- **financebench_id_01865** (simple, 3M_2022_10K, evidência NÃO vista): A resposta indica Safety & Industrial, mas o segmento apontado no gabarito é Consumer, que encolheu 0,9% organicamente.
- **financebench_id_00807** (agentic, 3M_2023Q2_10Q, evidência vista): The conclusion matches the gold answer, but the reported quick ratio of 0.85 materially differs from the gold value of 0.96.
- **financebench_id_00807** (simple, 3M_2023Q2_10Q, evidência NÃO vista): The gold answer gives a quick ratio of 0.96 and concludes liquidity needs improvement; the system answer says the ratio cannot be calculated and gives no matching conclusion.
- **financebench_id_02987** (simple, ACTIVISIONBLIZZARD_2019_10K, evidência NÃO vista): O sistema afirma que não é possível calcular o índice, mas a resposta correta é 24,26.
- **financebench_id_07966** (simple, ACTIVISIONBLIZZARD_2019_10K, evidência vista): The system says the average cannot be calculated, but the gold answer is 1.9%.
- **financebench_id_04735** (simple, ADOBE_2015_10K, evidência vista): The system says the ratio cannot be calculated, while the gold answer is 0.66.
- **financebench_id_07507** (simple, ADOBE_2016_10K, evidência NÃO vista): The system answer says the information was not found, while the income statement supports a year-over-year increase of 65.4%.
- **financebench_id_03856** (simple, ADOBE_2017_10K, evidência vista): The system says the ratio cannot be calculated, while the gold answer gives a calculable FY2017 ratio of 0.83.
- **financebench_id_00591** (simple, ADOBE_2022_10K, evidência vista): The system answer says the FCF conversion cannot be confirmed, while the gold answer says it improved from 143% in 2021 to 156% in 2022.
- **financebench_id_00540** (agentic, AES_2022_10K, evidência vista): The system answer calculates 12.1 times, which materially differs from the gold answer of 9.5 times.
- **financebench_id_00540** (simple, AES_2022_10K, evidência NÃO vista): The answer says the FY2022 inventory turnover cannot be determined, while the gold answer gives a turnover of 9.5 times.
- **financebench_id_10420** (agentic, AES_2022_10K, evidência vista): The system reports −1.42% (a ratio of −0.0142), which does not match the gold answer of −0.02 when rounded to two decimal places.
- **financebench_id_06655** (simple, AMAZON_2017_10K, evidência vista): The system says the DPO cannot be calculated because COGS is missing, while the gold answer gives a calculable value of 93.86.
- **financebench_id_01935** (agentic, AMCOR_2022_8K_dated-2022-07-01, evidência vista): The answer reverses the issuer substitution in its details: the Substitute Issuer replaced the Former Issuer, not vice versa.
- **financebench_id_01935** (simple, AMCOR_2022_8K_dated-2022-07-01, evidência vista): It identifies the supplemental indentures and the former and substitute issuers, but omits the key substance: the issuer substitution and assumption of covenants for the notes due 2026 and 2028.
- **financebench_id_00799** (agentic, AMCOR_2023_10K, evidência vista): It correctly says the quick ratio improved, but its reported values (0.53 to 0.57) materially conflict with the gold values (0.67 to 0.69).
- **financebench_id_00799** (simple, AMCOR_2023_10K, evidência vista): The gold answer says the quick ratio improved from 0.67 to 0.69; the system answer says the change cannot be determined.
- **financebench_id_01079** (simple, AMCOR_2023_10K, evidência vista): The answer mentions the Czech acquisition but omits the other two FY2023 acquisitions in the gold answer: the Shanghai medical-device packaging site and the New Zealand protein-packaging machine manufacturer.
- **financebench_id_01928** (simple, AMCOR_2023Q4_EARNINGS, evidência NÃO vista): The gold answer gives FY 2023 adjusted EBITDA as $2,018 million, while the system answer says the full-year figure is unavailable.
- **financebench_id_00222** (simple, AMD_2022_10K, evidência vista): The gold answer gives a quick ratio of 1.57 and concludes AMD’s liquidity is reasonably healthy; the system answer says the ratio cannot be calculated and gives no conclusion.
- **financebench_id_00917** (simple, AMD_2022_10K, evidência vista): It mentions acquisition-related amortization but does not identify the Xilinx acquisition amortization as the primary driver of the operating-margin change, instead saying the change cannot be determined.
- **financebench_id_00476** (simple, AMERICANEXPRESS_2022_10K, evidência NÃO vista): The answer says the information could not be found, rather than stating the gold answer that no debt securities are registered to trade on a national securities exchange.
- **financebench_id_01028** (simple, AMERICANEXPRESS_2022_10K, evidência NÃO vista): It lists selected countries and jurisdictions rather than the primary operating geographies: United States, EMEA, APAC, and LACC.
- **financebench_id_00723** (simple, AMERICANEXPRESS_2022_10K, evidência NÃO vista): The gold answer says AMEX does not measure performance through operating margin. The system answer instead says the information is unavailable and does not state that conclusion.
- **financebench_id_01964** (simple, AMERICANEXPRESS_2022_10K, evidência NÃO vista): The gold answer identifies customer deposits as the largest liability, while the system answer says it cannot determine the largest liability and instead names long-term debt among the items it found.
- **financebench_id_05718** (simple, AMERICANWATERWORKS_2020_10K, evidência NÃO vista): The system answer gives $0.389 billion, which rounds to $0.39 billion, not the gold answer of $0.40 billion; the difference exceeds the allowed rounding tolerance.
- **financebench_id_00070** (simple, AMERICANWATERWORKS_2022_10K, evidência vista): It correctly says working capital was negative, but claims the deficit cannot be calculated, contradicting the gold answer’s FY2022 value of -$1,561 million.
- **financebench_id_02608** (simple, BESTBUY_2017_10K, evidência NÃO vista): The system answer is blank and does not provide the 2.8% net profit margin.
- **financebench_id_00685** (simple, BESTBUY_2023_10K, evidência NÃO vista): The gold answer says gross margins were consistent, with only a 1.1% decline from FY2022 to FY2023; the system answer says this cannot be determined.
- **financebench_id_00460** (simple, BESTBUY_2024Q2_10Q, evidência vista): It correctly says the store count changed, but its totals (1,057 to 1,035) contradict the gold figures (982 to 969).
- **financebench_id_01902** (agentic, BESTBUY_2024Q2_10Q, evidência NÃO vista): The answer’s main conclusion is Computing and Mobile Phones, based on revenue share. The gold answer identifies Entertainment as the best-performing category, with 9% growth; the answer mentions that only as a caveat.
- **financebench_id_03838** (simple, BLOCK_2020_10K, evidência NÃO vista): The gold answer gives a total revenue growth rate of 101.5%; the system answer says it cannot be calculated.
- **financebench_id_00678** (simple, BOEING_2022_10K, evidência NÃO vista): The gold answer says Boeing’s gross margin improved from 4.8% in FY2021 to 5.3% in FY2022, while the system answer says improvement cannot be established.
- **financebench_id_01290** (simple, BOEING_2022_10K, evidência NÃO vista): The answer omits the US government, which the gold identifies as a primary customer accounting for 40% of FY2022 revenue, and does not state that Boeing serves a limited number of commercial airlines.
- **financebench_id_00585** (agentic, BOEING_2022_10K, evidência NÃO vista): The answer reverses the signs of both rates: the gold gives FY2022 as +0.62% and FY2021 as −14.76%, while the system answer reports FY2022 as negative and FY2021 as positive.
- **financebench_id_00585** (simple, BOEING_2022_10K, evidência NÃO vista): The answer reverses the signs of both rates and says FY2022 was lower; the gold answer gives 0.62% in FY2022 versus -14.76% in FY2021, so FY2022 was higher.
- **financebench_id_03473** (simple, COCACOLA_2017_10K, evidência NÃO vista): The gold answer gives FY2017 ROA as 0.01; the system answer says it could not find the information.
- **financebench_id_10130** (simple, CORNING_2020_10K, evidência vista): The answer gives 44.00 days from a reported metric, but the requested formula yields 63.86 days.
- **financebench_id_00005** (agentic, CORNING_2022_10K, evidência vista): Although it correctly says working capital was positive, it reports $2.278 million rather than the gold answer’s $831 million based on operating current assets and liabilities.
- **financebench_id_00005** (simple, CORNING_2022_10K, evidência vista): Both answers say working capital was positive, but the system gives $2.278 billion rather than the gold answer’s $831 million—a material difference.
- **financebench_id_05915** (simple, CVSHEALTH_2018_10K, evidência NÃO vista): The gold answer is 17.98; the system answer says the ratio cannot be calculated.
- **financebench_id_00790** (agentic, CVSHEALTH_2022_10K, evidência vista): The system answer concludes CVS is not capital-intensive, while the gold answer concludes it is, citing its extensive asset base and low ROA.
- **financebench_id_00790** (simple, CVSHEALTH_2022_10K, evidência NÃO vista): The gold answer concludes that CVS Health is capital-intensive based on its low ROA and asset base; the system answer says the information was not found.
- **financebench_id_04103** (simple, GENERALMILLS_2019_10K, evidência vista): The system answer says the CCC cannot be determined, while the gold answer gives a calculable FY2019 CCC of -3.7 days.
- **financebench_id_03471** (simple, GENERALMILLS_2020_10K, evidência vista): The system answer says the ratio cannot be calculated, while the gold answer gives a working capital ratio of 0.68.
- **financebench_id_00669** (simple, JOHNSON_JOHNSON_2022_10K, evidência NÃO vista): It mentions the COVID-19 vaccine exit costs and currency impacts but omits commodity inflation in MedTech and Consumer Health and the offsetting Consumer Health supply-chain benefits, which are key drivers in the gold answer.
- **financebench_id_00711** (simple, JOHNSON_JOHNSON_2022_10K, evidência vista): The gold answer gives inventory turnover of 2.7 times for FY2022, while the system answer says it cannot be calculated.
- **financebench_id_00651** (agentic, JOHNSON_JOHNSON_2022Q4_EARNINGS, evidência vista): Although it gives the gold’s 3.5% operational-growth conclusion, it also says the adjusted EPS guidance implies 4.0% growth and a marginal acceleration, contradicting the gold’s conclusion that growth decelerates slightly.
- **financebench_id_00651** (simple, JOHNSON_JOHNSON_2022Q4_EARNINGS, evidência vista): The gold answer says growth is expected to decelerate slightly, from 3.6% to 3.5%. The system answer instead concludes that adjusted EPS growth will accelerate based on a 4.0% midpoint.
- **financebench_id_00299** (agentic, JPMORGAN_2021Q1_10Q, evidência NÃO vista): The answer’s main conclusion is Commercial Banking, but the lowest net revenue overall was Corporate at -$473 million. Its caveat acknowledges this but does not change the stated answer.
- **financebench_id_00299** (simple, JPMORGAN_2021Q1_10Q, evidência NÃO vista): The answer identifies Commercial Banking as lowest, while the gold answer identifies Corporate at -$473 million.
- **financebench_id_02119** (agentic, JPMORGAN_2021Q1_10Q, evidência NÃO vista): The system answer gives $82.31 per share, not the gold answer of $66.56 per share.
- **financebench_id_02119** (simple, JPMORGAN_2021Q1_10Q, evidência NÃO vista): The gold answer gives $66.56 per share, while the system answer says the amount per share cannot be determined.
- **financebench_id_00394** (simple, JPMORGAN_2022Q2_10Q, evidência NÃO vista): The answer says the information was not found, but the highest-net-income segment was Corporate & Investment Bank.
- **financebench_id_10499** (simple, KRAFTHEINZ_2019_10K, evidência vista): The system answer says the ratio cannot be calculated, while the gold answer gives a FY2019 inventory turnover ratio of 6.25.
- **financebench_id_04412** (simple, LOCKHEEDMARTIN_2020_10K, evidência vista): The answer says the ratio cannot be calculated, but the gold answer gives an FY2020 asset turnover ratio of 1.33.
- **financebench_id_03031** (simple, LOCKHEEDMARTIN_2021_10K, evidência vista): The gold answer gives FY2021 net working capital of $5,818 million; the system answer says it cannot be calculated.
- **financebench_id_04171** (simple, MGMRESORTS_2018_10K, evidência NÃO vista): The system answer says the information was not found, but the FY2018 accounts payable amount was $303 million.
- **financebench_id_03849** (simple, MGMRESORTS_2020_10K, evidência NÃO vista): A resposta diz que não é possível calcular, mas o valor solicitado é 7,9%.
- **financebench_id_01911** (agentic, MGMRESORTS_2022Q4_EARNINGS, evidência vista): The gold answer gives a zero coverage ratio because Adjusted EBIT is negative; the system instead reports approximately 5.9x using Adjusted EBITDAR.
- **financebench_id_01911** (simple, MGMRESORTS_2022Q4_EARNINGS, evidência vista): The system says the information was not found, while the gold answer states the coverage ratio is zero because adjusted EBIT was negative.
- **financebench_id_00080** (agentic, PAYPAL_2022_10K, evidência vista): It correctly says working capital is positive, but reports $12.416 billion rather than the gold answer’s $1.6 billion—a material difference.
- **financebench_id_00080** (simple, PAYPAL_2022_10K, evidência vista): The gold answer states that PayPal had positive working capital of $1.6 billion at FY2022 year-end, while the system answer says it cannot be determined.
- **financebench_id_01009** (simple, PEPSICO_2022_10K, evidência vista): The answer omits several geographies in the gold answer, including Africa, the Middle East, and South Asia.
- **financebench_id_00735** (agentic, PEPSICO_2022_10K, evidência vista): The system answer concludes that an IRS tax dispute is an ongoing legal battle, while the gold answer says PepsiCo is not involved in material legal battles.
- **financebench_id_00735** (simple, PEPSICO_2022_10K, evidência NÃO vista): The gold answer says PepsiCo is not involved in material legal battles, while the system answer says the information could not be found.
- **financebench_id_01328** (agentic, PEPSICO_2022_10K, evidência vista): The gold answer is $411 million, while the system answer reports $0.
- **financebench_id_01328** (simple, PEPSICO_2022_10K, evidência vista): The system answer gives 0 as the requested value, while the gold answer is $411 million.
- **financebench_id_03620** (simple, PEPSICO_2022_10K, evidência vista): The system answer says EBITDA less capex cannot be determined, while the gold answer gives $9,068 million.
- **financebench_id_00302** (simple, PFIZER_2021_10K, evidência NÃO vista): The gold answer says Pfizer's PPNE increased year over year; the system answer says it could not find the information.
- **financebench_id_02416** (simple, PFIZER_2021_10K, evidência vista): It correctly names Trillium and Array but gives Pharmacia instead of Therachon.
- **financebench_id_00283** (agentic, Pfizer_2023Q2_10Q, evidência vista): The system answer gives approximately $70 million, which differs from the gold answer of $77.78 million by more than the allowed rounding tolerance.
- **financebench_id_00283** (simple, Pfizer_2023Q2_10Q, evidência vista): The system answer gives approximately $70 million, not the gold answer of $77.78 million.
- **financebench_id_02419** (agentic, Pfizer_2023Q2_10Q, evidência vista): The gold answer says Pfizer is spinning off Upjohn; the system answer says no and describes the Upjohn separation as completed in 2020.
- **financebench_id_02419** (simple, Pfizer_2023Q2_10Q, evidência vista): The gold answer says Pfizer is spinning off Upjohn, while the system answer says no and that the separation was completed in 2020.
- **financebench_id_00521** (simple, ULTABEAUTY_2023_10K, evidência NÃO vista): The answer says the information was not found, while the gold answer states that Ulta Beauty made no acquisitions in FY2023 or FY2022.
- **financebench_id_00603** (simple, ULTABEAUTY_2023Q4_EARNINGS, evidência vista): The gold answer attributes the increase to opening 47 new stores, while the system answer says the filing does not explain the cause.
- **financebench_id_02024** (simple, VERIZON_2021_10K, evidência NÃO vista): The gold answer specifies estimated 2024 pension benefits of $1,097 million and health care and life insurance benefits of $862 million; the system answer says it could not find the information.
- **financebench_id_00216** (simple, VERIZON_2022_10K, evidência NÃO vista): The gold answer gives a quick ratio of approximately 0.54 and concludes Verizon's liquidity profile was not healthy; the system answer says the ratio cannot be calculated and offers no such conclusion.
- **financebench_id_06247** (simple, WALMART_2018_10K, evidência vista): The system answer says the information was not found, while the gold answer gives FY2018 DPO as 42.69.
- **financebench_id_04784** (simple, WALMART_2019_10K, evidência NÃO vista): The answer says the information was not found, while the gold answer gives a change of 0.2%.
