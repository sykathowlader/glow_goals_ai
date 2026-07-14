from google.genai import types

from knowledge_base import KnowledgeBase
from shopify_client import ShopifyClient

_shopify = ShopifyClient()
_knowledge_base = KnowledgeBase()

_search_products_declaration = types.FunctionDeclaration(
    name="search_products",
    description=(
        "Search the Glow Goals Shopify store's real product catalog for skincare "
        "products. Always call this before recommending or mentioning any specific "
        "product — never invent a product that wasn't returned by this tool."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "search_term": {
                "type": "string",
                "description": (
                    "What to search for: an ingredient, skin concern, or product "
                    "type, e.g. 'snail mucin', 'dry skin moisturiser', 'sunscreen'."
                ),
            }
        },
        "required": ["search_term"],
    },
)

_search_knowledge_declaration = types.FunctionDeclaration(
    name="search_knowledge",
    description=(
        "Search Glow Goals' own store knowledge base for facts about shipping, "
        "delivery times, returns, refunds, and the brand. Use this for questions "
        "about how the store operates. Do NOT use this for general skincare "
        "education (e.g. what an ingredient does, how Korean skincare works) — "
        "answer those directly. Do NOT use this to find or recommend products — "
        "use search_products for that."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The customer's question about shipping, returns, or the store.",
            }
        },
        "required": ["question"],
    },
)

# One Tool holding every function the model can choose to call.
TOOLS = [
    types.Tool(
        function_declarations=[_search_products_declaration, _search_knowledge_declaration]
    )
]


def execute_tool(name: str, args: dict):
    """Runs the tool the model asked for and returns its result."""
    if name == "search_products":
        return _shopify.search_products(args["search_term"])
    if name == "search_knowledge":
        return _knowledge_base.search(args["question"])
    raise ValueError(f"Unknown tool: {name}")
