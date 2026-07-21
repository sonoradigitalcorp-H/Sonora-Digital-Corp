"""Custom exceptions for the Decision Engine."""


class NoProviderAvailableError(Exception):
    """All providers for the requested capability are unavailable."""
    def __init__(self, capability_id: str):
        self.capability_id = capability_id
        super().__init__(f"No providers available for capability '{capability_id}'")


class ProviderExecutionError(Exception):
    """The selected provider failed during execution."""
    def __init__(self, provider_id: str, capability_id: str, detail: str = ""):
        self.provider_id = provider_id
        self.capability_id = capability_id
        super().__init__(f"Provider '{provider_id}' failed for capability '{capability_id}': {detail}")
