"""
Query Processor for MCU AI Assistant
Processes natural language queries and extracts MCU requirements
"""

import re
from typing import Dict, List, Any, Tuple
import json

class QueryProcessor:
    """Processes user queries and extracts MCU requirements"""
    
    def __init__(self):
        """Initialize the query processor"""
        
        # Define requirement patterns and keywords
        self.requirement_patterns = {
            'low_power': {
                'keywords': ['low power', 'battery', 'power efficient', 'energy saving', 
                           'ultra low power', 'sleep mode', 'power consumption', 'battery life',
                           'energy harvesting', 'low current', 'standby', 'deep sleep'],
                'weight': 2.0
            },
            'high_performance': {
                'keywords': ['high performance', 'fast', 'high speed', 'powerful', 'high frequency',
                           'real-time', 'intensive', 'heavy computation', 'processing power',
                           'dual core', 'multi core', 'floating point', 'dsp'],
                'weight': 2.0
            },
            'wifi_support': {
                'keywords': ['wifi', 'wi-fi', '802.11', 'wireless', 'internet', 'web',
                           'cloud', 'iot', 'network', 'connectivity'],
                'weight': 3.0
            },
            'bluetooth_support': {
                'keywords': ['bluetooth', 'ble', 'bluetooth low energy', 'bt', 'wireless',
                           'pairing', 'beacon', 'mesh'],
                'weight': 3.0
            },
            'ethernet_support': {
                'keywords': ['ethernet', 'wired network', 'rj45', 'tcp/ip', 'lan'],
                'weight': 2.5
            },
            'usb_support': {
                'keywords': ['usb', 'usb host', 'usb device', 'usb otg'],
                'weight': 2.0
            },
            'can_support': {
                'keywords': ['can bus', 'can', 'automotive', 'vehicle', 'car'],
                'weight': 2.5
            },
            'small_size': {
                'keywords': ['small', 'compact', 'tiny', 'miniature', 'space constrained',
                           'portable', 'wearable', 'embedded'],
                'weight': 1.5
            },
            'low_cost': {
                'keywords': ['cheap', 'low cost', 'budget', 'affordable', 'inexpensive',
                           'cost effective', 'economical'],
                'weight': 1.5
            },
            'beginner_friendly': {
                'keywords': ['beginner', 'easy', 'simple', 'learning', 'education',
                           'tutorial', 'getting started', 'arduino', 'novice'],
                'weight': 1.0
            },
            'industrial': {
                'keywords': ['industrial', 'commercial', 'professional', 'robust',
                           'reliable', 'temperature range', 'harsh environment'],
                'weight': 2.0
            },
            'audio_processing': {
                'keywords': ['audio', 'sound', 'music', 'voice', 'microphone', 'speaker',
                           'audio codec', 'i2s', 'sound processing'],
                'weight': 2.5
            },
            'display_support': {
                'keywords': ['display', 'lcd', 'oled', 'screen', 'graphics', 'gui',
                           'touch screen', 'tft'],
                'weight': 2.0
            },
            'sensor_interface': {
                'keywords': ['sensor', 'adc', 'analog', 'measurement', 'monitoring',
                           'data acquisition', 'temperature', 'pressure', 'accelerometer'],
                'weight': 1.5
            },
            'motor_control': {
                'keywords': ['motor', 'servo', 'stepper', 'pwm', 'control', 'robotics',
                           'actuator', 'drive'],
                'weight': 2.0
            }
        }
        
        # Application categories
        self.application_patterns = {
            'iot': ['iot', 'internet of things', 'smart home', 'connected device'],
            'automotive': ['automotive', 'car', 'vehicle', 'can bus'],
            'medical': ['medical', 'health', 'biomedical', 'patient monitoring'],
            'industrial': ['industrial', 'automation', 'control system', 'manufacturing'],
            'consumer': ['consumer', 'home appliance', 'entertainment'],
            'education': ['education', 'learning', 'student', 'teaching'],
            'robotics': ['robot', 'robotics', 'autonomous', 'navigation'],
            'wearable': ['wearable', 'fitness tracker', 'smartwatch', 'portable'],
            'audio': ['audio', 'music', 'sound', 'voice', 'speaker'],
            'gaming': ['game', 'gaming', 'controller', 'interactive']
        }
        
        print("✅ Query processor initialized")
    
    def extract_requirements(self, query: str) -> Dict[str, Any]:
        """Extract MCU requirements from natural language query"""
        
        query_lower = query.lower().strip()
        requirements = {}
        
        # Extract boolean requirements
        for req_name, req_data in self.requirement_patterns.items():
            score = 0
            matched_keywords = []
            
            for keyword in req_data['keywords']:
                if keyword in query_lower:
                    score += req_data['weight']
                    matched_keywords.append(keyword)
            
            if score > 0:
                requirements[req_name] = True
                # Store additional info for debugging
                if hasattr(self, 'debug') and self.debug:
                    requirements[f'{req_name}_score'] = score
                    requirements[f'{req_name}_keywords'] = matched_keywords
        
        # Extract numeric requirements
        numeric_reqs = self._extract_numeric_requirements(query_lower)
        requirements.update(numeric_reqs)
        
        # Extract application category
        application = self._extract_application_category(query_lower)
        if application:
            requirements['application_category'] = application
        
        # Extract manufacturer preferences
        manufacturer = self._extract_manufacturer_preference(query_lower)
        if manufacturer:
            requirements['preferred_manufacturer'] = manufacturer
        
        # Extract architecture preferences
        architecture = self._extract_architecture_preference(query_lower)
        if architecture:
            requirements['preferred_architecture'] = architecture
        
        return requirements
    
    def _extract_numeric_requirements(self, query: str) -> Dict[str, Any]:
        """Extract numeric requirements like memory size, speed, etc."""
        
        numeric_reqs = {}
        
        # Memory requirements (Flash)
        flash_patterns = [
            r'(\d+)\s*(?:mb|megabyte).*flash',
            r'(\d+)\s*(?:kb|kilobyte).*flash',
            r'flash.*(\d+)\s*(?:mb|megabyte)',
            r'flash.*(\d+)\s*(?:kb|kilobyte)',
            r'(\d+)\s*(?:mb|kb).*memory'
        ]
        
        for pattern in flash_patterns:
            match = re.search(pattern, query)
            if match:
                size = int(match.group(1))
                unit = 'MB' if 'mb' in match.group(0).lower() else 'KB'
                numeric_reqs['min_flash_memory'] = f"{size}{unit}"
                break
        
        # RAM requirements
        ram_patterns = [
            r'(\d+)\s*(?:mb|megabyte).*ram',
            r'(\d+)\s*(?:kb|kilobyte).*ram',
            r'ram.*(\d+)\s*(?:mb|megabyte)',
            r'ram.*(\d+)\s*(?:kb|kilobyte)'
        ]
        
        for pattern in ram_patterns:
            match = re.search(pattern, query)
            if match:
                size = int(match.group(1))
                unit = 'MB' if 'mb' in match.group(0).lower() else 'KB'
                numeric_reqs['min_ram_memory'] = f"{size}{unit}"
                break
        
        # Speed requirements
        speed_patterns = [
            r'(\d+)\s*mhz',
            r'(\d+)\s*ghz',
            r'(\d+)\s*megahertz',
            r'(\d+)\s*gigahertz'
        ]
        
        for pattern in speed_patterns:
            match = re.search(pattern, query)
            if match:
                speed = int(match.group(1))
                unit = 'GHz' if 'ghz' in match.group(0).lower() else 'MHz'
                if unit == 'GHz':
                    speed *= 1000  # Convert to MHz for comparison
                numeric_reqs['min_cpu_speed_mhz'] = speed
                break
        
        # GPIO pin requirements
        gpio_patterns = [
            r'(\d+)\s*gpio',
            r'(\d+)\s*pins',
            r'(\d+)\s*i/o'
        ]
        
        for pattern in gpio_patterns:
            match = re.search(pattern, query)
            if match:
                pins = int(match.group(1))
                numeric_reqs['min_gpio_pins'] = pins
                break
        
        # Voltage requirements
        voltage_patterns = [
            r'(\d+(?:\.\d+)?)\s*v(?:olt)?',
            r'(\d+(?:\.\d+)?)\s*volt'
        ]
        
        for pattern in voltage_patterns:
            match = re.search(pattern, query)
            if match:
                voltage = float(match.group(1))
                numeric_reqs['operating_voltage'] = f"{voltage}V"
                break
        
        return numeric_reqs
    
    def _extract_application_category(self, query: str) -> str:
        """Extract application category from query"""
        
        for category, keywords in self.application_patterns.items():
            for keyword in keywords:
                if keyword in query:
                    return category
        
        return None
    
    def _extract_manufacturer_preference(self, query: str) -> str:
        """Extract manufacturer preference from query"""
        
        manufacturers = {
            'espressif': ['espressif', 'esp32', 'esp8266'],
            'microchip': ['microchip', 'atmel', 'pic', 'atmega', 'attiny', 'samd'],
            'stmicroelectronics': ['st', 'stm', 'stm32', 'stmicroelectronics'],
            'nordic': ['nordic', 'nrf52', 'nrf51', 'nrf53'],
            'texas_instruments': ['ti', 'texas instruments', 'msp430', 'tiva'],
            'nxp': ['nxp', 'lpc', 'kinetis', 'imx'],
            'raspberry_pi': ['raspberry pi', 'rp2040'],
            'arduino': ['arduino']
        }
        
        for manufacturer, keywords in manufacturers.items():
            for keyword in keywords:
                if keyword in query:
                    return manufacturer
        
        return None
    
    def _extract_architecture_preference(self, query: str) -> str:
        """Extract CPU architecture preference from query"""
        
        architectures = {
            'arm_cortex_m0': ['cortex-m0', 'cortex m0', 'arm m0'],
            'arm_cortex_m3': ['cortex-m3', 'cortex m3', 'arm m3'],
            'arm_cortex_m4': ['cortex-m4', 'cortex m4', 'arm m4'],
            'arm_cortex_m7': ['cortex-m7', 'cortex m7', 'arm m7'],
            'avr': ['avr', '8-bit'],
            'xtensa': ['xtensa', 'tensilica'],
            'risc_v': ['risc-v', 'riscv', 'risc v'],
            'mips': ['mips'],
            'arm': ['arm', 'cortex']
        }
        
        for arch, keywords in architectures.items():
            for keyword in keywords:
                if keyword in query:
                    return arch
        
        return None
    
    def analyze_query_complexity(self, query: str) -> Dict[str, Any]:
        """Analyze the complexity and specificity of the query"""
        
        query_lower = query.lower().strip()
        
        analysis = {
            'length': len(query),
            'word_count': len(query.split()),
            'technical_terms': 0,
            'specific_requirements': 0,
            'vague_terms': 0,
            'complexity_score': 0.0
        }
        
        # Count technical terms
        technical_terms = [
            'mcu', 'microcontroller', 'gpio', 'uart', 'spi', 'i2c', 'pwm', 'adc', 'dac',
            'cortex', 'arm', 'avr', 'mips', 'risc', 'xtensa', 'flash', 'ram', 'eeprom',
            'wifi', 'bluetooth', 'ethernet', 'can', 'usb', 'mhz', 'ghz', 'voltage',
            'current', 'power', 'consumption', 'sleep', 'standby'
        ]
        
        for term in technical_terms:
            if term in query_lower:
                analysis['technical_terms'] += 1
        
        # Count specific requirements
        for req_data in self.requirement_patterns.values():
            for keyword in req_data['keywords']:
                if keyword in query_lower:
                    analysis['specific_requirements'] += 1
                    break
        
        # Count vague terms
        vague_terms = ['good', 'best', 'nice', 'suitable', 'recommend', 'suggest', 'help']
        for term in vague_terms:
            if term in query_lower:
                analysis['vague_terms'] += 1
        
        # Calculate complexity score
        complexity_score = (
            analysis['technical_terms'] * 2 +
            analysis['specific_requirements'] * 3 +
            min(analysis['word_count'] / 10, 5) -
            analysis['vague_terms']
        )
        
        analysis['complexity_score'] = max(0.0, complexity_score)
        analysis['complexity_level'] = self._get_complexity_level(complexity_score)
        
        return analysis
    
    def _get_complexity_level(self, score: float) -> str:
        """Get complexity level based on score"""
        if score >= 15:
            return 'very_high'
        elif score >= 10:
            return 'high'
        elif score >= 5:
            return 'medium'
        elif score >= 2:
            return 'low'
        else:
            return 'very_low'
    
    def suggest_clarification_questions(self, requirements: Dict[str, Any]) -> List[str]:
        """Suggest clarification questions based on extracted requirements"""
        
        questions = []
        
        # If no specific requirements found
        if not any(req for req in requirements.values() if isinstance(req, bool)):
            questions.extend([
                "What will this microcontroller be used for?",
                "Do you need wireless connectivity (WiFi, Bluetooth)?",
                "What are your power consumption requirements?",
                "Are you working on a specific project type (IoT, robotics, etc.)?"
            ])
        
        # If power requirements unclear
        if not requirements.get('low_power') and not requirements.get('high_performance'):
            questions.append("What are your power consumption requirements?")
        
        # If connectivity unclear
        connectivity_reqs = ['wifi_support', 'bluetooth_support', 'ethernet_support', 'usb_support']
        if not any(requirements.get(req) for req in connectivity_reqs):
            questions.append("Do you need any specific connectivity options?")
        
        # If application unclear
        if not requirements.get('application_category'):
            questions.append("What type of application are you building?")
        
        # If no size/cost constraints mentioned
        if not requirements.get('small_size') and not requirements.get('low_cost'):
            questions.append("Do you have any size or cost constraints?")
        
        return questions[:3]  # Limit to top 3 questions
    
    def format_requirements_summary(self, requirements: Dict[str, Any]) -> str:
        """Format requirements into a readable summary"""
        
        if not requirements:
            return "No specific requirements detected."
        
        summary_parts = []
        
        # Boolean requirements
        bool_reqs = []
        for req_name, value in requirements.items():
            if isinstance(value, bool) and value:
                readable_name = req_name.replace('_', ' ').replace('support', '').strip()
                bool_reqs.append(readable_name)
        
        if bool_reqs:
            summary_parts.append(f"Features: {', '.join(bool_reqs)}")
        
        # Numeric requirements
        numeric_reqs = []
        for req_name, value in requirements.items():
            if req_name.startswith('min_') or req_name in ['operating_voltage']:
                readable_name = req_name.replace('min_', '').replace('_', ' ')
                numeric_reqs.append(f"{readable_name}: {value}")
        
        if numeric_reqs:
            summary_parts.append(f"Specifications: {', '.join(numeric_reqs)}")
        
        # Other requirements
        other_reqs = []
        for key, value in requirements.items():
            if key in ['application_category', 'preferred_manufacturer', 'preferred_architecture']:
                readable_key = key.replace('_', ' ')
                other_reqs.append(f"{readable_key}: {value}")
        
        if other_reqs:
            summary_parts.append(', '.join(other_reqs))
        
        return ' | '.join(summary_parts) if summary_parts else "General MCU requirements"

# Test function
def test_query_processor():
    """Test the query processor functionality"""
    
    print("🧪 Testing Query Processor...")
    
    processor = QueryProcessor()
    
    # Test queries
    test_queries = [
        "I need a low-power MCU with WiFi for IoT sensor monitoring",
        "Find me a high-performance ARM Cortex-M7 microcontroller with 1MB flash",
        "Suggest an Arduino-compatible MCU for beginners",
        "What's the best ESP32 for battery-powered applications?",
        "I need a microcontroller with Bluetooth and USB support for wearables",
        "Find a cheap 8-bit MCU with at least 32KB flash memory",
        "Recommend an STM32 for real-time audio processing with 120MHz speed"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test Query {i}: {query}")
        
        # Extract requirements
        requirements = processor.extract_requirements(query)
        print(f"📝 Requirements: {requirements}")
        
        # Analyze complexity
        analysis = processor.analyze_query_complexity(query)
        print(f"📊 Complexity: {analysis['complexity_level']} (score: {analysis['complexity_score']:.1f})")
        
        # Format summary
        summary = processor.format_requirements_summary(requirements)
        print(f"📋 Summary: {summary}")
        
        # Suggest questions if needed
        questions = processor.suggest_clarification_questions(requirements)
        if questions:
            print(f"❓ Clarification questions: {questions}")
        
        print("-" * 40)
    
    print("🎉 Query processor test completed!")

if __name__ == "__main__":
    test_query_processor()