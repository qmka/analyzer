### Анализатор страниц

[![linter-check](https://github.com/qmka/python-project-83/actions/workflows/linter-check.yml/badge.svg)](https://github.com/qmka/python-project-83/actions/workflows/linter-check.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/24811d0e7d0d21691a3d/maintainability)](https://codeclimate.com/github/qmka/python-project-83/maintainability)

Анализатор страниц - это приложение, которое позволяет выполнять проверку основных SEO-параметров сайта. Для использования нужно добавить сайт в базу данных приложения, зайти на страницу сайта в базе и нажать кнопку "Запустить проверку". Результаты каждой проверки выводятся в таблицу на странице сайта, что позволяет отследить изменения.

## Технологии

Flask, Bootstrap, PostgreSQL, BeautifulSoup

## Как использовать?

    make start

Для запуска на тестовом сервере:
    make dev

Для использования приложения должны быть созданы таблицы в базе PostgreSQL. Для создания таблиц используйте команды, прописанные в файле database.sql. Также потребуется задать переменные окружения. Для локальной разработки переменные передаются с помощью библиотеки dotenv. Для этого создайте файл .env в корневом каталоге со следующим содержимым:
    # адрес базы данных
    DATABASE_URL=postgresql://логин:пароль@localhost:5432/имя_базы_данных
    # секретный ключ (произвольный набор символов)
    SECRET_KEY=12345 
