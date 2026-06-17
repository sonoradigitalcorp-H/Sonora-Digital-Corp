# Internal Module Contracts: Omnichannel Communication

**Feature**: `004-omnichannel`

## `ChannelAdapter` (interface)

```python
class ChannelAdapter(Protocol):
    async def receive_webhook(self, request: Request) -> Message
    async def send_message(self, message: OutgoingMessage) -> SendResult
    def normalize(self, raw: dict) -> Message
    def format(self, response: str, channel: str) -> FormattedResponse
```

- Each channel implements this interface
- `normalize` converts raw webhook to unified `Message`
- `format` applies channel-specific formatting (markdown, plain text, rich media)

## `WhatsAppAdapter`

```python
async def handle_webhook(payload: dict) -> Message
async def send_text(to: str, text: str) -> SendResult
async def send_media(to: str, media_url: str, media_type: str) -> SendResult
async def send_quick_reply(to: str, text: str, options: list[str]) -> SendResult
```

- 15-second processing limit (send "typing..." placeholder)
- Media support: image, audio, document (max 16MB)

## `TelegramAdapter`

```python
async def handle_update(update: Update) -> Message
async def send_message(chat_id: str, text: str, parse_mode: str = "Markdown") -> SendResult
async def send_media(chat_id: str, media: InputMedia) -> SendResult
async def answer_inline_query(query: InlineQuery, results: list) -> None
```

- Supports Markdown and HTML parse modes
- Command handling via decorator pattern
- 30 msg/s rate limit with queue

## `VoiceAdapter`

```python
async def handle_incoming_call(call_sid: str, from_number: str) -> CallSession
async def process_speech(audio_url: str) -> str  # STT
async def speak_text(text: str, call_sid: str) -> None  # TTS
async def handle_interruption(call_sid: str) -> None
```

- Twilio webhooks for call lifecycle (incoming, status, recording)
- Interruption: user speaks → JARVIS stops TTS and listens

## `MCPServer`

```python
async def handle_initialize(params: dict) -> MCPServerInfo
async def handle_list_tools() -> list[ToolDefinition]
async def handle_call_tool(name: str, arguments: dict) -> ToolResult
```

- JSON-RPC 2.0 protocol
- Concurrent connections with session isolation
- Structured errors for invalid parameters
