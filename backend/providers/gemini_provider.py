import os

from google import genai

from .base import AIProvider


class GeminiProvider(AIProvider):
    """Talks to Google's Gemini API. One concrete implementation of AIProvider."""

    def __init__(self):
        api_key = os.environ["GEMINI_API_KEY"]
        self._client = genai.Client(api_key=api_key)
        self._model = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")

    def generate_response(self, message: str) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=message,
        )
        return response.text
