from typing import Any, Optional, Tuple, Union

import psycopg2
import psycopg2.extensions

from src.config import load_config


class DBManager:
    """Класс для управления запросами к базе данных."""

    def __init__(self, database_name: str) -> None:
        self.config: dict[str, str] = load_config()
        self.database_name: str = database_name

    def _execute_query(
        self, query: str, params: Optional[tuple] = None, fetch: bool = True
    ) -> Union[list[Tuple[Any, ...]], None]:
        """Выполнение SQL-запроса."""
        conn: psycopg2.extensions.connection = psycopg2.connect(
            host=self.config.get("host", "localhost"),
            user=self.config.get("user"),
            password=self.config.get("password"),
            port=self.config.get("port", "5432"),
            database=self.database_name,
        )
        cur: psycopg2.extensions.cursor = conn.cursor()

        try:
            cur.execute(query, params)
            result: Union[list[Tuple[Any, ...]], None] = None
            if fetch:
                result = cur.fetchall()
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()

        return result

    def get_companies_and_vacancies_count(self) -> list[Tuple[str, int]]:
        """Получение списка всех компаний с указанием количества вакансий."""
        query: str = """
            SELECT e.name, COUNT(v.vacancy_id) as vacancies_count
            FROM employers e
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id
            GROUP BY e.employer_id, e.name
            ORDER BY vacancies_count DESC
        """
        result: Optional[list[Tuple[Any, ...]]] = self._execute_query(query)
        if result:
            return [(str(row[0]), int(row[1])) for row in result]
        return []

    def get_all_vacancies(self) -> list[Tuple[str, str, Optional[int], Optional[int], Optional[str], str]]:
        """Получения списка всех вакансий с указанием названия компании, должности, заработной платы и URL-адреса."""
        query: str = """
            SELECT
                e.name as company_name,
                v.title,
                v.salary_from,
                v.salary_to,
                v.currency,
                v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            ORDER BY e.name, v.title
        """
        result: Optional[list[Tuple[Any, ...]]] = self._execute_query(query)
        if result:
            return [
                (
                    str(row[0]),
                    str(row[1]),
                    int(row[2]) if row[2] is not None else None,
                    int(row[3]) if row[3] is not None else None,
                    str(row[4]) if row[4] is not None else None,
                    str(row[5]),
                )
                for row in result
            ]
        return []

    def get_avg_salary(self) -> Optional[float]:
        """Получение средней заработной платы по всем вакансиям."""
        query: str = """
            SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0) as avg_salary
            FROM vacancies
            WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
        """
        result: Optional[list[Tuple[Any, ...]]] = self._execute_query(query)
        if result and result[0][0] is not None:
            return float(result[0][0])
        return None

    def get_vacancies_with_higher_salary(
        self,
    ) -> list[Tuple[str, str, Optional[int], Optional[int], Optional[str], str]]:
        """Получение вакансии с зарплатой выше средней."""
        avg_salary: Optional[float] = self.get_avg_salary()
        if avg_salary is None:
            return []

        query: str = """
            SELECT
                e.name as company_name,
                v.title,
                v.salary_from,
                v.salary_to,
                v.currency,
                v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2.0 > %s
            ORDER BY (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2.0 DESC
        """
        result: Optional[list[Tuple[Any, ...]]] = self._execute_query(query, (avg_salary,))
        if result:
            return [
                (
                    str(row[0]),
                    str(row[1]),
                    int(row[2]) if row[2] is not None else None,
                    int(row[3]) if row[3] is not None else None,
                    str(row[4]) if row[4] is not None else None,
                    str(row[5]),
                )
                for row in result
            ]
        return []

    def get_vacancies_with_keyword(
        self, keyword: str
    ) -> list[Tuple[str, str, Optional[int], Optional[int], Optional[str], str]]:
        """Получение вакансии, содержащие ключевое слово в заголовке."""
        query: str = """
            SELECT
                e.name as company_name,
                v.title,
                v.salary_from,
                v.salary_to,
                v.currency,
                v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE LOWER(v.title) LIKE LOWER(%s)
            ORDER BY e.name, v.title
        """
        result: Optional[list[Tuple[Any, ...]]] = self._execute_query(query, (f"%{keyword}%",))
        if result:
            return [
                (
                    str(row[0]),
                    str(row[1]),
                    int(row[2]) if row[2] is not None else None,
                    int(row[3]) if row[3] is not None else None,
                    str(row[4]) if row[4] is not None else None,
                    str(row[5]),
                )
                for row in result
            ]
        return []

    def get_vacancies_by_company(
        self, company_id: int
    ) -> list[Tuple[str, Optional[int], Optional[int], Optional[str], str]]:
        """Получение списка всех вакансий в конкретной компании."""
        query: str = """
            SELECT
                v.title,
                v.salary_from,
                v.salary_to,
                v.currency,
                v.url
            FROM vacancies v
            WHERE v.employer_id = %s
            ORDER BY v.title
        """
        result: Optional[list[Tuple[Any, ...]]] = self._execute_query(query, (company_id,))
        if result:
            return [
                (
                    str(row[0]),
                    int(row[1]) if row[1] is not None else None,
                    int(row[2]) if row[2] is not None else None,
                    str(row[3]) if row[3] is not None else None,
                    str(row[4]),
                )
                for row in result
            ]
        return []
