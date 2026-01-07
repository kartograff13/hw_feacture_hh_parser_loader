from src.database import Database
from src.hh_api import HHAPI


def load_data_to_db(employer_ids: list[str], db_name: str) -> None:
    """Загрузка данных из API HH в базу данных."""
    hh_api: HHAPI = HHAPI()
    db: Database = Database(db_name)

    db.create_database()
    db.create_tables()

    for employer_id in employer_ids:
        try:
            print(f"🔍 Обработка работодателя ID: {employer_id}")
            employer_data: dict = hh_api.get_employer(employer_id)

            if not employer_data:
                continue

            db.save_employer(employer_data)

            vacancies: list[dict] = hh_api.get_all_vacancies(employer_id)
            print(f"   Найдено вакансий: {len(vacancies)}")

            for vacancy in vacancies:
                db.save_vacancy(vacancy)

        except Exception as e:
            print(f"❌ Ошибка при обработке работодателя {employer_id}: {e}")
            continue

    print("✅ Загрузка данных завершена.")
