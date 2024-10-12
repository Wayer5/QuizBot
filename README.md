# Описание проекта

Телеграмм-бот для проведение викторин с использованием Web Apps. Так же проект предусматривает сбор  и анализ стастики ответов пользователей, которая доступна через админ панель. 

# Запуск проекта

Для запуска проекта надо:
- В папке /infra создать файл .env;
- По примеру из .env.example заполнить файл .env;
- WEB_URL - url вашего сервера. Обязательно должен принимать порт, который указан в файле .env и иметь подключение https
- В той же папке /infra нужно выполнить команду:
```shell
docker compose up --build
```

**После запуска первый пользователь становится администратором**

Возможные ошибки при запуске:

1. Все вариации с невозможностью подключения к базе данных -> либо удалите все volume(можно и все остальное) в docker`е, либо в docker-compose volume переименовать на другие
2. Не существует комманда и в конце команды '\r' тогда в command.sh надо открыть с помощью notepad++. Через поиск найти \r и заменить на пустоту.


# Структура проекта

## /infra

Содержит docker-compose  и файл env. Предназначена для запуска проекта

## /src

Содержит основные файлы проекта и requirements.txt Так же здесь находится command.sh, необходимый для запуска проекта

- bot.py - отвечает за работу бота
- admin.py - отвечает за работу админ панели
### views.py - представления, не имеющие шаблонов
### constants.py - константы
### models.py - модели
### jwt.py - индентификация пользователей
### init.py - инициализация Flask приложения. Чтобы Flask видел новые файлы или папки, нужно выполнить их импорт в последней строке.

В папке /crud находятся круд функции для викторин, категорий и вопросов, так же там описаны функции, необходимые для сбора и анализа стастистики ответов пользователей.

## /src/templates 

Здесь находятся шаблоны для работы web apps. Так же в папке /admin находятся шаблоны для админ панели.

## /src/static

Статика проекта, необходимая для работы фронта


## /docs

Документация по проекту

## /migrations

Миграции

## /.github/workflow

Автоматизация для git


# Создатели

- >Тимлид команды: [Клищенко Павел](https://github.com/PaShyKDF),
  >Автор: [Борисов Максим](https://github.com/Wayer5),
  >Автор: [Зайцев Дмитрий](https://github.com/of1nn),
  >Автор: [Клобков Павел](https://github.com/Pavel-K14),
  >Автор: [Бабич Денис](https://github.com/babichdenis),
  >Автор: [Ряднов Никита](https://github.com/Riadnov-dev).






