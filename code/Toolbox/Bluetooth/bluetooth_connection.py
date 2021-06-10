# @file bluetooth_connection.py
# @brief Connect to a device using Bleak bluetooth connection

# Author : Ackermann Gawen
# Last update : 10.06.2021
import asyncio
from bleak import BleakClient
import datetime


now = datetime.datetime.now()
address = "90:84:2B:50:36:43"
#address = "90:84:2B:8A:36:43"
LEGO_Hub_Service = "00001623-1212-EFDE-1623-785FEABCD123"
LEGO_Hub_Characteristic = "00001624-1212-EFDE-1623-785FEABCD123"

async def run(address):
    """Connect to a device and read a characteristic
    
    address : The mac address of the device to pair to
    """
    # Create a client from his mac address
    client = BleakClient(address)
    try:
        await client.connect()
        # Read a specific characteristc
        model_number = await client.read_gatt_char(LEGO_Hub_Characteristic)
        # Try to pairs self to a device
        is_paired = await client.pair()
        mod_num = ""
        for byte in model_number:
            mod_num += str(byte)
            
        if is_paired:
           print("paired")
           
        print("Model Number: {0}".format(mod_num))
    except Exception as e:
        print(e)
    finally:
        await client.disconnect()
        
# Execute the async loop
loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))

