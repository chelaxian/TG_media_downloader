from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeVideo, InputMediaUploadedDocument
import re
import os
from moviepy.editor import VideoFileClip

#=================================================================================================
# Вставьте свои данные
api_id = 'ваш_api_id'
api_hash = 'ваш_api_hash'
bot_token = 'ваш_bot_token'

# Укажите ID группы без -100 в начале, с которой бот должен работать (бот должен быть её членом)
target_group_id = 'ваш_group_id'
#=================================================================================================

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Генерация превью для длинных видео
def create_thumbnail(file_path):
    try:
        video = VideoFileClip(file_path)
        thumb_path = file_path.rsplit(".", 1)[0] + ".jpg"
        video.save_frame(thumb_path, t=1.0)
        return thumb_path
    except Exception as e:
        print(f"Error creating thumbnail for {file_path}: {e}")
        return None

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
            thumb_path = None  # Инициализируем переменную заранее
            if file_path:
                # Проверяем размер файла и создаем превью, если он больше 10 MB
                if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10 MB
                    thumb_path = create_thumbnail(file_path)
                    # Получаем информацию о видео (продолжительность, ширина, высота)
                    video = VideoFileClip(file_path)
                    duration = int(video.duration)
                    width, height = video.size
                    video.close()

                    # Загружаем видео и его превью в Telegram
                    uploaded_video = await client.upload_file(file_path)
                    uploaded_thumb = await client.upload_file(thumb_path) if thumb_path else None

                    # Создаем InputMediaUploadedDocument для корректной отправки видео с превью
                    attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, supports_streaming=True)]
                    media = InputMediaUploadedDocument(
                        file=uploaded_video,
                        mime_type='video/mp4',
                        attributes=attributes,
                        thumb=uploaded_thumb
                    )

                    # Отправляем обработанный медиафайл в личный чат бота с пользователем
                    await client.send_file(event.chat_id, file=media)
                else:
                    # Если видео меньше 10MB, отправляем оригинал
                    await client.send_file(event.chat_id, file=file_path)
                
                # Удаляем временные файлы после отправки
                os.remove(file_path)
                if thumb_path:
                    os.remove(thumb_path)  # Удаляем превью после отправки
                
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
