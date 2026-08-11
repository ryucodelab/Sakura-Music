<div align="center">

# 🌸 Sakura Music

A Telegram bot to search and download songs from YouTube straight into your chat, in MP3 format.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-20%2B-2CA5E0?logo=telegram&logoColor=white)](https://github.com/python-telegram-bot/python-telegram-bot)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Maintained](https://img.shields.io/badge/maintained-yes-success.svg)]()

</div>

---

## ✨ Features

- 🔎 Search songs by title or artist name (powered by YouTube search)
- 📄 Paginated search results (5 songs per page)
- ⬇️ Automatic MP3 download (via Savenow API)
- 🧹 Clean song titles — automatically strips noise like `(Audio)`, `(Official Video)`, `[Lyrics]`, etc.
- 🗑️ Auto-cleanup — prompt and query messages are deleted after being processed, keeping the chat tidy
- 🛡️ Collision-safe downloads — every download session uses a unique temp file, so concurrent users never clash
- ⚠️ Global error handling — a failure in one request won't take down the whole bot

## 📦 Project Structure

```
project/
├── main.py                 # Entry point — registers commands & handlers
├── requirements.txt         # Python dependencies
├── .env.example              # Example environment configuration
└── modules/
    ├── __init__.py
    ├── start.py             # /start, main menu, help
    └── sakura.py            # /search, search & download logic
```

## 🔧 Requirements

- Python 3.10 or newer
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- An API key from [Savenow](https://p.savenow.to) for audio conversion

## 🚀 Setup

### 1. Clone the repository

```bash
git clone https://github.com/username/sakura-music.git
cd sakura-music
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate      # Linux/Mac/Termux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> On Termux, if installation fails, try appending `--break-system-packages` to the `pip install` command.

### 4. Configure environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Then fill in the values:

| Variable | Description | Where to get it |
|---|---|---|
| `BOT_TOKEN` | Telegram bot token | Chat [@BotFather](https://t.me/BotFather) → `/newbot` |
| `BOT_USERNAME` | Bot username (without `@`) | Same as set during BotFather registration |
| `SAVENOW_API_KEY` | API key for YouTube → MP3 conversion | Sign up at [p.savenow.to](https://p.savenow.to) |

### 5. Run the bot

```bash
python main.py
```

On success, you should see:

```
🌸 Sakura Music Running...
```

## 🤖 Commands

| Command | Description |
|---|---|
| `/start` | Show the main menu |
| `/search` | Start a song search |
| `/help` | Show usage help |

## 📝 Usage

1. Send `/search`
2. Enter a song title or artist name
3. Pick a result from the search list (5 per page, navigate with ⬅️/➡️)
4. The bot downloads and sends the audio file automatically

## ⚠️ Notes

- This bot relies on a third-party service (Savenow) for audio conversion. If that service goes down, the download feature will be affected.
- To keep the bot running 24/7, consider using a VPS or hosting service with a process manager such as `pm2`, `screen`, or `systemd`.
- For the auto-delete feature to work properly in groups, make sure the bot is an admin with **Delete Messages** permission.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open a pull request or an issue.

## 📄 License

This project is licensed under the MIT License — free to use and modify.
