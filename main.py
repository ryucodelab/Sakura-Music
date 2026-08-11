import logging
import asyncio

from dotenv import load_dotenv

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from modules.start import (
    start_command,
    help_callback,
    back_callback,
)

from modules.sakura import (
    search_command,
    search_song,
    sakura_button,
)


load_dotenv()


logging.basicConfig(
    format=(
        "%(asctime)s - "
        "%(name)s - "
        "%(levelname)s - "
        "%(message)s"
    ),
    level=logging.INFO
)


from os import getenv


BOT_TOKEN = getenv(
    "BOT_TOKEN"
)



async def help_command(
    update,
    context
):

    await update.message.reply_text(
        "🌸 Gunakan /search untuk mencari musik."
    )



async def run():

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )



    # START

    app.add_handler(
        CommandHandler(
            "start",
            start_command
        )
    )



    # SEARCH

    app.add_handler(
        CommandHandler(
            "search",
            search_command
        )
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search_song
        )
    )



    # HELP

    app.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )



    # CALLBACK BUTTON
    # Handler spesifik (sakura_help, sakura_back) HARUS didaftarkan
    # sebelum handler umum "^sakura_" di bawah, karena PTB mengecek
    # handler sesuai urutan didaftarkan dan berhenti di match pertama.

    app.add_handler(
        CallbackQueryHandler(
            help_callback,
            pattern="^sakura_help$"
        )
    )


    app.add_handler(
        CallbackQueryHandler(
            back_callback,
            pattern="^sakura_back$"
        )
    )


    app.add_handler(
        CallbackQueryHandler(
            sakura_button,
            pattern="^sakura_"
        )
    )



    print(
        "🌸 Sakura Music Running..."
    )


    await app.initialize()

    await app.start()

    await app.updater.start_polling()


    await asyncio.Event().wait()



if __name__ == "__main__":

    asyncio.run(
        run()
    )
