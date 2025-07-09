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
GROUP_ID = -1002333766560
CACHE_FILE = "message_cache.txt"
RESULTS_PER_PAGE = 10
ADMIN_IDS = [6192971829]  # Replace with your admin user ID
USER_IDS_FILE = "id.txt"  # File to store user IDs

def save_to_cache(message_id: int, caption: str):
    with open(CACHE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{message_id}||{caption.strip()}\n")

def save_user_id(user_id: int):
    if not os.path.exists(USER_IDS_FILE):
        with open(USER_IDS_FILE, "w") as f:
            f.write(str(user_id) + "\n")
        return
    
    with open(USER_IDS_FILE, "r+") as f:
        existing_ids = {int(line.strip()) for line in f.readlines()}
        if user_id not in existing_ids:
            f.write(str(user_id) + "\n")

# ✅ Modified function for exact matching where all words must exist together
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
    
    await update.message.reply_text(f"🔍 🔍 Send me a movie or web series name, and I'll find related videos for you!! \n "
    
    f" मुझे कोई फ़िल्म या वेब सीरीज़ का नाम भेजो, मैं उससे जुड़े वीडियो ढूंढकर भेजूंगा!    Example :- panchayat  , squid game \n ")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    help_text = """
Admin Commands:
/message_catch - Get the message cache file
/chat_id - Get the user IDs file
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
                filename="user_ids.txt"
            )
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

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
    
    user_message = update.message.text.strip()
    first_name = update.message.from_user.first_name or "User"
    print(f"User searched: '{user_message}'")
    matches = search_multiple_matches(user_message)

    if not matches:
        await update.message.reply_text(f"❌ No matching content found. Please check your spelling or try searching correct spelling on Google. If the spelling is correct and content is still not found, 🖍️ report it to @moviezonehelp with the correct spelling. Your content may become available within a few days, so feel free to request again later.\n " 
        
      f"❌ कोई मेल खाता कंटेंट नहीं मिला। कृपया अपनी वर्तनी जांचें या Google पर खोजें। अगर वर्तनी सही है और फिर भी कंटेंट नहीं मिला, तो 🖍️ कृपया सही वर्तनी के साथ @moviezonehelp पर रिपोर्ट करें। आपका कंटेंट कुछ दिनों में उपलब्ध हो सकता है, इसलिए बाद में दोबारा अनुरोध करें। ")
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

async def delete_messages_after_delay(context: ContextTypes.DEFAULT_TYPE, session_data: dict, delay: int):
    await asyncio.sleep(delay)
    
    try:
        # Only delete messages for private chats
        if session_data.get("is_private", False):
            try:
                await context.bot.delete_message(
                    chat_id=session_data["chat_id"],
                    message_id=session_data["search_msg"]
                )
            except:
                pass
                
            try:
                await context.bot.delete_message(
                    chat_id=session_data["chat_id"],
                    message_id=session_data["button_msg"]
                )
            except:
                pass
            
            for video_msg_id in session_data["sent_videos"]:
                try:
                    await context.bot.delete_message(
                        chat_id=session_data["chat_id"],
                        message_id=video_msg_id
                    )
                except:
                    pass
            
            # Send the final message only in private chats
            await context.bot.send_message(
                chat_id=session_data["chat_id"],
                text=f"👤 Dear {session_data['first_name']}, Your message has been removed due to copyright concerns. If you need the content again, please submit a request. || प्रिय उपभोक्ता, कॉपीराइट कारणों से आपका संदेश हटा दिया गया है। यदि आपको पुनः सामग्री की आवश्यकता हो, तो कृपया अनुरोध भेजें। "
            )
    except Exception as e:
        print(f"Error deleting messages: {e}")

async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("message_catch", message_catch))
    app.add_handler(CommandHandler("chat_id", chat_id_command))
    app.add_handler(MessageHandler(
        (filters.CAPTION | filters.TEXT) & filters.ChatType.GROUPS, 
        cache_group_messages
    ))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
