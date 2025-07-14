import re
import os
import json
from moviepy.editor import VideoFileClip
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeVideo, InputMediaUploadedDocument
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

# Загрузка конфигурации из файла config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

api_id = config['api_id']
api_hash = config['api_hash']
bot_token = config['bot_token']
target_group_id = config['target_group_id']

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Загрузка списка ACL из файла
def load_acl():
    try:
        with open('acl.txt', 'r') as file:
            return set(line.strip() for line in file if line.strip())
    except FileNotFoundError:
        print("ACL file not found. Bot will respond only to group members.")
        return set()

acl_list = load_acl()

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

# Синхронная проверка ACL
def is_in_acl(user):
    return (str(user.id) in acl_list or
            (user.username and f"@{user.username}" in acl_list) or
            (user.phone and f"+{user.phone}" in acl_list))

# Асинхронная проверка членства в группе
async def is_group_member(user_id):
    """
    Returns True if user_id is a member of target_group_id, else False.
    """
    chat_id = int(f'-100{target_group_id}')
    try:
        # Проверяем участника через GetParticipantRequest
        await client(GetParticipantRequest(channel=chat_id, participant=user_id))
        return True
    except UserNotParticipantError:
        return False
    except Exception as e:
        print(f"Error checking membership for {user_id}: {e}")
        return False

async def download_and_send_media(event, chat_id, message_id):
    try:
        message = await client.get_messages(chat_id, ids=message_id)
        if not message:
            await event.respond('Не удалось получить сообщение. Возможно, у бота нет прав.')
            print('Message not found.')
            return

        if message.media:
            file_path = await message.download_media(file='/tmp/')
            thumb_path = None  # initialize thumbnail path

            if file_path:
                # If file is larger than 10 MB — create thumbnail
                if os.path.getsize(file_path) > 10 * 1024 * 1024:
                    thumb_path = create_thumbnail(file_path)

                    # extract video info
                    video = VideoFileClip(file_path)
                    duration = int(video.duration)
                    width, height = video.size
                    video.close()

                    # upload files
                    uploaded_video = await client.upload_file(file_path)
                    uploaded_thumb = await client.upload_file(thumb_path) if thumb_path else None

                    # prepare attributes and send with thumb
                    attributes = [
                        DocumentAttributeVideo(
                            duration=duration, w=width, h=height, supports_streaming=True
                        )
                    ]
                    media = InputMediaUploadedDocument(
                        file=uploaded_video,
                        mime_type='video/mp4',
                        attributes=attributes,
                        thumb=uploaded_thumb
                    )
                    await client.send_file(event.chat_id, file=media)
                else:
                    # send original if <= 10 MB
                    await client.send_file(event.chat_id, file=file_path)

                # cleanup temp files
                os.remove(file_path)
                if thumb_path and os.path.exists(thumb_path):
                    os.remove(thumb_path)

                print(f"Media {file_path} sent successfully.")
            else:
                await event.respond('Не удалось загрузить медиафайл.')
                print("Не удалось загрузить медиафайл.")
        else:
            await event.respond('В указанном сообщении нет медиафайла.')
            print("В указанном сообщении нет медиафайла.")
    except Exception as e:
        await event.respond(f'Ошибка при загрузке медиафайла: {e}')
        print(f'Error: {e}')


@client.on(events.NewMessage(pattern=r'https://t\.me/c/\d+/(\d+)', incoming=True))
async def handler(event):
    if not event.is_private:
        return

    sender = await event.get_sender()
    user_id = sender.id

    # Доступ, если в ACL или член target_group
    if not (is_in_acl(sender) or await is_group_member(user_id)):
        print(f"Access denied for user {user_id}")
        return

    match = re.search(r'https://t\.me/c/(\d+)/(\d+)', event.text)
    if not match:
        await event.respond('Неверная ссылка. Формат: https://t.me/c/ID/MessageID')
        return

    group_id, message_id = match.group(1), int(match.group(2))
    if group_id != target_group_id:
        await event.respond('Ссылки из этой группы не разрешены.')
        print(f'Link from group {group_id} rejected.')
        return

    chat_id = int(f'-100{group_id}')
    try:
        entity = await client.get_entity(chat_id)
        print(f"Access to chat {entity.title} confirmed.")
    except Exception as e:
        await event.respond(f'Ошибка доступа к чату: {e}')
        print(f'Chat access error: {e}')
        return

    await download_and_send_media(event, chat_id, message_id)

print("Bot is running...")
client.run_until_disconnected()
