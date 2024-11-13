import asyncio
import json
from bleak import BleakClient, BleakGATTCharacteristic


# Load configuration from JSON file
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Read the MAC address from the configuration
THINGY_MAC_ADDRESS = config["thingy_mac_address"]


# UUIDs for the sensors
# see https://nordicsemiconductor.github.io/Nordic-Thingy52-FW/documentation/firmware_architecture.html
TEMPERATURE_UUID = "EF680201-9B35-4933-9B10-52FFA9740042"
HUMIDITY_UUID = "EF680203-9B35-4933-9B10-52FFA9740042"
AIR_QUALITY_UUID = "EF680204-9B35-4933-9B10-52FFA9740042"

# Notification handler to process incoming data
def notification_handler(sender: BleakGATTCharacteristic, data: bytearray):
    print(sender.description, "data:", list(data))
    
    if sender.uuid.lower() == TEMPERATURE_UUID.lower():
        # Convert temperature data (2 bytes)
        # Read the temperature data
        integer_part = int.from_bytes(data[0:1], byteorder="little", signed=True)  # First byte as int8_t
        decimal_part = int.from_bytes(data[1:2], byteorder="little")  # Second byte as uint8_t
        
        temperature = integer_part + (decimal_part / 100.0)  # Combine integer and decimal parts
        print(f"Temperature: {temperature:.2f} °C")

    elif sender.uuid.lower() == HUMIDITY_UUID.lower():
        # Convert humidity data (1 byte, integer percentage)
        humidity = int.from_bytes(data, byteorder="little")
        print(f"Humidity: {humidity}%")

    elif sender.uuid.lower() == AIR_QUALITY_UUID.lower():
        # Convert air quality data (4 byte)
        air_eCO2 = int.from_bytes(data[0:2], byteorder="little")  # First 2 bytes for eCO2
        air_TVOC = int.from_bytes(data[2:4], byteorder="little")  # Next 2 bytes for TVOC
        
        print(f"eCO2: {air_eCO2} ppm, TVOC: {air_TVOC} ppb")

async def main():
    async with BleakClient(THINGY_MAC_ADDRESS) as client:
        # Check if the client is connected
        if client.is_connected:
            print("Connected to Nordic Thingy:52")

            # Start receiving notifications
            await client.start_notify(TEMPERATURE_UUID, notification_handler)
            await client.start_notify(HUMIDITY_UUID, notification_handler)
            await client.start_notify(AIR_QUALITY_UUID, notification_handler)

            # Keep the connection alive for a sepcified period
            await asyncio.sleep(10)

            # Stop notifications when done
            await client.stop_notify(TEMPERATURE_UUID)
            await client.stop_notify(HUMIDITY_UUID)
            await client.stop_notify(AIR_QUALITY_UUID)

# Run the main function
asyncio.run(main())
