import json
import math
import os

from google import genai

_KNOWLEDGE_FILE = os.path.join(os.path.dirname(__file__), "knowledge", "store_info.json")


class KnowledgeBase:
    """Simple RAG over a small local JSON file. No hosted vector database —
    at this size (a few dozen facts), comparing embeddings in memory with
    plain Python is more than fast enough, and needs one less moving part.
    """

    def __init__(self):
        api_key = os.environ["GEMINI_API_KEY"]
        self._client = genai.Client(api_key=api_key)
        self._model = os.environ.get("EMBEDDING_MODEL", "gemini-embedding-001")

        with open(_KNOWLEDGE_FILE) as f:
            self._chunks = json.load(f)

        # Embed every chunk once at startup, so search() only has to embed
        # the incoming question.
        texts = [chunk["content"] for chunk in self._chunks]
        response = self._client.models.embed_content(model=self._model, contents=texts)
        self._chunk_embeddings = [e.values for e in response.embeddings]

    def search(self, question: str, top_k: int = 3) -> list[str]:
        response = self._client.models.embed_content(model=self._model, contents=[question])
        question_embedding = response.embeddings[0].values

        scored_chunks = [
            (self._cosine_similarity(question_embedding, chunk_embedding), chunk["content"])
            for chunk, chunk_embedding in zip(self._chunks, self._chunk_embeddings)
        ]
        scored_chunks.sort(key=lambda pair: pair[0], reverse=True)
        return [content for _, content in scored_chunks[:top_k]]

    @staticmethod
    def _cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
        dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
        magnitude_a = math.sqrt(sum(a * a for a in vector_a))
        magnitude_b = math.sqrt(sum(b * b for b in vector_b))
        return dot_product / (magnitude_a * magnitude_b)
