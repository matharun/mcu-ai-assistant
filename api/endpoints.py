from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uvicorn
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_rag_system import EnhancedMCUSystem
import json

# Initialize FastAPI app
app = FastAPI(
    title="MCU AI Assistant API",
    description="AI-powered microcontroller recommendation system",
    version="1.0.0"
)

# Initialize the MCU system (this takes time, so we do it once at startup)
print("🚀 Initializing MCU AI Assistant API...")
mcu_system = EnhancedMCUSystem()
print("✅ API ready to serve requests!")

# Pydantic models for request/response
class MCUQuery(BaseModel):
    query: str
    max_results: Optional[int] = 5
    use_web_fallback: Optional[bool] = True

class MCUResponse(BaseModel):
    success: bool
    query: str
    ai_recommendation: str
    requirements: Dict[str, Any]
    database_results: List
    web_results: List
    web_fallback_used: bool
    processing_time: float
    error_message: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str
    components: Dict[str, str]

@app.get("/", response_model=Dict[str, str])
async def root():
    """API root endpoint"""
    return {
        "message": "MCU AI Assistant API is running!",
        "version": "1.0.0",
        "endpoints": {
            "/ask": "POST - Ask for MCU recommendations",
            "/health": "GET - Check API health",
            "/docs": "GET - API documentation"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health status"""
    try:
        # Test database connection
        db_status = "✅ Connected"
        try:
            all_mcus = mcu_system.db.get_all_mcus()
            db_status += f" ({len(all_mcus)} MCUs)"
        except:
            db_status = "❌ Error"
        
        # Test embedding model
        embedding_status = "✅ Loaded"
        try:
            test_embedding = mcu_system.embedding_manager.model.encode(["test"])
            embedding_status += f" (dim: {len(test_embedding[0])})"
        except:
            embedding_status = "❌ Error"
        
        # Test LLM
        llm_status = "✅ Loaded"
        try:
            model_name = mcu_system.llm_manager.model_name
            llm_status += f" ({model_name})"
        except:
            llm_status = "❌ Error"
        
        return HealthResponse(
            status="healthy",
            message="All systems operational",
            components={
                "database": db_status,
                "embeddings": embedding_status,
                "llm": llm_status,
                "web_scraper": "✅ Ready"
            }
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            message=f"System error: {str(e)}",
            components={}
        )

@app.post("/ask", response_model=MCUResponse)
async def ask_mcu_recommendation(request: MCUQuery):
    """Get MCU recommendation based on user query"""
    try:
        # Validate input
        query = request.query.strip()
        if len(query) < 10:
            return MCUResponse(
                success=False,
                query=query,
                ai_recommendation="Please describe your requirements in more detail. For example: 'I need a low power MCU with WiFi for an IoT sensor'",
                requirements={},
                database_results=[],
                web_results=[],
                web_fallback_used=False,
                processing_time=0.0,
                error_message="Query too short"
            )
        print(f"📝 Received query: {request.query}")
        
        # Process the query
        result = mcu_system.process_query_with_fallback(request.query)
        
        return MCUResponse(
            success=True,
            query=result["query"],
            ai_recommendation=result["ai_recommendation"],
            requirements=result["requirements"],
            database_results=result["database_results"],
            web_results=result["web_results"],
            web_fallback_used=result["web_fallback_used"],
            processing_time=result["processing_time"]
        )
        
    except Exception as e:
        print(f"❌ Error processing query: {str(e)}")
        return MCUResponse(
            success=False,
            query=request.query,
            ai_recommendation="",
            requirements={},
            database_results=[],
            web_results=[],
            web_fallback_used=False,
            processing_time=0.0,
            error_message=str(e)
        )

@app.get("/stats")
async def get_api_stats():
    """Get API usage statistics"""
    try:
        total_mcus = mcu_system.db.get_mcu_count()
        
        return {
            "total_searches": 0,
            "average_response_time": 0,
            "recent_queries": [],
            "database_mcus": total_mcus
        }
        
    except Exception as e:
        return {"error": str(e)}

# Run the server
if __name__ == "__main__":
    uvicorn.run(
        "endpoints:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)