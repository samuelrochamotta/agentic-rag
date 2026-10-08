"""Gera data/manual_simulado.pdf — manual corporativo FICTÍCIO usado na avaliação.

O conteúdo foi desenhado de propósito para expor fraquezas do RAG simples
(embed da pergunta -> top-5 chunks por cosseno -> responde):

- multi_hop: fatos que só se completam combinando páginas distantes
  (gerente citado na p.3, orçamento na p.13 identificado só pelo nome da cidade);
- codigo_exato: códigos parecidos (ACX-7714, ACX-7417, ACX-7741...) e o código
  certo aparece uma única vez, num trecho de assunto diferente;
- agregacao: incidentes classe 3 de 2024 e multas espalhados por várias seções,
  sem total consolidado em lugar nenhum;
- distrator: seções quase duplicadas (reembolso 2023 x 2025, SLA 2024 x 2025,
  frota Sul x Sudeste);
- referencia_secao: perguntas do tipo "o que diz a seção 7.3?" / "página 15";
- sem_resposta: temas que o manual deliberadamente NÃO cobre.

Cada página é montada explicitamente e separada por PageBreak, para que a
numeração seja determinística. Fonte Helvetica (padrão) para extração limpa.

Uso: uv run python data/gerar_pdf.py
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

SAIDA = Path(__file__).parent / "manual_simulado.pdf"
TITULO_DOC = "Nébula Logística S.A. — Manual de Operações e Políticas"

# ---------------------------------------------------------------------------
# Estilos (todos em Helvetica, a fonte padrão do PDF)
# ---------------------------------------------------------------------------
CORPO = ParagraphStyle("corpo", fontName="Helvetica", fontSize=10, leading=14, spaceAfter=7)
CAPA = ParagraphStyle("capa", fontName="Helvetica-Bold", fontSize=20, leading=26, spaceAfter=10)
SUBCAPA = ParagraphStyle("subcapa", fontName="Helvetica", fontSize=12, leading=16, spaceAfter=14)
CAPITULO = ParagraphStyle(
    "capitulo", fontName="Helvetica-Bold", fontSize=14, leading=18, spaceBefore=8, spaceAfter=8
)
SECAO = ParagraphStyle(
    "secao", fontName="Helvetica-Bold", fontSize=11, leading=15, spaceBefore=6, spaceAfter=5
)


def p(texto: str) -> Paragraph:
    """Parágrafo de texto corrido."""
    return Paragraph(texto, CORPO)


def cap(texto: str) -> Paragraph:
    """Título de capítulo (ex.: '6 Políticas Financeiras')."""
    return Paragraph(texto, CAPITULO)


def sec(texto: str) -> Paragraph:
    """Título de seção (ex.: '6.2 Política de Reembolso...')."""
    return Paragraph(texto, SECAO)


def tabela(linhas: list[list[str]], larguras: list[float]) -> Table:
    """Tabela simples com cabeçalho em negrito. A primeira coluna nunca é numérica,
    para não confundir o detector de cabeçalhos do chunker."""
    t = Table(linhas, colWidths=[w * cm for w in larguras], hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF4")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return t


# ---------------------------------------------------------------------------
# Conteúdo, página a página
# ---------------------------------------------------------------------------
def pagina_01():
    return [
        Paragraph("Manual de Operações e Políticas", CAPA),
        Paragraph("Nébula Logística S.A. — documento interno, edição de março de 2025", SUBCAPA),
        cap("1 Apresentação"),
        sec("1.1 Sobre a empresa"),
        p(
            "A Nébula Logística S.A. foi fundada em 2009, na cidade de Curitiba (PR), onde mantém "
            "sua sede administrativa até hoje. A empresa nasceu como transportadora regional de "
            "cargas fracionadas e, ao longo de pouco mais de uma década, passou a operar uma rede "
            "própria de centros de distribuição, frota rodoviária e serviços de armazenagem com "
            "controle de temperatura para clientes dos setores farmacêutico, alimentício e de "
            "bens de consumo."
        ),
        p(
            "Hoje a companhia atende clientes nas regiões Sul, Sudeste e Nordeste, com operação "
            "integrada entre transporte, armazenagem e gestão de estoques. A Nébula é uma "
            "sociedade anônima de capital fechado e possui certificações de boas práticas de "
            "armazenagem e distribuição exigidas pelos seus clientes do setor de saúde."
        ),
        sec("1.2 Objetivo e abrangência"),
        p(
            "Este manual consolida as regras operacionais, as políticas corporativas e os "
            "procedimentos de segurança aplicáveis a todos os colaboradores, prestadores de "
            "serviço e fornecedores que atuam nas instalações da Nébula. Ele substitui as "
            "circulares avulsas publicadas até dezembro de 2024."
        ),
        p(
            "Em caso de conflito entre este manual e um contrato específico com cliente, "
            "prevalece o contrato, desde que aprovado pela Diretoria Jurídica."
        ),
        sec("1.3 Como usar este manual"),
        p(
            "O documento está organizado em capítulos e seções numeradas. Algumas políticas "
            "foram revisadas recentemente; nesses casos, a versão anterior foi mantida no texto "
            "apenas para fins de histórico e está sempre identificada como revogada ou "
            "substituída. Somente a versão marcada como vigente deve ser aplicada."
        ),
        p(
            "Os registros de ocorrências citados ao longo do manual são lançados uma única vez, "
            "na área responsável pela operação em que o evento aconteceu. Por isso, cada "
            "ocorrência aparece em apenas uma seção, e não há duplicidade entre áreas. Os "
            "anexos ao final complementam as seções e têm a mesma validade do corpo do texto."
        ),
    ]


def pagina_02():
    return [
        cap("2 Estrutura Organizacional"),
        sec("2.1 Diretoria"),
        p(
            "A Nébula é administrada por uma Diretoria Executiva composta pelo Diretor-Presidente, "
            "pela Diretora de Operações, pelo Diretor Financeiro e pela Diretora Jurídica. A "
            "Diretoria se reúne quinzenalmente e responde ao Conselho de Administração, que se "
            "reúne a cada trimestre para aprovar orçamento, investimentos e metas."
        ),
        p(
            "Os centros de distribuição respondem diretamente à Diretoria de Operações. As áreas "
            "corporativas listadas a seguir dão suporte às unidades e são responsáveis pelas "
            "políticas descritas nos capítulos seguintes."
        ),
        sec("2.2 Áreas corporativas e responsáveis"),
        p("A tabela abaixo indica o responsável por cada área corporativa e o ramal interno de contato."),
        tabela(
            [
                ["Área corporativa", "Responsável", "Ramal"],
                ["Controladoria", "Beatriz Moura Saldanha", "2210"],
                ["Suprimentos Estratégicos", "Otávio Ramalho Prates", "3528"],
                ["Saúde e Segurança do Trabalho", "Clara Nogueira Ventura", "2645"],
                ["Gestão de Pessoas", "Henrique Lacerda Pimentel", "2731"],
                ["Qualidade e Cadeia Fria", "Silvana Torres Aguiar", "3302"],
                ["Tecnologia da Informação", "Diego Amaral Fontes", "3190"],
                ["Fiscal e Tributário", "Patrícia Rezende Couto", "2488"],
            ],
            [6.5, 6.0, 2.0],
        ),
        Spacer(1, 10),
        sec("2.3 Alçadas de aprovação"),
        p(
            "Despesas operacionais de até R$ 20.000 podem ser aprovadas pelo gerente da unidade. "
            "Valores entre R$ 20.000 e R$ 150.000 exigem aprovação conjunta do gerente da unidade "
            "e da Controladoria. Acima de R$ 150.000, a aprovação cabe à Diretoria Executiva, e "
            "investimentos acima de R$ 1.000.000 dependem do Conselho de Administração."
        ),
        p(
            "Nenhum colaborador pode aprovar despesa em benefício próprio ou de parente até o "
            "segundo grau. Nesses casos, a aprovação sobe automaticamente um nível na alçada."
        ),
    ]


def pagina_03():
    return [
        cap("3 Rede de Centros de Distribuição"),
        sec("3.1 Unidades em operação"),
        p(
            "A rede da Nébula é formada por seis centros de distribuição (CDs). Cada unidade "
            "recebe um código interno usado em sistemas, etiquetas e relatórios de ocorrência."
        ),
        tabela(
            [
                ["Código", "Cidade", "UF", "Área coberta (m²)", "Inauguração"],
                ["NB-CD-01", "Curitiba", "PR", "18.400", "2010"],
                ["NB-CD-02", "Campinas", "SP", "22.900", "2013"],
                ["NB-CD-03", "Contagem", "MG", "14.200", "2016"],
                ["NB-CD-04", "Joinville", "SC", "11.700", "2018"],
                ["NB-CD-05", "Canoas", "RS", "12.300", "2020"],
                ["NB-CD-06", "Recife", "PE", "9.800", "2023"],
            ],
            [2.6, 3.4, 1.4, 3.2, 2.8],
        ),
        Spacer(1, 10),
        sec("3.2 Gestão das unidades"),
        p(
            "Cada centro de distribuição tem um gerente de unidade, responsável por pessoas, "
            "segurança, indicadores de serviço e execução do orçamento local. A unidade de "
            "Curitiba é gerida por Fernando Guedes Albuquerque, que também acumula a coordenação "
            "de projetos de melhoria contínua da rede."
        ),
        p(
            "Em Campinas, a gerência está a cargo de Rafael Bittencourt Lins desde a reforma do "
            "galpão principal. A unidade de Contagem é conduzida por Juliana Paes Carvalho, e a "
            "de Joinville, por Mariana Teixeira Lopes. Em Canoas, o gerente é Eduardo Siqueira "
            "Brandt, e a unidade de Recife, a mais recente, é liderada por Tiago Falcão Medeiros."
        ),
        p(
            "Os gerentes de unidade se reúnem mensalmente com a Diretoria de Operações para a "
            "revisão de indicadores. Substituições temporárias de gerentes devem ser comunicadas "
            "à Gestão de Pessoas com antecedência mínima de cinco dias úteis."
        ),
    ]


def pagina_04():
    return [
        sec("3.3 Frota própria — Região Sul"),
        p(
            "A frota própria da Região Sul atende as unidades de Curitiba, Joinville e Canoas e é "
            "composta por 48 caminhões e 12 veículos urbanos de carga (VUCs). A idade média dos "
            "veículos é de 4,1 anos, e a renovação segue o plano quinquenal aprovado pelo "
            "Conselho de Administração."
        ),
        p(
            "Todos os veículos da Região Sul possuem rastreamento por satélite, telemetria de "
            "condução e sensores de temperatura nos baús refrigerados. A manutenção preventiva "
            "é feita a cada 20.000 km em oficina credenciada. No ano de 2024, a operação de "
            "frota da Região Sul registrou 2 incidentes classe 3, ambos relacionados a "
            "tombamento de carga em rodovia, sem vítimas."
        ),
        sec("3.4 Frota própria — Região Sudeste"),
        p(
            "A frota própria da Região Sudeste atende as unidades de Campinas e Contagem e é "
            "composta por 73 caminhões e 21 veículos urbanos de carga (VUCs). A idade média dos "
            "veículos é de 3,6 anos, e a renovação segue o plano quinquenal aprovado pelo "
            "Conselho de Administração."
        ),
        p(
            "Todos os veículos da Região Sudeste possuem rastreamento por satélite, telemetria de "
            "condução e sensores de temperatura nos baús refrigerados. A manutenção preventiva "
            "é feita a cada 20.000 km em oficina credenciada. No ano de 2024, a operação de "
            "frota da Região Sudeste registrou 4 incidentes classe 3, três deles por colisão "
            "traseira em perímetro urbano e um por falha de freio em descida de serra."
        ),
        p(
            "Motoristas das duas regiões seguem as mesmas regras de jornada, descanso e "
            "direção defensiva. A troca de veículos entre regiões só é permitida com autorização "
            "da Diretoria de Operações e registro no sistema de gestão de frota."
        ),
    ]


def pagina_05():
    return [
        sec("3.5 Janelas de recebimento e expedição"),
        p(
            "O recebimento de mercadorias nos centros de distribuição ocorre em janelas "
            "agendadas pelo portal de transportadoras. Cargas sem agendamento podem ser "
            "recusadas na portaria. A expedição prioriza pedidos de clientes com contrato de "
            "nível de serviço diferenciado e cargas refrigeradas."
        ),
        p(
            "Veículos que chegarem com mais de duas horas de atraso em relação à janela "
            "agendada perdem a prioridade e são reencaixados conforme a disponibilidade de "
            "docas. As docas refrigeradas não podem permanecer abertas por mais de quinze "
            "minutos sem cortina de ar acionada."
        ),
        cap("4 Segurança Operacional"),
        sec("4.1 Classificação de incidentes"),
        p(
            "Todo evento que cause ou possa causar dano a pessoas, cargas, equipamentos ou ao "
            "meio ambiente deve ser registrado e classificado em uma das três classes abaixo."
        ),
        p(
            "<b>Classe 1</b> — ocorrência leve, sem afastamento e sem perda de carga, como "
            "pequenas avarias em embalagens ou quase-acidentes. <b>Classe 2</b> — ocorrência "
            "moderada, com afastamento de até quinze dias, perda parcial de carga ou dano a "
            "equipamento que exija reparo. <b>Classe 3</b> — ocorrência grave, com afastamento "
            "superior a quinze dias, perda total de carga, vazamento de produto perigoso, "
            "acidente rodoviário com tombamento ou colisão, ou qualquer evento com repercussão "
            "externa relevante."
        ),
        p(
            "A classificação inicial é feita pelo líder do turno e confirmada pela área de Saúde e "
            "Segurança do Trabalho em até 24 horas. Em caso de dúvida, adota-se sempre a classe "
            "mais grave até a conclusão da análise."
        ),
    ]


def pagina_06():
    return [
        sec("4.2 Resposta a incidentes"),
        p(
            "Incidentes classe 1 são tratados pelo próprio turno e registrados no sistema até o "
            "fim do expediente. Incidentes classe 2 exigem abertura de análise de causa em até "
            "três dias úteis e comunicação ao gerente da unidade."
        ),
        p(
            "Para incidentes classe 3, o gerente da unidade deve notificar a Diretoria de "
            "Operações e a área de Saúde e Segurança do Trabalho em até duas horas após o "
            "conhecimento do fato. Um comitê de crise é instalado no mesmo dia, com participação "
            "obrigatória da Diretoria Jurídica, e a comunicação com clientes e imprensa fica "
            "centralizada na Diretoria Executiva."
        ),
        sec("4.3 Ocorrências relevantes de 2025"),
        p(
            "Em 14 de março de 2025, foi registrado um vazamento de amônia no sistema de "
            "refrigeração da câmara fria principal do NB-CD-04. A área foi evacuada em onze "
            "minutos, dois colaboradores receberam atendimento ambulatorial e não houve perda de "
            "carga. A ocorrência foi classificada como classe 3 em razão do envolvimento de "
            "produto perigoso, e a câmara permaneceu interditada por nove dias."
        ),
        p(
            "Como consequência, todas as unidades com refrigeração por amônia passaram a ter "
            "inspeção semestral obrigatória das tubulações e simulado anual de evacuação. A "
            "análise de causa apontou corrosão em uma válvula de alívio instalada fora da "
            "especificação do fabricante."
        ),
        p(
            "Outras ocorrências de 2025 foram classificadas como classe 1 ou classe 2 e constam "
            "apenas nos relatórios mensais das unidades, não sendo reproduzidas neste manual."
        ),
    ]


def pagina_07():
    return [
        sec("4.4 Equipamentos de movimentação"),
        p(
            "As transpaleteiras elétricas utilizadas nos centros de distribuição são identificadas "
            "por um código de patrimônio iniciado por ACX. A tabela abaixo apresenta os modelos "
            "padronizados na rede e a respectiva capacidade nominal de carga."
        ),
        tabela(
            [
                ["Código", "Modelo", "Capacidade nominal", "Uso principal"],
                ["ACX-7714", "Transpaleteira elétrica de patolas longas", "2,5 t", "Docas secas"],
                ["ACX-7417", "Transpaleteira elétrica compacta", "1,8 t", "Separação fracionada"],
                ["ACX-7147", "Transpaleteira elétrica com plataforma", "3,0 t", "Cross-docking"],
                ["ACX-7471", "Transpaleteira elétrica para câmara fria", "2,0 t", "Câmaras frias"],
            ],
            [2.4, 6.6, 3.2, 3.6],
        ),
        Spacer(1, 10),
        p(
            "É proibido operar qualquer transpaleteira acima da capacidade nominal indicada na "
            "plaqueta do equipamento. Apenas operadores com treinamento válido podem conduzir "
            "os equipamentos, e a checagem pré-uso deve ser registrada no início de cada turno."
        ),
        sec("4.5 Equipamentos de proteção individual"),
        p(
            "O uso de calçado de segurança, colete refletivo e luvas é obrigatório em todas as "
            "áreas operacionais. Nas câmaras frias, acrescentam-se japona térmica, calça térmica "
            "e capuz, e a permanência contínua é limitada a quarenta e cinco minutos, seguida de "
            "pausa de recuperação térmica de quinze minutos em ambiente aquecido."
        ),
        p(
            "Os equipamentos de proteção são fornecidos gratuitamente e substituídos sempre que "
            "apresentarem desgaste. A recusa injustificada de uso é considerada falta grave."
        ),
    ]


def pagina_08():
    return [
        cap("5 Pessoas e Rotinas de Trabalho"),
        sec("5.1 Jornada e escalas"),
        p(
            "A jornada padrão dos colaboradores administrativos e operacionais é de 44 horas "
            "semanais, distribuídas de segunda a sábado conforme a escala de cada unidade. As "
            "operações noturnas seguem escala de revezamento definida em acordo coletivo, com "
            "adicional noturno pago conforme a legislação."
        ),
        p(
            "O controle de ponto é eletrônico e obrigatório para todos os cargos operacionais. "
            "Horas extras precisam de autorização prévia do líder imediato e são compensadas por "
            "banco de horas em até seis meses."
        ),
        sec("5.2 Férias e afastamentos"),
        p(
            "O pedido de férias deve ser registrado no sistema de Gestão de Pessoas com "
            "antecedência mínima de trinta dias. O fracionamento em até três períodos é "
            "permitido, desde que um deles tenha pelo menos quatorze dias corridos."
        ),
        p(
            "Afastamentos por motivo de saúde devem ser comunicados ao líder imediato no mesmo "
            "dia, e o atestado deve ser entregue em até 48 horas."
        ),
        sec("5.3 Treinamentos obrigatórios"),
        p(
            "Todo colaborador operacional passa por integração de segurança antes do primeiro "
            "turno. Operadores de equipamentos de movimentação precisam de certificação "
            "específica, renovada a cada dois anos. Colaboradores das equipes de inventário "
            "recebem treinamento no protocolo de contagem cíclica descrito na seção 10.1."
        ),
        p(
            "Os treinamentos são registrados na plataforma de ensino corporativa, e o gerente da "
            "unidade é responsável por garantir que nenhum colaborador atue com certificação "
            "vencida."
        ),
    ]


def pagina_09():
    return [
        cap("6 Políticas Financeiras"),
        sec("6.1 Política de Reembolso de Despesas — versão 2023 (revogada)"),
        p(
            "<i>Texto mantido apenas para histórico; revogado em 1º de janeiro de 2025.</i> "
            "Despesas de viagem e de representação realizadas a serviço da empresa podem ser "
            "reembolsadas mediante apresentação de nota fiscal ou recibo válido. O pedido de "
            "reembolso deve ser registrado no sistema financeiro em até 30 dias corridos após a "
            "data da despesa, acompanhado dos comprovantes digitalizados."
        ),
        p(
            "O valor máximo reembolsável para alimentação é de R$ 85 por dia de viagem. "
            "Despesas com bebidas alcoólicas não são reembolsáveis. O deslocamento com veículo "
            "próprio é reembolsado por quilômetro rodado, conforme tabela da Controladoria. "
            "Pedidos fora do prazo serão recusados, salvo autorização do gerente da unidade."
        ),
        sec("6.2 Política de Reembolso de Despesas — versão 2025 (vigente)"),
        p(
            "<i>Em vigor desde 1º de janeiro de 2025.</i> Despesas de viagem e de representação "
            "realizadas a serviço da empresa podem ser reembolsadas mediante apresentação de nota "
            "fiscal ou recibo válido. O pedido de reembolso deve ser registrado no sistema "
            "financeiro em até 45 dias corridos após a data da despesa, acompanhado dos "
            "comprovantes digitalizados."
        ),
        p(
            "O valor máximo reembolsável para alimentação é de R$ 120 por dia de viagem. "
            "Despesas com bebidas alcoólicas não são reembolsáveis. O deslocamento com veículo "
            "próprio é reembolsado por quilômetro rodado, conforme tabela da Controladoria. "
            "Pedidos fora do prazo serão recusados, salvo autorização do gerente da unidade."
        ),
    ]


def pagina_10():
    return [
        sec("6.3 Viagens corporativas"),
        p(
            "Viagens a serviço devem ser solicitadas com antecedência mínima de sete dias pelo "
            "portal de viagens, que concentra a emissão de passagens e as reservas de hotel em "
            "agência credenciada. Viagens internacionais exigem aprovação da Diretoria Executiva."
        ),
        sec("6.4 Prazos de entrega ao cliente — revisão 2024 (substituída)"),
        p(
            "<i>Revisão substituída; mantida apenas para histórico.</i> O prazo máximo de entrega "
            "para destinos em capitais atendidas pela rede é de 72 horas a partir da coleta. Para "
            "cidades do interior, o prazo é de cinco dias úteis, e para áreas de difícil acesso "
            "o prazo é combinado caso a caso com o cliente."
        ),
        sec("6.5 Prazos de entrega ao cliente — revisão 2025 (vigente)"),
        p(
            "<i>Revisão vigente.</i> O prazo máximo de entrega para destinos em capitais "
            "atendidas pela rede é de 54 horas a partir da coleta. Para cidades do interior, o "
            "prazo é de quatro dias úteis, e para áreas de difícil acesso o prazo é combinado "
            "caso a caso com o cliente."
        ),
        sec("6.6 Penalidade contratual por atraso"),
        p(
            "Quando um atraso de entrega for causado por falha da própria Nébula e ultrapassar em "
            "mais de 24 horas o prazo vigente, aplica-se ao centro de distribuição responsável "
            "uma multa interna de R$ 2.500 por ocorrência, debitada do orçamento da unidade. Os "
            "valores arrecadados alimentam o fundo de melhoria de nível de serviço."
        ),
        p(
            "Atrasos causados por eventos climáticos, bloqueios de rodovia ou indisponibilidade "
            "do destinatário não geram penalidade, desde que devidamente documentados no "
            "sistema de rastreamento."
        ),
    ]


def pagina_11():
    return [
        cap("7 Gestão de Fornecedores"),
        sec("7.1 Homologação"),
        p(
            "Nenhum fornecedor pode ser contratado sem homologação prévia. O processo é conduzido "
            "pela área de Suprimentos Estratégicos, que verifica regularidade fiscal, capacidade "
            "técnica, referências comerciais e aderência às exigências de segurança e de "
            "qualidade da Nébula."
        ),
        p(
            "Fornecedores de serviços críticos, como transporte terceirizado, manutenção de "
            "sistemas de refrigeração e segurança patrimonial, passam também por visita técnica "
            "antes da aprovação."
        ),
        sec("7.2 Avaliação periódica"),
        p(
            "Os fornecedores homologados são avaliados a cada trimestre em uma escala de zero a "
            "dez, considerando pontualidade, qualidade, conformidade documental e atendimento. "
            "O resultado é compartilhado com o fornecedor, que pode apresentar plano de ação "
            "corretivo em até quinze dias."
        ),
        sec("7.3 Descredenciamento"),
        p(
            "O fornecedor que obtiver nota inferior a 6,0 em duas avaliações trimestrais "
            "consecutivas será descredenciado. A Nébula comunicará a decisão por escrito e "
            "concederá aviso prévio de 75 dias para a transição dos serviços, período em que o "
            "contrato continua plenamente válido."
        ),
        p(
            "Um fornecedor descredenciado só pode solicitar nova homologação após doze meses da "
            "data da comunicação. Casos de fraude, corrupção ou violação grave de segurança "
            "levam ao descredenciamento imediato, sem aviso prévio."
        ),
    ]


def pagina_12():
    return [
        cap("8 Cadeia Fria"),
        sec("8.1 Faixas de temperatura"),
        p(
            "Produtos refrigerados devem ser mantidos entre 2 °C e 8 °C durante toda a "
            "armazenagem e o transporte. Produtos congelados devem permanecer a menos dezoito "
            "graus Celsius ou abaixo disso. Os sensores das câmaras e dos baús registram a "
            "temperatura a cada cinco minutos, e os registros são guardados por cinco anos."
        ),
        sec("8.2 Desvios de temperatura"),
        p(
            "Qualquer leitura fora da faixa por mais de trinta minutos configura desvio e deve "
            "ser tratada pela área de Qualidade e Cadeia Fria. Quando o desvio for causado por "
            "falha operacional evitável, como porta de câmara deixada aberta ou equipamento "
            "desligado sem autorização, aplica-se à unidade uma multa interna de R$ 7.800 por "
            "evento, além da análise de causa obrigatória."
        ),
        p(
            "Perdas físicas por avaria durante a movimentação interna também são acompanhadas "
            "pela Qualidade: conforme o Anexo C-3, a perda máxima aceitável por avaria em "
            "manuseio, por unidade e por mês, é de 0,8% do volume movimentado. Acima desse "
            "limite, a unidade apresenta plano de ação à Diretoria de Operações."
        ),
        p(
            "Em 2024, a operação de cadeia fria registrou 1 incidente classe 3, com perda total "
            "de um lote de insumos hospitalares após pane elétrica prolongada em uma câmara."
        ),
        sec("8.3 Cargas com lacre violado"),
        p(
            "Cargas recebidas com lacre rompido, divergente da nota fiscal ou com sinais de "
            "violação seguem o PRT-0093: a carga é segregada em quarentena na doca de retenção, "
            "fotografada e mantida intacta por até 72 horas, aguardando a vistoria do cliente e da "
            "seguradora. Nenhum volume pode ser aberto ou movimentado durante esse período sem "
            "autorização da Qualidade."
        ),
        p(
            "Encerrada a vistoria, a carga é liberada, devolvida ao remetente ou descartada, "
            "conforme a decisão registrada pelo cliente no portal."
        ),
    ]


def pagina_13():
    return [
        cap("9 Orçamento 2025"),
        sec("9.1 Orçamento operacional por unidade"),
        p(
            "O orçamento operacional anual de 2025 foi aprovado pelo Conselho de Administração em "
            "dezembro de 2024. Os valores abaixo cobrem pessoal, utilidades, manutenção predial e "
            "materiais de consumo de cada centro de distribuição, e não incluem frota nem "
            "investimentos."
        ),
        tabela(
            [
                ["Unidade", "Orçamento operacional 2025", "Variação sobre 2024"],
                ["CD Curitiba", "R$ 5.120.000", "+4,0%"],
                ["CD Campinas", "R$ 4.870.000", "+6,5%"],
                ["CD Contagem", "R$ 3.940.000", "+3,1%"],
                ["CD Joinville", "R$ 3.210.000", "+2,8%"],
                ["CD Canoas", "R$ 3.360.000", "+3,4%"],
                ["CD Recife", "R$ 2.750.000", "+11,2%"],
            ],
            [4.5, 5.5, 4.5],
        ),
        Spacer(1, 10),
        p(
            "Remanejamentos entre linhas do orçamento de uma mesma unidade podem ser feitos pelo "
            "gerente, desde que comunicados à Controladoria. Remanejamentos entre unidades "
            "exigem aprovação da Diretoria Financeira."
        ),
        sec("9.2 Investimentos"),
        p(
            "O plano de investimentos de 2025 prioriza a modernização dos sistemas de "
            "refrigeração, a ampliação da área de armazenagem em Recife e a renovação parcial da "
            "frota. Cada projeto deve ter estudo de viabilidade aprovado pela Controladoria antes "
            "da liberação de recursos."
        ),
    ]


def pagina_14():
    return [
        cap("10 Armazenagem e Inventário"),
        sec("10.1 Inventário e devoluções"),
        p(
            "Todas as unidades realizam contagem cíclica semanal das posições de maior giro, "
            "conforme o PRT-0039, e inventário geral uma vez por ano. As devoluções de clientes "
            "seguem o PRT-0930, com conferência item a item e registro fotográfico antes da "
            "reintegração ao estoque."
        ),
        p(
            "No ano de 2024, a operação de armazenagem registrou 3 incidentes classe 3, todos "
            "decorrentes de queda de paletes das estruturas porta-paletes durante a "
            "movimentação, com perda total das cargas envolvidas."
        ),
        sec("10.2 Manutenção de equipamentos"),
        p(
            "A manutenção preventiva dos equipamentos de movimentação é feita mensalmente por "
            "empresa homologada. Em 2024, a unidade de Joinville recebeu uma transpaleteira de "
            "modelo especial, registrada sob o patrimônio ACX-7741, com capacidade nominal de "
            "2,7 t e garfos reforçados para bobinas. Esse equipamento ainda não consta da "
            "tabela padronizada da rede e só pode ser operado por condutores certificados pela "
            "própria fabricante."
        ),
        sec("10.3 Descarte de resíduos"),
        p(
            "Resíduos de embalagens, paletes danificados e materiais contaminados devem ser "
            "segregados e destinados exclusivamente a empresas licenciadas. O descarte irregular "
            "de resíduos, como o envio de material contaminado junto com recicláveis, sujeita a "
            "unidade a uma multa interna de R$ 4.200 por ocorrência, independentemente de "
            "eventuais sanções ambientais externas."
        ),
    ]


def pagina_15():
    return [
        cap("11 Conformidade Fiscal e Documental"),
        sec("11.1 Documentos de transporte"),
        p(
            "Nenhum veículo pode sair de um centro de distribuição sem o manifesto eletrônico, os "
            "conhecimentos de transporte e as notas fiscais correspondentes. A conferência "
            "documental é feita na portaria e registrada no sistema de expedição."
        ),
        p(
            "A emissão de documento fiscal com dados incorretos, ou a saída de veículo sem a "
            "documentação completa, gera para a unidade uma multa interna de R$ 1.350 por "
            "documento, além da obrigação de regularização junto à área Fiscal e Tributária no "
            "mesmo dia."
        ),
        sec("11.2 Guarda de documentos"),
        p(
            "Os documentos fiscais e de transporte são arquivados eletronicamente pelo prazo "
            "legal. Vias físicas assinadas por destinatários devem ser digitalizadas em até "
            "cinco dias úteis."
        ),
        cap("12 Expansão Nordeste"),
        sec("12.1 Operação regional"),
        p(
            "Com a inauguração da unidade de Recife, a Nébula passou a atender diretamente "
            "Pernambuco, Paraíba e Alagoas. A frota própria da Região Nordeste é composta por 29 "
            "caminhões e 8 veículos urbanos de carga (VUCs), com rotas diárias entre Recife, "
            "João Pessoa e Maceió."
        ),
        p(
            "No ano de 2024, a operação regional do Nordeste registrou 2 incidentes classe 3, "
            "ambos roubos de carga em rodovia, que levaram à adoção de escolta armada nas rotas "
            "noturnas de maior risco."
        ),
    ]


def pagina_16():
    return [
        cap("13 Disposições Finais"),
        sec("13.1 Revisão do manual"),
        p(
            "Este manual é revisado anualmente pela Diretoria Executiva. Sugestões de melhoria "
            "podem ser enviadas por qualquer colaborador à área de Qualidade e Cadeia Fria, que "
            "consolida as propostas para a revisão seguinte."
        ),
        cap("14 Anexos"),
        p(
            "<b>Anexo C-1 — Checklist de abertura de doca.</b> Lista de verificação a ser "
            "preenchida pelo conferente antes da abertura de cada doca, incluindo nivelador, "
            "iluminação, cortina de ar e sinalização de piso."
        ),
        p(
            "<b>Anexo C-2 — Tolerância de divergência de inventário.</b> Define que a "
            "divergência máxima aceitável entre estoque físico e estoque sistêmico, por unidade "
            "e por mês, é de 1,5% do número de posições contadas."
        ),
        p(
            "<b>Anexo C-3 — Tolerância de avaria no manuseio.</b> Limite mensal de perdas por "
            "avaria em manuseio interno; o percentual e as regras de aplicação estão descritos na "
            "seção 8.2."
        ),
        p(
            "<b>Anexo C-4 — Tolerância de atraso de expedição.</b> Define que o percentual máximo "
            "aceitável de pedidos expedidos fora da janela programada, por unidade e por mês, é "
            "de 2,0% do total de pedidos."
        ),
        p(
            "<b>Anexo C-5 — Modelo de relatório de incidente.</b> Formulário padrão para "
            "registro de incidentes, com campos de classificação, descrição, causas imediatas, "
            "ações de contenção e responsáveis."
        ),
    ]


PAGINAS = [
    pagina_01, pagina_02, pagina_03, pagina_04, pagina_05, pagina_06, pagina_07, pagina_08,
    pagina_09, pagina_10, pagina_11, pagina_12, pagina_13, pagina_14, pagina_15, pagina_16,
]


def rodape(canvas, doc):
    """Cabeçalho e rodapé de cada página. Nenhuma linha começa com dígito,
    para não ser confundida com título de seção pelo chunker."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawString(2 * cm, A4[1] - 1.2 * cm, TITULO_DOC)
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page} de {len(PAGINAS)}")
    canvas.restoreState()


def main() -> None:
    doc = SimpleDocTemplate(
        str(SAIDA),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Manual de Operações e Políticas — Nébula Logística S.A. (fictício)",
        author="Nébula Logística S.A. (empresa fictícia)",
    )
    historia = []
    for i, montar in enumerate(PAGINAS):
        historia.extend(montar())
        if i < len(PAGINAS) - 1:
            historia.append(PageBreak())
    doc.build(historia, onFirstPage=rodape, onLaterPages=rodape)
    print(f"PDF gerado em {SAIDA}")


if __name__ == "__main__":
    main()
