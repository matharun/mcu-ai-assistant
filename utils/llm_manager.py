from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import Dict, List, Any
import re

class LLMManager:
    def __init__(self, model_name="distilgpt2"):
        """Initialize Hugging Face LLM for MCU recommendations"""
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load model and tokenizer
        try:
            print(f"Loading lightweight model: {model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            print("✅ LLM model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("⚠️ Using fallback response system...")
            self.tokenizer = None
            self.model = None

    def generate_mcu_recommendation(self, query: str, context: str, requirements: Dict) -> str:
        """Generate MCU recommendation using context"""
        
        # If models failed to load, use rule-based responses
        if self.model is None or self.tokenizer is None:
            return self.create_rule_based_response(query, context, requirements)
        
        # Try normal LLM generation
        try:
            prompt = self.create_mcu_prompt(query, context, requirements)
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 150,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    attention_mask=torch.ones(inputs.shape, dtype=torch.long)
                )
            
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = full_response[len(prompt):].strip()
            
            if len(response) < 20:
                return self.create_rule_based_response(query, context, requirements)
            
            return response
            
        except Exception as e:
            print(f"Error in generation: {e}")
            return self.create_rule_based_response(query, context, requirements)

    def create_mcu_prompt(self, query: str, context: str, requirements: Dict) -> str:
        """Create a structured prompt for MCU recommendations"""
        req_text = ", ".join([f"{k}: {v}" for k, v in requirements.items()])
        
        prompt = f"""MCU Expert System

Question: {query}
Requirements: {req_text}

Available MCUs:
{context}

Recommendation:"""
        
        return prompt

    def create_rule_based_response(self, query: str, context: str, requirements: Dict) -> str:
        """Create intelligent responses without LLM"""
        
        # Extract MCU names from context
        mcu_matches = re.findall(r'MCU: ([A-Za-z0-9-]+)', context)
        
        response_parts = []
        
        # Header
        response_parts.append("## MCU Recommendation Analysis")
        
        # Based on requirements
        if requirements:
            response_parts.append("\n**Your Requirements:**")
            for req, value in requirements.items():
                if req == 'flash_size_kb_min':
                    response_parts.append(f"• Minimum Flash Memory: {value}KB")
                elif req == 'ram_size_kb_min':
                    response_parts.append(f"• Minimum RAM: {value}KB")
                elif req == 'low_power':
                    response_parts.append("• Low power consumption required")
                elif req == 'wifi_support':
                    response_parts.append("• WiFi connectivity needed")
                elif req == 'bluetooth_support':
                    response_parts.append("• Bluetooth connectivity needed")
        
        # Recommended MCUs
        if mcu_matches:
            response_parts.append(f"\n**Recommended MCU(s):** {', '.join(mcu_matches[:3])}")
            
            # Add specific advice based on context
            if 'ESP32' in context:
                response_parts.append("\n**ESP32 Series Benefits:**")
                response_parts.append("• Built-in WiFi and Bluetooth")
                response_parts.append("• Excellent for IoT projects")
                response_parts.append("• Large community support")
                response_parts.append("• Arduino IDE compatible")
            
            if 'STM32' in context:
                response_parts.append("\n**STM32 Series Benefits:**")
                response_parts.append("• Ultra-low power consumption")
                response_parts.append("• Professional development tools")
                response_parts.append("• Industrial grade reliability")
                response_parts.append("• Wide range of peripherals")
            
            if 'ATMEGA' in context:
                response_parts.append("\n**ATmega Series Benefits:**")
                response_parts.append("• Arduino compatible")
                response_parts.append("• Simple to program")
                response_parts.append("• Cost-effective")
                response_parts.append("• Great for learning")
        else:
            response_parts.append("\n**General Recommendation:**")
            response_parts.append("Based on your requirements, consider reviewing the specifications of available MCUs in our database.")
        
        # General advice
        response_parts.append("\n**Next Steps:**")
        response_parts.append("• Review detailed datasheets")
        response_parts.append("• Check development board availability")
        response_parts.append("• Consider toolchain and IDE support")
        response_parts.append("• Evaluate total system cost")
        
        return "\n".join(response_parts)

    def test_generation(self) -> str:
        """Test the LLM generation capability"""
        if self.model is None:
            return "Fallback system active - no model testing needed"
        
        try:
            test_prompt = "MCU recommendation:"
            inputs = self.tokenizer.encode(test_prompt, return_tensors="pt")
            outputs = self.model.generate(inputs, max_length=50, temperature=0.7)
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response
        except Exception as e:
            return f"Test failed: {e}"