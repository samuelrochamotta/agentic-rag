"""Textos de instrução compartilhados entre o RAG simples e o agêntico.

A comparação só é justa se os dois sistemas recebem a MESMA regra de resposta
(citar páginas, admitir quando não encontrou). Por isso o texto mora aqui, num
lugar só, e os dois módulos o importam.
"""

# Frase exata que pedimos ao modelo quando não houver evidência. O avaliador
# procura variações dela para pontuar as perguntas da categoria "sem_resposta".
NOT_FOUND = "Não encontrei essa informação no documento"

ANSWER_RULES = f"""Regras para a resposta final:
- Responda em português, de forma direta e completa, usando APENAS informações do documento.
- Cite a página de cada afirmação no formato [p. N] (ex.: "O prazo é de 30 dias [p. 4].").
- Se o documento não trouxer evidência suficiente, responda exatamente: "{NOT_FOUND}." \
Não invente nem use conhecimento externo."""
