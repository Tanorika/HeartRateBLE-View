import asyncio
import json
from bleak import BleakScanner, BleakClient

class HeartRateMonitor:
    def __init__(self, device_name, callback):
        self.device_name = device_name
        self.callback = callback
        self.HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
    
    async def run(self):
        print("扫描蓝牙设备中...")
        device = None
        for _ in range(5):  # 最多扫描5次
            devices = await BleakScanner.discover()
            for d in devices:
                if self.device_name in (d.name or ""):
                    device = d
                    break
            if device:
                break

        if not device:
            print(f"❌ 未找到设备: {self.device_name}")
            return

        print(f"✅ 连接设备: {device.name} ({device.address})")
        async with BleakClient(device.address) as client:
            await client.start_notify(self.HEART_RATE_UUID, self.notification_handler)
            print("📡 正在接收心率数据...")
            while True:
                await asyncio.sleep(1)
    
    def notification_handler(self, sender, data):
        if len(data) >= 2:
            heart_rate = data[1]
            print(f"心率: {heart_rate}")
            self.callback(heart_rate)

async def start_ble_client(device_name, callback):
    monitor = HeartRateMonitor(device_name, callback)
    await monitor.run()