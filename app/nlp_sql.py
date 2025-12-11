from app.llm.factory import get_llm_client


def natural_language_to_sql(question: str) -> str:
    """
    превращает вопрос на естественном языке в SQL
    """
    llm = get_llm_client()
    return llm.generate_sql(question)
