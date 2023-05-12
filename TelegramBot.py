import logging
import urllib.parse
import urllib.request
import os

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Custom bot token. It's used if there is no BOT_TOKEN environment variable.
BOT_TOKEN = ""

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

#Helper functions
def get_image_filename(url: str) -> str:
    # Parse the URL to get the image filename and extension
    parsed_url = urllib.parse.urlparse(url)
    pathname, extension = os.path.splitext(parsed_url.path)
    cnt = 0
    for index, char in enumerate(pathname):
        if char == '/':
            cnt = index + 1

    # If the URL has a valid extension for an image file, return True
    if extension and extension[1:].lower() in {"jpg", "jpeg", "png", "gif"}:
        return pathname[cnt:] + extension
    else:
        return ""
    
def get_bot_token() -> str:
    token = os.environ.get("BOT_TOKEN")
    if token:
        return token
    return BOT_TOKEN

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(f"Hello {update.effective_user.name}! I am a bot that sends you back an image when you provide me with it's URL. Go ahead and try it!")

# Our message handler
async def image_echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Checks whether the message is an image URL. If yes, downloads it and sends it back to user."""
    filename = get_image_filename(update.message.text)
    if not filename:
        await update.message.reply_text("The URL you provided does not belong to an image. Please try giving me a valid image URL.")
    else:
        # Download image
        with urllib.request.urlopen(update.message.text) as response, open(filename, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        # Send the image
        with open(filename, 'rb') as in_file:
            await context.bot.send_photo(update.message.chat_id, in_file)
        

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(get_bot_token()).build()

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Add the image echo handler
    application.add_handler(MessageHandler((filters.PHOTO & ~filters.COMMAND) | filters.TEXT, image_echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()