import nest_asyncio
import asyncio
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)

nest_asyncio.apply()

TOKEN = "8172311063:AAEzTaO163ClmTtCrjh-wDplMrPi3kaHfcg"
GROUP_ID = -1002619230970
CACHE_FILE = "message_cache.txt"
RESULTS_PER_PAGE = 10
ADMIN_IDS = [6192971829]  # Replace with your admin user ID
USER_IDS_FILE = "id.txt"  # File to store user IDs (one per line)
WELCOME_IMAGE_PATH = "welcome.png"  # Path to your welcome image

def save_to_cache(message_id: int, caption: str):
    with open(CACHE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{message_id}||{caption.strip()}\n")

def load_user_ids():
    """Load user IDs from file (one ID per line)"""
    if not os.path.exists(USER_IDS_FILE):
        return set()
    
    with open(USER_IDS_FILE, "r") as f:
        return {int(line.strip()) for line in f if line.strip().isdigit()}

def save_user_id(user_id: int):
    """Save user ID to file if not already present (one ID per line)"""
    existing_ids = load_user_ids()
    if user_id not in existing_ids:
        with open(USER_IDS_FILE, "a") as f:
            f.write(f"{user_id}\n")

def search_multiple_matches(user_query: str):
    results = []
    if not os.path.exists(CACHE_FILE):
        return results
    
    search_words = user_query.lower().split()

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in reversed(lines):
            try:
                msg_id, caption = line.strip().split("||", 1)
                caption_lower = caption.lower()
                
                if all(word in caption_lower for word in search_words):
                    results.append((int(msg_id), caption))
            except Exception as e:
                print(f"Skipping invalid line: {line} | Error: {e}")
    return results

def format_small_text(text: str) -> str:
    small_map = {
        'a': 'ᵃ', 'b': 'ᵇ', 'c': 'ᶜ', 'd': 'ᵈ', 'e': 'ᵉ', 
        'f': 'ᶠ', 'g': 'ᵍ', 'h': 'ʰ', 'i': 'ⁱ', 'j': 'ʲ',
        'k': 'ᵏ', 'l': 'ˡ', 'm': 'ᵐ', 'n': 'ⁿ', 'o': 'ᵒ',
        'p': 'ᵖ', 'q': 'ʷ', 'r': 'ʳ', 's': 'ˢ', 't': 'ᵗ',
        'u': 'ᵘ', 'v': 'ᵛ', 'w': 'ʷ', 'x': 'ˣ', 'y': 'ʸ',
        'z': 'ᶻ', 'A': 'ᴬ', 'B': 'ᴮ', 'C': 'ᶜ', 'D': 'ᴰ',
        'E': 'ᴱ', 'F': 'ᶠ', 'G': 'ᴳ', 'H': 'ᴴ', 'I': 'ᴵ',
        'J': 'ᴶ', 'K': 'ᴷ', 'L': 'ᴸ', 'M': 'ᴹ', 'N': 'ᴺ',
        'O': 'ᴼ', 'P': 'ᴾ', 'Q': 'ᵠ', 'R': 'ᴿ', 'S': 'ˢ',
        'T': 'ᵀ', 'U': 'ᵁ', 'V': 'ⱽ', 'W': 'ᵂ', 'X': 'ˣ',
        'Y': 'ʸ', 'Z': 'ᶻ', '0': '⁰', '1': '¹', '2': '²',
        '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷',
        '8': '⁸', '9': '⁹', ' ': ' ', '(': '⁽', ')': '⁾'
    }
    return ''.join(small_map.get(c, c) for c in text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    save_user_id(user_id)
    
    first_name = update.message.from_user.first_name or "User"
    
    welcome_text = (
        f"Hey 👋 {first_name}\n\n"
        "🍿 <b>Welcome To The World's Coolest Search Engine!</b>\n\n"
        "Here You Can Request Movie's, Just Sent Movie OR WebSeries Name With Proper <a href='https://www.google.com'>Google</a> Spelling..!!\n\n"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Search movies & webseries", callback_data="search_guide")],
        [InlineKeyboardButton("Share with friends", url=f"https://t.me/share/url?url=https://t.me/{(await context.bot.get_me()).username}")]
    ])
    
    if os.path.exists(WELCOME_IMAGE_PATH):
        with open(WELCOME_IMAGE_PATH, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=welcome_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
    else:
        await update.message.reply_text(
            welcome_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    help_text = """
Admin Commands:
/message_catch - Get the message cache file
/chat_id - Get the user IDs file
/message - Broadcast message to all users
/upload_caches - Upload new cache file (replace existing)
/upload_ids - Upload new user IDs file (replace existing)
/help - Show this help message
"""
    await update.message.reply_text(help_text)

async def message_catch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    try:
        if not os.path.exists(CACHE_FILE):
            await update.message.reply_text("No cache file exists yet.")
            return
            
        with open(CACHE_FILE, "rb") as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename="message_cache.txt"
            )
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def chat_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    try:
        if not os.path.exists(USER_IDS_FILE):
            await update.message.reply_text("No user IDs file exists yet.")
            return
            
        with open(USER_IDS_FILE, "rb") as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename="id.txt"
            )
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def upload_caches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    await update.message.reply_text(
        "Please upload the new cache file (must be named 'message_cache.txt'). I will replace the existing one.\n\n"
        "Only document files will be accepted. Any other message type will be rejected."
    )
    context.user_data['waiting_for_cache_upload'] = True

async def upload_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    await update.message.reply_text(
        "Please upload the new user IDs file (must be named 'id.txt'). I will replace the existing one.\n\n"
        "Only document files will be accepted. Any other message type will be rejected."
    )
    context.user_data['waiting_for_ids_upload'] = True

async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not update.message.document:
        if context.user_data.get('waiting_for_cache_upload', False) or context.user_data.get('waiting_for_ids_upload', False):
            await update.message.reply_text("❌ Please upload a file document. Text messages, photos or other media are not accepted for this operation.")
            return

    if context.user_data.get('waiting_for_cache_upload', False):
        if update.message.document.file_name != "message_cache.txt":
            await update.message.reply_text("❌ Invalid filename! File must be named 'message_cache.txt'")
            context.user_data['waiting_for_cache_upload'] = False
            return
            
        file = await context.bot.get_file(update.message.document)
        await file.download_to_drive(CACHE_FILE)
        await update.message.reply_text("✅ Cache file has been successfully updated!")
        context.user_data['waiting_for_cache_upload'] = False
        return

    if context.user_data.get('waiting_for_ids_upload', False):
        if update.message.document.file_name != "id.txt":
            await update.message.reply_text("❌ Invalid filename! File must be named 'id.txt'")
            context.user_data['waiting_for_ids_upload'] = False
            return
            
        file = await context.bot.get_file(update.message.document)
        await file.download_to_drive(USER_IDS_FILE)
        await update.message.reply_text("✅ User IDs file has been successfully updated!")
        context.user_data['waiting_for_ids_upload'] = False
        return

async def message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    await update.message.reply_text(
        "I am ready for sending broadcast message, please send me anything (text, photo, or video) and I will send it to all users.\n\n"
        "After sending this message, you'll need to use /message command again to send another broadcast."
    )
    
    context.user_data['waiting_for_broadcast'] = True

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_broadcast', False):
        user_id = update.message.from_user.id
        if user_id in ADMIN_IDS:
            message_text = update.message.text or ""
            media = None
            media_type = None

            if update.message.photo:
                media = update.message.photo[-1].file_id
                media_type = 'photo'
            elif update.message.video:
                media = update.message.video.file_id
                media_type = 'video'

            user_ids = load_user_ids()
            successful = 0
            blocked = 0
            total_users = len(user_ids)

            for uid in user_ids:
                try:
                    if media:
                        if media_type == 'photo':
                            await context.bot.send_photo(uid, photo=media, caption=message_text)
                        elif media_type == 'video':
                            await context.bot.send_video(uid, video=media, caption=message_text)
                    else:
                        await context.bot.send_message(uid, message_text)
                    successful += 1
                except Exception as e:
                    print(f"Error sending message to {uid}: {e}")
                    blocked += 1

            await update.message.reply_text(
                f"Broadcast sent successfully!\n"
                f"Message sent to {successful} users.\n"
                f"Blocked users: {blocked}\n"
                f"Total users: {total_users}\n\n"
                f"To send another broadcast, use /message command again."
            )
            
            context.user_data['waiting_for_broadcast'] = False
        else:
            await update.message.reply_text("You are not authorized to send this message.")

async def cache_group_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.caption or update.message.text:
        message_id = update.message.message_id
        caption = update.message.caption or update.message.text
        print(f"Saving message ID {message_id} with caption: {caption[:50]}")
        save_to_cache(message_id, caption)

user_sessions = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    save_user_id(user_id)
    
    if context.user_data.get('waiting_for_broadcast', False):
        await handle_broadcast(update, context)
        return
    
    if context.user_data.get('waiting_for_cache_upload', False) or context.user_data.get('waiting_for_ids_upload', False):
        await handle_file_upload(update, context)
        return
    
    user_message = update.message.text.strip()
    first_name = update.message.from_user.first_name or "User"
    print(f"User searched: '{user_message}'")
    matches = search_multiple_matches(user_message)

    if not matches:
        await update.message.reply_text(
            f"😕No matching content found.\n"
            f"Maybe spelling is wrong.\n"
            f"Go to <a href='https://www.google.com'>Google</a> and check correct spelling\n"
            f"Otherwise comment @U_P_DATE With Correct Name",
            parse_mode='HTML'
        )
        return

    user_sessions[user_id] = {
        "all_matches": matches,
        "current_page": 0,
        "search_msg": update.message.message_id,
        "first_name": first_name,
        "chat_id": update.message.chat_id,
        "sent_videos": [],
        "user_query": user_message,
        "is_private": update.message.chat.type == "private"
    }

    await show_results_page(update, context, user_id)

async def show_results_page(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    session = user_sessions[user_id]
    matches = session["all_matches"]
    page = session["current_page"]
    start_idx = page * RESULTS_PER_PAGE
    end_idx = start_idx + RESULTS_PER_PAGE
    page_matches = matches[start_idx:end_idx]

    buttons = []
    for msg_id, caption in page_matches:
        small_caption = format_small_text(caption)
        button = InlineKeyboardButton(
            text=small_caption,
            callback_data=f"vid_{msg_id}"
        )
        buttons.append([button])

    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"nav_{page-1}"))
    if end_idx < len(matches):
        navigation_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"nav_{page+1}"))
    
    if navigation_buttons:
        buttons.append(navigation_buttons)

    message_text = f"🎬 Results for: '{session['user_query']}' (Page {page+1})"
    
    if "button_msg" in session:
        try:
            await context.bot.edit_message_text(
                chat_id=session["chat_id"],
                message_id=session["button_msg"],
                text=message_text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except:
            button_msg = await context.bot.send_message(
                chat_id=session["chat_id"],
                text=message_text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            session["button_msg"] = button_msg.message_id
    else:
        button_msg = await context.bot.send_message(
            chat_id=session["chat_id"],
            text=message_text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        session["button_msg"] = button_msg.message_id

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data.startswith("vid_"):
        msg_id = int(query.data.split("_")[1])
        session = user_sessions.get(user_id)
        
        if session:
            try:
                sent_msg = await context.bot.copy_message(
                    chat_id=session["chat_id"],
                    from_chat_id=GROUP_ID,
                    message_id=msg_id
                )
                session["sent_videos"].append(sent_msg.message_id)
                
                # Schedule deletion after 1 minute
                asyncio.create_task(delete_video_after_delay(
                    context=context,
                    chat_id=session["chat_id"],
                    message_id=sent_msg.message_id,
                    delay=60  # 60 seconds = 1 minute
                ))
                
                asyncio.create_task(delete_messages_after_delay(
                    context, 
                    session,
                    delay=60
                ))
            except Exception as e:
                print(f"Error: {e}")
                await query.message.reply_text("⚠️ Failed to send video. It may no longer be available.")

    elif query.data.startswith("nav_"):
        page = int(query.data.split("_")[1])
        if user_id in user_sessions:
            user_sessions[user_id]["current_page"] = page
            await show_results_page(update, context, user_id)
    
    elif query.data == "search_guide":
        search_guide_text = (
            "📨 <b>Sᴇɴᴅ Mᴏᴠɪᴇ Oʀ Sᴇʀɪᴇs Nᴀᴍᴇ ᴀɴᴅ Yᴇᴀʀ Aꜱ Pᴇʀ Gᴏᴏɢʟᴇ Sᴘᴇʟʟɪɴɢ..!!</b> 👍\n\n"
            "⚠️ <b>Exᴀᴍᴘʟᴇ Fᴏʀ Mᴏᴠɪᴇ</b> 👇\n\n"
            "👉 Jailer\n"
            "👉 Jailer 2023\n\n"
            "⚠️ <b>Exᴀᴍᴘʟᴇ Fᴏʀ WᴇʙSᴇʀɪᴇs</b> 👇\n\n"
            "👉 Stranger Things\n"
            "👉 Stranger Things S02 E04\n\n"
            "⚠️ <b>ᴅᴏɴ'ᴛ ᴀᴅᴅ ᴇᴍᴏᴊɪꜱ ᴀɴᴅ ꜱʏᴍʙᴏʟꜱ ɪɴ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ, ᴜꜱᴇ ʟᴇᴛᴛᴇʀꜱ ᴏɴʟʏ..!!</b> ❌"
        )
        await query.message.reply_text(search_guide_text, parse_mode='HTML')

async def delete_video_after_delay(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int):
    """Delete a specific video message after a delay"""
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    except Exception as e:
        print(f"Error deleting video message {message_id}: {e}")

async def delete_messages_after_delay(context: ContextTypes.DEFAULT_TYPE, session_data: dict, delay: int):
    await asyncio.sleep(delay)
    
    try:
        # Only delete messages for private chats
        if session_data.get("is_private", False):
            try:
                await context.bot.delete_message(
                    chat_id=session_data["chat_id"],
                    message_id=session_data["button_msg"]
                )
                
                # Delete all sent videos
                for msg_id in session_data.get("sent_videos", []):
                    try:
                        await context.bot.delete_message(
                            chat_id=session_data["chat_id"],
                            message_id=msg_id
                        )
                    except:
                        pass
                
                # Send the final message only in private chats
                await context.bot.send_message(
                    chat_id=session_data["chat_id"],
                    text=f"👤 Dear {session_data['first_name']}, Your message has been removed due to copyright concerns. If you need the content again, please submit a request."
                )
            except:
                pass
    except Exception as e:
        print(f"Error deleting messages: {e}")

async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("message_catch", message_catch))
    app.add_handler(CommandHandler("chat_id", chat_id_command))
    app.add_handler(CommandHandler("message", message_command))
    app.add_handler(CommandHandler("upload_caches", upload_caches))
    app.add_handler(CommandHandler("upload_ids", upload_ids))
    app.add_handler(MessageHandler(
        (filters.CAPTION | filters.TEXT) & filters.ChatType.GROUPS, 
        cache_group_messages
    ))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VIDEO & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL & ~filters.COMMAND, handle_file_upload))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
