import asyncio
import json
import random
from telethon import TelegramClient

# Загрузка конфигурации из файла config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

api_id = config['api_id']
api_hash = config['api_hash']
target_group_id = config['target_group_id']

# Создаем клиент для подключения от вашего аккаунта
client = TelegramClient('session_name', api_id, api_hash)

def get_random_delay(prev_delay: float = None) -> float:
    """
    Генерирует случайную задержку от 1.0 до 1.5 секунд.
    Если prev_delay задан, новая задержка будет отличаться минимум на 0.1 секунды.
    """
    while True:
        delay = random.uniform(1.0, 1.5)
        if prev_delay is None or abs(delay - prev_delay) >= 0.1:
            return delay

async def fetch_group_members():
    try:
        # Преобразуем ID группы в формат, используемый Telegram (-100 перед group_id)
        chat_id = int('-100' + target_group_id)

        user_ids = []
        counter = 0
        prev_delay = None  # Для хранения предыдущей задержки

        # Итерируем по участникам группы с помощью асинхронного итератора
        async for participant in client.iter_participants(chat_id, limit=None):
            # Формируем минимальный вывод информации об участнике
            minimal_info = {
                "id": participant.id,
                "first_name": participant.first_name,
                "last_name": participant.last_name,
                "username": participant.username,
                "phone": participant.phone,
                "photo": participant.photo,
                "usernames": participant.usernames
            }
            print(minimal_info)
            
            user_ids.append(str(participant.id))
            counter += 1

            # Получаем случайную задержку, отличную от предыдущей минимум на 0.1 сек.
            delay = get_random_delay(prev_delay)
            prev_delay = delay
            await asyncio.sleep(delay)

            # Дополнительная пауза каждые 50 участников (если применимо)
            if counter % 50 == 0:
                await asyncio.sleep(2)

        # Записываем все ID участников в файл acl.txt
        with open('acl.txt', 'w') as file:
            file.write('\n'.join(user_ids))

        print("Все ID участников группы успешно сохранены в файл acl.txt.")
    except Exception as e:
        print(f"Произошла ошибка при получении участников группы: {e}")

# Основная функция
async def main():
    await fetch_group_members()

if __name__ == "__main__":
    # Запускаем клиента и основную функцию
    with client:
        client.loop.run_until_complete(main())
