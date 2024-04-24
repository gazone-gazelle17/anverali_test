import os
import psycopg2
from dotenv import load_dotenv
from fast_bitrix24 import Bitrix

load_dotenv()

# Загружает переменные окружения.
webhook = os.getenv('WEBHOOK')
database_url = os.getenv('DATABASE_URL')

# Инициализирует Bitrix
bitrix = Bitrix(webhook)

# Подключается к базе данных
conn = psycopg2.connect(database_url)


def get_contact_data(contact_id):
    """Получает данные контакта."""
    try:
        contact = bitrix.get_all('crm.contact.get', params={'id': contact_id})
        return contact
    except Exception as e:
        print("Возникла ошибка получения данных", e)
        return None


def check_name_gender(contact_name):
    """Проверяет имя на принадлежность к гендеру."""
    with conn.cursor() as cur:
        cur.execute(
            'SELECT 1 FROM names_woman WHERE name = %s', (contact_name,)
        )
        if cur.fetchone():
            return 'Женщина'
        cur.execute(
            'SELECT 1 FROM names_man WHERE name = %s', (contact_name,)
        )
        if cur.fetchone():
            return 'Мужчина'
    return None


def update_contact(contact_id, gender):
    """Обновляет гендер контакта."""
    try:
        result = bitrix.call(
            'crm.contact.update',
            {'id': contact_id, 'fields': {'gender': gender}}
        )
        return result
    except Exception as e:
        print("Ошибка при обновлении контакта:", e)
        return False


def main():
    """Итоговая логика программы."""
    contact_id = input("Введите ID контакта: ")
    contact_name = input(
        "Введите имя контакта (оставьте пустым, если имя неизвестно): "
    )

    if not contact_name:
        contact_data = get_contact_data(contact_id)
        if contact_data:
            contact_name = contact_data['NAME']
        else:
            print("Контакт не найден.")
            return

    gender = check_name_gender(contact_name)
    if gender:
        update_result = update_contact(contact_id, gender)
        print("Обновление выполнено:", update_result)
    else:
        print("Имя не найдено в базе данных.")


if __name__ == '__main__':
    main()
