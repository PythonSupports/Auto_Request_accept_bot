import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatJoinRequest

# Initialize bot with environment variables
pr0fess0r_99 = Client(
    "𝗕𝗼𝘁 𝗦𝘁𝗮𝗿𝘁𝗲𝗱 𝗣𝗹𝗲𝗮𝘀𝗲 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗯𝗲 𝗢𝗽𝘂𝘀𝗧𝗲𝗰𝗵𝘇",
    bot_token=os.environ["BOT_TOKEN"],
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"]
)

# Environment variables for chat ID and custom messages
CHAT_ID = int(os.environ.get("CHAT_ID", 0))
TEXT = os.environ.get("APPROVED_WELCOME_TEXT", "Hello {mention}\nWelcome to {title}\n\nYou have been auto-approved!")
APPROVED = os.environ.get("APPROVED_WELCOME", "on").lower()

# Handle the `/start` command
@pr0fess0r_99.on_message(filters.private & filters.command(["start"]))
async def start(client: pr0fess0r_99, message: Message):
    # Define buttons for user interaction
    buttons = [
        [
            InlineKeyboardButton("𝚄𝙿𝙳𝙰𝚃𝙴𝚉", url="https://t.me/Krishnetwork"),
            InlineKeyboardButton("𝚂𝚄𝙿𝙿𝙾𝚁𝚃", url="https://t.me/krishnetwork")
        ],
        [
            InlineKeyboardButton("𝚂𝚄𝙱𝚂𝙲𝚁𝙸𝙱𝙴", url="https://www.youtube.com/@Coderkrishsupport")
        ]
    ]
    
    # Reply with welcome text and buttons
    await message.reply_text(
        text="**𝙷𝙴𝙻𝙻𝙾...⚡\n\n𝙸𝙰𝙼 𝙰 𝚂𝙸𝙼𝙿𝙻𝙴 𝚃𝙴𝙻𝙴𝙶𝚁𝙰𝙼 𝙰𝚄𝚃𝙾 𝚁𝙴𝚀𝚄𝙴𝚂𝚃 𝙰𝙲𝙲𝙴𝙿𝚃 𝙱𝙾𝚃.\n𝙵𝙾𝚁 𝚈𝙾𝚄𝚁 𝙲𝙷𝙰𝚃𝚂 𝙲𝚁𝙴𝙰𝚃𝙴 𝙾𝙽𝙴 𝙱𝙾𝚃... \n𝚅𝙸𝙳𝙴𝙾 𝙾𝙽 𝙼𝚈 𝚈𝙾𝚄𝚃𝚄𝙱𝙴 𝙲𝙷𝙰𝙽𝙽𝙴𝙻**",
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )

# Handle new chat join requests
@pr0fess0r_99.on_chat_join_request(filters.chat(CHAT_ID))
async def autoapprove(client: pr0fess0r_99, message: ChatJoinRequest):
    chat = message.chat  # Get chat information
    user = message.from_user  # Get user who requested to join
    
    # Log user joining
    print(f"{user.first_name} 𝙹𝙾𝙸𝙽𝙴𝙳 ⚡")

    # Approve chat join request
    await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    
    # Send welcome message if approval is enabled
    if APPROVED == "on":
        await client.send_message(
            chat_id=chat.id, 
            text=TEXT.format(mention=user.mention, title=chat.title)
        )

# Start the bot
print("𝗕𝗼𝘁 𝗦𝘁𝗮𝗿𝘁𝗲𝗱 𝗣𝗹𝗲𝗮𝘀𝗲 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗯𝗲 𝗰𝗼𝗱𝗲𝗿 𝗸𝗿𝗶𝘀𝗵 𝘀𝘂𝗽𝗽𝗼𝗿𝘁")
pr0fess0r_99.run()
