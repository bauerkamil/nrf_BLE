import asyncio
from bleak import BleakClient

# Replace with your Nordic device's MAC address
NORDIC_MAC_ADDRESS = "XX:XX:XX:XX:XX:XX"

# Replace with your characteristic UUID for LED control
LED_CONTROL_UUID = "ABCD1234-5678-5678-5678-1234567890AB"

# Command values to control LEDs
# These should match the protocol defined on your Nordic device
LED_COMMANDS = {
    "LED1_ON": bytearray([0x01]),  # Command to turn on LED 1
    "LED2_ON": bytearray([0x02]),  # Command to turn on LED 2
    "LED3_ON": bytearray([0x03]),  # Command to turn on LED 3
    "LED4_ON": bytearray([0x04]),  # Command to turn on LED 4
    "ALL_OFF": bytearray([0x00])   # Command to turn off all LEDs
}

async def control_led(mac_address, command):
    async with BleakClient(mac_address) as client:
        # Check if connected
        if client.is_connected:
            print(f"Connected to {mac_address}")
            
            # Send command to LED control characteristic
            try:
                await client.write_gatt_char(LED_CONTROL_UUID, command)
                print("Command sent successfully")
            except Exception as e:
                print(f"Failed to send command: {e}")
        else:
            print(f"Failed to connect to {mac_address}")

# Main function to send a command to light up LED 1
async def main():
    # Send a command to turn on LED 1
    await control_led(NORDIC_MAC_ADDRESS, LED_COMMANDS["LED1_ON"])

# Run the script
asyncio.run(main())
