from typing import Optional, Tuple

from src.db_manager import DBManager
from src.utils import load_data_to_db


def main() -> None:
    employer_ids: list[str] = [
        "1740",  # Яндекс
        "15478",  # VK
        "3529",  # Сбер
        "78638",  # Тинькофф
        "2180",  # Ozon
        "84585",  # Авито
        "80",  # Альфа-Банк
        "39305",  # Газпром нефть
        "3776",  # МТС
        "2748",  # Ростелеком
        "4181",  # ВТБ
        "87021",  # Wildberries
    ]

    database_name: str = "hh_vacancies"

    print("📥 Загрузка данных с HH.ru...")
    load_data_to_db(employer_ids, database_name)

    print("\n" + "=" * 60)
    print("📊 Запросы к базе данных:")
    print("=" * 60)

    db_manager: DBManager = DBManager(database_name)

    print("\n1. 📈 Компании и количество вакансий:")
    companies: list[Tuple[str, int]] = db_manager.get_companies_and_vacancies_count()
    for company, count in companies:
        print(f"   • {company}: {count} вакансий")

    print("\n2. 📋 Пример всех вакансий (первые 5):")
    all_vacancies: list[Tuple[str, str, Optional[int], Optional[int], Optional[str], str]] = (
        db_manager.get_all_vacancies()
    )
    for i, vacancy in enumerate(all_vacancies[:5]):
        s_from1: str = str(vacancy[2]) if vacancy[2] else "?"
        s_to1: str = str(vacancy[3]) if vacancy[3] else "?"
        curr1: str = vacancy[4] if vacancy[4] else ""
        print(f"   {i+1}. {vacancy[0]} - {vacancy[1]}: {s_from1}-{s_to1} {curr1}")

    print("\n3. 💰 Средняя зарплата:")
    avg_salary: Optional[float] = db_manager.get_avg_salary()
    if avg_salary:
        print(f"   {avg_salary:,.2f} RUB")
    else:
        print("   Нет данных о зарплатах")

    print("\n4. ⬆️ Вакансии с зарплатой выше средней (первые 5):")
    high_salary_vacancies: list[Tuple[str, str, Optional[int], Optional[int], Optional[str], str]] = (
        db_manager.get_vacancies_with_higher_salary()
    )
    for i, vacancy in enumerate(high_salary_vacancies[:5]):
        s_from2: str = str(vacancy[2]) if vacancy[2] else "?"
        s_to2: str = str(vacancy[3]) if vacancy[3] else "?"
        curr2: str = vacancy[4] if vacancy[4] else ""
        print(f"   {i+1}. {vacancy[0]} - {vacancy[1]}: {s_from2}-{s_to2} {curr2}")

    print("\n5. 🐍 Вакансии с ключевым словом 'Python':")
    python_vacancies: list[Tuple[str, str, Optional[int], Optional[int], Optional[str], str]] = (
        db_manager.get_vacancies_with_keyword("Python")
    )
    if python_vacancies:
        for i, vacancy in enumerate(python_vacancies[:5]):
            s_from3: str = str(vacancy[2]) if vacancy[2] else "?"
            s_to3: str = str(vacancy[3]) if vacancy[3] else "?"
            curr3: str = vacancy[4] if vacancy[4] else ""
            print(f"   {i+1}. {vacancy[0]} - {vacancy[1]}: {s_from3}-{s_to3} {curr3}")
        if len(python_vacancies) > 5:
            print(f"   ... и ещё {len(python_vacancies) - 5} вакансий")
    else:
        print("   Вакансий не найдено")

    print("\n6. 📊 Вакансии с ключевым словом 'Data':")
    data_vacancies: list[Tuple[str, str, Optional[int], Optional[int], Optional[str], str]] = (
        db_manager.get_vacancies_with_keyword("Data")
    )
    if data_vacancies:
        for i, vacancy in enumerate(data_vacancies[:5]):
            s_from4: str = str(vacancy[2]) if vacancy[2] else "?"
            s_to4: str = str(vacancy[3]) if vacancy[3] else "?"
            curr4: str = vacancy[4] if vacancy[4] else ""
            print(f"   {i+1}. {vacancy[0]} - {vacancy[1]}: {s_from4}-{s_to4} {curr4}")
        if len(data_vacancies) > 5:
            print(f"   ... и ещё {len(data_vacancies) - 5} вакансий")
    else:
        print("   Вакансий не найдено")

    print("\n7. 📊 Статистика:")
    print(f"   • Всего компаний: {len(companies)}")
    print(f"   • Всего вакансий: {len(all_vacancies)}")
    if avg_salary:
        print(f"   • Средняя зарплата: {avg_salary:,.2f} RUB")


if __name__ == "__main__":
    main()
