from abc import ABC, abstractmethod
from typing import Callable, Optional


class AIProvider(ABC):
    """Common interface every LLM provider must implement.

    Application code depends only on this interface, never on a specific
    provider's SDK — so the underlying model can be swapped by adding a new
    subclass, without changing any calling code.

    Known simplification: `tools` is passed straight through in whatever
    shape the concrete provider's own SDK expects (e.g. Gemini's
    `types.Tool`). With a single provider this is harmless, but adding a
    second provider with function-calling would need a neutral tool format
    each provider translates into its own — deferred until that's needed.
    """

    @abstractmethod
    def generate_response(
        self,
        message: str,
        tools: Optional[list] = None,
        execute_tool: Optional[Callable[[str, dict], object]] = None,
    ) -> str:
        ...
