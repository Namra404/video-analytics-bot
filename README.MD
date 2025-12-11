# Telegram-бот для аналитики по видео

Бот отвечает на вопросы на естественном русском языке и считает метрики по базе
статистики видео (итоговые данные + почасовые снапшоты).  
На вход — текстовый запрос, на выход — **одно число**.

---

## 1. Подготовка

### 1.1. Клонирование репозитория

```bash
  git clone https://github.com/Namra404/video-analytics-bot.git
```
### 1.2. В корне проекта должна лежать папка data с файлом:
```
  data/videos.json
```
## 2. Переменные окружения
### Создайте файл .env в корне проекта:
```
# Postgres
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=video_analytics
DB_SHOW_QUERY=false

# Telegram
TELEGRAM_BOT_TOKEN=1234567890:XXXXXXXXXXXXXX

# LLM (Mistral)
MISTRAL_API_KEY=sk-...
MISTRAL_MODEL=mistral-small-latest  # или нужная модель
LLM_PROVIDER=mistral
```
## 3. Запуск с Docker
### Из корня проекта выполните команду:
```bash
  docker compose up --build
```
---
## Структура проекта
Проект состоит из трёх основных уровней:

1. **Telegram-слой (бот)**  
   - `app/bot.py` — точка входа бота на aiogram.  
   - Обрабатывает `/start` и обычные текстовые сообщения.  
   - Для каждого текстового запроса:
     1. вызывает `natural_language_to_sql()` (модуль `app/nlp_sql.py`),  
     2. получает SQL-запрос в виде строки,
     3. передаёт его в `run_sql_and_get_number()` (модуль `app/sql_executor.py`),
     4. отправляет пользователю одно число.

2. **Работа с БД**  
   - `app/core/db.py` — настройка async SQLAlchemy (engine + session maker).  
   - Используется **Core-подход**: сырые SQL-строки через `text()`, без ORM-моделей.  
   - Функция `execute_sql_and_get_number(sql: str)`:
     - выполняет запрос в транзакции,
     - достаёт первую ячейку первой строки,
     - проверяет, что результат числовой (int/float),
     - логирует результат и возвращает его.  
   - Миграции и схема базы — через Alembic (`alembic/`, `alembic.ini`).  
   - `app/loader.py` — утилита для первоначальной загрузки `data/videos.json` в таблицы
     `videos` и `video_snapshots` (bulk-insert через async-сессию).

3. **Слой LLM / генерации SQL**  
   - `app/llm/base.py` — абстракция `LLMClient` с методом `generate_sql(question: str) -> str`.  
   - `app/llm/mistral_client.py` — реализация клиента для Mistral API.  
   - `app/llm/factory.py` — фабрика, которая по настройкам (`settings.llm.provider`) выбирает нужную реализацию.  
   - `app/prompts.py` — системный промпт c описанием схемы БД и правилами генерации SQL.  
   - `app/nlp_sql.py` — тонкая обёртка над клиентом: принимает текст вопроса, вызывает LLM и возвращает SQL-строку.

Дополнительно:
- `app/tg_prepare_message.py` — текст хелпа для `/start` с примерами запросов.
- `app/core/logging_conf.py` — единая настройка логгера (вопрос, SQL, результат).

---


## LLM 

Для преобразования естественного языка в SQL используется LLM Mistral:

- Библиотека: официальный Python-клиент `mistralai`.
- Модель задаётся в `.env` (`MISTRAL_MODEL=...`).
- Ключ API — `MISTRAL_API_KEY` в `.env`.

Пайплайн такой:

1. Пользователь отправляет текстовый запрос в чат.
2. Бот вызывает `natural_language_to_sql(text)`:
   - внутри создаётся клиент через `LLMClientFactory` (`app/llm/factory.py`);
   - вызывается `client.generate_sql(question)`.
3. `MistralLLMClient` (`app/llm/mistral_client.py`):
   - отправляет в Mistral два сообщения:
     - `system` — большой промпт с описанием таблиц и правил;
     - `user` — текст вопроса пользователя.
   - получает ответ, вытаскивает из него блок ```sql ... ``` с помощью `_extract_sql()`;
   - проверяет, что в запросе нет опасных ключевых слов (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`);
   - логирует сгенерированный SQL.

Используемый системный промпт лежит в `app/prompts.py`
