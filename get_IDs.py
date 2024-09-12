from telethon import TelegramClient
import os

#=================================================================================================
# Вставьте свои данные
api_id = 'ваш_api_id'
api_hash = 'ваш_api_hash'

# Укажите ID группы без -100 в начале, из которой нужно получить всех участников
target_group_id = 'ваш_group_id'
#=================================================================================================

# Создаем клиент для подключения от вашего аккаунта
client = TelegramClient('session_name', api_id, api_hash)

async def fetch_group_members():
    try:
        # Преобразуем ID группы в формат, который использует Telegram (-100 перед group_id)
        chat_id = int('-100' + target_group_id)

        # Получаем список всех участников группы
        participants = await client.get_participants(chat_id)

        # Получаем список всех ID участников
        user_ids = [str(participant.id) for participant in participants]

        # Записываем все ID в файл acl.txt
        with open('acl.txt', 'w') as file:
            file.write('\n'.join(user_ids))

        print("Все ID участников группы успешно сохранены в файл acl.txt.")
    except Exception as e:
        print(f"Произошла ошибка при получении участников группы: {e}")

# Основная функция
async def main():
    await fetch_group_members()

if __name__ == "__main__":
    # Запускаем клиента
    with client:
        client.loop.run_until_complete(main())
