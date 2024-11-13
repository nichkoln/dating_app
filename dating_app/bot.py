import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo # pylint: disable=no-name-in-module
from telegram.ext import Application, CommandHandler, CallbackContext

BOT_TOKEN = ''
WEB_APP_URL = ''  

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None: # pylint: disable=unused-argument
    
    user = update.message.from_user
    web_app_url_with_params = f"{WEB_APP_URL}?id={user.id}&first_name={user.first_name}&last_name={user.last_name}&username={user.username}"
    
    keyboard = [
        [
            InlineKeyboardButton("Open Web App", web_app=WebAppInfo(url=web_app_url_with_params))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Welcome! Click the button below to open the Web App:', reply_markup=reply_markup)

async def send_message(user_id: int, text: str, url: str) -> None:
    """_summary_

    Args:
        user_id (int): _description_
        text (str): _description_
        url (str): _description_
    """
    application = Application.builder().token(BOT_TOKEN).build()
    web_app_url_with_params = f"{url}?id={user_id}"
    keyboard = [
        [
            InlineKeyboardButton("Open Web App", web_app=WebAppInfo(url=web_app_url_with_params))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await application.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == '__main__':
    main()
