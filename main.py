from utils.embeddings import EmbeddingManager
from utils.groq_llm_manager import GroqAPIManager
from utils.query_processor import QueryProcessor
from database.db_manager import MCUDatabase

def main():
    print("🚀 Starting MCU AI Assistant...")

    em = EmbeddingManager()
    groq = GroqAPIManager()
    qp = QueryProcessor()
    db = MCUDatabase()

    print(f"📦 Database has {db.get_mcu_count()} MCUs")
    print("\n💬 Ask me anything about microcontrollers!")
    print("Type 'exit' to quit\n")

    while True:
        query = input("You: ").strip()

        if query.lower() == "exit":
            print("Goodbye!")
            break

        if not query:
            continue

        # Extract requirements
        requirements = qp.extract_requirements(query)

        # Search similar MCUs
        results = em.search_similar_mcus(query, top_k=5)
        mcu_ids = [r[0] for r in results]

        # Get context
        context = em.get_mcu_context(mcu_ids)

        # Generate response
        response = groq.generate_mcu_recommendation(query, context, requirements)

        print(f"\nAssistant: {response}\n")
        print("-" * 60)

        # Log search
        db.log_search(query, len(results), 0)

if __name__ == "__main__":
    main() 
