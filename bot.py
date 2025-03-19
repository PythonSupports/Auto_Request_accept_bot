import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatJoinRequest

# Initialize bot
pr0fess0r_99 = Client(
    "Auto Accept Bot",
    bot_token=os.environ["BOT_TOKEN"],
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"]
)

# Environment Variables
CHAT_ID = int(os.environ.get("CHAT_ID", 0))
APPROVED_WELCOME_TEXT = os.environ.get("APPROVED_WELCOME_TEXT", "Hello {mention}\nWelcome to {title}\n\nYou have been auto-approved!")
APPROVED = os.environ.get("APPROVED_WELCOME", "on").lower()
BROADCAST_USERS_DB = set()  # Store accepted users for broadcasting

# ✅ Start Command
@pr0fess0r_99.on_message(filters.private & filters.command(["start"]))
async def start(client: pr0fess0r_99, message: Message):
    buttons = [
        [
            InlineKeyboardButton("𝚄𝙿𝙳𝙰𝚃𝙴𝚉", url="https://t.me/Krishnetwork"),
            InlineKeyboardButton("𝚂𝚄𝙿𝙿𝙾𝚁𝚃", url="https://t.me/krishnetwork")
        ],
        [
            InlineKeyboardButton("𝚂𝚄𝙱𝚂𝙲𝚁𝙸𝙱𝙴", url="https://www.youtube.com/@Coderkrishsupport")
        ]
    ]
    await message.reply_video(
        video="https://files.catbox.moe/81j930.mp4",
        caption="**𝙷𝙴𝙻𝙻𝙾...⚡\n\n𝙸𝙰𝙼 𝙰 𝚂𝙸𝙼𝙿𝙻𝙴 𝚃𝙴𝙻𝙴𝙶𝚁𝙰𝙼 𝙰𝚄𝚃𝙾 𝚁𝙴𝚀𝚄𝙴𝚂𝚃 𝙰𝙲𝙲𝙴𝙿𝚃 𝙱𝙾𝚃.\n𝙵𝙾𝚁 𝚈𝙾𝚄𝚁 𝙲𝙷𝙰𝚃𝚂 𝙲𝚁𝙴𝙰𝚃𝙴 𝙾𝙽𝙴 𝙱𝙾𝚃... \n𝚅𝙸𝙳𝙴𝙾 𝙾𝙽 𝙼𝚈 𝚈𝙾𝚄𝚃𝚄𝙱𝙴 𝙲𝙷𝙰𝙽𝙽𝙴𝙻**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ✅ Auto Accept Group & Channel Requests + Send DM
@pr0fess0r_99.on_chat_join_request()
async def autoapprove(client: pr0fess0r_99, request: ChatJoinRequest):
    chat = request.chat
    user = request.from_user

    # Approve the request
    await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    print(f"Approved: {user.first_name} ({user.id}) in {chat.title}")

    # Store user for broadcasting
    BROADCAST_USERS_DB.add(user.id)

    # Send DM to the user
    if APPROVED == "on":
        try:
            await client.send_message(
                chat_id=user.id,
                text=APPROVED_WELCOME_TEXT.format(mention=user.mention, title=chat.title)
            )
        except Exception as e:
            print(f"Could not send DM to {user.first_name}: {e}")

# ✅ Admin Broadcast Command
@pr0fess0r_99.on_message(filters.private & filters.user(int(os.environ.get("OWNER_ID", 0))) & filters.command("broadcast"))
async def broadcast(client: pr0fess0r_99, message: Message):
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        await message.reply_text("❌ **Usage:** `/broadcast Your Message`")
        return

    broadcast_message = text[1]
    success_count = 0

    for user_id in BROADCAST_USERS_DB:
        try:
            await client.send_message(chat_id=user_id, text=broadcast_message)
            success_count += 1
            await asyncio.sleep(0.5)  # Delay to avoid spam
        except Exception as e:
            print(f"Error sending to {user_id}: {e}")

    await message.reply_text(f"✅ **Broadcast Sent to {success_count} Users!**")

# ✅ Tag All Members with "Good Morning" on /krish
@pr0fess0r_99.on_message(filters.group & filters.command("krish"))
async def tag_all(client: pr0fess0r_99, message: Message):
    chat_id = message.chat.id
    sender = message.from_user

    # Check if sender is admin
    admins = [admin.user.id async for admin in client.get_chat_members(chat_id, filter="administrators")]
    if sender.id not in admins:
        await message.reply_text("❌ **Only admins can use this command!**")
        return

    # Fetch all members
    members = [member.user for member in client.get_chat_members(chat_id)]
    
    # Send greeting message with mentions
    for user in members:
        if user.is_bot:
            continue
        try:
            mention = f"[{user.first_name}](tg://user?id={user.id})"
            await client.send_message(chat_id, f"Good morning to everyone ❤️👌 {mention}")
            await asyncio.sleep(1)  # Delay to avoid spam
        except Exception as e:
            print(f"Error tagging {user.first_name}: {e}")

# ✅ Start the Bot
print("🚀 Bot Started Successfully!")
pr0fess0r_99.run()
