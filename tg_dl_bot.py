from telethon import TelegramClient, events
import re
import os

# Вставьте свои данные
api_id = 'ваш_api_id'
api_hash = 'ваш_api_hash'
bot_token = 'ваш_bot_token'

# Укажите ID группы без -100 в начале, с которой бот должен работать (бот должен быть её членом)
target_group_id = 'ваш_group_id'

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def download_and_send_media(event, chat_id, message_id):
    try:
        # Получаем сообщение с указанным ID
        message = await client.get_messages(chat_id, ids=message_id)

        if message is None:
            await event.respond('Не удалось получить сообщение. Возможно, у бота нет прав на доступ к этому сообщению.')
            print('Сообщение не найдено.')
            return

        print(f"Сообщение найдено: {message.id}")

        if message.media:
            # Указываем путь для загрузки в /tmp
            file_path = await message.download_media(file='/tmp/')
            if file_path:
                # Отправляем медиафайл только в личный чат с пользователем
                await event.respond('Медиафайл загружен:', file=file_path)
                os.remove(file_path)  # Удаляем файл после отправки
                print(f"Медиафайл {file_path} успешно загружен и отправлен.")
            else:
                await event.respond('Не удалось загрузить медиафайл.')
                print("Не удалось загрузить медиафайл.")
        else:
            await event.respond('В указанном сообщении нет медиафайла.')
            print("В указанном сообщении нет медиафайла.")
    except Exception as e:
        await event.respond(f'Ошибка при загрузке медиафайла: {str(e)}')
        print(f'Ошибка: {str(e)}')

@client.on(events.NewMessage(pattern=r'https://t\.me/c/\d+/(\d+)', incoming=True))
async def handler(event):
    # Убедимся, что бот реагирует только на сообщения из личных чатов
    if event.is_private: 
        # Парсинг ссылки
        match = re.search(r'https://t\.me/c/(\d+)/(\d+)', event.text)
        if match:
            group_id = match.group(1)
            message_id = int(match.group(2))

            # Проверяем, что группа соответствует указанному target_group_id
            if group_id != target_group_id:
                await event.respond('Ссылки из этой группы не разрешены.')
                print(f'Ссылка из группы {group_id} отклонена.')
                return

            chat_id = int('-100' + group_id)  # Преобразование в формат идентификатора группы

            print(f"Получен запрос для группы {chat_id} и сообщения {message_id}")

            # Проверка на возможность доступа к чату
            try:
                entity = await client.get_entity(chat_id)
                print(f"Доступ к чату {entity.title} подтвержден.")
            except Exception as e:
                await event.respond(f'Ошибка доступа к чату: {str(e)}')
                print(f'Ошибка доступа к чату: {str(e)}')
                return

            # Вызов функции для загрузки и отправки медиа
            await download_and_send_media(event, chat_id, message_id)
        else:
            await event.respond('Неверная ссылка. Пожалуйста, отправьте ссылку в формате https://t.me/c/ID/MessageID.')
            print('Неверная ссылка. Пожалуйста, отправьте ссылку в формате https://t.me/c/ID/MessageID.')

print("Бот запущен...")
client.run_until_disconnected()
