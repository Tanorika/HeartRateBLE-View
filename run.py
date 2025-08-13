import sys
import json
import os
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView

class HeartRateWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()  # 确保赋值给self.config
        self.init_ui()
        
    def load_config(self):
        try:
            # 确保使用正确的文件路径
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # 添加调试信息
            print("成功加载配置文件:")
            print(json.dumps(config, indent=2))
            
            # 验证必要字段
            if "window" not in config:
                raise ValueError("配置文件中缺少 'window' 字段")
            if "base_width" not in config["window"] or "base_height" not in config["window"]:
                raise ValueError("window 中缺少 base_width 或 base_height")
                
            return config
            
        except Exception as e:
            print(f"加载配置文件出错: {e}")
            # 返回默认配置
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
        # 计算实际窗口尺寸
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
        
        # 窗口设置
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 浏览器设置
        self.browser = QWebEngineView()
        self.browser.setAttribute(Qt.WA_TranslucentBackground)
        self.browser.setStyleSheet("background: transparent; border: none;")
        self.browser.page().setBackgroundColor(Qt.transparent)
        
        # 加载HTML
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.html")
        self.browser.load(QUrl.fromLocalFile(html_path))
        
        # 关键设置：注入缩放因子到HTML
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
        
        # 点击穿透设置
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        if sys.platform == "win32":
            try:
                import ctypes
                hwnd = self.winId().__int__()
                ctypes.windll.user32.SetWindowLongW(hwnd, -20, 0x00080000 | 0x00000020)
            except:
                pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeartRateWindow()
    window.show()
    sys.exit(app.exec_())