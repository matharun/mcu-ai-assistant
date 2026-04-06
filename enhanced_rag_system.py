from utils.embeddings import EmbeddingManager
from utils.query_processor import QueryProcessor
from utils.llm_manager import LLMManager
from utils.web_scraper import MCUWebScraper
from database.db_manager import MCUDatabase
import time

class EnhancedMCUSystem:
    def __init__(self):
        """Initialize enhanced MCU system with web fallback"""
        print("🚀 Initializing Enhanced MCU AI Assistant...")
        
        # Initialize all components
        self.db = MCUDatabase()
        self.embedding_manager = EmbeddingManager()
        self.query_processor = QueryProcessor()
        self.llm_manager = LLMManager()
        self.web_scraper = MCUWebScraper()
        
        # Thresholds for fallback
        self.similarity_threshold = 0.6  # If best match is below this, search web
        self.min_results = 2  # Minimum results before web search
        
        print("✅ Enhanced system initialized successfully!")

    def process_query_with_fallback(self, user_query: str) -> dict:
        """Process query with web fallback capability"""
        start_time = time.time()
        
        print(f"\n🔍 Processing query: {user_query}")
        
        # Step 1: Extract requirements
        requirements = self.query_processor.extract_requirements(user_query)
        print(f"📝 Extracted requirements: {requirements}")
        
        # Step 2: Database search first
        similar_mcus = self.embedding_manager.search_similar_mcus(user_query, top_k=5)
        print(f"🎯 Database found {len(similar_mcus)} similar MCUs")
        
        # Step 3: Check if we need web fallback
        use_web_fallback = self.should_use_web_fallback(similar_mcus)
        
        web_results = []
        web_context = ""
        
        if use_web_fallback:
            print("🌐 Triggering web search fallback...")
            web_results = self.web_scraper.search_mcu_specs(user_query, max_results=3)
            web_context = self.web_scraper.create_web_context(web_results)
        
        # Step 4: Create combined context
        db_context = ""
        if similar_mcus:
            mcu_ids = [mcu_id for mcu_id, similarity in similar_mcus]
            db_context = self.embedding_manager.get_mcu_context(mcu_ids)
        
        combined_context = self.combine_contexts(db_context, web_context)
        
        # Step 5: Generate LLM response
        print("🤖 Generating AI recommendation...")
        ai_response = self.llm_manager.generate_mcu_recommendation(
            user_query, combined_context, requirements
        )
        
        # Step 6: Compile results
        processing_time = time.time() - start_time
        
        result = {
            "query": user_query,
            "requirements": requirements,
            "database_results": similar_mcus,
            "web_results": web_results,
            "web_fallback_used": use_web_fallback,
            "combined_context": combined_context,
            "ai_recommendation": ai_response,
            "processing_time": processing_time
        }
        
        # Log to database
        self.log_search(user_query, len(similar_mcus) + len(web_results), processing_time)
        
        return result

    def should_use_web_fallback(self, similar_mcus: list) -> bool:
        """Determine if web fallback should be used"""
        if not similar_mcus:
            return True
        
        if len(similar_mcus) < self.min_results:
            return True
        
        best_similarity = similar_mcus[0][1] if similar_mcus else 0
        if best_similarity < self.similarity_threshold:
            return True
        
        return False

    def combine_contexts(self, db_context: str, web_context: str) -> str:
        """Combine database and web contexts"""
        combined = []
        
        if db_context:
            combined.append("=== DATABASE RESULTS ===")
            combined.append(db_context)
        
        if web_context:
            combined.append("\n=== WEB SEARCH RESULTS ===")
            combined.append(web_context)
        
        if not combined:
            return "No relevant MCU data found."
        
        return "\n".join(combined)

    def log_search(self, query: str, results_found: int, response_time: float):
        """Log search to database"""
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_history (query, results_found, response_time)
            VALUES (?, ?, ?)
        ''', (query, results_found, response_time))
        
        conn.commit()
        conn.close()

    def display_enhanced_results(self, result: dict):
        """Display enhanced results with fallback info"""
        print("\n" + "="*60)
        print("🎯 ENHANCED MCU AI ASSISTANT")
        print("="*60)
        
        print(f"\n📝 Query: {result['query']}")
        print(f"⏱️  Processing Time: {result['processing_time']:.2f} seconds")
        print(f"🌐 Web Fallback Used: {'Yes' if result['web_fallback_used'] else 'No'}")
        
        print(f"\n📊 Results Summary:")
        print(f"   • Database results: {len(result['database_results'])}")
        print(f"   • Web results: {len(result['web_results'])}")
        
        print(f"\n🤖 AI Recommendation:")
        print("-" * 40)
        print(result['ai_recommendation'])
        print("-" * 40)


if __name__ == "__main__":
    # Initialize enhanced system
    enhanced_system = EnhancedMCUSystem()
    
    # Test queries that might need web fallback
    test_queries = [
        "I need the latest ESP32-S3 specifications for AI applications",  # Might need web
        "Suggest MCU for low-power IoT with 32KB flash",  # Should find in DB
        "What about the new STM32H7 series for high-performance applications?"  # Might need web
    ]
    
    for query in test_queries:
        result = enhanced_system.process_query_with_fallback(query)
        enhanced_system.display_enhanced_results(result)
        print("\n" + "="*60 + "\n")