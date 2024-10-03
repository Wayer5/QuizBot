# Шаблон для проектов со стилизатором Ruff

## Основное

1. Базовая версия Python - 3.11.
2. В файле `requirements_style.txt` находятся зависимости для стилистики.
3. В каталоге `src` находится базовая структура проекта
4. В файле `srd/requirements.txt` прописываются базовые зависимости.
5. В каталоге `infra` находятся настроечные файлы проекта. Здесь же размещать файлы для docker compose.

## Стилистика

Для стилизации кода используется пакеты `Ruff` и `Pre-commit`

Проверка стилистики кода осуществляется командой
```shell
ruff check
```

Если одновременно надо пофиксить то, что можно поиксить автоматически, то добавляем параметр `--fix`
```shell
ruff check --fix
```

Что бы стилистика автоматически проверялась и поправлялась при комитах надо добавить hook pre-commit к git

```shell
pre-commit install
```

## Запуск проекта



Для запуска проекта надо 
- Скопировать в infra файл .env.example и переименовать его в .env
- В файле .env указать telegram token и адресс ngrok (опционально), обязательно на том же порте (8000 по умолчанию).
Далее
```shell
docker compose up --build
```

Ошибки:

1. Все вариации с невозможностью подключения к базе данных -> либо удалите все volume(можно и все остальное) в docker`е, либо в docker-compose volume переименовать на другие
2. Не существует комманда и в конце команды '\r' тогда в command.sh надо открыть с помощью notepad++. Через поиск найти \r и заменить на пустоту.
