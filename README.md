# Visa Slot Listener

A Telegram bot that watches H-1B / H-4 visa appointment channels in real time, runs OCR on every screenshot that gets posted, and **alerts you the moment slots may be available** — both with an audible voice notification and by forwarding the image to your private channel.

---

## How It Works

```
Telegram Channel (H1B_H4_Visa_Dropbox_slots)
        │
        ▼
   New image posted
        │
        ▼
   Download & OCR  ──────► No match? → discard
        │
     Match found
        │
        ├──► Forward screenshot to your private Telegram channel
        └──► Text-to-speech alert ("visa slots might be available")
```

The bot listens for new messages in the source channel. When someone posts a screenshot (which is how slot availability is typically shared), it:

1. Downloads the image.
2. Runs Tesseract OCR to extract text.
3. Checks for keywords like the current year and your target consulate city (e.g. `CHENNAI`).
4. If matched — forwards the image and announces it out loud.

---

## Getting Started

### 1. Prerequisites

| Requirement | Why |
|---|---|
| **Python >= 3.10** | Runtime for the bot |
| **Tesseract OCR** | Extracts text from screenshots |
| **Telegram account** | Authenticated at [web.telegram.org](https://web.telegram.org) |
| **H-1B Telegram channel membership** | You must be enrolled in an H-1B visa dropbox Telegram channel (e.g. `H1B_H4_Visa_Dropbox_slots`) where members post screenshots of appointment slot availability |
| **Telegram API credentials** | `API_ID` and `API_KEY` from [my.telegram.org](https://my.telegram.org) |

### 2. One-Command Setup

Everything is handled by the setup script — it checks your Python version, installs `uv` if needed, pulls all dependencies, and activates the virtual environment:

```bash
source setup.sh
```

That's it. The script will also warn you if Tesseract is missing and tell you exactly how to install it for your OS.

### 3. Configure Credentials

Open `visa_listener.py` and set your Telegram API credentials:

```python
API_ID: int = 123456          # from my.telegram.org
API_KEY: str = 'your_api_key' # from my.telegram.org
```

### 4. Run the Bot

```bash
uv run visa_listener.py
```

The bot connects to Telegram and starts listening. Keep it running — it will alert you the moment a relevant screenshot appears.

---

## Running Continuously (VNC / Remote Server)

Visa slots can open at any time of day, so you ideally want this bot polling around the clock. The recommended setup:

1. **Spin up a small VM or remote machine** (a cheap cloud instance works fine).
2. **Set up a VNC session** (or `tmux` / `screen`) so the bot keeps running even after you disconnect.
3. **Turn the volume up** — the bot uses text-to-speech to alert you audibly. Over VNC with audio forwarding, or on a machine with speakers, this means you'll hear the alert live.

Example with `tmux`:

```bash
# SSH into your server
tmux new -s visa-bot
source setup.sh
uv run visa_listener.py
# Ctrl+B, D to detach — bot keeps running
```

---

## About the Telegram Channel

This bot is designed to work with **H-1B / H-4 visa dropbox appointment** Telegram channels. These are community-run groups where members actively share screenshots of the US visa appointment scheduling portal whenever new slots open up.

To use this bot, you need to:

- **Join one of these channels** (the default is `H1B_H4_Visa_Dropbox_slots`).
- Update `SRC_CHANNEL_ID` in the script if your channel name differs.
- Update `TARGET_CHANNEL_URL` to point to your own private group/channel where you want alerts forwarded.

---

## Project Structure

```
visa-tracker/
├── visa_listener.py   # The bot — all logic lives here
├── pyproject.toml     # Project metadata & dependencies
├── setup.sh           # One-command bootstrap script
├── images/            # Temp directory for downloaded screenshots (auto-cleaned)
└── README.md
```

---

## Notes

- **OCR keywords** are hardcoded in `visa_listener.py` (`2026`, `2027`, `CHENNAI`). Update them for your target year and consulate city.
- **Text-to-speech** works on macOS (`say`) and Windows (`pyttsx3`). Linux support is not yet implemented.
- The first time you run the bot, Telegram will ask you to authenticate (phone number + code). After that, the session is cached locally.

---

## Contact

Built by **Prajyot Gupta** — reach out at **prajyotgupta@gmail.com** for API credentials, questions, or anything else.
