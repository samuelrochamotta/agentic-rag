# FinanceBench (open source) · chat `deepseek/deepseek-v4.1-flash` · juiz `openai/gpt-6-luna`

Um índice por documento (configuração *single store* do artigo). `recall de evidência` = a página anotada pelos autores está entre as que o sistema viu. "Erros com evidência em mãos" exclui as perguntas em que o read_page da página de evidência foi truncado (contadas à parte).

| sistema | grupo | n | erros do juiz | acurácia | recall de evidência | erros com evidência em mãos | página de evidência truncada | precisão de citação | US$/pergunta | US$ total | latência s | chamadas LLM |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| agentic | **TOTAL** | 150 | 0 | 84.7% | 94% | 13 | 21 | 96% | 0.00272 | 0.4084 | 18.1 | 5.1 |
| agentic | domain-relevant | 50 | 0 | 82.0% | 92% | 8 | 8 | 96% | 0.00418 | 0.2089 | 33.4 | 6.3 |
| agentic | metrics-generated | 50 | 0 | 98.0% | 100% | 1 | 2 | 93% | 0.00201 | 0.1007 | 9.1 | 4.7 |
| agentic | novel-generated | 50 | 0 | 74.0% | 90% | 4 | 11 | 98% | 0.00198 | 0.0988 | 11.7 | 4.2 |
| simple | **TOTAL** | 150 | 0 | 53.3% | 69% | 34 | 0 | 96% | 0.00081 | 0.1211 | 20.1 | 1.0 |
| simple | domain-relevant | 50 | 0 | 44.0% | 56% | 10 | 0 | 98% | 0.00076 | 0.0379 | 20.1 | 1.0 |
| simple | metrics-generated | 50 | 0 | 50.0% | 74% | 15 | 0 | 90% | 0.00096 | 0.0482 | 9.4 | 1.0 |
| simple | novel-generated | 50 | 0 | 66.0% | 78% | 9 | 0 | 99% | 0.00070 | 0.0351 | 30.9 | 1.0 |

## Erros

- **financebench_id_00499** (agentic, 3M_2022_10K, evidência vista): The gold answer concludes that 3M is not capital-intensive, while the system answer says the classification cannot be confirmed directly rather than giving that conclusion.
- **financebench_id_00499** (simple, 3M_2022_10K, evidência NÃO vista): The gold answer concludes that 3M is not capital-intensive, while the system answer says it cannot determine the conclusion.
- **financebench_id_01226** (simple, 3M_2022_10K, evidência vista): The answer lists relevant cost pressures, but does not state the key conclusion that 3M’s operating margin decreased by 1.7% in FY2022.
- **financebench_id_01865** (simple, 3M_2022_10K, evidência NÃO vista): The gold answer identifies the consumer segment, which shrank 0.9% organically; the system answer instead discusses personal safety and does not identify the consumer segment.
- **financebench_id_00807** (simple, 3M_2023Q2_10Q, evidência NÃO vista): The gold answer gives a quick ratio of 0.96 and concludes liquidity is not quite healthy by that measure; the system answer says the ratio cannot be determined.
- **financebench_id_02987** (simple, ACTIVISIONBLIZZARD_2019_10K, evidência NÃO vista): The gold answer gives a calculable FY2019 fixed asset turnover ratio of 24.26; the system answer incorrectly says it cannot be calculated.
- **financebench_id_07966** (simple, ACTIVISIONBLIZZARD_2019_10K, evidência vista): The gold answer is 1.9%; the system answer says the figure cannot be calculated.
- **financebench_id_04735** (simple, ADOBE_2015_10K, evidência vista): The answer says the ratio cannot be calculated, while the gold answer gives 0.66.
- **financebench_id_07507** (simple, ADOBE_2016_10K, evidência NÃO vista): The system answer says the information was not found, but the gold answer gives a year-over-year increase of 65.4%.
- **financebench_id_03856** (simple, ADOBE_2017_10K, evidência vista): The system does not provide the requested ratio and says it cannot be calculated, while the gold answer is 0.83.
- **financebench_id_00591** (agentic, ADOBE_2022_10K, evidência vista): The gold answer says FCF conversion improved from 143% in 2021 to 156% in 2022; the system answer incorrectly says the information cannot be found.
- **financebench_id_00591** (simple, ADOBE_2022_10K, evidência vista): The gold answer says FCF conversion improved from 143% in 2021 to 156% in 2022, while the system answer says it cannot be confirmed.
- **financebench_id_01319** (simple, AES_2022_10K, evidência NÃO vista): The gold answer is 0; the system answer says it could not find the information.
- **financebench_id_00540** (agentic, AES_2022_10K, evidência vista): The system answer gives an inventory turnover of about 12.1 times, rather than the gold answer of 9.5 times.
- **financebench_id_00540** (simple, AES_2022_10K, evidência NÃO vista): The gold answer states AES converted its inventory 9.5 times in FY2022, while the system answer says the ratio cannot be calculated.
- **financebench_id_10420** (agentic, AES_2022_10K, evidência vista): The system uses consolidated net loss of $505 million, yielding −1.42%. The gold value −0.02 corresponds to about −2% when expressed as a decimal ratio, consistent with using the attributable net loss instead; the reported ROA does not match.
- **financebench_id_06655** (simple, AMAZON_2017_10K, evidência vista): The gold answer gives a calculable DPO of 93.86; the system answer incorrectly says it cannot be calculated.
- **financebench_id_01935** (agentic, AMCOR_2022_8K_dated-2022-07-01, evidência vista): The answer reverses the issuer substitution: the Substitute Issuer replaced the Former Issuer, not vice versa.
- **financebench_id_01935** (simple, AMCOR_2022_8K_dated-2022-07-01, evidência vista): It identifies the supplemental indenture and the parties, but does not state the key purpose: substituting Amcor Flexibles North America for Amcor Finance and assuming the indenture covenants for the 2026 and 2028 notes.
- **financebench_id_00799** (simple, AMCOR_2023_10K, evidência vista): The gold answer says the quick ratio improved slightly, from 0.67 to 0.69; the system answer says it cannot be determined.
- **financebench_id_01079** (simple, AMCOR_2023_10K, evidência vista): The answer lists only the Czech acquisition and omits the FY2023 Shanghai medical-device packaging site and New Zealand protein-packaging machinery manufacturer named in the gold answer.
- **financebench_id_01928** (simple, AMCOR_2023Q4_EARNINGS, evidência NÃO vista): The answer says the FY 2023 adjusted EBITDA was not found, while the gold answer gives $2,018 million.
- **financebench_id_00222** (simple, AMD_2022_10K, evidência vista): The gold answer gives a FY22 quick ratio of 1.57 and concludes AMD has reasonably healthy liquidity; the system answer says it cannot be calculated.
- **financebench_id_00917** (simple, AMD_2022_10K, evidência vista): The answer says the driver was not found and mentions acquisition-related amortization only generally; it does not identify Xilinx-related intangible amortization as the primary driver.
- **financebench_id_00476** (simple, AMERICANEXPRESS_2022_10K, evidência NÃO vista): A resposta diz que não encontrou a informação, enquanto a resposta correta é que não há títulos de dívida registrados para negociação em uma bolsa nacional.
- **financebench_id_01028** (simple, AMERICANEXPRESS_2022_10K, evidência NÃO vista): The answer lists selected countries and subsidiary locations rather than identifying the primary operating regions: United States, EMEA, APAC, and LACC.
- **financebench_id_00723** (simple, AMERICANEXPRESS_2022_10K, evidência NÃO vista): The gold answer states that performance is not measured through operating margin, while the system answer only says the margin cannot be evaluated and does not provide that conclusion.
- **financebench_id_00720** (simple, AMERICANEXPRESS_2022_10K, evidência NÃO vista): The gold answer states that gross margin is not a measure used to assess performance; the system answer only says it could not find the information.
- **financebench_id_01964** (simple, AMERICANEXPRESS_2022_10K, evidência NÃO vista): The answer says it cannot determine the largest liability and discusses items within other liabilities, but the largest liability was customer deposits.
- **financebench_id_05718** (simple, AMERICANWATERWORKS_2020_10K, evidência NÃO vista): The system answer gives cash dividends paid as $0.389 billion, while the gold answer is $0.40 billion; the difference exceeds the allowed rounding tolerance.
- **financebench_id_02608** (simple, BESTBUY_2017_10K, evidência NÃO vista): The gold answer gives a three-year average net profit margin of 2.8%; the system answer says it cannot be calculated.
- **financebench_id_00685** (simple, BESTBUY_2023_10K, evidência NÃO vista): The gold answer concludes that gross margins were consistent, with only a 1.1% decline from FY2022 to FY2023. The system answer says this cannot be determined.
- **financebench_id_01902** (agentic, BESTBUY_2024Q2_10Q, evidência NÃO vista): The gold answer identifies Entertainment as the best performer by growth (up 9%), while the system answer names Computing and Mobile Phones based on revenue size.
- **financebench_id_03838** (simple, BLOCK_2020_10K, evidência NÃO vista): The system answer says the information was not found, but the FY2019–FY2020 revenue growth rate is 101.5%.
- **financebench_id_00678** (agentic, BOEING_2022_10K, evidência vista): The gold answer says Boeing’s gross margin improved from 4.8% in FY2021 to 5.3% in FY2022. The system answer instead says gross margin is not reported or useful and does not give that conclusion.
- **financebench_id_00678** (simple, BOEING_2022_10K, evidência NÃO vista): The system answer says there is no evidence of improvement, while the gold answer says gross profit and gross margin both improved from FY2021 to FY2022.
- **financebench_id_01290** (simple, BOEING_2022_10K, evidência NÃO vista): It identifies the commercial aviation industry but omits the US government, which the gold answer names as a primary customer and says accounted for 40% of FY2022 revenue.
- **financebench_id_00494** (agentic, BOEING_2022_10K, evidência vista): It contradicts the forecast for the 777X: after saying production was expected to resume in 2023, it says production would be paused during both 2022 and 2023, rather than forecasting an increase in 2023.
- **financebench_id_00585** (agentic, BOEING_2022_10K, evidência NÃO vista): The system answer reverses the signs: the gold says FY2022 was +0.62% and FY2021 was −14.76%, while the system reports FY2022 as negative and FY2021 as positive.
- **financebench_id_00585** (simple, BOEING_2022_10K, evidência NÃO vista): The answer reverses the signs of both rates: FY2022 was 0.62%, while FY2021 was -14.76%.
- **financebench_id_03473** (simple, COCACOLA_2017_10K, evidência NÃO vista): The gold answer is 0.01, while the system answer says it could not find the information.
- **financebench_id_06272** (simple, COCACOLA_2022_10K, evidência vista): The system says the ratio cannot be calculated, but the gold answer is 0.80.
- **financebench_id_10130** (simple, CORNING_2020_10K, evidência vista): The system answer gives 44 days, which does not match the formula-based DPO of 63.86 days.
- **financebench_id_00005** (agentic, CORNING_2022_10K, evidência NÃO vista): It correctly concludes that working capital was positive, but gives $2.278 million rather than the gold answer’s $831 million.
- **financebench_id_00005** (simple, CORNING_2022_10K, evidência vista): It correctly says working capital was positive, but gives $2,278 million rather than the gold answer’s $831 million.
- **financebench_id_05915** (simple, CVSHEALTH_2018_10K, evidência NÃO vista): The system says the ratio cannot be calculated, while the gold answer is 17.98.
- **financebench_id_00790** (agentic, CVSHEALTH_2022_10K, evidência vista): The gold answer concludes CVS is capital-intensive, citing its extensive asset base and low ROA. The system answer instead concludes its capital intensity is relatively low.
- **financebench_id_00790** (simple, CVSHEALTH_2022_10K, evidência NÃO vista): The answer says the information was not found, but the gold answer concludes that CVS Health is capital-intensive based on its low ROA and extensive asset base.
- **financebench_id_04103** (simple, GENERALMILLS_2019_10K, evidência vista): The gold answer gives a FY2019 CCC of -3.7 days, while the system answer says it cannot be determined.
- **financebench_id_03471** (simple, GENERALMILLS_2020_10K, evidência vista): The filing provides total current liabilities, allowing the ratio to be calculated; the gold answer is 0.68, not indeterminable.
- **financebench_id_10136** (simple, GENERALMILLS_2022_10K, evidência vista): The gold answer is 0.54. The system answer uses rounded dividends of $1.2 billion and reports 0.56, rather than the cash-dividend amount that yields 0.54.
- **financebench_id_00956** (simple, JOHNSON_JOHNSON_2022_10K, evidência NÃO vista): The response does not conclude that JnJ was not a high-growth company; it says no explicit classification was found. The gold answer concludes no, citing FY2022 sales growth of 1.3%.
- **financebench_id_00669** (simple, JOHNSON_JOHNSON_2022_10K, evidência NÃO vista): The system answer says the filing does not explain gross-margin drivers, but the gold answer identifies COVID-19 vaccine exit costs, pharmaceutical currency impacts, commodity inflation, and partially offsetting Consumer Health supply-chain benefits.
- **financebench_id_00711** (simple, JOHNSON_JOHNSON_2022_10K, evidência vista): The gold answer gives an FY2022 inventory turnover of 2.7 times, while the system answer says it cannot be calculated.
- **financebench_id_00651** (agentic, JOHNSON_JOHNSON_2022Q4_EARNINGS, evidência vista): Although it answers that there is no clear acceleration, it says reported adjusted EPS growth is slightly above FY2022, rather than the gold answer’s slight deceleration from 3.6% to 3.5%.
- **financebench_id_00651** (simple, JOHNSON_JOHNSON_2022Q4_EARNINGS, evidência vista): Although it notes 3.6% growth slowing to 3.5%, it also says the adjusted EPS midpoint implies acceleration, contradicting the gold answer that growth is expected to decelerate slightly.
- **financebench_id_01487** (simple, JOHNSON_JOHNSON_2023Q2_EARNINGS, evidência vista): The gold answer says reported net earnings as a percent of sales increased from 20% to 20.1%; the system instead answers no using adjusted earnings and says the reported margin is not stated.
- **financebench_id_00299** (agentic, JPMORGAN_2021Q1_10Q, evidência NÃO vista): The answer’s main conclusion is Commercial Banking, but the lowest net revenue was Corporate at -$473 million.
- **financebench_id_02119** (agentic, JPMORGAN_2021Q1_10Q, evidência NÃO vista): The system answer gives $82.31 per share, while the gold answer is $66.56 per share.
- **financebench_id_02119** (simple, JPMORGAN_2021Q1_10Q, evidência NÃO vista): The gold answer gives $66.56 per share; the system answer says the amount cannot be determined.
- **financebench_id_00206** (simple, JPMORGAN_2022_10K, evidência NÃO vista): The answer says the information was not found, but the gold answer states that gross margin is not a relevant metric for a financial institution like JPM.
- **financebench_id_00394** (simple, JPMORGAN_2022Q2_10Q, evidência NÃO vista): The answer says the information was not found, while the gold answer identifies Corporate & Investment Bank as having the highest net income.
- **financebench_id_10499** (simple, KRAFTHEINZ_2019_10K, evidência vista): The gold answer gives an FY2019 inventory turnover ratio of 6.25; the system answer says it cannot be calculated.
- **financebench_id_04412** (simple, LOCKHEEDMARTIN_2020_10K, evidência vista): The system answer says the ratio cannot be calculated, while the gold answer gives an FY2020 asset turnover ratio of 1.33.
- **financebench_id_03031** (simple, LOCKHEEDMARTIN_2021_10K, evidência vista): The system answer says net working capital cannot be determined, but the gold value is $5,818 million.
- **financebench_id_04171** (simple, MGMRESORTS_2018_10K, evidência NÃO vista): The gold answer gives accounts payable of $303.00 million; the system answer says it could not find the information.
- **financebench_id_03849** (simple, MGMRESORTS_2020_10K, evidência NÃO vista): The system answer says the information was not found, but the gold answer is 7.9%.
- **financebench_id_01911** (agentic, MGMRESORTS_2022Q4_EARNINGS, evidência vista): The gold answer says FY2022 Adjusted EBIT was negative, so the interest coverage ratio is zero. The system instead uses Adjusted EBITDAR and reports a positive 5.88x ratio.
- **financebench_id_01911** (simple, MGMRESORTS_2022Q4_EARNINGS, evidência vista): The gold answer states the coverage ratio is zero because Adjusted EBIT is negative; the system answer says it could not find the information.
- **financebench_id_00080** (agentic, PAYPAL_2022_10K, evidência vista): The answer says working capital is positive, but reports $12.4 billion rather than the gold answer’s $1.6 billion.
- **financebench_id_00080** (simple, PAYPAL_2022_10K, evidência vista): The gold answer states that PayPal had positive working capital of $1.6 billion at FY2022 year-end, while the system answer says it cannot be determined.
- **financebench_id_04980** (simple, PEPSICO_2021_10K, evidência vista): It says the amount cannot be found using the cash flow statement and offers $4.625 billion only from outside the requested source, rather than answering under the stated constraint.
- **financebench_id_01009** (simple, PEPSICO_2022_10K, evidência vista): The answer omits Africa, the Middle East, and South Asia from the FY2022 geography list, so it does not provide the same set of geographies as the gold answer.
- **financebench_id_00735** (simple, PEPSICO_2022_10K, evidência NÃO vista): The system answer says the information was not found, while the gold answer concludes that PepsiCo is not involved in material legal battles.
- **financebench_id_01328** (agentic, PEPSICO_2022_10K, evidência vista): The gold answer gives FY2022 restructuring costs of $411 million, while the system answer says $0.
- **financebench_id_01328** (simple, PEPSICO_2022_10K, evidência vista): The system answer concludes $0, while the gold answer is $411 million.
- **financebench_id_03620** (simple, PEPSICO_2022_10K, evidência vista): The gold answer is $9,068 million for unadjusted EBITDA less capex. The system answer does not provide this value and says capex cannot be determined.
- **financebench_id_00302** (simple, PFIZER_2021_10K, evidência NÃO vista): The gold answer says Pfizer's PPNE increased year over year; the system answer says it could not find the information.
- **financebench_id_02416** (agentic, PFIZER_2021_10K, evidência vista): The answer lists Arena instead of Therachon among its three main companies, though it mentions Therachon separately.
- **financebench_id_02416** (simple, PFIZER_2021_10K, evidência vista): It names Trillium and Array, but omits Therachon and substitutes Pharmacia.
- **financebench_id_00283** (agentic, Pfizer_2023Q2_10Q, evidência vista): The answer gives approximately $700 million in total separation costs (about $70 million remaining), not the expected $77.78 million.
- **financebench_id_00283** (simple, Pfizer_2023Q2_10Q, evidência vista): The system answer estimates $70 million, while the gold answer is $77.78 million; the difference exceeds the permitted rounding tolerance.
- **financebench_id_02419** (agentic, Pfizer_2023Q2_10Q, evidência vista): The gold answer says Pfizer is spinning off Upjohn, while the system answer says no and describes that spin-off as already completed.
- **financebench_id_02419** (simple, Pfizer_2023Q2_10Q, evidência vista): The gold answer says Pfizer is spinning off Upjohn, while the system answer says the Upjohn spin-off was completed in 2020 and no spin-off is underway.
- **financebench_id_00521** (agentic, ULTABEAUTY_2023_10K, evidência vista): It does not reliably cover both requested years: it says the cited filing excludes FY2023 and concludes there were no acquisitions in FY2022 and FY2021, rather than FY2023 and FY2022.
- **financebench_id_00521** (simple, ULTABEAUTY_2023_10K, evidência NÃO vista): The gold answer states that Ulta Beauty made no acquisitions in FY2023 or FY2022; the system answer says it could not find the information.
- **financebench_id_00603** (simple, ULTABEAUTY_2023Q4_EARNINGS, evidência vista): The gold answer attributes the inventory increase to opening 47 new stores, while the system answer says the filing gives no cause.
- **financebench_id_00605** (agentic, ULTABEAUTY_2023Q4_EARNINGS, evidência vista): The gold answer treats the period ended January 28, 2023 as FY2023 and gives 36%; the system answer says the information was not found.
- **financebench_id_02024** (simple, VERIZON_2021_10K, evidência NÃO vista): The answer says the information was not found, but the filing estimated $1,097 million in pension benefits and $862 million in health care and life insurance benefits for 2024.
- **financebench_id_00216** (agentic, VERIZON_2022_10K, evidência vista): Although it calculates the quick ratio as approximately 0.54, it does not conclude that Verizon's liquidity profile was unhealthy; it says the document does not permit that conclusion.
- **financebench_id_00216** (simple, VERIZON_2022_10K, evidência NÃO vista): The gold answer gives a quick ratio of approximately 0.54 and concludes Verizon’s liquidity profile was not healthy; the system answer says the ratio cannot be determined.
- **financebench_id_06247** (simple, WALMART_2018_10K, evidência vista): The gold answer gives FY2018 DPO as 42.69; the system answer incorrectly says it cannot be calculated.
- **financebench_id_04784** (simple, WALMART_2019_10K, evidência NÃO vista): The answer gives a -0.1 percentage-point change for Walmart U.S., while the gold answer is a +0.2% change for Walmart.
