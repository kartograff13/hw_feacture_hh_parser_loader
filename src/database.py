from typing import Any, Optional

import psycopg2
import psycopg2.extensions
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.config import load_config


class Database:
    """Класс для операций с базой данных."""

    def __init__(self, database_name: str) -> None:
        self.config: dict[str, str] = load_config()
        self.database_name: str = database_name
        self.params: dict[str, str] = self.config.copy()
        self.params.pop("dbname", None)

        self._test_connection()

    def _test_connection(self) -> None:
        """Проверка подключения к PostgreSQL."""
        try:
            conn: psycopg2.extensions.connection = psycopg2.connect(
                host=self.params.get("host", "localhost"),
                user=self.params.get("user"),
                password=self.params.get("password"),
                port=self.params.get("port", "5432"),
            )
            conn.close()
            print("✓ Подключение к PostgreSQL успешно установлено.")
        except psycopg2.OperationalError as e:
            print(f"✗ Ошибка подключения к PostgreSQL: {e}")
            raise

    def create_database(self) -> None:
        """Создание базы данных, если она еще не существует."""
        conn: psycopg2.extensions.connection = psycopg2.connect(
            host=self.params.get("host", "localhost"),
            user=self.params.get("user"),
            password=self.params.get("password"),
            port=self.params.get("port", "5432"),
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur: psycopg2.extensions.cursor = conn.cursor()

        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.database_name}'")
        exists: Optional[tuple] = cur.fetchone()

        if not exists:
            cur.execute(f"CREATE DATABASE {self.database_name}")
            print(f"✓ База данных '{self.database_name}' успешно создана.")
        else:
            print(f"✓ База данных '{self.database_name}' уже существует.")

        cur.close()
        conn.close()

    def create_tables(self) -> None:
        """Создание таблиц для работодателей и вакансий."""
        conn: psycopg2.extensions.connection = psycopg2.connect(
            host=self.params.get("host", "localhost"),
            user=self.params.get("user"),
            password=self.params.get("password"),
            port=self.params.get("port", "5432"),
            database=self.database_name,
        )
        cur: psycopg2.extensions.cursor = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS employers (
                employer_id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url VARCHAR(255),
                description TEXT,
                area VARCHAR(100),
                open_vacancies INTEGER
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id INTEGER PRIMARY KEY,
                employer_id INTEGER REFERENCES employers(employer_id),
                title VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                currency VARCHAR(10),
                experience VARCHAR(100),
                employment VARCHAR(100),
                url VARCHAR(255),
                published_at TIMESTAMP
            )
            """
        )

        conn.commit()
        cur.close()
        conn.close()
        print("✓ Таблицы 'employers' и 'vacancies' успешно созданы.")

    def save_employer(self, employer_data: dict[str, Any]) -> None:
        """Сохранение данных о работодателе в базу данных."""
        conn: psycopg2.extensions.connection = psycopg2.connect(
            host=self.params.get("host", "localhost"),
            user=self.params.get("user"),
            password=self.params.get("password"),
            port=self.params.get("port", "5432"),
            database=self.database_name,
        )
        cur: psycopg2.extensions.cursor = conn.cursor()

        cur.execute(
            """
            INSERT INTO employers (employer_id, name, url, description, area, open_vacancies)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (employer_id) DO UPDATE SET
                name = EXCLUDED.name,
                url = EXCLUDED.url,
                description = EXCLUDED.description,
                area = EXCLUDED.area,
                open_vacancies = EXCLUDED.open_vacancies
            """,
            (
                employer_data.get("id"),
                employer_data.get("name"),
                employer_data.get("alternate_url"),
                employer_data.get("description"),
                employer_data.get("area", {}).get("name"),
                employer_data.get("open_vacancies", 0),
            ),
        )

        conn.commit()
        cur.close()
        conn.close()

    def save_vacancy(self, vacancy_data: dict[str, Any]) -> None:
        """Сохранение данных о вакансиях в базу данных."""
        conn: psycopg2.extensions.connection = psycopg2.connect(
            host=self.params.get("host", "localhost"),
            user=self.params.get("user"),
            password=self.params.get("password"),
            port=self.params.get("port", "5432"),
            database=self.database_name,
        )
        cur: psycopg2.extensions.cursor = conn.cursor()

        salary: Optional[dict[str, Any]] = vacancy_data.get("salary")
        salary_from: Optional[int] = salary.get("from") if salary else None
        salary_to: Optional[int] = salary.get("to") if salary else None
        currency: Optional[str] = salary.get("currency") if salary else None

        cur.execute(
            """
            INSERT INTO vacancies (
                vacancy_id, employer_id, title, salary_from, salary_to,
                currency, experience, employment, url, published_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (vacancy_id) DO UPDATE SET
                title = EXCLUDED.title,
                salary_from = EXCLUDED.salary_from,
                salary_to = EXCLUDED.salary_to,
                currency = EXCLUDED.currency,
                experience = EXCLUDED.experience,
                employment = EXCLUDED.employment,
                url = EXCLUDED.url,
                published_at = EXCLUDED.published_at
            """,
            (
                vacancy_data.get("id"),
                vacancy_data.get("employer", {}).get("id"),
                vacancy_data.get("name"),
                salary_from,
                salary_to,
                currency,
                vacancy_data.get("experience", {}).get("name"),
                vacancy_data.get("employment", {}).get("name"),
                vacancy_data.get("alternate_url"),
                vacancy_data.get("published_at"),
            ),
        )

        conn.commit()
        cur.close()
        conn.close()
