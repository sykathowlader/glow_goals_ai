import os
import time

import requests


class ShopifyClient:
    """Talks to the real Glow Goals Shopify store. No AI concepts live here —
    just authentication and two queries: product search and order lookup."""

    def __init__(self):
        self._domain = os.environ["SHOPIFY_STORE_DOMAIN"]
        self._client_id = os.environ["SHOPIFY_CLIENT_ID"]
        self._client_secret = os.environ["SHOPIFY_CLIENT_SECRET"]
        self._api_version = os.environ.get("SHOPIFY_API_VERSION", "2026-07")
        self._access_token = None
        self._token_expires_at = 0

    def _get_access_token(self) -> str:
        """Returns a cached token, or requests a new one if it's missing/expired.

        Shopify custom apps no longer hand out a static token (deprecated
        2026-01-01) — instead we exchange our Client ID/Secret for a
        short-lived (~24h) token via OAuth's client credentials grant.
        """
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        response = requests.post(
            f"https://{self._domain}/admin/oauth/access_token",
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
        )
        response.raise_for_status()
        token_data = response.json()

        self._access_token = token_data["access_token"]
        # Refresh a minute early so we never call the API with a token that
        # expires mid-request.
        self._token_expires_at = time.time() + token_data["expires_in"] - 60
        return self._access_token

    def _graphql(self, query: str, variables: dict) -> dict:
        """Runs a GraphQL query against the Admin API and returns the `data` field."""
        response = requests.post(
            f"https://{self._domain}/admin/api/{self._api_version}/graphql.json",
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": self._get_access_token(),
            },
            json={"query": query, "variables": variables},
        )
        response.raise_for_status()
        return response.json()["data"]

    def search_products(self, search_term: str) -> list[dict]:
        """Searches the real catalog and returns a short list of matching products."""
        query = """
            query SearchProducts($searchTerm: String!) {
              products(first: 5, query: $searchTerm) {
                nodes {
                  title
                  description
                  productType
                  totalInventory
                  priceRangeV2 {
                    minVariantPrice {
                      amount
                      currencyCode
                    }
                  }
                }
              }
            }
        """
        data = self._graphql(query, {"searchTerm": search_term})
        return data["products"]["nodes"]

    def track_order(self, order_number: str, email: str) -> dict:
        """Looks up an order by number, but only returns its details if the
        supplied email matches the order's contact email. This stops someone
        from guessing an order number and seeing a stranger's order."""
        normalized_number = order_number if order_number.startswith("#") else f"#{order_number}"
        query = """
            query FindOrder($searchQuery: String!) {
              orders(first: 1, query: $searchQuery) {
                nodes {
                  name
                  email
                  displayFulfillmentStatus
                  displayFinancialStatus
                  createdAt
                  fulfillments {
                    trackingInfo {
                      number
                      url
                      company
                    }
                  }
                }
              }
            }
        """
        data = self._graphql(query, {"searchQuery": f"name:{normalized_number}"})
        orders = data["orders"]["nodes"]

        if not orders or orders[0]["email"].strip().lower() != email.strip().lower():
            return {"found": False}

        order = orders[0]
        tracking_info = [
            info for fulfillment in order["fulfillments"] for info in fulfillment["trackingInfo"]
        ]
        return {
            "found": True,
            "order_number": order["name"],
            "fulfillment_status": order["displayFulfillmentStatus"],
            "payment_status": order["displayFinancialStatus"],
            "placed_on": order["createdAt"],
            "tracking": tracking_info,
        }
