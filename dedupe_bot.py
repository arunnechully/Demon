import os
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("dedupe_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ================= DB =================
conn = sqlite3.connect("dedupe.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS messages (
    chat_id INTEGER,
    msg_type TEXT,
    content TEXT,
    PRIMARY KEY (chat_id, msg_type, content)
)
""")
conn.commit()

# ================= Enabled Chats =================
enabled_chats = set()

# ========== /start ==========
@app.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    await message.reply_text(
        "☠️ **Welcome to The Real Reaper**\n\n"
        "I'm watching your group for **duplicate text or files**.\n"
        "Use /enable in a group to activate me."
    )

# ========== /enable ==========
@app.on_message(filters.command("enable") & filters.group)
async def enable(client, message: Message):
    enabled_chats.add(message.chat.id)
    await message.reply_text("✅ Duplicate detection enabled in this group!")

@app.on_message(filters.command("disable") & filters.group)
async def disable(client, message: Message):
    enabled_chats.discard(message.chat.id)
    await message.reply_text("❌ Duplicate detection disabled in this group!")

# ========== Helper ==========
def is_duplicate(chat_id: int, msg_type: str, content: str) -> bool:
    cur.execute("SELECT 1 FROM messages WHERE chat_id = ? AND msg_type = ? AND content = ?",
                (chat_id, msg_type, content))
    return cur.fetchone() is not None

def save_entry(chat_id: int, msg_type: str, content: str):
    cur.execute("INSERT OR IGNORE INTO messages (chat_id, msg_type, content) VALUES (?, ?, ?)",
                (chat_id, msg_type, content))
    conn.commit()

# ========== Duplicate Detection ==========
@app.on_message(filters.group)
async def detect_duplicates(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in enabled_chats:
        return

    try:
        # Check for text messages
        if message.text:
            msg_type = "text"
            content = message.text.strip()
        # Check for media
        elif message.photo:
            msg_type = "photo"
            content = message.photo.file_unique_id
        elif message.document:
            msg_type = "document"
            content = message.document.file_unique_id
        elif message.audio:
            msg_type = "audio"
            content = message.audio.file_unique_id
        elif message.video:
            msg_type = "video"
            content = message.video.file_unique_id
        elif message.voice:
            msg_type = "voice"
            content = message.voice.file_unique_id
        else:
            return  # Skip unsupported messages

        if is_duplicate(chat_id, msg_type, content):
            await message.delete()
            print(f"Deleted duplicate {msg_type} in chat {chat_id}")
        else:
            save_entry(chat_id, msg_type, content)
    except Exception as e:
        print(f"Error processing message: {e}")

# ========== Graceful Shutdown ==========
import atexit
@atexit.register
def cleanup():
    conn.close()

# ========== Run ==========
app.run()
