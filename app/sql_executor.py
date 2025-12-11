from app.core.db import execute_sql_and_get_number


async def run_sql_and_get_number(sql: str):
    """
    Асинхронный вызов выполнения SQL и получения одного ответа
    """
    return await execute_sql_and_get_number(sql)
