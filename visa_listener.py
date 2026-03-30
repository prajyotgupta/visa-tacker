########################################################################################
## Author       : Prajyot
## Contact      : prajyotgupta@gmail.com
## Description  : Telegram bot that monitors a visa-slots channel, runs OCR on posted
##                screenshots, and alerts (voice + forward) when slots may be available.
########################################################################################
#
# Prerequisites (system-level):
#   - Tesseract OCR engine: brew install tesseract  (macOS) / apt-get install tesseract-ocr (Linux)
#   - A Telegram account authenticated at https://web.telegram.org
#   - Being enrolled in the H-1B telegram channel
#
# Quick start:
#   uv sync && uv run visa_listener.py
#

import asyncio
import logging
import os
import platform
from typing import Optional

import cv2 as cv
import pytesseract as tes
from telethon import TelegramClient, events

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.INFO
)

# ---------------------------------------------------------------------------
# Telegram credentials & channel config
# ---------------------------------------------------------------------------
# TODO: Move API_ID and API_KEY to environment variables or a .env file
#       so credentials aren't committed to source control.
# API_ID: int =
# API_KEY: str = ''
SRC_CHANNEL_ID: str = 'H1B_H4_Visa_Dropbox_slots'

TARGET_CHANNEL_URL: Optional[str] = 'https://t.me/+l97HFDmvYN5hNDQ1'
SESSION_NAME: str = 'pb_visa_bot'

# Telegram client singleton used throughout the script
client = TelegramClient(SESSION_NAME, API_ID, API_KEY)


# ---------------------------------------------------------------------------
# OCR — extract text from a screenshot and check for relevant keywords
# ---------------------------------------------------------------------------
async def ocr(path: str) -> bool:
    # TODO: Update these keywords each year / for different consulate cities.
    matches = ["2026", "2027", "CHENNAI"]
    img = cv.imread(path)
    data = tes.image_to_string(img)
    if any(x in data for x in matches):
        return True
    return False


# ---------------------------------------------------------------------------
# Text-to-speech — audible alert so you don't have to watch the screen
# ---------------------------------------------------------------------------
async def text_to_speech(message: str) -> None:
    if platform.system() == 'Darwin':
        os.system(f'say "{message}"')
    elif platform.system() == 'Windows':
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
    # TODO: Add Linux support (e.g. espeak or festival).


# ---------------------------------------------------------------------------
# Forward matched screenshot to a private notification channel
# ---------------------------------------------------------------------------
async def forward_to_target_channel(path) -> None:
    logging.info("Request to upload")
    entity = await client.get_entity(TARGET_CHANNEL_URL)
    await client.send_file(entity, path, caption="Uploaded by listener")
    logging.info(f"Sent downloaded file '{path}'")


# ---------------------------------------------------------------------------
# Event handler — fires on every new message in the source channel
# ---------------------------------------------------------------------------
@client.on(events.NewMessage(chats=SRC_CHANNEL_ID))
async def handler(event) -> None:
    try:
        media = event.original_update.message.media

        # Skip plain-text messages
        if not media:
            logging.info(f"Text message received: {event.message.text}")
            return

        # Only process photos or JPEG documents (the usual screenshot formats)
        if hasattr(media, 'photo') or (hasattr(media, 'document') and media.document.mime_type == 'image/jpeg'):
            media_id = media.photo.id if hasattr(media, 'photo') else media.document.id
            logging.info(f'{"Photo" if hasattr(media, "photo") else "Document"} uploaded, id: {media_id}')

            # Download, OCR, and conditionally alert
            path = f"images/{media_id}"
            download_path = await client.download_media(media, path)
            logging.info("Download complete")

            if await ocr(download_path):
                logging.info("OCR detected")
                message = 'Important message: Screenshot uploaded, visa slots might be available'
                await forward_to_target_channel(download_path)
                await text_to_speech(message)

            os.remove(download_path)

    except Exception as e:
        logging.error(f"Error processing message: {e}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
async def main():
    await client.start()
    logging.info('PB Listener Bot :: Listening to events...')
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
