"""Textos de instrução compartilhados entre o RAG simples e o agêntico.

A comparação só é justa se os dois sistemas recebem a MESMA regra de resposta
(citar páginas, admitir quando não encontrou). Por isso o texto mora aqui, num
lugar só, e os dois módulos o importam.
"""

# Frase exata que pedimos quando nenhuma parte da pergunta puder ser respondida. O avaliador
# procura variações dela para pontuar as perguntas da categoria "sem_resposta".
NOT_FOUND = "Não encontrei essa informação no documento"

ANSWER_RULES = f"""Regras para a resposta final:
- Responda em português, de forma direta e completa, usando APENAS informações do documento.
- Cite a página de cada afirmação no formato [p. N] (ex.: "O prazo é de 30 dias [p. 4].").
- Se houver evidência para apenas parte da pergunta, responda essa parte e indique \
explicitamente quais dados não encontrou no documento. Não omita informações disponíveis \
porque outro dado está ausente; não calcule valores quando faltarem dados necessários.
- Somente se nenhuma parte da pergunta puder ser respondida com as evidências disponíveis, \
responda exatamente: "{NOT_FOUND}."
- Não invente nem use conhecimento externo."""
