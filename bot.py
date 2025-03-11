# bot.py
import logging
from telegram import Update, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ChatJoinRequestHandler,
)
import pymongo
import requests
from config import BOT_TOKEN, OWNER_ID, MONGO_URI

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# MongoDB setup
client = pymongo.MongoClient(MONGO_URI)
db = client['telegram_bot']
accepted_collection = db['accepted_members']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a start message with a welcome text, video, and bot invite link."""
    chat_id = update.message.chat_id
    start_text = (
        "**Hello! Welcome to the Auto Accept Bot.**\n\n"
        "✅ I automatically approve join requests for groups & channels.\n"
        "✅ I send a DM to notify the user upon approval.\n"
        "✅ The owner can use `/broadcast` to send messages to all accepted members.\n\n"
        "📌 **Add me to your group/channel:** [Click Here](https://t.me/YourBotUsername?startgroup=true)"
    )
    
    # Send the start message
    await update.message.reply_text(start_text, parse_mode="Markdown", disable_web_page_preview=True)

    # Download the video and send it
    video_url = "https://files.catbox.moe/1cz1po.mp4"
    video_path = "start_video.mp4"

    try:
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(video_path, "wb") as video_file:
                for chunk in response.iter_content(chunk_size=1024):
                    video_file.write(chunk)
            await context.bot.send_video(chat_id=chat_id, video=InputFile(video_path))
    except Exception as e:
        logger.error(f"Failed to send start video: {e}")

async def handle_chat_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles join requests, approves them, and notifies the user."""
    join_request = update.chat_join_request
    if join_request:
        chat_id = join_request.chat.id
        user_id = join_request.from_user.id
        username = join_request.from_user.username or join_request.from_user.full_name

        try:
            await context.bot.approve_chat_join_request(chat_id, user_id)
            logger.info(f"Approved join request for {username} in chat {chat_id}")

            chat_type = join_request.chat.type
            message_text = "Your request has been accepted!"
            if chat_type in ["group", "supergroup"]:
                message_text = "Your **group** request has been accepted!"
            elif chat_type == "channel":
                message_text = "Your **channel** request has been accepted!"

            try:
                await context.bot.send_message(chat_id=user_id, text=message_text, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Failed to send DM to {username}: {e}")

            accepted_collection.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {"$set": {"username": username}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error processing join request for {username}: {e}")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows the owner to send a broadcast message to all accepted members."""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if context.args:
        broadcast_text = " ".join(context.args)
    else:
        await update.message.reply_text("Please provide a message to broadcast.")
        return

    accepted_members = accepted_collection.find()
    count = 0
    for member in accepted_members:
        try:
            await context.bot.send_message(chat_id=member["user_id"], text=broadcast_text)
            count += 1
        except Exception as e:
            logger.error(f"Failed to send message to {member.get('username', 'unknown')} ({member['user_id']}): {e}")

    await update.message.reply_text(f"Broadcast message sent to {count} members.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(ChatJoinRequestHandler(handle_chat_join_request))
    application.add_handler(CommandHandler("broadcast", broadcast_command))

    application.run_polling()

if __name__ == '__main__':
    main()
