import os
import re
import time
import uuid
import asyncio
import logging
import requests
import yt_dlp

from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import ContextTypes


load_dotenv()


logger = logging.getLogger(
    "SakuraMusic"
)


API_KEY = os.getenv(
    "SAVENOW_API_KEY"
)


DOWNLOAD_DIR = "downloads"

os.makedirs(
    DOWNLOAD_DIR,
    exist_ok=True
)


BASE_URL = "https://p.savenow.to/ajax"



# ==========================
# STORAGE
# ==========================

waiting = {}

songs_cache = {}

request_count = {}

user_tasks = {}



# ==========================
# CLEAN NAME
# ==========================

def clean_filename(name):

    if not name:
        return "Sakura Music"


    for c in '\\/:*?"<>|':
        name = name.replace(
            c,
            ""
        )

    return name[:100]



# ==========================
# CLEAN TITLE (DISPLAY)
# ==========================
# Menghapus label bawaan YouTube seperti "(Audio)",
# "(Official Video)", "[Lyrics]", dsb, supaya judul yang
# ditampilkan ke user lebih rapi.

TITLE_NOISE_WORDS = (
    r"(?:official|music|audio|video|lyrics?|"
    r"visualizer|mv|hd|hq|4k|full)"
)


TITLE_NOISE_PATTERN = re.compile(
    r"[\(\[]\s*"
    + TITLE_NOISE_WORDS
    + r"(?:\s+" + TITLE_NOISE_WORDS + r")*"
    + r"\s*[\)\]]",
    re.IGNORECASE
)


def clean_title(name):

    if not name:
        return "Unknown"


    cleaned = TITLE_NOISE_PATTERN.sub(
        "",
        name
    )


    cleaned = re.sub(
        r"\s{2,}",
        " ",
        cleaned
    ).strip(" -")


    return cleaned or name



# ==========================
# YT-DLP SEARCH
# ==========================

def youtube_search(
    keyword
):

    options = {

        "quiet": True,

        "extract_flat": True,

        "skip_download": True,

        "noplaylist": True,

        "ignoreerrors": True,

    }


    with yt_dlp.YoutubeDL(
        options
    ) as ydl:


        data = ydl.extract_info(
            f"ytsearch10:{keyword}",
            download=False
        )


    results = []


    for item in data.get(
        "entries",
        []
    ):


        if not item:
            continue


        video_id = item.get(
            "id"
        )


        title = item.get(
            "title",
            "Unknown"
        )


        if video_id:

            results.append(
                {
                    "title": clean_title(title),

                    "url":
                    f"https://youtube.com/watch?v={video_id}"
                }
            )


    if not results:

        raise Exception(
            "Tidak ada hasil"
        )


    return results



# ==========================
# SAVENOW ENGINE
# ==========================

def create_download(
    url
):

    params = {

        "url": url,

        "format": "mp3",

        "apikey": API_KEY,

        "add_info": "1",

        "allow_extended_duration": "1",

        "no_merge": "0"

    }


    response = requests.get(
        f"{BASE_URL}/download.php",
        params=params,
        timeout=30
    )


    response.raise_for_status()


    data = response.json()


    if not data.get(
        "success"
    ):

        raise Exception(
            "Savenow gagal"
        )


    return data



def wait_download(
    download_id
):

    while True:


        response = requests.get(
            f"{BASE_URL}/progress.php",
            params={
                "id": download_id
            },
            timeout=30
        )


        response.raise_for_status()


        data = response.json()


        progress = data.get(
            "progress",
            0
        )


        logger.info(
            f"Sakura progress: {progress}"
        )



        if (
            data.get("success")
            and progress >= 1000
        ):

            return data



        time.sleep(3)



def save_file(
    url,
    filename
):

    filepath = os.path.join(
        DOWNLOAD_DIR,
        filename
    )


    with requests.get(
        url,
        stream=True,
        timeout=120
    ) as response:


        response.raise_for_status()


        with open(
            filepath,
            "wb"
        ) as file:


            for chunk in response.iter_content(
                8192
            ):

                if chunk:

                    file.write(
                        chunk
                    )


    return filepath



def download_youtube(
    url
):


    request = create_download(
        url
    )


    raw_title = request.get(
        "info",
        {}
    ).get(
        "title",
        "Sakura Music"
    )


    title = clean_title(
        clean_filename(
            raw_title
        )
    )



    result = wait_download(
        request["id"]
    )



    download_url = result.get(
        "download_url"
    )



    if not download_url:

        raise Exception(
            "URL audio tidak ditemukan"
        )


    # Nama file dibuat unik (title + uuid) supaya kalau ada
    # dua user download lagu yang sama secara bersamaan,
    # file mereka tidak saling tabrakan/kehapus satu sama lain.

    unique_id = uuid.uuid4().hex[:8]


    filepath = save_file(
        download_url,
        f"{title}_{unique_id}.mp3"
    )


    return filepath, title



# ==========================
# KEYBOARD BUILDER
# ==========================

def build_keyboard(
    songs,
    page=0
):

    per_page = 5

    start = page * per_page

    end = start + per_page


    buttons = []


    for i in range(
        start,
        min(end, len(songs))
    ):

        buttons.append(
            InlineKeyboardButton(
                str(i + 1),
                callback_data=f"sakura_select_{i}"
            )
        )


    navigation = []


    if page > 0:

        navigation.append(
            InlineKeyboardButton(
                "⬅️ Prev",
                callback_data="sakura_prev"
            )
        )


    if end < len(songs):

        navigation.append(
            InlineKeyboardButton(
                "Next ➡️",
                callback_data="sakura_next"
            )
        )


    return InlineKeyboardMarkup(
        [
            buttons,
            navigation,
            [
                InlineKeyboardButton(
                    "❌ Close",
                    callback_data="sakura_close"
                )
            ]
        ]
    )



# ==========================
# SONG LIST TEXT BUILDER
# ==========================
# Dipakai bareng oleh hasil search awal dan handler next/prev,
# supaya teks daftar lagu selalu sinkron dengan halaman yang
# sedang ditampilkan di keyboard.

def build_song_list_text(
    songs,
    page=0
):

    per_page = 5

    start = page * per_page

    end = start + per_page


    text = (
        "🌸 <b>Sakura Music</b>\n\n"
        "🎵 Pilih lagu:\n\n"
    )


    for i in range(
        start,
        min(end, len(songs))
    ):

        text += (
            f"{i + 1}. {songs[i]['title']}\n"
        )


    return text



# ==========================
# SEARCH COMMAND
# ==========================

async def search_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id


    prompt = await update.message.reply_text(
        "🌸 <b>Sakura Music Search</b>\n\n"
        "Masukkan judul lagu atau artis.\n\n"
        "Contoh:\n"
        "<code>Just Pretend Bad Omens</code>",
        parse_mode="HTML"
    )


    # Simpan message_id prompt supaya bisa dihapus begitu
    # user mengirimkan query pencariannya.

    waiting[user_id] = prompt.message_id



# ==========================
# SEARCH PROCESS
# ==========================

async def search_song(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id


    if user_id not in waiting:

        return



    keyword = update.message.text


    prompt_message_id = waiting.pop(
        user_id,
        None
    )


    # Bersihkan pesan prompt "Masukkan judul lagu..." dan pesan
    # query dari user, supaya chat gak numpuk pesan yang udah
    # gak relevan lagi. Dibungkus try/except karena bot mungkin
    # gak punya izin hapus pesan (misal di grup tanpa hak admin).

    try:

        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=prompt_message_id
        )

    except Exception:

        pass


    try:

        await update.message.delete()

    except Exception:

        pass


    status = await update.effective_chat.send_message(
        "🔎 Mencari lagu..."
    )


    try:


        songs = await asyncio.to_thread(
            youtube_search,
            keyword
        )


        songs_cache[user_id] = {

            "songs": songs,

            "page": 0

        }



        await status.edit_text(
            build_song_list_text(
                songs,
                0
            ),
            parse_mode="HTML",
            reply_markup=build_keyboard(
                songs,
                0
            )
        )



    except Exception as e:


        logger.exception(
            "Search error"
        )


        await status.edit_text(
            f"❌ Pencarian gagal, silakan coba lagi.\n\n"
            f"<code>{e}</code>",
            parse_mode="HTML"
        )



# ==========================
# CALLBACK BUTTON
# ==========================

async def sakura_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    uid = query.from_user.id



    if query.data == "sakura_close":

        await query.message.delete()

        return



    if uid not in songs_cache:

        await query.answer(
            "Sesi pencarian sudah kedaluwarsa. Silakan /search ulang.",
            show_alert=True
        )

        return



    data = songs_cache[uid]

    songs = data["songs"]



    # ======================
    # NEXT PAGE
    # ======================

    if query.data == "sakura_next":

        data["page"] += 1


        await query.edit_message_text(
            build_song_list_text(
                songs,
                data["page"]
            ),
            parse_mode="HTML",
            reply_markup=build_keyboard(
                songs,
                data["page"]
            )
        )

        return



    # ======================
    # PREV PAGE
    # ======================

    if query.data == "sakura_prev":

        data["page"] -= 1


        await query.edit_message_text(
            build_song_list_text(
                songs,
                data["page"]
            ),
            parse_mode="HTML",
            reply_markup=build_keyboard(
                songs,
                data["page"]
            )
        )

        return



    # ======================
    # SELECT SONG
    # ======================

    index = int(
        query.data.split("_")[2]
    )


    song = songs[index]



    if uid in user_tasks:

        await query.answer(
            "⏳ Masih ada proses lain yang sedang berjalan, tunggu sebentar.",
            show_alert=True
        )

        return



    user_tasks[uid] = True



    await query.edit_message_text(
        "🌸 <b>Sakura Music</b> — Memproses permintaan Anda\n\n"
        f"🎵 {song['title']}\n"
        "⬇️ Mengunduh audio, mohon tunggu...",
        parse_mode="HTML"
    )



    filepath = None



    try:


        filepath, title = await asyncio.to_thread(
            download_youtube,
            song["url"]
        )



        await query.edit_message_text(
            "📤 <b>Sakura Music</b> — Mengirim audio...",
            parse_mode="HTML"
        )



        username = (

            f"@{query.from_user.username}"

            if query.from_user.username

            else query.from_user.first_name

        )



        caption = (

            f"🎵 <b>Judul:</b> {title}\n\n"

            f"👤 <b>Diminta oleh:</b> {username}\n\n"

            "🌸 Sakura Music"

        )



        with open(
            filepath,
            "rb"
        ) as audio:


            await query.message.reply_audio(
                audio=audio,
                title=title,
                caption=caption,
                parse_mode="HTML"
            )



        await query.message.delete()



    except Exception as e:


        logger.exception(
            "Download error"
        )


        await query.message.reply_text(
            f"❌ Gagal memproses audio, silakan coba lagi.\n\n<code>{e}</code>",
            parse_mode="HTML"
        )



    finally:


        user_tasks.pop(
            uid,
            None
        )



        if filepath and os.path.exists(
            filepath
        ):

            os.remove(
                filepath
            )


            logger.info(
                f"Cleanup: {filepath}"
            )
