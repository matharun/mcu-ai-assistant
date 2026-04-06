import requests
import json
from typing import Dict, List, Any
import time
import re
import os
from dotenv import load_dotenv
load_dotenv()
class HuggingFaceAPIManager:
    def __init__(self, api_key: str = None):
        """Initialize Hugging Face API manager"""
        # PUT YOUR API KEY HERE - Replace hf_YOUR_API_KEY_GOES_HERE with your actual key
        self.api_key = os.getenv("HF_API_KEY") # ← REPLACE THIS WITH YOUR KEY
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # Working API endpoints (updated 2025)
        self.text_generation_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        self.embeddings_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
        
        print("✅ Hugging Face API manager initialized!")
        
    def test_api_connection(self) -> bool:
        """Test if API key works"""
        try:
            test_data = {"inputs": "Hello"}
            response = requests.post(
                self.text_generation_url,
                headers=self.headers,
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ API connection successful!")
                return True
            elif response.status_code == 503:
                print("🔄 Model loading on server, this is normal")
                return True  # Model loading is OK
            elif response.status_code == 401:
                print("❌ Invalid API key! Check your Hugging Face token.")
                return False
            else:
                print(f"❌ API test failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ API connection error: {e}")
            return False

    def generate_mcu_recommendation(self, query: str, context: str, requirements: Dict) -> str:
        """Generate MCU recommendation using Hugging Face API"""
        
        # Create prompt
        prompt = self.create_mcu_prompt(query, context, requirements)
        
        try:
            # API request data
            data = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            print(f"🌐 Sending request to Hugging Face API...")
            
            # Make API request
            response = requests.post(
                self.text_generation_url,
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract generated text
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                elif isinstance(result, dict):
                    generated_text = result.get('generated_text', '')
                else:
                    generated_text = str(result)
                
                # Clean up the response
                clean_response = self.clean_api_response(generated_text)
                print(f"✅ API response received!")
                return clean_response
                
            elif response.status_code == 503:
                print("⏳ Model is loading, trying again in 10 seconds...")
                time.sleep(10)
                return self.generate_mcu_recommendation(query, context, requirements)
                
            else:
                print(f"❌ API request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return self.generate_fallback_response(requirements)
                
        except Exception as e:
            print(f"❌ API request error: {e}")
            return self.generate_fallback_response(requirements)

    def create_mcu_prompt(self, query: str, context: str, requirements: dict) -> str:
        return EnhancedPromptEngineering.create_comprehensive_mcu_prompt(query, context, requirements)
        """Create a focused prompt for MCU recommendation"""
        
        prompt = f"""Based on the following MCU database information, provide a detailed recommendation:

Query: {query}

Available MCUs:
{context[:800]}  # Limit context to prevent token overflow

Requirements detected:
{json.dumps(requirements, indent=2)}

Please recommend the best MCU with detailed reasoning, including:
- Why this MCU fits the requirements
- Key specifications
- Use case suitability
- Any trade-offs or considerations

Recommendation:"""
        
        return prompt

    def clean_api_response(self, response: str) -> str:
        """Clean and format API response"""
        
        if not response:
            return "Unable to generate recommendation at this time."
        
        # Remove repeated phrases and clean up
        cleaned = response.strip()
        
        # Remove common API artifacts
        cleaned = re.sub(r'\n+', '\n', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Ensure it starts properly
        if not cleaned:
            return "Based on your requirements, I'd recommend checking the MCU database for suitable options."
            
        return cleaned

    def generate_fallback_response(self, requirements: Dict) -> str:
        """Generate fallback response when API fails"""
        
        response = "🔍 **MCU Recommendation** (Fallback Analysis)\n\n"
        
        if requirements.get('low_power'):
            response += "• For low power: Consider ARM Cortex-M0+ or M4 based MCUs\n"
        
        if requirements.get('wifi_support'):
            response += "• For WiFi: ESP32, ESP8266, or WiFi-enabled MCUs recommended\n"
        
        if requirements.get('bluetooth_support'):
            response += "• For Bluetooth: ESP32, nRF series, or integrated BLE MCUs\n"
        
        if requirements.get('high_performance'):
            response += "• For performance: ARM Cortex-M7 or dual-core options\n"
        
        if requirements.get('small_size'):
            response += "• For compact size: Look for QFN or BGA packages\n"
        
        response += "\n💡 For specific model recommendations, please check the MCU database or try again when the AI service is available."
        
        return response

    def test_simple_generation(self) -> bool:
        """Simple test for text generation"""
        try:
            simple_prompt = "The best microcontroller for IoT projects is"
            
            data = {
                "inputs": simple_prompt,
                "parameters": {
                    "max_new_tokens": 50,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                headers=self.headers,
                json=data,
                timeout=15
            )
            
            if response.status_code == 200:
                print("✅ Text generation test successful!")
                return True
            elif response.status_code == 503:
                print("🔄 Model loading for text generation")
                return True
            else:
                print(f"❌ Text generation test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Text generation test error: {e}")
            return False

# Alternative simpler API manager if main one fails
class SimpleHuggingFaceAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
    
    def generate_text(self, prompt: str, max_length: int = 100) -> str:
        """Simple text generation"""
        try:
            data = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": max_length}
            }
            
            response = requests.post(self.url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list):
                    return result[0].get('generated_text', prompt)
                return str(result)
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"

# Test function
def test_api_manager():
    """Test the API manager"""
    print("🧪 Testing HuggingFace API Manager...")
    
    # Initialize with your API key
    manager = HuggingFaceAPIManager("hf_YOUR_API_KEY_GOES_HERE")  # Replace with your key
    
    # Test connection
    if manager.test_api_connection():
        print("✅ Connection test passed!")
        
        # Test simple generation
        if manager.test_simple_generation():
            print("✅ Generation test passed!")
        else:
            print("❌ Generation test failed!")
    else:
        print("❌ Connection test failed!")

if __name__ == "__main__":
    test_api_manager()