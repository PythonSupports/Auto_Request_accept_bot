import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatJoinRequest

# Initialize bot
bot = Client(
    "AutoAcceptBot",
    bot_token=os.environ["BOT_TOKEN"],
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"]
)

# Configs
APPROVED_WELCOME_TEXT = os.environ.get(
    "APPROVED_WELCOME_TEXT",
    "👋 Hello {mention}\n\nWelcome to **{title}**!\n\nYou have been auto-approved ✅"
)
APPROVED = os.environ.get("APPROVED_WELCOME", "on").lower()
OWNER_ID = int(os.environ.get("OWNER_ID", 0))

# Memory DB to store accepted users for broadcast
ACCEPTED_USERS = set()

# ──────────────────────────────────────────────
# /start command (Private only)
@bot.on_message(filters.private & filters.command("start"))
async def start(_, message: Message):
    buttons = [
        [
            InlineKeyboardButton("📢 Updates", url="https://t.me/Krishnetwork"),
            InlineKeyboardButton("💬 Support", url="https://t.me/krishnetwork")
        ]
    ]
    await message.reply_video(
        video="https://files.catbox.moe/glnmnh.mp4",
        caption="**👋 Hello!\n\nI’m a Telegram Auto Request Accept Bot.**\n\n"
                "➤ Add me to your group/channel and enable join requests.\n"
                "➤ I’ll auto-approve new members and optionally DM them a welcome message.\n\n"
                "**Made with ❤️ by @Krishnetwork**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ──────────────────────────────────────────────
# Auto-approve chat join requests
@bot.on_chat_join_request()
async def auto_approve(_, request: ChatJoinRequest):
    user = request.from_user
    chat = request.chat

    try:
        await bot.approve_chat_join_request(chat.id, user.id)
        print(f"[APPROVED] {user.first_name} ({user.id}) in {chat.title}")
        ACCEPTED_USERS.add(user.id)

        if APPROVED == "on":
            await bot.send_message(
                chat_id=user.id,
                text=APPROVED_WELCOME_TEXT.format(
                    mention=user.mention,
                    title=chat.title
                )
            )
    except Exception as e:
        print(f"Failed to approve/send DM to {user.id}: {e}")

# ──────────────────────────────────────────────
# Broadcast command (Owner only)
@bot.on_message(filters.private & filters.user(OWNER_ID) & filters.command("broadcast"))
async def broadcast(_, message: Message):
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        return await message.reply_text("❌ Usage: `/broadcast your message`", quote=True)

    broadcast_text = text[1]
    success, fail = 0, 0

    for user_id in list(ACCEPTED_USERS):
        try:
            await bot.send_message(user_id, broadcast_text)
            success += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")
            fail += 1

    await message.reply_text(f"✅ Broadcast complete!\n\n🟢 Success: `{success}`\n🔴 Failed: `{fail}`")

# ──────────────────────────────────────────────
# /krish - Tag all (Admins only)
@bot.on_message(filters.group & filters.command("krish"))
async def tag_all(_, message: Message):
    sender = message.from_user
    chat_id = message.chat.id

    # Check if admin
    admins = [admin.user.id async for admin in bot.get_chat_members(chat_id, filter="administrators")]
    if sender.id not in admins:
        return await message.reply_text("❌ Only admins can use this command.")

    # Tag non-bot members
    try:
        async for member in bot.get_chat_members(chat_id):
            user = member.user
            if user.is_bot:
                continue
            mention = f"[{user.first_name}](tg://user?id={user.id})"
            await bot.send_message(chat_id, f"🌞 Good morning, {mention}!")
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Tagging failed: {e}")
        await message.reply_text("❌ Could not tag all members.")

# ──────────────────────────────────────────────
print("🚀 Bot is running...")
bot.run()
