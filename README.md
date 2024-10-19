# ТЕЛЕГРАММ-БОТ ДЛЯ ПРОВЕДЕНИЯ ВИКТОРИН С ИСПОЛЬЗОВАНИЕМ WEB APPS

# Описание проекта

## 📖 О проекте

Телеграмм-бот, позволяющий пользователям проходить викторины с использованием Web Apps. Проект также собирает и анализирует статистику ответов пользователей, которая доступна через админ панель.

## Использованные технологии в проекте

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/> <img src="https://img.shields.io/badge/Webhooks-FF7F50?style=for-the-badge&logo=webhooks&logoColor=white"/> <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white"/> <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white"/> <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/> <img src="https://img.shields.io/badge/SQLAlchemy-CCA76E?style=for-the-badge&logo=alchemy&logoColor=white"/> <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white"/> 

---

## 🚀 Запуск проекта

Для запуска проекта нужно:

- В папке `/infra` создать файл `.env`.
- Заполнить файл `.env` по примеру из `.env.example`.
- Параметр `WEB_URL` должен содержать URL вашего сервера. Обязательно использовать порт, который указан в `.env` и обеспечить подключение через HTTPS.
- В той же папке `/infra` выполнить команду:

```shell
docker compose up --build
```

**Примечание**: первый пользователь, вошедший в систему, автоматически становится администратором.

### Возможные ошибки при запуске:
1. Если возникает ошибка при подключении к базе данных, необходимо либо удалить все volume в Docker, либо переименовать volume в `docker-compose` файле.
2. Если появляется ошибка с символом `'
'` в конце команды, откройте файл `command.sh` с помощью Notepad++, найдите и удалите все `
`.

---

## 📂 Структура проекта

```text
MedStat_Solutions_team3/
│
├── infra/
│   ├── .env
│   ├── .env.example
│   ├── docker-compose.yml
│   └── docker-compose.production.yml
│
├── logs/
│
├── migrations/
│
├── src/
│   ├── admin/
│   ├── crud/
│   ├── instance/
│   ├── models/
│   ├── static/
│   │   ├── css/
│   │   ├── images/
│   │   └── js/
│   ├── templates/
│   │   ├── admin/
│   │   ├── csrf/
│   │   ├── errors/
│   │   └── ...
│   ├── views/
│   ├── api_views.py
│   ├── bot.py
│   ├── command.sh
│   ├── constants.py
│   ├── error_handlers.py
│   ├── jwt.py
│   ├── run_server.py
│   └── utils.py
│
├── docs/
│   ├── dir_visualization.pdf
│   ├── models_schema.pdf
│   └── webhook_report.txt
│
└── .github/
    └── workflows/
        └── ci_cd.yml
```

Проект состоит из следующих основных директорий и файлов:

### `/infra`
Содержит файлы для развертывания проекта, такие как `docker-compose.yml` и `.env` файл, необходимый для настройки окружения.

### `/logs`
Здесь хранятся лог-файлы приложения.

### `/migrations`
Миграции базы данных, необходимые для обновления схемы данных при изменении моделей.

### `/src`
Содержит основной код проекта, включая модули бота, CRUD операции, модели и обработчики ошибок.

- **`/admin`** — файлы, отвечающие за административную панель.
- **`/crud`** — CRUD классы для работы с сущностями: викторинами, категориями, вопросами и статистикой ответов пользователей.
- **`/models`** — модели данных проекта, используемые в базе данных.
- **`/templates`** — HTML шаблоны для страниц пользователя и административной панели.
- **`/static`** — статические файлы проекта, такие как CSS, изображения и JS.
- **`/views`** — представления для обработки запросов (включая представления бота и админки).

### `/src/static`
Статические файлы проекта, включая стили, скрипты и изображения.

### `/docs`
Документация по проекту, включающая схемы, описания и объяснения по работе с системой.

### `/.github/workflows`
Файлы для автоматизации CI/CD через GitHub Actions.

---

## 👥 Участники проекта

- **Тимлид команды**: [Клищенко Павел](https://github.com/PaShyKDF)

### Авторы
- [Борисов Максим](https://github.com/Wayer5)
- [Зайцев Дмитрий](https://github.com/of1nn)
- [Клобков Павел](https://github.com/Pavel-K14)
- [Бабич Денис](https://github.com/babichdenis)
- [Ряднов Никита](https://github.com/Riadnov-dev)






