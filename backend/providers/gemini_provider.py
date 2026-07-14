import os

from google import genai
from google.genai import types

from .base import AIProvider


class GeminiProvider(AIProvider):
    """Talks to Google's Gemini API. One concrete implementation of AIProvider."""

    def __init__(self):
        api_key = os.environ["GEMINI_API_KEY"]
        self._client = genai.Client(api_key=api_key)
        self._model = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")

    def generate_response(self, message, tools=None, execute_tool=None) -> str:
        config = types.GenerateContentConfig(tools=tools) if tools else None

        response = self._client.models.generate_content(
            model=self._model,
            contents=message,
            config=config,
        )

        if not response.function_calls:
            return response.text

        # The model wants to call a tool instead of answering directly.
        # Run it, then send the result back so it can write the real answer.
        call = response.function_calls[0]
        call_content = response.candidates[0].content
        result = execute_tool(call.name, dict(call.args))

        response = self._client.models.generate_content(
            model=self._model,
            contents=[
                types.Content(role="user", parts=[types.Part.from_text(text=message)]),
                call_content,
                types.Content(
                    role="tool",
                    parts=[
                        types.Part.from_function_response(
                            name=call.name, response={"result": result}
                        )
                    ],
                ),
            ],
            config=config,
        )
        return response.text
