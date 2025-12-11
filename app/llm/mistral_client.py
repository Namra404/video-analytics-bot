import logging
import re

from mistralai import Mistral

from app.core.config import settings
from app.llm.base import LLMClient
from app.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


SQL_BLOCK_RE = re.compile(r"```sql(.*?)```", re.DOTALL | re.IGNORECASE) # регулярка для вытаскивания SQL из ответа llm.


def _extract_sql(text: str) -> str:
    """
    Достаем чистый SQL из ответа llm.
    """
    m = SQL_BLOCK_RE.search(text or "")
    if not m:
        return text.strip()
    return m.group(1).strip()


class MistralLLMClient(LLMClient):
    """
    Реализация LLM-клиента для Mistral AI.
    """

    def __init__(self) -> None:
        if not settings.llm.mistral_api_key:
            raise RuntimeError("MISTRAL_API_KEY is not set")

        self.client = Mistral(api_key=settings.llm.mistral_api_key)
        self.model = settings.llm.mistral_model

    def generate_sql(self, question: str) -> str:

        resp = self.client.chat.complete(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0.0,
        )

        raw = resp.choices[0].message.content # строка с ответом
        sql = _extract_sql(raw)

        lowered = sql.lower()
        forbidden = ("insert", "update", "delete", "drop", "alter", "truncate")
        if any(word in lowered for word in forbidden):
            raise ValueError("Generated query contains forbidden keyword")

        logger.info("[Mistral] SQL: %s", sql.replace("\n", " "))
        return sql
