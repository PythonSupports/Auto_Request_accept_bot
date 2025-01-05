from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from motor.motor_asyncio import AsyncIOMotorClient  
from os import environ as env
import asyncio, datetime, time


ACCEPTED_TEXT = "𝐇𝐄𝐘 {user}\n\n𝐘our 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐅𝐨𝐫 {chat} 𝐈𝐬 𝐀𝐜𝐜𝐞𝐩𝐭𝐞𝐝 ✅"
START_TEXT = "𝐇𝐚𝐢 {}\n\n𝐈 𝐚𝐦 𝐀𝐮𝐭𝐨 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐀𝐜𝐜𝐞𝐩𝐭 𝐁𝐨𝐭 𝐖𝐨𝐫𝐤𝐢𝐧𝐠 𝐅𝐨𝐫 𝐀𝐥𝐥 𝐂𝐡𝐚𝐧𝐧𝐞𝐥𝐬. 𝐀𝐝𝐝 𝐌𝐞 𝐈𝐧 𝐘𝐨𝐮𝐫 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐓𝐨 𝐔𝐬𝐞."

# Environment variables for configuration
API_ID = int(env.get('API_ID'))
API_HASH = env.get('API_HASH')
BOT_TOKEN = env.get('BOT_TOKEN')
DB_URL = env.get('DB_URL')
ADMINS = int(env.get('ADMINS'))

# MongoDB setup
Dbclient = AsyncIOMotorClient(DB_URL)
Cluster = Dbclient['Cluster0']
Data = Cluster['users']

# Initialize the bot
Bot = Client(name='AutoAcceptBot', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@Bot.on_message(filters.command("start") & filters.private)                    
async def start_handler(c, m):
    user_id = m.from_user.id
    if not await Data.find_one({'id': user_id}):
        await Data.insert_one({'id': user_id})
    button = [[        
        InlineKeyboardButton('𝐔𝐩𝐝𝐚𝐭𝐞𝐬🪐, url=' https://t.me/krishnetwork '),
        InlineKeyboardButton('𝐒𝐮𝐩𝐩𝐨𝐫𝐭💗, url=' https://t.me/krishsupport ')
    ]]
    return await m.reply_text(
        text=START_TEXT.format(m.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(button)
    )

@Bot.on_message(filters.command(["𝐛𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭", "users"]) & filters.user(𝐀𝐃𝐌𝐈𝐍𝐒))  
async def broadcast(c, m):
    if m.text == "/users":
        total_users = await Data.count_documents({})
        return await m.reply(f"Total Users: {total_users}")

    b_msg = m.reply_to_message
    sts = await m.reply_text("𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭𝐢𝐧𝐠 𝐲𝐨𝐮𝐫 𝐦𝐞𝐬𝐬𝐚𝐠𝐞𝐬...")
    users = Data.find({})
    total_users = await Data.count_documents({})
    𝐝𝐨𝐧𝐞, 𝐟𝐚𝐢𝐥𝐞𝐝, success = 0, 0, 0
    start_time = time.time()

    async for user in users:
        user_id = int(user['id'])
        try:
            await b_msg.copy(chat_id=user_id)
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await b_msg.copy(chat_id=user_id)
            success += 1
        except InputUserDeactivated:
            await Data.delete_many({'id': user_id})
            failed += 1
        except UserIsBlocked:
            failed += 1
        except PeerIdInvalid:
            await Data.delete_many({'id': user_id})
            failed += 1
        except Exception:
            failed += 1
        done += 1
        if not 𝐬𝐮𝐜𝐜𝐞𝐬𝐬20:
            await sts.edit(f"𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐢𝐧 𝐩𝐫𝐨𝐠𝐫𝐞𝐬𝐬:\n\nTotal 𝐔𝐬𝐞𝐫𝐬 {total_users}\𝐧𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}")

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.delete()
    await m.reply_text(
        f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}",
        quote=True
    )

@Bot.on_chat_join_request()
async def req_accept(c, m):
    user_id = m.from_user.id
    chat_id = m.chat.id
    if not await Data.find_one({'id': user_id}):
        await Data.insert_one({'id': user_id})
    await c.approve_chat_join_request(chat_id, user_id)
    try:
        await c.send_message(user_id, accepted_text.format(user=m.from_user.mention, chat=m.chat.title))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    Bot.start()
    print("Bot is running...")
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(1))  # Short delay for initialization
    idle()  # Keeps the bot running
    Bot.stop()
