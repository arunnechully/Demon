import os
import sqlite3
from pyrogram import Client, filters

# Load environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize SQLite database
conn = sqlite3.connect("seen_files.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
        file_unique_id TEXT PRIMARY KEY
    )
""")
conn.commit()

# Initialize bot
app = Client("dedupe_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def is_duplicate(file_id):
    cursor.execute("SELECT 1 FROM files WHERE file_unique_id = ?", (file_id,))
    return cursor.fetchone() is not None

def mark_seen(file_id):
    cursor.execute("INSERT OR IGNORE INTO files (file_unique_id) VALUES (?)", (file_id,))
    conn.commit()

@app.on_message(filters.document | filters.video | filters.photo | filters.audio)
def handle_files(client, message):
    media = message.document or message.video or message.photo or message.audio

    if media and hasattr(media, 'file_unique_id'):
        unique_id = media.file_unique_id

        if is_duplicate(unique_id):
            print(f"Duplicate file detected: {unique_id}")
            message.delete()
        else:
            print(f"New file: {unique_id}")
            mark_seen(unique_id)

app.run()
