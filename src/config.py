from configparser import ConfigParser


def load_config(filename: str = "database.ini", section: str = "postgresql") -> dict[str, str]:
    """Загрузка конфигурации базы данных из файла .ini."""
    parser: ConfigParser = ConfigParser()
    parser.read(filename)

    db: dict[str, str] = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f"Раздел {section} не найден в {filename}")

    return db
