import pandas as pd
from database.db_manager import MCUDatabase

db = MCUDatabase()

def clean_value(val):
    """Convert NaN and weird values to None"""
    if pd.isna(val) if not isinstance(val, str) else False:
        return None
    return str(val).strip() if val else None

# ===== MOUSER =====
def import_mouser():
    print("\n📦 Importing Mouser data...")
    df = pd.read_csv('MouserSearchDownload.csv')
    count = 0
    for _, row in df.iterrows():
        mcu = {
            "name": clean_value(row.get("Mfr Part Number")),
            "manufacturer": clean_value(row.get("Mfr.")),
            "cpu_architecture": clean_value(row.get("Core")),
            "cpu_speed": clean_value(row.get("Maximum Clock Frequency")),
            "flash_memory": clean_value(row.get("Program Memory Size")),
            "ram_memory": clean_value(row.get("Data RAM Size")),
            "package_type": clean_value(row.get("Package/Case")),
            "gpio_pins": clean_value(row.get("Number of I/Os")),
            "datasheet_url": clean_value(row.get("Datasheet")),
            "data_bus_width": clean_value(row.get("Data Bus Width")),
            "adc_resolution": clean_value(row.get("ADC Resolution")),
            "min_operating_temp": clean_value(row.get("Minimum Operating Temperature")),
            "max_operating_temp": clean_value(row.get("Maximum Operating Temperature")),
            "mounting_style": clean_value(row.get("Mounting Style")),
            "source": "mouser"
        }
        if mcu["name"]:
            db.add_mcu(mcu)
            count += 1
    print(f"✅ Mouser: {count} MCUs imported")

# ===== NXP =====
def import_nxp():
    print("\n📦 Importing NXP data...")
    df = pd.read_excel('NXPProductSelectorResults.xls', header=5)
    count = 0
    for _, row in df.iterrows():
        mcu = {
            "name": clean_value(row.get("Part Number")),
            "manufacturer": "NXP",
            "description": clean_value(row.get("Marketing Description")),
            "status": clean_value(row.get("Status")),
            "cpu_architecture": clean_value(row.get("Core Type")),
            "cpu_speed": clean_value(row.get("Operating Frequency [Max] (MHz)")),
            "flash_memory": clean_value(row.get("Flash (kB)")),
            "ram_memory": clean_value(row.get("SRAM (kB)")),
            "eeprom": clean_value(row.get("EEPROM (kB)")),
            "gpio_pins": clean_value(row.get("GPIO")),
            "package_type": clean_value(row.get("Package Type")),
            "operating_voltage": clean_value(row.get("Supply Voltage [Min to Max] (V)")),
            "operating_temp": clean_value(row.get("Ambient Operating Temperature (Min to Max) (℃)")),
            "communication_interfaces": clean_value(row.get("Serial Communication")),
            "can": clean_value(row.get("CAN")),
            "ethernet": clean_value(row.get("Ethernet")),
            "usb": clean_value(row.get("USB Controllers")),
            "adc": clean_value(row.get("ADC [Number, bits]")),
            "dac": clean_value(row.get("DAC [Number, bits]")),
            "pwm": clean_value(row.get("PWM [Number, bits]")),
            "timers": clean_value(row.get("Timers [Number, bits]")),
            "security": clean_value(row.get("Security")),
            "price": clean_value(row.get("Budgetary Price excluding tax(US$)")),
            "source": "nxp"
        }
        if mcu["name"]:
            db.add_mcu(mcu)
            count += 1
    print(f"✅ NXP: {count} MCUs imported")

# ===== RENESAS =====
def import_renesas():
    print("\n📦 Importing Renesas data...")
    df = pd.read_excel(
        'Renesas - Product Selector Microcontrollers & Microprocessors - 2025.9.5.xlsx',
        header=3
    )
    count = 0
    for _, row in df.iterrows():
        mcu = {
            "name": clean_value(row.get("Part Number")),
            "manufacturer": "Renesas",
            "description": clean_value(row.get("Product Title")),
            "status": clean_value(row.get("Status")),
            "package_type": clean_value(row.get("Package")),
            "family": clean_value(row.get("Family Name")),
            "series": clean_value(row.get("Series Name")),
            "cpu_architecture": clean_value(row.get("CPU Architecture")),
            "cpu_core": clean_value(row.get("Main CPU")),
            "bit_length": clean_value(row.get("Bit Length")),
            "flash_memory": clean_value(row.get("Program Memory (KB)")),
            "data_flash": clean_value(row.get("Data Flash (KB)")),
            "ram_memory": clean_value(row.get("RAM (KB)")),
            "gpio_pins": clean_value(row.get("I/O Ports")),
            "operating_voltage": clean_value(row.get("Supply Voltage (V)")),
            "operating_temp": clean_value(row.get("Temp. Range (°C)")),
            "cpu_speed": clean_value(row.get("Operating Freq (Max) (MHz)")),
            "ethernet": clean_value(row.get("Ethernet (ch)")),
            "usb": clean_value(row.get("USB Ports (#)")),
            "can": clean_value(row.get("CAN (ch)")),
            "uart": clean_value(row.get("SCI or UART (ch)")),
            "spi": clean_value(row.get("SPI (ch)")),
            "i2c": clean_value(row.get("I2C (#)")),
            "adc_12bit": clean_value(row.get("12-Bit A/D Converter (ch)")),
            "dac_12bit": clean_value(row.get("12-Bit D/A Converter (ch)")),
            "pwm_output": clean_value(row.get("PWM Output (pin#)")),
            "security": clean_value(row.get("Security & Encryption")),
            "wireless": clean_value(row.get("Wireless")),
            "floating_point": clean_value(row.get("Floating Point Unit")),
            "price": clean_value(row.get("Price (USD)")),
            "longevity": clean_value(row.get("Longevity")),
            "source": "renesas"
        }
        if mcu["name"]:
            db.add_mcu(mcu)
            count += 1
    print(f"✅ Renesas: {count} MCUs imported")

# ===== RUN ALL =====
if __name__ == "__main__":
    print("🚀 Starting MCU data import to MongoDB...")
    import_mouser()
    import_nxp()
    import_renesas()
    print(f"\n🎉 Done! Total MCUs in DB: {db.get_mcu_count()}")
