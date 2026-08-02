"""Twilio MCP Server — Voice calls and SMS via Twilio REST API."""

import json
import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "")


async def make_call(to: str, twiml_url: str = "") -> str:
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER]):
        return json.dumps({"error": "Twilio not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER"})
    if not to:
        return json.dumps({"error": "to is required"})

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        twiml = twiml_url or f"<Response><Say language='es-MX'>Hola, llamada desde Sonora Digital Corp.</Say></Response>"
        call = client.calls.create(
            to=to,
            from_=TWILIO_FROM_NUMBER,
            twiml=twiml if not twiml_url else None,
            url=twiml_url or None,
        )
        return json.dumps({"call_sid": call.sid, "status": call.status, "to": to, "from": TWILIO_FROM_NUMBER})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def send_sms(to: str, message: str) -> str:
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER]):
        return json.dumps({"error": "Twilio not configured"})
    if not to or not message:
        return json.dumps({"error": "to and message are required"})

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg = client.messages.create(to=to, from_=TWILIO_FROM_NUMBER, body=message)
        return json.dumps({"message_sid": msg.sid, "status": msg.status, "to": to})
    except Exception as e:
        return json.dumps({"error": str(e)})


MCP_TOOLS = {
    "twilio_call": {
        "description": "Make a phone call via Twilio",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Phone number to call (E.164 format)"},
                "twiml_url": {"type": "string", "description": "URL with TwiML instructions (optional)"},
            },
            "required": ["to"],
        },
        "handler": lambda args: make_call(args["to"], args.get("twiml_url", "")),
    },
    "twilio_sms": {
        "description": "Send an SMS via Twilio",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Phone number (E.164 format)"},
                "message": {"type": "string", "description": "SMS text content"},
            },
            "required": ["to", "message"],
        },
        "handler": lambda args: send_sms(args["to"], args["message"]),
    },
}
