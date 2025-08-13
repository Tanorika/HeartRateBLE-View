# server.py
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import asyncio
from ble_client import start_ble_client
import json
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 读取配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"配置文件不存在: {CONFIG_PATH}")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

DEVICE_NAME = config["device_name"]

# 存储心率
current_hr = 0
max_hr = 0
min_hr = float('inf')

# BLE 回调
def hr_callback(heart_rate):
    global current_hr, max_hr, min_hr
    current_hr = heart_rate
    max_hr = max(max_hr, heart_rate)
    min_hr = min(min_hr, heart_rate)
    # 发送给前端
    socketio.emit('heart_rate', {
        'current': current_hr,
        'max': max_hr,
        'min': min_hr
    })

@app.route('/')
def index():
    return render_template('index.html')

def run_ble_client():
    asyncio.run(start_ble_client(DEVICE_NAME, hr_callback))

if __name__ == '__main__':
    # 启动 BLE 客户端线程
    ble_thread = threading.Thread(target=run_ble_client, daemon=True)
    ble_thread.start()

    # 启动 Flask-SocketIO
    socketio.run(app, host='0.0.0.0', port=5000)
