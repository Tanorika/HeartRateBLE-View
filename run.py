import sys
import json
import os
import threading
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from flask import Flask, render_template
from flask_socketio import SocketIO
import asyncio
from ble_client import start_ble_client

class HeartRateWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.init_ui()
        
    def load_config(self):
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            print("成功加载配置文件:")
            print(json.dumps(config, indent=2))
            
            if "window" not in config:
                raise ValueError("配置文件中缺少 'window' 字段")
            if "base_width" not in config["window"] or "base_height" not in config["window"]:
                raise ValueError("window 中缺少 base_width 或 base_height")
                
            return config
            
        except Exception as e:
            print(f"加载配置文件出错: {e}")
            return {
                "device_name": "HUAWEI WATCH HR-487",
                "window": {
                    "x": 100,
                    "y": 100,
                    "base_width": 400,
                    "base_height": 200
                },
                "scale": 1.0
            }
        
    def init_ui(self):
        try:
            base_width = int(self.config["window"]["base_width"])
            base_height = int(self.config["window"]["base_height"])
            scale = float(self.config.get("scale", 1.0))
            
            real_width = int(base_width * scale)
            real_height = int(base_height * scale)
            
            print(f"窗口尺寸: {real_width}x{real_height} (缩放: {scale}x)")
            
        except KeyError as e:
            print(f"配置缺少必要字段: {e}")
            return
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.browser = QWebEngineView()
        self.browser.setAttribute(Qt.WA_TranslucentBackground)
        self.browser.setStyleSheet("background: transparent; border: none;")
        self.browser.page().setBackgroundColor(Qt.transparent)
        
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.html")
        self.browser.load(QUrl.fromLocalFile(html_path))
        
        self.browser.page().runJavaScript(f"""
            document.documentElement.style.setProperty('--scale-factor', {scale});
        """)
        
        self.setCentralWidget(self.browser)
        self.setGeometry(
            self.config["window"]["x"],
            self.config["window"]["y"],
            real_width,
            real_height
        )
        
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        if sys.platform == "win32":
            try:
                import ctypes
                hwnd = self.winId().__int__()
                ctypes.windll.user32.SetWindowLongW(hwnd, -20, 0x00080000 | 0x00000020)
            except:
                pass

def run_flask_server():
    # 创建Flask应用
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # 存储心率
    current_hr = 0
    max_hr = 0
    min_hr = float('inf')

    # BLE 回调
    def hr_callback(heart_rate):
        nonlocal current_hr, max_hr, min_hr
        current_hr = heart_rate
        max_hr = max(max_hr, heart_rate)
        min_hr = min(min_hr, heart_rate)
        socketio.emit('heart_rate', {
            'current': current_hr,
            'max': max_hr,
            'min': min_hr
        })

    @app.route('/')
    def index():
        return render_template('index.html')

    def run_ble_client():
        asyncio.run(start_ble_client(config["device_name"], hr_callback))

    # 启动 BLE 客户端线程
    ble_thread = threading.Thread(target=run_ble_client, daemon=True)
    ble_thread.start()

    # 启动 Flask-SocketIO
    socketio.run(app, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # 加载配置
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # 启动Flask服务器线程
    server_thread = threading.Thread(target=run_flask_server, daemon=True)
    server_thread.start()
    
    # 启动PyQt5客户端
    app = QApplication(sys.argv)
    window = HeartRateWindow()
    window.show()
    sys.exit(app.exec_())
