from pymongo import MongoClient, ASCENDING
from typing import List, Dict, Any
from config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION

class MCUDatabase:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.collection = self.db[MONGO_COLLECTION]
        self.search_history = self.db["search_history"]
        self._init_indexes()
        print("✅ MongoDB connected successfully")

    def _init_indexes(self):
        """Create indexes for faster search"""
        self.collection.create_index([("name", ASCENDING)])
        self.collection.create_index([("manufacturer", ASCENDING)])

    def add_mcu(self, mcu_data: Dict[str, Any]) -> bool:
        """Add a new MCU to the database"""
        try:
            self.collection.insert_one(mcu_data)
            return True
        except Exception as e:
            print(f"Error adding MCU: {e}")
            return False

    def get_all_mcus(self) -> List[Dict[str, Any]]:
        """Get all MCUs from the database"""
        try:
            mcus = list(self.collection.find({}, {"_id": 0}))
            return mcus
        except Exception as e:
            print(f"Error fetching MCUs: {e}")
            return []

    def search_mcus(self, query_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search MCUs by field values"""
        try:
            results = list(self.collection.find(query_dict, {"_id": 0}))
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def get_mcu_by_name(self, name: str) -> Dict[str, Any]:
        """Get a specific MCU by name"""
        try:
            result = self.collection.find_one({"name": name}, {"_id": 0})
            return result or {}
        except Exception as e:
            print(f"Error fetching MCU: {e}")
            return {}

    def log_search(self, query: str, results_found: int, response_time: float):
        """Log search history"""
        try:
            self.search_history.insert_one({
                "query": query,
                "results_found": results_found,
                "response_time": response_time
            })
        except Exception as e:
            print(f"Log error: {e}")

    def get_mcu_count(self) -> int:
        """Get total number of MCUs in database"""
        return self.collection.count_documents({})