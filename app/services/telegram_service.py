import logging

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


class TelegramService:
    """Send notifications to a configured Telegram chat."""

    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id

    @property
    def enabled(self) -> bool:
        return bool(
            self.bot_token
            and self.chat_id
            and self.bot_token != "replace_me"
            and self.chat_id != "replace_me"
        )

    def send_message(self, message: str) -> bool:
        if not self.enabled:
            logger.warning(
                "Telegram notifications are disabled: "
                "credentials are not configured."
            )
            return False

        url = (
            f"https://api.telegram.org/bot"
            f"{self.bot_token}/sendMessage"
        )

        payload = {
            "chat_id": self.chat_id,
            "text": message,
        }

        try:
            response = httpx.post(
                url,
                json=payload,
                timeout=10.0,
            )

            response.raise_for_status()

            data = response.json()

            if not data.get("ok"):
                logger.error(
                    "Telegram API returned an unsuccessful response: %s",
                    data,
                )
                return False

            logger.info("Telegram notification sent successfully.")
            return True

        except Exception:
            logger.exception(
                "Failed to send Telegram notification."
            )
            return False