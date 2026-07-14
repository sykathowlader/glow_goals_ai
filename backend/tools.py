from google.genai import types

from shopify_client import ShopifyClient

_shopify = ShopifyClient()

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

# A list because a provider can be given several tools at once; for now there's just one.
PRODUCT_TOOLS = [types.Tool(function_declarations=[_search_products_declaration])]


def execute_tool(name: str, args: dict):
    """Runs the tool the model asked for and returns its result."""
    if name == "search_products":
        return _shopify.search_products(args["search_term"])
    raise ValueError(f"Unknown tool: {name}")
