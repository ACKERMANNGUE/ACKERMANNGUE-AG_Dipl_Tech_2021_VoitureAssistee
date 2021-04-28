import asyncio
from bleak import BleakClient, BleakScanner
import datetime


now = datetime.datetime.now()
address = "90:84:2B:50:36:43"
#address = "90:84:2B:8A:36:43"
MODEL_NBR_UUID = "00001624-1212-EFDE-1623-785FEABCD123"


async def research(address):
    print(str(now))
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)


async def run(address):
    client = BleakClient(address)
    try:
        await client.connect()
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        is_paired = await client.pair()
        mod_num = ""
        desc = ""
        for byte in model_number:
            mod_num += str(byte)
            
        if is_paired:
           print("paired")
           
        print("Model Number: {0}".format(mod_num))
    except Exception as e:
        print(e)
    finally:
        await client.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))
# loop.run_until_complete(research())
