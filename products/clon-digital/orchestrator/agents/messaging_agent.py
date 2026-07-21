import logging
from typing import Optional
from twilio.rest import Client as TwilioClient

from core.config import settings

logger = logging.getLogger(__name__)


class MessagingAgent:
    def __init__(self):
        self.client = None
        if settings.twilio_account_sid and settings.twilio_auth_token:
            self.client = TwilioClient(settings.twilio_account_sid, settings.twilio_auth_token)

    def _ensure_client(self):
        if not self.client:
            raise RuntimeError("Twilio not configured")

    async def send_whatsapp(self, to: str, message: str, media_url: Optional[str] = None) -> bool:
        self._ensure_client()
        try:
            kwargs = {
                "body": message,
                "to": f"whatsapp:{to}",
                "from_": f"whatsapp:{settings.twilio_whatsapp}",
            }
            if media_url:
                kwargs["media_url"] = [media_url]
            self.client.messages.create(**kwargs)
            logger.info(f"WhatsApp sent to {to}")
            return True
        except Exception as e:
            logger.error(f"WhatsApp send failed to {to}: {e}")
            return False

    async def send_sms(self, to: str, message: str) -> bool:
        self._ensure_client()
        try:
            self.client.messages.create(
                body=message,
                to=to,
                from_=settings.twilio_phone,
            )
            return True
        except Exception as e:
            logger.error(f"SMS failed to {to}: {e}")
            return False

    def parse_whatsapp_webhook(self, form_data: dict) -> dict:
        media_url = None
        if form_data.get("NumMedia") and int(form_data.get("NumMedia", "0")) > 0:
            media_url = form_data.get("MediaUrl0")

        return {
            "from": form_data.get("From", "").replace("whatsapp:", ""),
            "body": form_data.get("Body", ""),
            "media_url": media_url,
            "message_sid": form_data.get("SmsMessageSid", ""),
        }
