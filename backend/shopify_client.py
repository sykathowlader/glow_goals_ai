import os
import time

import requests


class ShopifyClient:
    """Talks to the real Glow Goals Shopify store. No AI concepts live here —
    just authentication and one product search query."""

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
        response = requests.post(
            f"https://{self._domain}/admin/api/{self._api_version}/graphql.json",
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": self._get_access_token(),
            },
            json={"query": query, "variables": {"searchTerm": search_term}},
        )
        response.raise_for_status()
        return response.json()["data"]["products"]["nodes"]
