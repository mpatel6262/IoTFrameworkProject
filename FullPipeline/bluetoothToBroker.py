import asyncio
import platform
import json
import paho.mqtt.client as mqtt
import time
import sys

from bleak import BleakClient
from bleak import BleakScanner
from bleak.uuids import uuid16_dict
from uuid import UUID

mqttBroker = "mqtt.eclipseprojects.io"
mqttClient = mqtt.Client("TISENSORTAGDATA")
mqttClient.connect(mqttBroker)

def normalize_uuid_str(uuid: str) -> str:
    """
    Normaizes a UUID to the format used by Bleak.

    - Converted to lower case.
    - 16-bit and 32-bit UUIDs are expanded to 128-bit.

    Example::

        # 16-bit
        uuid1 = normalize_uuid_str("1234")
        # uuid1 == "00001234-1000-8000-00805f9b34fb"

        # 32-bit
        uuid2 = normalize_uuid_str("12345678")
        # uuid2 == "12345678-1000-8000-00805f9b34fb"

        # 128-bit
        uuid3 = normalize_uuid_str("12345678-1234-1234-1234567890ABC")
        # uuid3 == "12345678-1234-1234-1234567890abc"

    .. versionadded:: 0.20
    .. versionchanged:: 0.21
        Added support for 32-bit UUIDs.
    """
    # See: BLUETOOTH CORE SPECIFICATION Version 5.4 | Vol 3, Part B - Section 2.5.1
    if len(uuid) == 4:
        # Bluetooth SIG registered 16-bit UUIDs
        uuid = f"0000{uuid}-0000-1000-8000-00805f9b34fb"
    elif len(uuid) == 8:
        # Bluetooth SIG registered 32-bit UUIDs
        uuid = f"{uuid}-0000-1000-8000-00805f9b34fb"

    # let UUID class do the validation and conversion to lower case
    return str(UUID(uuid))

def normalize_uuid_16(uuid: int) -> str:
    """
    Normaizes a 16-bit integer UUID to the format used by Bleak.

    Returns:
        128-bit UUID as string with the format ``"0000xxxx-1000-8000-00805f9b34fb"``.

    Example::

        uuid = normalize_uuid_16(0x1234)
        # uuid == "00001234-1000-8000-00805f9b34fb"

    .. versionadded:: 0.21
    """
    return normalize_uuid_str(f"{uuid:04X}")

ADDRESS = (
    "24:71:89:cc:09:05"
    if platform.system() != "Darwin"
    else "B9EA5233-37EF-4DD6-87A8-2A875E821C46"
)

ALL_SENSORTAG_CHARACTERISTIC_UUIDS = """
00002a00-0000-1000-8000-00805f9b34fb
00002a01-0000-1000-8000-00805f9b34fb
00002a04-0000-1000-8000-00805f9b34fb
00002a23-0000-1000-8000-00805f9b34fb
00002a24-0000-1000-8000-00805f9b34fb
00002a25-0000-1000-8000-00805f9b34fb
00002a26-0000-1000-8000-00805f9b34fb
00002a27-0000-1000-8000-00805f9b34fb
00002a28-0000-1000-8000-00805f9b34fb
00002a29-0000-1000-8000-00805f9b34fb
00002a2a-0000-1000-8000-00805f9b34fb
00002a50-0000-1000-8000-00805f9b34fb
00002a19-0000-1000-8000-00805f9b34fb
f000aa01-0451-4000-b000-000000000000
f000aa02-0451-4000-b000-000000000000
f000aa03-0451-4000-b000-000000000000
f000aa21-0451-4000-b000-000000000000
f000aa22-0451-4000-b000-000000000000
f000aa23-0451-4000-b000-000000000000
f000aa41-0451-4000-b000-000000000000
f000aa42-0451-4000-b000-000000000000
f000aa44-0451-4000-b000-000000000000
f000aa81-0451-4000-b000-000000000000
f000aa82-0451-4000-b000-000000000000
f000aa83-0451-4000-b000-000000000000
f000aa71-0451-4000-b000-000000000000
f000aa72-0451-4000-b000-000000000000
f000aa73-0451-4000-b000-000000000000
0000ffe1-0000-1000-8000-00805f9b34fb
f000aa65-0451-4000-b000-000000000000
f000aa66-0451-4000-b000-000000000000
f000ac01-0451-4000-b000-000000000000
f000ac02-0451-4000-b000-000000000000
f000ac03-0451-4000-b000-000000000000
f000ccc1-0451-4000-b000-000000000000
f000ccc2-0451-4000-b000-000000000000
f000ccc3-0451-4000-b000-000000000000
f000ffc1-0451-4000-b000-000000000000
f000ffc2-0451-4000-b000-000000000000
f000ffc3-0451-4000-b000-000000000000
f000ffc4-0451-4000-b000-000000000000
"""

uuid16_lookup = {v: normalize_uuid_16(k) for k, v in uuid16_dict.items()}

SYSTEM_ID_UUID = uuid16_lookup["System ID"]
MODEL_NBR_UUID = uuid16_lookup["Model Number String"]
DEVICE_NAME_UUID = uuid16_lookup["Device Name"]
FIRMWARE_REV_UUID = uuid16_lookup["Firmware Revision String"]
HARDWARE_REV_UUID = uuid16_lookup["Hardware Revision String"]
SOFTWARE_REV_UUID = uuid16_lookup["Software Revision String"]
MANUFACTURER_NAME_UUID = uuid16_lookup["Manufacturer Name String"]
BATTERY_LEVEL_UUID = uuid16_lookup["Battery Level"]
KEY_PRESS_UUID = normalize_uuid_16(0xFFE1)

IO_DATA_CHAR_UUID = "f000aa01-0451-4000-b000-000000000000"
IO_CONFIG_CHAR_UUID = "f000aa02-0451-4000-b000-000000000000"


async def main():
    while True:
        devices = await BleakScanner.discover()
        addresses = []
        for d in devices:
            if(d.name == "CC2650 SensorTag"):
                addresses.append(d.address)
        for address in addresses:
            async with BleakClient(address, winrt=dict(use_cached_services=True)) as client:
                system_id = await client.read_gatt_char(SYSTEM_ID_UUID)
                model_number = await client.read_gatt_char(MODEL_NBR_UUID)
                device_name = ""
                try:
                    device_name = await client.read_gatt_char(DEVICE_NAME_UUID)
                    print("Device Name: {0}".format("".join(map(chr, device_name))))
                except Exception:
                    pass
                manufacturer_name = await client.read_gatt_char(MANUFACTURER_NAME_UUID)
                firmware_revision = await client.read_gatt_char(FIRMWARE_REV_UUID)
                hardware_revision = await client.read_gatt_char(HARDWARE_REV_UUID)
                software_revision = await client.read_gatt_char(SOFTWARE_REV_UUID)
                battery_level = await client.read_gatt_char(BATTERY_LEVEL_UUID)
                
                sensorTag = {
                    "system_id":  ":".join(["{:02x}".format(x) for x in system_id[::-1]]),
                    "model_number": "".join(map(chr, model_number)),
                    "device_name": "".join(map(chr, device_name)),
                    "manufacturer_name": "".join(map(chr, manufacturer_name)),
                    "firmware_revision": "".join(map(chr, firmware_revision)),
                    "hardware_revision": "".join(map(chr, hardware_revision)),
                    "software_revision": "".join(map(chr, software_revision)),
                    "battery_level": "{0}%".format(int(battery_level[0]))
                }
                
                sensorJSON = json.dumps(sensorTag)
                print("-----------------------------------------")
                print(sensorJSON)
                print("-----------------------------------------")

                mqttClient.publish("TISENSORTAGDATA", sensorJSON)
                
        time.sleep(5)
    

asyncio.run(main())

