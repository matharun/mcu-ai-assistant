from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import numpy as np
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION, EMBEDDING_MODEL

class EmbeddingManager:
    def __init__(self):
        print(f"📥 Loading embedding model...")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.client = MongoClient(MONGO_URI)
        self.collection = self.client[MONGO_DB_NAME][MONGO_COLLECTION]
        print("✅ Embedding model loaded successfully")

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not text or not isinstance(text, str):
            return []
        embedding = self.model.encode(text)
        return embedding.tolist()

    def mcu_to_text(self, mcu: dict) -> str:
        """Convert MCU document to searchable text"""
        parts = []
        fields = [
            "name", "manufacturer", "cpu_architecture", "cpu_core",
            "cpu_speed", "flash_memory", "ram_memory", "gpio_pins",
            "communication_interfaces", "ethernet", "usb", "can",
            "uart", "spi", "i2c", "wireless", "operating_voltage",
            "operating_temp", "security", "description", "family", "series"
        ]
        for field in fields:
            val = mcu.get(field)
            if val and val != "None":
                parts.append(f"{field}: {val}")
        return " | ".join(parts)

    def build_embeddings_index(self):
        """Generate and store embeddings for all MCUs in MongoDB"""
        print("🔨 Building embeddings index...")
        mcus = list(self.collection.find({}))
        count = 0
        for mcu in mcus:
            if mcu.get("embedding"):
                continue  # Skip if already has embedding
            text = self.mcu_to_text(mcu)
            if not text:
                continue
            embedding = self.get_embedding(text)
            self.collection.update_one(
                {"_id": mcu["_id"]},
                {"$set": {"embedding": embedding}}
            )
            count += 1
        print(f"✅ Embeddings built for {count} MCUs")

    def search_similar_mcus(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar MCUs using cosine similarity"""
        query_embedding = np.array(self.get_embedding(query))
        mcus = list(self.collection.find({"embedding": {"$exists": True}}))

        if not mcus:
            print("⚠️ No embeddings found. Run build_embeddings_index() first.")
            return []

        scores = []
        for mcu in mcus:
            mcu_embedding = np.array(mcu["embedding"])
            # Cosine similarity
            similarity = np.dot(query_embedding, mcu_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(mcu_embedding) + 1e-10
            )
            scores.append((str(mcu["_id"]), float(similarity), mcu))

        # Sort by similarity
        scores.sort(key=lambda x: x[1], reverse=True)
        return [(s[0], s[1], s[2]) for s in scores[:top_k]]

    def get_mcu_context(self, mcu_ids: List[str]) -> str:
        """Get formatted context string from list of MCU ids"""
        from bson import ObjectId
        context_parts = []
        for mcu_id in mcu_ids:
            mcu = self.collection.find_one({"_id": ObjectId(mcu_id)}, {"embedding": 0})
            if mcu:
                context_parts.append(self.mcu_to_text(mcu))
        return "\n\n".join(context_parts)