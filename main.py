import dbus
import logging
from bluezero import peripheral, adapter, async_tools
import subprocess

logging.basicConfig(level=logging.DEBUG)

DEVICE_NAME = "BLE Router Peripheral"

DATA_TRANSFER_SERVICE = "c8edc62d-8604-40c6-a4b4-8878d228ec1c"

DATA_TRANSFER_SERVICE_ID = 1

UPLOAD_DATA_CHARACTERISTIC = "124a03e2-46c2-4ddd-8cf2-b643a1e91071"
UPLOAD_DESTINATION_CHARACTERISTIC = "d7299075-a344-48a7-82bb-2baa19838b2d"
UPLOAD_BLE_MAC_CHARACTERISTIC = "99afe545-946e-437f-905e-06206b8d0f15"
DOWNLOAD_DATA_CHARACTERISTIC = "b4bf78a1-b41a-4412-b3a9-97740d7003e0"

UPLOAD_DATA_CHARACTERISTIC_ID = 1
UPLOAD_DESTINATION_CHARACTERISTIC_ID = 2
UPLOAD_BLE_MAC_CHARACTERISTIC_ID = 3
DOWNLOAD_DATA_CHARACTERISTIC_ID = 4

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

up_data = "sample".encode("UTF-8")
def update_up_data(characteristic):
  global up_data
  characteristic.set_value(up_data)

  return characteristic.is_notifying

# Callback Functions
def up_data_cb(notifying, characteristic):
  global up_data

  logging.debug("Notify")

  if notifying:
    async_tools.add_timer_seconds(5, update_up_data, characteristic)

up_destination = [192, 168, 64, 1]
def up_destination_cb():
  global up_destination

  logging.debug(f"Read Destination: {up_destination}")

up_ble_mac = [0, 0, 0, 0, 0, 0]
def up_ble_mac_cb():
  global up_ble_mac
  
  logging.debug(f"Read BLE MAC: {up_ble_mac}")

down_data = []
def down_data_cb(cls, value, option):
  global down_data
  down_data = value

  logging.debug(f"Download Data: {value}")

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
    my_peripheral.add_service(DATA_TRANSFER_SERVICE_ID, DATA_TRANSFER_SERVICE, True)

    # Add Characteristics
    my_peripheral.add_characteristic(
      srv_id = DATA_TRANSFER_SERVICE_ID,
      chr_id = UPLOAD_DATA_CHARACTERISTIC_ID,
      uuid = UPLOAD_DATA_CHARACTERISTIC,
      value = up_data,
      flags = ["notify"],
      notify_callback = up_data_cb,
      notifying = False,
    )

    my_peripheral.add_characteristic(
      srv_id = DATA_TRANSFER_SERVICE_ID,
      chr_id = UPLOAD_DESTINATION_CHARACTERISTIC_ID,
      uuid = UPLOAD_DESTINATION_CHARACTERISTIC,
      value = up_destination,
      flags = ["read"],
      read_callback = up_destination_cb,
      notifying = False,
    )

    my_peripheral.add_characteristic(
      srv_id = DATA_TRANSFER_SERVICE_ID,
      chr_id = UPLOAD_BLE_MAC_CHARACTERISTIC_ID,
      uuid = UPLOAD_BLE_MAC_CHARACTERISTIC,
      value = up_ble_mac,
      flags = ["read"],
      read_callback = up_destination_cb,
      notifying = False,
    )

    my_peripheral.add_characteristic(
      srv_id = DATA_TRANSFER_SERVICE_ID,
      chr_id = DOWNLOAD_DATA_CHARACTERISTIC_ID,
      uuid = DOWNLOAD_DATA_CHARACTERISTIC,
      value = down_data,
      flags = ["write-without-response"],
      write_callback = down_data_cb,
      notifying = False,
    )

    # Start Advertising
    my_peripheral.publish()

  except dbus.exceptions.DBusException as e:
      logging.error(f"DBus error: {e}")
      logging.info("Please check if bluetoothd is running and you have the necessary permissions.")
  except Exception as e:
      logging.error(f"Unexpected error: {e}", stack_info=True)
  finally:
      print("stop")

if __name__ == "__main__":
  main()
