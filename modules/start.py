import os

from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ContextTypes,
)


load_dotenv()


BOT_NAME = "Sakura Music"

BOT_USERNAME = os.getenv(
    "BOT_USERNAME",
    "SakuraMusicBot"
)


DEVELOPER = (
    "https://t.me/oneofrisuofc"
)



# =========================
# MAIN MENU
# =========================

def main_keyboard():

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "➕ Add to Group",
                    url=(
                        f"https://t.me/"
                        f"{BOT_USERNAME}"
                        "?startgroup=true"
                    )
                )
            ],
            [
                InlineKeyboardButton(
                    "❓ Help",
                    callback_data="sakura_help"
                ),

                InlineKeyboardButton(
                    "👨‍💻 Developer",
                    url=DEVELOPER
                )
            ]
        ]
    )



def main_text():

    return (
        "🌸 <b>Sakura Music</b>\n\n"

        "Your personal music companion.\n\n"

        "🎧 Search your favorite songs\n"
        "🎵 High quality audio\n"
        "✨ Fast • Simple • Clean\n\n"

        "Gunakan <code>/search</code> "
        "untuk mulai mencari musik."
    )



# =========================
# START
# =========================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        main_text(),
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )



# =========================
# HELP
# =========================

async def help_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query


    await query.answer()



    text = (

        "🌸 <b>Sakura Music Help</b>\n\n"

        "🎵 <b>Cara menggunakan:</b>\n\n"

        "1. Gunakan command:\n"
        "<code>/search</code>\n\n"

        "2. Masukkan judul lagu "
        "atau nama artis.\n\n"

        "3. Pilih lagu dari hasil pencarian.\n\n"

        "4. Sakura Music akan menyiapkan "
        "audio untuk kamu.\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "📌 <b>Commands</b>\n"

        "/start - Menu utama\n"
        "/search - Cari lagu\n"
        "/help - Bantuan\n\n"

        "🌸 Enjoy your music."
    )



    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="sakura_back"
                )
            ]
        ]
    )


    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )



# =========================
# BACK
# =========================

async def back_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query


    await query.answer()



    await query.edit_message_text(
        main_text(),
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )