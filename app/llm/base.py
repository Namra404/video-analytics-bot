from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def generate_sql(self, question: str) -> str:
        """
        Абстрактный метод для генерации sql запроса
        """
        raise NotImplementedError
