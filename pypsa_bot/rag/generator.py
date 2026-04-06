"""Groq LLM answer generator with fallback."""
from groq import Groq
from pypsa_bot.config import Config
from pypsa_bot.rag.prompts import SYSTEM_PROMPT, RAG_PROMPT_TEMPLATE
from pypsa_bot.rag.retriever import RetrievedDocument
from pypsa_bot.utils.logging import logger


class AnswerGenerator:
    def __init__(self, config: Config):
        self._client = Groq(api_key=config.groq_api_key)
        self._model_primary = config.groq_model_primary
        self._model_fallback = config.groq_model_fallback
        self._temperature = config.llm_temperature

    def _format_context(self, documents):
        parts = []
        for i, doc in enumerate(documents, 1):
            url = doc.metadata.get("url", "unknown")
            lib = doc.metadata.get("library", "unknown")
            parts.append(f"[Source {i}] ({lib}) {url}\n{doc.content}")
        return "\n\n---\n\n".join(parts)

    def generate(self, question, documents):
        context = self._format_context(documents)
        prompt = RAG_PROMPT_TEMPLATE.format(
            system_prompt=SYSTEM_PROMPT, context=context, question=question,
        )
        for model in [self._model_primary, self._model_fallback]:
            try:
                resp = self._client.chat.completions.create(
                    model=model, messages=[{"role": "user", "content": prompt}],
                    temperature=self._temperature, max_tokens=2048,
                )
                answer = resp.choices[0].message.content.strip()
                logger.info(f"Answer generated ({model}): {len(answer)} chars")
                return answer
            except Exception as e:
                logger.warning(f"Generation failed with {model}: {e}")
        return "⚠️ I couldn't generate an answer right now. Please try again."
