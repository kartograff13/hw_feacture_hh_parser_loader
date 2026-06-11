# HH Parser & Loader

Проект для парсинга данных о компаниях и вакансиях с сайта hh.ru и загрузки их в базу данных PostgreSQL.

## Функциональность

1. Получение данных о 10+ компаниях с hh.ru через публичное API
2. Создание структуры базы данных PostgreSQL
3. Загрузка данных в таблицы employers и vacancies
4. Класс DBManager для выполнения запросов к базе данных

## Установка и настройка

### Требования
- Python 3.8+
- PostgreSQL 12+
- Poetry для управления зависимостями

### Установка

1. Клонировать репозиторий:
```
git clone <repository-url>
cd HH_parser&loader
```
2. Установить зависимости:
```
poetry install
```
3. Настроить базу данных:

- Создать файл database.ini по образцу
- Указать данные для подключения к PostgreSQL

## Структура базы данных

### Таблица employers:

- employer_id (INTEGER, PRIMARY KEY)
- name (VARCHAR)
- url (VARCHAR)
- description (TEXT)
- area (VARCHAR)
- open_vacancies (INTEGER)

### Таблица vacancies:

- vacancy_id (INTEGER, PRIMARY KEY)
- employer_id (INTEGER, FOREIGN KEY)
- title (VARCHAR)
- salary_from (INTEGER)
- salary_to (INTEGER)
- currency (VARCHAR)
- experience (VARCHAR)
- employment (VARCHAR)
- url (VARCHAR)
- published_at (TIMESTAMP)

## Использование

### Запустить основной скрипт:

```
poetry run python main.py
```

Скрипт автоматически:

- Создаст базу данных (если не существует)
- Создаст таблицы
- Загрузит данные с hh.ru
- Выполнит запросы через DBManager

## Методы DBManager
***get_companies_and_vacancies_count()*** - компании и количество вакансий

***get_all_vacancies()*** - все вакансии с информацией

***get_avg_salary()*** - средняя зарплата

***get_vacancies_with_higher_salary()*** - вакансии с зарплатой выше средней

***get_vacancies_with_keyword(keyword)*** - вакансии по ключевому слову