"""Mock LLM client for testing."""


def ask(prompt: str) -> str:
    return '{"entities": [], "relationships": []}'


def chat_completion(messages, **kwargs):
    return {
        "content": "Mock response",
        "reasoning": None,
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        "cost": 0.0,
    }


def stream_chat_completion(messages, **kwargs):
    yield "Mock "
    yield "response"
    return {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}


def list_models():
    return ["mock-model-v1"]
