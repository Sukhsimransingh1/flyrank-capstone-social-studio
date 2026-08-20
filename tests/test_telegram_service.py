from unittest.mock import Mock, patch

from app.services.telegram_service import TelegramService


def test_telegram_disabled_without_credentials():
    with patch(
        "app.services.telegram_service.settings"
    ) as settings:
        settings.telegram_bot_token = "replace_me"
        settings.telegram_chat_id = "replace_me"

        service = TelegramService()

        assert service.enabled is False
        assert service.send_message("Hello") is False


def test_telegram_sends_message():
    with patch(
        "app.services.telegram_service.settings"
    ) as settings:
        settings.telegram_bot_token = "test-token"
        settings.telegram_chat_id = "123456789"

        service = TelegramService()

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "ok": True,
            "result": {
                "message_id": 1,
            },
        }

        with patch(
            "app.services.telegram_service.httpx.post",
            return_value=mock_response,
        ) as mock_post:

            result = service.send_message(
                "FlyRank scheduler test"
            )

            assert result is True

            mock_post.assert_called_once_with(
                "https://api.telegram.org/bottest-token/sendMessage",
                json={
                    "chat_id": "123456789",
                    "text": "FlyRank scheduler test",
                },
                timeout=10.0,
            )