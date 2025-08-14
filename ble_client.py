import asyncio
import json
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError
import time
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeartRateMonitor:
    def __init__(self, device_name, callback):
        self.device_name = device_name
        self.callback = callback
        self.HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
        self.is_connected = False
        self.should_reconnect = True
        self.retry_interval = 5  # 重试间隔(秒)
        self.scan_timeout = 10  # 扫描超时(秒)
        self.max_scan_attempts = 10  # 最大扫描尝试次数

    async def connect_to_device(self):
        """尝试连接设备"""
        device = None
        scan_attempts = 0
        
        while scan_attempts < self.max_scan_attempts and not device:
            scan_attempts += 1
            logger.info(f"尝试扫描设备 (尝试 {scan_attempts}/{self.max_scan_attempts})...")
            
            try:
                devices = await BleakScanner.discover(timeout=self.scan_timeout)
                for d in devices:
                    if self.device_name in (d.name or ""):
                        device = d
                        logger.info(f"找到设备: {d.name} ({d.address})")
                        break
            except Exception as e:
                logger.error(f"扫描设备时出错: {e}")
            
            if not device:
                await asyncio.sleep(1)  # 短暂等待后重试
        
        if not device:
            logger.error(f"❌ 未找到设备: {self.device_name}")
            return None
        
        try:
            client = BleakClient(device.address)
            await client.connect()
            self.is_connected = True
            logger.info(f"✅ 成功连接设备: {device.name} ({device.address})")
            return client
        except Exception as e:
            logger.error(f"连接设备时出错: {e}")
            return None

    async def run(self):
        """主运行循环，包含自动重连逻辑"""
        while self.should_reconnect:
            try:
                client = await self.connect_to_device()
                if not client:
                    logger.info(f"等待 {self.retry_interval} 秒后重试...")
                    await asyncio.sleep(self.retry_interval)
                    continue
                
                # 设置通知处理器
                await client.start_notify(self.HEART_RATE_UUID, self.notification_handler)
                logger.info("📡 正在接收心率数据...")
                
                # 保持连接状态
                while self.should_reconnect:
                    if not client.is_connected:
                        self.is_connected = False
                        logger.warning("⚠️ 连接已断开")
                        break
                    await asyncio.sleep(1)
                
            except BleakError as e:
                logger.error(f"蓝牙通信错误: {e}")
                self.is_connected = False
            except Exception as e:
                logger.error(f"未知错误: {e}")
                self.is_connected = False
            finally:
                if client and client.is_connected:
                    try:
                        await client.stop_notify(self.HEART_RATE_UUID)
                        await client.disconnect()
                    except Exception as e:
                        logger.error(f"断开连接时出错: {e}")
                
                if self.should_reconnect:
                    logger.info(f"等待 {self.retry_interval} 秒后尝试重新连接...")
                    await asyncio.sleep(self.retry_interval)

    def notification_handler(self, sender, data):
        """处理心率数据通知"""
        if len(data) >= 2:
            heart_rate = data[1]
            logger.info(f"心率: {heart_rate} BPM")
            self.callback(heart_rate)

async def start_ble_client(device_name, callback):
    """启动BLE客户端"""
    monitor = HeartRateMonitor(device_name, callback)
    await monitor.run()
