# TG_media_downloader
Download and send media from private groups with restricted resending/downloading (you need to add bot to this group)

## Downloading
```bash
git clone https://github.com/chelaxian/TG_media_downloader
```

## Installation
```bash
pip install -r requirements.txt
```
## Settings

Get API ID and API HASH here \
https://my.telegram.org/apps

Create bot and Get Bothfather Token here \
https://t.me/BotFather

Allow Groups and Groups Privacy to that bot in Botfather's Bot settings \

Add bot to your private group and Get this Group ID here \
https://t.me/getmy_idbot

Fill in gotten data in code here
```diff
# Вставьте свои данные
-api_id = 'ваш_api_id'
+api_id = '1234567'
-api_hash = 'ваш_api_hash'
+api_hash = 'abcdef1234567890abcdef2134567890'
-bot_token = 'ваш_bot_token'
+bot_token = '12345678:ABcdef_ABcfed12345678912345679'

# Укажите ID группы без -100 в начале, с которой бот должен работать (бот должен быть её членом)
-# -100234567890
+# 234567890

-target_group_id = 'ваш_group_id'
+target_group_id = '234567890'
```

## Running
```bash
python3 tg_dl_bot.py
```
## Using

right-click (long-tap) on message, copy link to message like `https://t.me/c/1234567/123` and send to bot.
