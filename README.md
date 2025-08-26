# Quality Linter 🛠️

[![CI](https://github.com/emnigma/quality-linter/actions/workflows/ci.yml/badge.svg)](https://github.com/emnigma/quality-linter/actions)

## 📌 Общее описание проекта

**Quality Linter** - это интеллектуальный анализатор кода, использующий большие языковые модели (LLM) для выявления
сложных архитектурных проблем и антипаттернов, которые не обнаруживают традиционные линтеры.

**Ключевые особенности:**

- 🔍 Анализ и оценка кода по заданным критериям и приведенным примерам
- 🤖 Использование GPT-4o, o3-mini и других LLM

## 🚀 Запуск

Для запуска проекта, необходимо спуллить репозиторий и установить зависимости.
Далее в метод review класса Reviewer можно передать путь к проверяемой директории и название файла для проверки, а также
объект класса CriteriaDto (из файла `dtos.py`), который содержит критерии проверки.

## 🖥 Пример работы:

code review человека:

```json
{
    "path": "CW2/Button/MainWindow.axaml.cs",
    "start_line": 77,
    "end_line": 77,
    "body": "Так каждый раз создаётся новый Random, хотя нужен только один (и сборщику мусора это всё собирать). Правильнее было бы сделать его статическим полем или вообще использовать Random.Shared"
}
```

code review quality-linter:

```json
{
    "path": "CW2/Button/MainWindow.axaml.cs",
    "start_line": 77,
    "end_line": 77,
    "body": "Random instances should be reused to avoid performance bottlenecks and enhance randomness quality."
}
```