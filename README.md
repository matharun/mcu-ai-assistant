MCU AI Assistant 🤖
An AI-powered microcontroller recommendation system that understands natural language queries and suggests the most suitable MCU from a database of 1500+ real-world microcontrollers.

What It Does
Instead of manually searching datasheets, just describe what you need:

"I need a low power MCU with secure features for an industrial application"

The system searches through the MCU database, finds the most relevant options, and gives you a detailed recommendation with specs, reasoning, alternatives and trade-offs — powered by Groq LLM.

How It Works
User Query (natural language)
        ↓
Query Processor → extracts requirements (low power, WiFi, speed, etc.)
        ↓
Embedding Search → finds top 5 similar MCUs from MongoDB using cosine similarity
        ↓
Context Builder → formats MCU specs into readable text
        ↓
Groq LLM (llama-3.3-70b-versatile) → generates detailed recommendation
        ↓
Response with specs, reasoning, alternatives and trade-offs

Tech Stack
ComponentTechnologyDatabaseMongoDBEmbeddingssentence-transformers/all-MiniLM-L6-v2LLMGroq API — llama-3.3-70b-versatileLanguagePython 3.10+Query ProcessingCustom NLP rule-based parser

Project Structure
mcu_ai_assistant/
├── database/
│   └── db_manager.py        # MongoDB connection and CRUD operations
├── utils/
│   ├── embeddings.py        # Embedding generation and semantic search
│   ├── groq_llm_manager.py  # Groq API integration
│   ├── query_processor.py   # Natural language requirement extraction
│   ├── llm_manager.py       # LLM abstraction layer
│   └── web_scraper.py       # Web scraping for additional MCU data
├── api/
│   └── endpoints.py         # API endpoints
├── config.py                # Configuration and environment variables
├── main.py                  # Entry point — interactive CLI assistant
├── import_to_mongodb.py     # Data import script
├── enhanced_rag_system.py   # Full RAG pipeline orchestrator
└── requirements.txt         # Python dependencies

Setup and Installation
1. Clone the repository
bashgit clone https://github.com/matharun/mcu-ai-assistant.git
cd mcu-ai-assistant
2. Create and activate virtual environment
bashpython -m venv venv

# Windows
venv\Scriptsctivate

# Mac/Linux
source venv/bin/activate
3. Install dependencies
bashpip install -r requirements.txt
4. Set up environment variables
Create a .env file in the project root:
MONGO_URI=mongodb://localhost:27017/
GROQ_API_KEY=your_groq_api_key_here
Get your free Groq API key at https://console.groq.com
5. Make sure MongoDB is running locally
Download MongoDB Community Edition from https://www.mongodb.com/try/download/community if you have not already.
6. Import MCU data
bashpython import_to_mongodb.py
7. Build embeddings index
bashpython -c "from utils.embeddings import EmbeddingManager; em = EmbeddingManager(); em.build_embeddings_index()"
This will take 2-3 minutes for 1500+ MCUs.
8. Run the assistant
bashpython main.py

Example Queries You Can Ask

I need a low power MCU with secure features for an industrial application
Suggest an ARM Cortex-M4 with at least 512KB flash and Ethernet support
What is the best MCU for motor control with PWM and CAN bus?
Find me an NXP microcontroller with USB and high operating temperature range
I need a 32-bit MCU with SPI and I2C for a sensor node


Requirements
pymongo
python-dotenv
sentence-transformers
groq
pandas
openpyxl
xlrd
requests
numpy

Notes

Make sure MongoDB is running before starting the assistant
The embeddings index only needs to be built once. If you add new MCUs, run build_embeddings_index() again
Never commit your .env file to GitHub — it contains your API key
The .env file is already in .gitignore by default

## Frontend
React-based chat UI → https://github.com/matharun/mcu-ai-frontend

## Running the Full Stack
# Terminal 1 — Backend
cd api
uvicorn endpoints:app --reload --port 8000

# Terminal 2 — Frontend  
cd frontend
npm run dev

Author
GitHub: https://github.com/matharun 
