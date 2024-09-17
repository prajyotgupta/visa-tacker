########################################################################################
## Author       : Prajyot
## Contact      : prajyotg@nvidia.com
## Description  : Script to read telegram account for any open slots 
########################################################################################

# Login to Telegram on web browser https://web.telegram.org
# Install tesseract-ocr: apt-get install tesseract-ocr && pip install pytesseract
# Install Telethon lib: pip install telethon
# Install Text-to-Speech lib if using Windows: pip install pyttsx3
# To run, increase speaker volume to 100% & in your cmd prompt: python3 listener_visa_slots.py

import asyncio
import logging
import os
import platform
from typing import Optional

import cv2 as cv
import pytesseract as tes
from telethon import TelegramClient, events

# Configure logging
logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.INFO
)

# Bot Configuration
API_ID: int = 25299843  
API_KEY: str = '05560746eb6b655720de8aa05d30e966'  
SRC_CHANNEL_ID: str = 'H1B_H4_Visa_Dropbox_slots'

TARGET_CHANNEL_URL: Optional[str] = 'https://t.me/+l97HFDmvYN5hNDQ1'
SESSION_NAME: str = 'pb_visa_bot'

# Initialize TelegramClient
client = TelegramClient(SESSION_NAME, API_ID, API_KEY)


async def ocr(path: str) -> bool:
    """Perform OCR on the image and check for 2024 or 2025."""
    matches = ["2024", "2025", "CHENNAI"]
    img = cv.imread(path)
    data = tes.image_to_string(img)
    if any(x in data for x in matches):
        return True


async def text_to_speech(message: str) -> None:
    """Convert text to speech based on the platform."""
    if platform.system() == 'Darwin':
        os.system(f'say "{message}"')
    elif platform.system() == 'Windows':
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()


async def forward_to_target_channel(path) -> None:
    """Forward the message to the target channel if configured."""
    logging.info("Requst to upload")
    entity = await client.get_entity(TARGET_CHANNEL_URL)
    await client.send_file(entity, path, caption="Uploaded by listener")
    logging.info(f"Sent downloaded file '{path}'")


@client.on(events.NewMessage(chats=SRC_CHANNEL_ID))
async def handler(event) -> None:
    try:
        media = event.original_update.message.media
        if not media:
            logging.info(f"Text message received: {event.message.text}")
            return

        if hasattr(media, 'photo') or (hasattr(media, 'document') and media.document.mime_type == 'image/jpeg'):
            media_id = media.photo.id if hasattr(media, 'photo') else media.document.id
            logging.info(f'{"Photo" if hasattr(media, "photo") else "Document"} uploaded, id: {media_id}')

            path = f"images/{media_id}"
            download_path = await client.download_media(media, path)
            logging.info("Download complete")

            if await ocr(download_path):
                logging.info("OCR detected")
                message = 'Important message: Screenshot uploaded, visa slots might be available'
                await forward_to_target_channel(download_path)
                await text_to_speech(message)

            # Clean up the downloaded file
            os.remove(download_path)

    except Exception as e:
        logging.error(f"Error processing message: {e}")


async def main():
    await client.start()
    logging.info('PB Listner Bot :: Listening to events...')
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
