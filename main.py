import dbus
import logging
from bluezero import peripheral, adapter, async_tools
import subprocess

logging.basicConfig(level=logging.DEBUG)

DEVICE_NAME = "BLE Router Peripheral"

UPLOAD_SERVICE = "c8edc62d-8604-40c6-a4b4-8878d228ec1c"
DOWNLOAD_SERVICE = "e1f803e0-7bb5-40a2-a826-2219f54fab56"

UPLOAD_SERVICE_ID = 1
DOWNLOAD_SERVICE_ID = 2

UPLOAD_DATA_CHARACTERISTIC = "124a03e2-46c2-4ddd-8cf2-b643a1e91071"
UPLOAD_ID_CHARACTERISTIC = "d7299075-a344-48a7-82bb-2baa19838b2d"
DOWNLOAD_DATA_CHARACTERISTIC = "b4bf78a1-b41a-4412-b3a9-97740d7003e0"

UPLOAD_DATA_CHARACTERISTIC_ID = 1
UPLOAD_ID_CHARACTERISTIC_ID = 2
DOWNLOAD_DATA_CHARACTERISTIC_ID = 3

def get_system_info():
    info = {}
    info["bluetooth_status"] = subprocess.getoutput("systemctl is-active bluetooth")
    info["dbus_status"] = subprocess.getoutput("systemctl is-active dbus")
    info["bluez_version"] = subprocess.getoutput("bluetoothctl --version")

    return info

def get_bluetooth_adapter():
    try:
        adapters = adapter.list_adapters()
        if adapters:
            return adapters[0]
        else:
            logging.error("No Bluetooth adapters found.")
            return None
    except Exception as e:
        logging.error(f"Error getting Bluetooth adapter: {e}")
        return None

def main():
  system_info = get_system_info()
  logging.info(f"System info: {system_info}")

  adapter_address = get_bluetooth_adapter()

  if adapter_address is None:
    raise Exception("No Bluetooth adapter found")

  logging.info(f"Using Bluetooth adapter: {adapter_address}")

  try:
    # Setup Peripheral
    my_peripheral = peripheral.Peripheral(adapter_address, local_name= DEVICE_NAME)

    # Add Services
    my_peripheral.add_service(UPLOAD_SERVICE_ID, UPLOAD_SERVICE, True)
    my_peripheral.add_service(DOWNLOAD_SERVICE_ID, DOWNLOAD_SERVICE, True)

    # Add Characteristics
    my_peripheral.add_characteristic(
      srv_id = UPLOAD_SERVICE_ID,
      chr_id = UPLOAD_DATA_CHARACTERISTIC_ID,
      uuid = UPLOAD_DATA_CHARACTERISTIC,
      value = [],
      notifying = False,
      flags = ["read"],
      notify_callback = None,
    )

    my_peripheral.add_characteristic(
      srv_id = UPLOAD_SERVICE_ID,
      chr_id = UPLOAD_ID_CHARACTERISTIC_ID,
      uuid = UPLOAD_ID_CHARACTERISTIC,
      value = [],
      notifying = False,
      flags = ["notify"],
      notify_callback = None,
    )

    my_peripheral.add_characteristic(
      srv_id = DOWNLOAD_SERVICE_ID,
      chr_id = DOWNLOAD_DATA_CHARACTERISTIC_ID,
      uuid = DOWNLOAD_DATA_CHARACTERISTIC,
      value = [],
      notifying = False,
      flags = ["write"],
      notify_callback = None,
    )

    # Start Advertising
    my_peripheral.publish()

  except dbus.exceptions.DBusException as e:
      logging.error(f"DBus error: {e}")
      logging.info("Please check if bluetoothd is running and you have the necessary permissions.")
  except Exception as e:
      logging.error(f"Unexpected error: {e}")
  finally:
      print("stop")

if __name__ == "__main__":
  main()