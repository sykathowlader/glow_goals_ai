from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Common interface every LLM provider must implement.

    Application code depends only on this interface, never on a specific
    provider's SDK — so the underlying model can be swapped by adding a new
    subclass, without changing any calling code.
    """

    @abstractmethod
    def generate_response(self, message: str) -> str:
        ...
