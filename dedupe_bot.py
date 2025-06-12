import os
from pyrogram import Client, filters

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("dedupe_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

seen_files = set()

@app.on_message(filters.group)
def remove_duplicates(client, message):
    file_id = None
    if message.photo:
        file_id = message.photo.file_unique_id
    elif message.video:
        file_id = message.video.file_unique_id
    elif message.document:
        file_id = message.document.file_unique_id
    elif message.audio:
        file_id = message.audio.file_unique_id
    elif message.voice:
        file_id = message.voice.file_unique_id

    if file_id:
        if file_id in seen_files:
            message.delete()
        else:
            seen_files.add(file_id)

if __name__ == "__main__":
    app.run()
