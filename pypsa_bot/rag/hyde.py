"""HyDE — Hypothetical Document Embeddings."""
from groq import Groq
from pypsa_bot.config import Config
from pypsa_bot.rag.prompts import HYDE_PROMPT_TEMPLATE
from pypsa_bot.utils.logging import logger


class HyDEGenerator:
    def __init__(self, config: Config):
        self._client = Groq(api_key=config.groq_api_key)
        self._model_primary = config.groq_model_primary
        self._model_fallback = config.groq_model_fallback

    def generate_hypothetical_answer(self, question: str) -> str:
        prompt = HYDE_PROMPT_TEMPLATE.format(question=question)
        for model in [self._model_primary, self._model_fallback]:
            try:
                resp = self._client.chat.completions.create(
                    model=model, messages=[{"role": "user", "content": prompt}],
                    temperature=0.5, max_tokens=300,
                )
                return resp.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"HyDE failed with {model}: {e}")
        logger.warning("All HyDE models failed, using original question")
        return question
