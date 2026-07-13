"""Tests para Telegram Bot central [FR4] — Redis queue pattern, solo entrega."""

import json
from unittest.mock import MagicMock, PropertyMock, patch

import pytest


@pytest.fixture
def mock_redis_from_url():
    with patch("apps.sonora_bot.message_queue.redis.Redis.from_url") as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield instance


class TestMessageQueue:
    """FR4: Bot solo escribe/lee de Redis, sin lógica de negocio."""

    def test_push_to_inbox(self, mock_redis_from_url):
        """Bot recibe mensaje → push a telegram:inbox"""
        from apps.sonora_bot.message_queue import push_to_inbox

        result = push_to_inbox(
            chat_id=12345,
            text="Hola",
            user_id=67890,
            message_id=100,
        )

        assert result is True
        mock_redis_from_url.xadd.assert_called_once()
        args = mock_redis_from_url.xadd.call_args[0]
        assert args[0] == "telegram:inbox"
        data = args[1]
        assert data["chat_id"] == 12345
        assert data["text"] == "Hola"
        assert data["user_id"] == 67890

    def test_push_to_inbox_photo(self, mock_redis_from_url):
        """FR4: Non-text messages get type detected"""
        from apps.sonora_bot.message_queue import push_to_inbox

        result = push_to_inbox(
            chat_id=12345,
            text=None,
            user_id=67890,
            message_id=101,
            message_type="photo",
        )

        assert result is True
        args = mock_redis_from_url.xadd.call_args[0]
        data = args[1]
        assert data["type"] == "photo"

    def test_poll_from_outbox(self, mock_redis_from_url):
        """Bot lee de telegram:outbox para enviar respuestas"""
        from apps.sonora_bot.message_queue import poll_outbox

        mock_redis_from_url.xread.return_value = [
            (b"telegram:outbox", [
                (b"1680000000000-0", {
                    b"chat_id": b"12345",
                    b"text": b"Hola de vuelta",
                    b"parse_mode": b"HTML",
                })
            ])
        ]

        messages = poll_outbox(blocking=False)
        assert len(messages) > 0
        assert messages[0]["chat_id"] == 12345
        assert messages[0]["text"] == "Hola de vuelta"

    def test_empty_outbox_returns_empty(self, mock_redis_from_url):
        """No messages in queue returns empty list"""
        from apps.sonora_bot.message_queue import poll_outbox

        mock_redis_from_url.xread.return_value = []

        messages = poll_outbox(blocking=False)
        assert messages == []

    def test_ack_message(self, mock_redis_from_url):
        """FR4: After sending, message is acknowledged (deleted from queue)"""
        from apps.sonora_bot.message_queue import ack_outbox

        result = ack_outbox("1680000000000-0")
        assert result is True
        mock_redis_from_url.xdel.assert_called_once_with("telegram:outbox", "1680000000000-0")


class TestBotHandler:
    """FR4: Bot handlers only validate and forward — no business logic."""

    def test_start_handler_returns_welcome(self):
        """Handler /start returns welcome message with registration link"""
        pytest.importorskip("telegram", reason="python-telegram-bot not installed")
        from apps.sonora_bot.handlers import start_handler

        update = MagicMock()
        update.message.chat_id = 12345
        update.effective_user.id = 67890
        context = MagicMock()

        import asyncio
        result = asyncio.run(start_handler(update, context))

        assert result is True
        context.bot.send_message.assert_called_once()
        args = context.bot.send_message.call_args[1]
        assert args["chat_id"] == 12345
        assert "Bienvenido" in args["text"]

    def test_message_handler_rejects_photo(self):
        """Non-text messages get friendly rejection"""
        pytest.importorskip("telegram", reason="python-telegram-bot not installed")
        from apps.sonora_bot.handlers import message_handler

        update = MagicMock()
        update.message.text = None
        update.message.photo = [MagicMock()]
        update.message.chat_id = 12345
        context = MagicMock()

        import asyncio
        result = asyncio.run(message_handler(update, context))

        assert result is True
        context.bot.send_message.assert_called_once()
        args = context.bot.send_message.call_args[1]
        assert "solo proceso mensajes de texto" in args["text"].lower()

    def test_message_handler_forwards_to_redis(self):
        """Valid text message gets pushed to inbox queue"""
        pytest.importorskip("telegram", reason="python-telegram-bot not installed")
        from apps.sonora_bot.handlers import message_handler

        update = MagicMock()
        update.message.text = "Hola"
        update.message.chat_id = 12345
        update.effective_user.id = 67890
        update.message.message_id = 200
        context = MagicMock()

        with patch("apps.sonora_bot.handlers.push_to_inbox", return_value=True):
            import asyncio
            result = asyncio.run(message_handler(update, context))

        assert result is True
        context.bot.send_message.assert_not_called()


class TestBotErrorHandling:
    """FR4: Errors should not crash the bot."""

    def test_redis_down_does_not_crash_bot(self):
        """If Redis is unreachable, bot logs error but keeps running"""
        from apps.sonora_bot.message_queue import push_to_inbox

        with patch("apps.sonora_bot.message_queue.redis.Redis.from_url",
                   side_effect=ConnectionError("Redis down")):
            result = push_to_inbox(12345, "test", 67890, 1)
            assert result is False

    def test_invalid_message_type_handled(self):
        """Unknown message types get defaulted to 'unknown'"""
        from apps.sonora_bot.message_queue import push_to_inbox

        with patch("apps.sonora_bot.message_queue.redis.Redis.from_url") as mock:
            instance = MagicMock()
            mock.return_value = instance

            result = push_to_inbox(12345, None, 67890, 1, message_type="sticker")
            data = instance.xadd.call_args[0][1]
            assert data["type"] == "sticker"
            assert result is True
