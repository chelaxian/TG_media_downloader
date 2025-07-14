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

Allow Groups and Groups Privacy to that bot in Botfather's Bot settings 

Add bot to your private group and Get this Group ID here \
https://t.me/getmy_idbot

Fill in gotten data in `config.json` code here
```diff 
// Вставьте свои данные в значения параметров ниже

{
-  "api_id": "ваш_api_id",
-  "api_hash": "ваш_api_hash",
-  "bot_token": "ваш_bot_token",
-  "target_group_id": "ваш_group_id"
+  "api_id": "1234567",
+  "api_hash": "abcdef1234567890abcdef2134567890",
+  "bot_token": "12345678:ABcdef_ABcfed12345678912345679",
+  "target_group_id": "234567890"
}

// Укажите выше ID группы без -100 в начале, с которой бот должен работать
// (Для проверки членства в группе - бот должен быть админом группы)
// (Для проверки по ACL - админские права не обязательны)
-// -100234567890
+// 234567890

```
Manually add allowed users ID/nickname/phone number to `acl.txt` or run `python3 get_IDs.py` to automatocaly get users ID from group (you need admin rights).
```diff
-123456789  # укажи ID пользователя
-@username  # или Никнейм
-+1234567890  # или Номер телефона
+7654321
+@ivanov_ivan
++79261234567
```

## Running
```bash
python3 tg_dl_bot.py
```
## Using

right-click (long-tap) on message, copy link to message like `https://t.me/c/1234567/123` and send to bot.
