"""Checagens do avaliador que não precisam de API: citações e sem_resposta com juiz."""

from agentic_rag.evaluate import anchors, check_citations, cited_pages, grade

PAGES = {
    2: "Controladoria — responsável: Beatriz Moura Saldanha, ramal 2210.",
    6: "Em 14 de março de 2025 houve vazamento de amônia no NB-CD-04. O orçamento é R$ 4.870.000.",
}


def test_cited_pages_entende_listas_e_intervalos():
    assert cited_pages("3 e p. 6") == [3, 6]
    assert cited_pages("4-5") == [4, 5]
    assert cited_pages("12") == [12]


def test_anchors_pega_codigos_numeros_e_nomes_mas_nao_a_citacao():
    a = anchors("A gerente é Beatriz Moura Saldanha, do NB-CD-04, com R$ 4.870.000 [p. 6].")
    assert "Beatriz Moura Saldanha" in a and "NB-CD-04" in a and "4.870.000" in a
    assert "6" not in a


def test_citacao_certa_errada_e_valor_calculado():
    texto = ("O vazamento ocorreu no NB-CD-04 [p. 6]. "
             "A responsável é Beatriz Moura Saldanha [p. 6]. "
             "O total somado é 9.999.123 [p. 6].")
    c = check_citations(texto, PAGES)
    assert c["supported"] == 1           # NB-CD-04 está na p. 6
    assert c["elsewhere"] == 1           # o nome está na p. 2, não na 6
    assert c["derived"] == 1             # conta do modelo: não está no documento
    assert c["precision"] == 0.5
    assert "p. [2]" in c["issues"][0]


def test_numero_reformatado_ainda_bate_e_pagina_inexistente_conta():
    c = check_citations("O orçamento é de 4870000 reais [p. 6]. Ramal 2210 [p. 99].", PAGES)
    assert c["supported"] == 1
    assert c["bad_page"] == 1


class _Judge:
    def __init__(self, correct):
        self.correct = correct

    def chat(self, messages, response_format=None):
        class M:
            content = '{"correct": %s, "reason": "inventou o valor"}' % ("true" if self.correct else "false")
        return M()


def test_sem_resposta_exige_declarar_ausencia_e_nao_inventar():
    q = {"category": "sem_resposta", "question": "Qual a PLR?", "gold": "O manual não trata de PLR."}
    # Antes, só a regex: "não encontrei, mas é 5%" passava.
    assert grade(q, "Não encontrei essa informação no documento, mas a PLR é 5%.", _Judge(False))["correct"] is False
    assert grade(q, "Não encontrei essa informação no documento.", _Judge(True))["correct"] is True
    assert grade(q, "A PLR é 5%.", _Judge(True))["correct"] is False


def test_retry_repete_402_temporario(monkeypatch):
    from types import SimpleNamespace

    from openai import APIStatusError

    from agentic_rag import llm

    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            exc = APIStatusError.__new__(APIStatusError)  # sem rede: só os campos que o retry lê
            exc.status_code = 402
            exc.response = SimpleNamespace(headers={"retry-after": "1"})
            raise exc
        return "ok"

    assert llm._with_retry(flaky) == "ok" and calls["n"] == 3


def test_numero_curto_fora_da_pagina_nao_vira_citacao_errada():
    # "2210" está na p. 2; "40" não está na p. 6. Só o primeiro é citação errada.
    c = check_citations("O ramal é 2210 e a espera foi de 40 minutos [p. 6].", {**PAGES, 9: "limite de 40 itens"})
    assert c["elsewhere"] == 1 and c["derived"] == 1


def test_anos_e_secoes_nao_viram_citacao_errada():
    c = check_citations("Conforme a seção 4.4, em 2024 [p. 6].", {6: "nada", 7: "4.4 Seção; ano 2024"})
    assert c["elsewhere"] == 0 and c["derived"] == 2


def test_declaracao_de_ausencia_com_markdown():
    from agentic_rag.evaluate import declares_not_found
    assert declares_not_found("Ou seja, o documento **não informa** o número de patrimônio.")
    assert declares_not_found("Esse dado não consta no manual.")
