import dbus
import logging
from bluezero import peripheral, adapter, async_tools
import subprocess
import uuid

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)

DEVICE_NAME = "Sample Bluetooth Router Peripheral"

# UUIDの定義
DATA_TRANSFER_SERVICE_UUID = "04871924-adfd-b9a9-96f9-afc7772c0d60"
UPLOAD_CHARACTERISTIC_UUID = "be1b5b26-c070-7372-6d04-e5214ca64d91"
DOWNLOAD_CHARACTERISTIC_UUID = "42b1f1c2-4d9a-f841-6097-67eccdeb32b7"

write_value = ""

def update_value(characteristic):
    new_value = uuid.uuid4()

    characteristic.set_value(new_value)

    return characteristic.is_notifying

# コールバック関数
def char_notify(notifying, characteristic):
    logging.debug(f"Characteristic notify")

    if notifying:
        async_tools.add_timer_seconds(5, update_value, characteristic)

def char_write(value):
    logging.debug(f"Characteristic write: {value}")

# システム情報を取得
def get_system_info():
    info = {}
    info["bluetooth_status"] = subprocess.getoutput("systemctl is-active bluetooth")
    info["dbus_status"] = subprocess.getoutput("systemctl is-active dbus")
    info["bluez_version"] = subprocess.getoutput("bluetoothctl --version")
    return info

# 利用可能なBluetoothアダプタを取得
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

# メイン処理
def main():
    # システム情報を表示
    system_info = get_system_info()
    logging.info(f"System info: {system_info}")

    # Bluetoothアダプタの取得
    adapter_address = get_bluetooth_adapter()
    if adapter_address is None:
        raise Exception("No Bluetooth adapter found")

    logging.info(f"Using Bluetooth adapter: {adapter_address}")

    try:
        # Peripheral の設定
        my_peripheral = peripheral.Peripheral(adapter_address, local_name= DEVICE_NAME)

        # サービスの追加
        my_peripheral.add_service(1, DATA_TRANSFER_SERVICE_UUID, True)

        # 特性の追加
        my_peripheral.add_characteristic( 
            srv_id=1,
            chr_id=1,
            uuid=UPLOAD_CHARACTERISTIC_UUID,
            value=[],
            notifying=False,
            flags=["notfiy"],
            notify_callback=char_notify
        )
        
        my_peripheral.add_characteristic( 
            srv_id=1,
            chr_id=2,
            uuid=DOWNLOAD_CHARACTERISTIC_UUID,
            value=write_value,
            notifying=False,
            flags=["write"],
            write_callback=char_write
        )

        # アドバタイジングの開始
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
