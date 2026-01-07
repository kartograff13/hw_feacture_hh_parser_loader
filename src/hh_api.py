import time
from typing import Any, Optional, cast

import requests


class HHAPI:
    """Класс для взаимодействия с API HH.ru"""

    BASE_URL: str = "https://api.hh.ru/"

    def __init__(self, retries: int = 3, timeout: int = 30, request_delay: float = 0.2) -> None:
        self.session: requests.Session = requests.Session()
        self.session.headers.update({"User-Agent": "HH-Parser/1.0 (you@example.com)"})
        self.retries: int = retries
        self.timeout: int = timeout
        self.request_delay: float = request_delay
        self.last_request_time: float = 0

    def _throttle(self) -> None:
        """Ограничение частоты запросов для соблюдения лимитов API."""
        current_time: float = time.time()
        time_since_last: float = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)

        self.last_request_time = time.time()

    def _make_request(self, url: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Выполнение запроса с повторными попытками."""
        for attempt in range(self.retries):
            try:
                self._throttle()
                response: requests.Response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return cast(dict[str, Any], response.json())
            except requests.exceptions.RequestException as e:
                if attempt == self.retries - 1:
                    raise e
                time.sleep(2**attempt)

        # Этот код недостижим, но нужен для mypy
        raise requests.exceptions.RequestException("Max retries exceeded")

    def get_employer(self, employer_id: str) -> dict[str, Any]:
        """Получение информации о работодателе по идентификатору."""
        url: str = f"{self.BASE_URL}employers/{employer_id}"
        return self._make_request(url)

    def get_vacancies(self, employer_id: str, page: int = 0, per_page: int = 100) -> dict[str, Any]:
        """Получение списка вакансий от конкретного работодателя."""
        url: str = f"{self.BASE_URL}vacancies"
        params: dict[str, Any] = {
            "employer_id": employer_id,
            "page": page,
            "per_page": per_page,
            "only_with_salary": True,
        }
        return self._make_request(url, params)

    def get_all_vacancies(self, employer_id: str) -> list[dict[str, Any]]:
        """Получение списка всех вакансий для работодателя (с постраничной навигацией)."""
        all_vacancies: list[dict[str, Any]] = []
        page: int = 0

        while True:
            try:
                data: dict[str, Any] = self.get_vacancies(employer_id, page)
                vacancies: list[dict[str, Any]] = cast(list[dict[str, Any]], data.get("items", []))
                all_vacancies.extend(vacancies)

                page += 1
                if page >= data.get("pages", 0):
                    break
            except requests.exceptions.RequestException:
                break

        return all_vacancies
