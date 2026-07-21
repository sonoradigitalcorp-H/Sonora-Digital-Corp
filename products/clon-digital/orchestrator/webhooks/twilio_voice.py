import logging
from fastapi import APIRouter, Form, Request

from core.config import settings
from agents.voice_agent import VoiceAgent

logger = logging.getLogger(__name__)

router = APIRouter()
voice_agent = VoiceAgent()


@router.post("/twilio/voice")
async def incoming_call(request: Request):
    form = await request.form()
    call_sid = form.get("CallSid", "")
    caller = form.get("From", "")
    twiml = voice_agent.handle_incoming_call(call_sid, caller)
    return twiml


@router.post("/twilio/voice-response")
async def voice_response(request: Request):
    form = await request.form()
    call_sid = form.get("CallSid", "")
    speech_result = form.get("SpeechResult", "")

    order_id = voice_agent.get_order_for_call(call_sid)
    twiml = voice_agent.handle_speech_result(speech_result, order_id)
    return twiml


@router.post("/twilio/voice-intent")
async def voice_intent(request: Request):
    form = await request.form()
    call_sid = form.get("CallSid", "")
    speech_result = form.get("SpeechResult", "")

    twiml = voice_agent.handle_speech_result(speech_result)
    return twiml


@router.post("/twilio/voice-status")
async def voice_status(request: Request):
    form = await request.form()
    call_sid = form.get("CallSid", "")
    call_status = form.get("CallStatus", "")

    logger.info(f"Call {call_sid} status: {call_status}")

    if call_status in ("busy", "no-answer", "failed"):
        order_id = voice_agent.get_order_for_call(call_sid)
        if order_id:
            logger.info(f"Retry scheduled for order {order_id}")

    return ""
