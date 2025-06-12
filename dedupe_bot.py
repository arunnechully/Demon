import os
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("dedupe_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ========== SQLite Setup ==========
conn = sqlite3.connect("dedupe.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS messages (
    chat_id INTEGER,
    content TEXT,
    PRIMARY KEY (chat_id, content)
)
""")
conn.commit()

# ========== /start ==========
@app.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    await message.reply_text(
        "☠️ **Welcome to The Real Reaper**\n\n"
        "I'm watching your chat for duplicates. Add me to a group and use /enable to activate."
    )

# ========== /enable ==========
enabled_chats = set()

@app.on_message(filters.command("enable") & filters.group)
async def enable(client, message: Message):
    enabled_chats.add(message.chat.id)
    await message.reply_text("✅ Duplicate detection enabled in this group!")

@app.on_message(filters.command("disable") & filters.group)
async def disable(client, message: Message):
    enabled_chats.discard(message.chat.id)
    await message.reply_text("❌ Duplicate detection disabled in this group!")

# ========== Duplicate Detector ==========
@app.on_message(filters.text & filters.group)
async def detect_duplicates(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in enabled_chats:
        return

    content = message.text.strip()

    # Check if already exists
    cur.execute("SELECT 1 FROM messages WHERE chat_id = ? AND content = ?", (chat_id, content))
    if cur.fetchone():
        try:
            await message.delete()
            print(f"Deleted duplicate in chat {chat_id}")
        except Exception as e:
            print("Failed to delete:", e)
    else:
        cur.execute("INSERT OR IGNORE INTO messages (chat_id, content) VALUES (?, ?)", (chat_id, content))
        conn.commit()

# ========== Graceful Shutdown ==========
import atexit
@atexit.register
def cleanup():
    conn.close()

# ========== Run ==========
app.run()
