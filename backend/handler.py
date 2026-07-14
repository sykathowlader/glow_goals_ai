import json

from dotenv import load_dotenv

load_dotenv()

from providers.gemini_provider import GeminiProvider
from tools import PRODUCT_TOOLS, execute_tool

provider = GeminiProvider()


def handler(event, context):
    """AWS Lambda-shaped entry point: takes an event dict, returns a response dict.

    Locally we call this function directly. Once API Gateway is wired up
    (Milestone 8), API Gateway will call this same function the same way.
    """
    body = json.loads(event.get("body") or "{}")
    message = body.get("message", "").strip()

    if not message:
        return {"statusCode": 400, "body": json.dumps({"error": "message is required"})}

    reply = provider.generate_response(message, tools=PRODUCT_TOOLS, execute_tool=execute_tool)
    return {"statusCode": 200, "body": json.dumps({"reply": reply})}


if __name__ == "__main__":
    fake_event = {"body": json.dumps({"message": "Do you have anything with snail mucin?"})}
    result = handler(fake_event, None)
    print(result)
