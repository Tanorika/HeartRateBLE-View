# 本地心率监测系统

一个实时显示蓝牙心率设备数据的透明窗口应用，支持自定义字体和样式。

## 功能特点

- 实时显示当前心率、最大心率和最小心率
- 三种颜色动画效果根据心率强度变化
- 透明窗口设计，可叠加在其他应用上
- 支持自定义字体和界面缩放

## 依赖安装

```bash
pip install PyQt5 PyQtWebEngine bleak flask flask-socketio
```

## 使用方法

1. 克隆仓库

2. 确保你的蓝牙心率设备已开启并可被发现

3. 修改 `config.json` 中的 `device_name` 为你的设备名称

4. 运行方式：
   - 双击运行 `run.cmd`
   - 或者通过命令行运行：
     ```bash
     python run.py
     ```

## 自定义配置

- **字体**：替换 `bear.ttf` 为你想要的字体文件，并在 `main.html` 中更新字体名称
- **窗口位置**：修改 `config.json` 中的 `window` 参数
- **缩放比例**：调整 `config.json` 中的 `scale` 值

## 文件说明

- `ble_client.py` - BLE客户端连接逻辑 (参考了 [PCBLEtoVRC](https://github.com/SinkStarUR/PCBLEtoVRC))
- `server.py` - WebSocket服务器和BLE数据处理
- `run.py` - 透明窗口应用主程序
- `main.html` - 心率显示界面
- `config.json` - 配置文件
- `green.webm`/`orange.webm`/`red.webm` - 心率动画文件 (来自Hyperate)

## 注意事项

1. 首次使用可能需要授予蓝牙权限
2. 心率动画文件需放在同一目录下
3. 在Windows上可实现点击穿透，其他系统可能有限制
