"""
Web Scraper for MCU AI Assistant
Optional component for scraping MCU data from various sources
"""

import requests
from typing import Dict, List, Any, Optional
import time
import re

# Check for optional dependencies
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    BeautifulSoup = None

class MCUWebScraper:
    """Web scraper for MCU information (optional component)"""
    
    def __init__(self, enable_scraping: bool = False):
        """Initialize the web scraper"""
        
        self.enable_scraping = enable_scraping and BS4_AVAILABLE
        self.session = requests.Session()
        
        # Set user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Rate limiting
        self.request_delay = 1.0  # Delay between requests in seconds
        self.last_request_time = 0
        
        if not BS4_AVAILABLE:
            print("⚠️ BeautifulSoup4 not available. Web scraping disabled.")
            print("💡 Install with: pip install beautifulsoup4")
        elif not enable_scraping:
            print("📡 Web scraper initialized (disabled by default)")
        else:
            print("📡 Web scraper initialized and enabled")
    
    def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, timeout: int = 10) -> Optional[requests.Response]:
        """Make a web request with error handling"""
        
        if not self.enable_scraping:
            return None
        
        try:
            self._rate_limit()
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"⚠️ Request failed for {url}: {e}")
            return None
    
    def scrape_manufacturer_page(self, manufacturer_url: str) -> List[Dict[str, Any]]:
        """Scrape MCU data from manufacturer website (placeholder)"""
        
        print(f"📡 Scraping manufacturer page: {manufacturer_url}")
        
        if not self.enable_scraping:
            print("⚠️ Web scraping is disabled")
            return []
        
        response = self._make_request(manufacturer_url)
        if not response:
            return []
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # This is a placeholder implementation
            # Each manufacturer would need specific parsing logic
            mcus = []
            
            # Generic approach - look for common patterns
            # This would need to be customized for each manufacturer's website
            product_links = soup.find_all('a', href=re.compile(r'product|mcu|microcontroller', re.I))
            
            for link in product_links[:5]:  # Limit to first 5 for testing
                product_url = link.get('href')
                if product_url and not product_url.startswith('http'):
                    product_url = manufacturer_url.rstrip('/') + '/' + product_url.lstrip('/')
                
                mcu_data = self.scrape_product_page(product_url)
                if mcu_data:
                    mcus.append(mcu_data)
            
            return mcus
            
        except Exception as e:
            print(f"⚠️ Error parsing manufacturer page: {e}")
            return []
    
    def scrape_product_page(self, product_url: str) -> Optional[Dict[str, Any]]:
        """Scrape individual MCU product page (placeholder)"""
        
        if not self.enable_scraping:
            return None
        
        response = self._make_request(product_url)
        if not response:
            return None
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Generic extraction - would need customization per site
            mcu_data = {
                'name': self._extract_product_name(soup),
                'manufacturer': self._extract_manufacturer(soup),
                'cpu_architecture': self._extract_architecture(soup),
                'cpu_speed': self._extract_cpu_speed(soup),
                'flash_memory': self._extract_flash_memory(soup),
                'ram_memory': self._extract_ram_memory(soup),
                'operating_voltage': self._extract_voltage(soup),
                'power_consumption': self._extract_power_consumption(soup),
                'package_type': self._extract_package_type(soup),
                'gpio_pins': self._extract_gpio_count(soup),
                'communication_interfaces': self._extract_interfaces(soup),
                'special_features': self._extract_features(soup),
                'typical_applications': self._extract_applications(soup),
                'price_range': self._extract_price(soup),
                'datasheet_url': product_url
            }
            
            # Filter out None values
            mcu_data = {k: v for k, v in mcu_data.items() if v is not None}
            
            return mcu_data if len(mcu_data) > 3 else None  # Only return if we got some data
            
        except Exception as e:
            print(f"⚠️ Error parsing product page {product_url}: {e}")
            return None
    
    def _extract_product_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product name from page"""
        # Look for common title patterns
        selectors = [
            'h1',
            '.product-title',
            '.product-name',
            '[class*="title"]',
            '[class*="name"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.text.strip():
                return element.text.strip()
        
        return None
    
    def _extract_manufacturer(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract manufacturer from page"""
        # Look for manufacturer in various places
        text = soup.get_text().lower()
        
        manufacturers = [
            'espressif', 'microchip', 'stmicroelectronics', 'nordic',
            'texas instruments', 'nxp', 'raspberry pi', 'atmel',
            'infineon', 'renesas', 'cypress', 'silicon labs'
        ]
        
        for manufacturer in manufacturers:
            if manufacturer in text:
                return manufacturer.title()
        
        return None
    
    def _extract_architecture(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract CPU architecture from page"""
        text = soup.get_text().lower()
        
        architectures = [
            ('arm cortex-m7', 'ARM Cortex-M7'),
            ('arm cortex-m4', 'ARM Cortex-M4'),
            ('arm cortex-m3', 'ARM Cortex-M3'),
            ('arm cortex-m0', 'ARM Cortex-M0'),
            ('xtensa', 'Xtensa'),
            ('avr', 'AVR'),
            ('mips', 'MIPS'),
            ('risc-v', 'RISC-V')
        ]
        
        for pattern, name in architectures:
            if pattern in text:
                return name
        
        return None
    
    def _extract_cpu_speed(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract CPU speed from page"""
        text = soup.get_text()
        
        # Look for speed patterns
        speed_pattern = r'(\d+)\s*(?:MHz|GHz|megahertz|gigahertz)'
        match = re.search(speed_pattern, text, re.IGNORECASE)
        
        if match:
            speed = match.group(1)
            unit = 'MHz' if 'mhz' in match.group(0).lower() else 'GHz'
            return f"{speed}{unit}"
        
        return None
    
    def _extract_flash_memory(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract flash memory from page"""
        text = soup.get_text()
        
        # Look for flash memory patterns
        flash_patterns = [
            r'(\d+)\s*(?:MB|KB|megabyte|kilobyte).*flash',
            r'flash.*(\d+)\s*(?:MB|KB|megabyte|kilobyte)',
            r'(\d+)\s*(?:MB|KB).*program.*memory'
        ]
        
        for pattern in flash_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                size = match.group(1)
                unit = 'MB' if 'mb' in match.group(0).lower() else 'KB'
                return f"{size}{unit}"
        
        return None
    
    def _extract_ram_memory(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract RAM memory from page"""
        text = soup.get_text()
        
        # Look for RAM patterns
        ram_patterns = [
            r'(\d+)\s*(?:MB|KB|megabyte|kilobyte).*(?:RAM|SRAM|memory)',
            r'(?:RAM|SRAM).*(\d+)\s*(?:MB|KB|megabyte|kilobyte)'
        ]
        
        for pattern in ram_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                size = match.group(1)
                unit = 'MB' if 'mb' in match.group(0).lower() else 'KB'
                return f"{size}{unit}"
        
        return None
    
    def _extract_voltage(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract operating voltage from page"""
        text = soup.get_text()
        
        # Look for voltage patterns
        voltage_patterns = [
            r'(\d+(?:\.\d+)?)\s*V(?:olt)?.*operating',
            r'operating.*(\d+(?:\.\d+)?)\s*V(?:olt)?',
            r'(\d+(?:\.\d+)?)\s*to\s*(\d+(?:\.\d+)?)\s*V'
        ]
        
        for pattern in voltage_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return None
    
    def _extract_power_consumption(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract power consumption from page"""
        text = soup.get_text()
        
        # Look for power consumption patterns
        power_patterns = [
            r'\d+(?:\.\d+)?\s*(?:mA|µA|uA).*(?:active|running)',
            r'(?:active|running).*\d+(?:\.\d+)?\s*(?:mA|µA|uA)',
            r'power.*\d+(?:\.\d+)?\s*(?:mW|mA|µA|uA)'
        ]
        
        for pattern in power_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return None
    
    def _extract_package_type(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract package type from page"""
        text = soup.get_text()
        
        packages = ['QFN', 'LQFP', 'BGA', 'DIP', 'SOIC', 'TSSOP', 'QFP', 'WLCSP']
        
        for package in packages:
            if package.lower() in text.lower():
                return package
        
        return None
    
    def _extract_gpio_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract GPIO pin count from page"""
        text = soup.get_text()
        
        # Look for GPIO patterns
        gpio_patterns = [
            r'(\d+)\s*GPIO',
            r'(\d+)\s*I/O.*pin',
            r'(\d+)\s*digital.*pin'
        ]
        
        for pattern in gpio_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_interfaces(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract communication interfaces from page"""
        text = soup.get_text().lower()
        
        interfaces = []
        interface_keywords = [
            'wifi', 'bluetooth', 'ethernet', 'usb', 'can', 'spi', 'i2c', 'uart', 'i2s'
        ]
        
        for interface in interface_keywords:
            if interface in text:
                interfaces.append(interface.upper())
        
        return ', '.join(interfaces) if interfaces else None
    
    def _extract_features(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract special features from page"""
        text = soup.get_text().lower()
        
        features = []
        feature_keywords = [
            'low power', 'dual core', 'floating point', 'dsp', 'crypto',
            'security', 'touch', 'lcd', 'adc', 'dac', 'timer'
        ]
        
        for feature in feature_keywords:
            if feature in text:
                features.append(feature.title())
        
        return ', '.join(features) if features else None
    
    def _extract_applications(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract typical applications from page"""
        text = soup.get_text().lower()
        
        applications = []
        app_keywords = [
            'iot', 'automotive', 'industrial', 'medical', 'consumer',
            'wearable', 'smart home', 'sensor', 'control'
        ]
        
        for app in app_keywords:
            if app in text:
                applications.append(app.title())
        
        return ', '.join(applications) if applications else None
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract price information from page"""
        text = soup.get_text()
        
        # Look for price patterns
        price_patterns = [
            r'\$(\d+(?:\.\d+)?)',
            r'USD\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*dollars'
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            prices.extend([float(price) for price in matches])
        
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            if min_price == max_price:
                return f"${min_price:.2f}"
            else:
                return f"${min_price:.2f}-${max_price:.2f}"
        
        return None
    
    def search_mcu_online(self, query: str) -> List[Dict[str, Any]]:
        """Search for MCU information online (placeholder)"""
        
        print(f"🔍 Searching online for: {query}")
        
        if not self.enable_scraping:
            print("⚠️ Online search disabled (web scraping not enabled)")
            return []
        
        # This would implement actual search functionality
        # Could search manufacturer websites, distributors, etc.
        
        # Placeholder implementation
        search_urls = [
            f"https://example-distributor.com/search?q={query}",
            f"https://example-manufacturer.com/products?search={query}"
        ]
        
        results = []
        for url in search_urls:
            # This is just a placeholder - would need real implementation
            print(f"📡 Would search: {url}")
        
        return results
    
    def get_latest_mcu_releases(self) -> List[Dict[str, Any]]:
        """Get latest MCU releases (placeholder)"""
        
        print("📡 Fetching latest MCU releases...")
        
        if not self.enable_scraping:
            print("⚠️ Latest releases fetch disabled")
            return []
        
        # Placeholder for fetching latest releases from various sources
        # Could scrape tech news sites, manufacturer announcement pages, etc.
        
        return []
    
    def validate_mcu_data(self, mcu_data: Dict[str, Any]) -> bool:
        """Validate scraped MCU data"""
        
        required_fields = ['name']
        
        # Check if we have at least the name
        if not mcu_data.get('name'):
            return False
        
        # Check if we have at least 3 meaningful fields
        meaningful_fields = 0
        for key, value in mcu_data.items():
            if value and value != 'None' and len(str(value).strip()) > 0:
                meaningful_fields += 1
        
        return meaningful_fields >= 3

# Test function
def test_web_scraper():
    """Test the web scraper functionality"""
    
    print("🧪 Testing Web Scraper...")
    
    # Test with scraping disabled (default)
    scraper = MCUWebScraper(enable_scraping=False)
    
    # Test basic functionality
    print("✅ Web scraper initialized (disabled)")
    
    # Test online search (will show placeholder behavior)
    results = scraper.search_mcu_online("ESP32")
    print(f"✅ Online search returned {len(results)} results")
    
    # Test latest releases
    releases = scraper.get_latest_mcu_releases()
    print(f"✅ Latest releases returned {len(releases)} items")
    
    # Test data validation
    test_data = {
        'name': 'Test MCU',
        'manufacturer': 'Test Corp',
        'cpu_speed': '100MHz'
    }
    
    is_valid = scraper.validate_mcu_data(test_data)
    print(f"✅ Data validation result: {is_valid}")
    
    print("🎉 Web scraper test completed!")
    print("💡 To enable actual web scraping, install beautifulsoup4 and set enable_scraping=True")

if __name__ == "__main__":
    test_web_scraper()