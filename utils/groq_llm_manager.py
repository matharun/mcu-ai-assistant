import requests
import json
from typing import Dict, List, Any
import time

class GroqAPIManager:
    def __init__(self, api_key: str = None):
        """Initialize Groq API manager - Much easier than HuggingFace!"""
        # PUT YOUR GROQ API KEY HERE (replace the placeholder)
        import os
        from dotenv import load_dotenv
        load_dotenv()
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Groq API endpoint - works immediately!
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Available models (all free!)
        self.model = "llama-3.3-70b-versatile"  # Fast and smart
        # Alternative models:
        # "llama3-70b-8192"    - More powerful but slower
        # "mixtral-8x7b-32768" - Good for complex tasks
        # "gemma-7b-it"        - Google's model
        
        print("✅ Groq API manager initialized!")
        
    def test_api_connection(self) -> bool:
        """Test if Groq API key works"""
        try:
            # Simple test message
            test_data = {
                "messages": [
                    {"role": "user", "content": "Hello, just testing the connection"}
                ],
                "model": self.model,
                "max_tokens": 50,
                "temperature": 0.5
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=test_data,
                timeout=15
            )
            
            if response.status_code == 200:
                print("✅ Groq API connection successful!")
                result = response.json()
                message = result['choices'][0]['message']['content']
                print(f"✅ Test response: {message[:50]}...")
                return True
            elif response.status_code == 401:
                print("❌ Invalid Groq API key!")
                print("Go to https://console.groq.com/ and get your API key")
                return False
            else:
                print(f"❌ Groq API test failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Groq API connection error: {e}")
            return False

    def generate_mcu_recommendation(self, query: str, context: str, requirements: Dict) -> str:
        """Generate MCU recommendation using Groq API"""
        
        # Create focused prompt for MCU recommendation
        prompt = self.create_mcu_prompt(query, context, requirements)
        
        try:
            # Groq API request
            data = {
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are an expert embedded systems engineer specializing in microcontroller recommendations. Provide detailed, practical advice."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "model": self.model,
                "max_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            print(f"🚀 Sending request to Groq API...")
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract the AI response
                ai_response = result['choices'][0]['message']['content']
                
                print(f"✅ Groq response received!")
                return self.clean_api_response(ai_response)
                
            elif response.status_code == 429:
                print("⏳ Rate limited, waiting 5 seconds...")
                time.sleep(5)
                return self.generate_mcu_recommendation(query, context, requirements)
                
            else:
                print(f"❌ Groq API request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return self.generate_fallback_response(requirements)
                
        except Exception as e:
            print(f"❌ Groq API request error: {e}")
            return self.generate_fallback_response(requirements)

    def create_mcu_prompt(self, query: str, context: str, requirements: Dict) -> str:
        """Create a focused prompt for MCU recommendation"""
        
        prompt = f"""Based on the MCU database information below, provide a detailed recommendation for the best microcontroller.

USER QUERY: {query}

DETECTED REQUIREMENTS:
{json.dumps(requirements, indent=2)}

AVAILABLE MCUs IN DATABASE:
{context[:1000]}

Please provide:
1. **Recommended MCU**: Specific model name and why it's the best choice
2. **Key Specifications**: CPU, memory, peripherals, power consumption
3. **Why It Fits**: How it meets the specific requirements
4. **Alternative Options**: 1-2 backup choices if available
5. **Trade-offs**: Any limitations or considerations

Format your response clearly with headers and bullet points."""
        
        return prompt

    def clean_api_response(self, response: str) -> str:
        """Clean and format API response"""
        if not response:
            return "Unable to generate recommendation at this time."
        
        # Clean up the response
        cleaned = response.strip()
        
        # Ensure good formatting
        if not cleaned:
            return "Based on your requirements, please check the MCU database for suitable options."
            
        return cleaned

    def generate_fallback_response(self, requirements: Dict) -> str:
        """Generate fallback response when API fails"""
        
        response = "🔍 **MCU Recommendation** (Fallback Analysis)\n\n"
        
        if requirements.get('low_power'):
            response += "• **Low Power**: ARM Cortex-M0+, M4, or ultra-low power MCUs like MSP430\n"
        
        if requirements.get('wifi_support'):
            response += "• **WiFi**: ESP32, ESP8266, or WiFi-enabled development boards\n"
        
        if requirements.get('bluetooth_support'):
            response += "• **Bluetooth**: ESP32, Nordic nRF series, or integrated BLE MCUs\n"
        
        if requirements.get('high_performance'):
            response += "• **High Performance**: ARM Cortex-M7, dual-core processors, or RISC-V\n"
        
        if requirements.get('small_size'):
            response += "• **Compact Size**: Look for QFN, BGA packages, or integrated modules\n"
        
        response += "\n💡 **Next Steps**: Check the MCU database for specific models or try the API again."
        
        return response

# Test function
def test_groq_api():
    """Test the Groq API manager"""
    print("🧪 Testing Groq API Manager...")
    
    # Initialize with your API key
    manager = GroqAPIManager("gsk_YOUR_GROQ_API_KEY_HERE")  # Replace with your key
    
    # Test connection
    if manager.test_api_connection():
        print("✅ Connection test passed!")
        
        # Test MCU recommendation
        test_requirements = {"low_power": True, "wifi_support": True}
        test_context = "ESP32: WiFi, Bluetooth, low power modes. Arduino Uno: Basic, no wireless."
        
        print("\n🧪 Testing MCU recommendation...")
        recommendation = manager.generate_mcu_recommendation(
            "Suggest a low-power WiFi MCU for IoT sensor",
            test_context,
            test_requirements
        )
        
        print(f"\n✅ Test Recommendation:\n{recommendation[:200]}...")
        print("\n🎉 Groq API is working perfectly!")
    else:
        print("❌ Connection test failed!")

if __name__ == "__main__":
    test_groq_api()