# RC 机器人系统 · 上位机(ROS2) + 下位机(STM32)

> 霸气的恐龙王 · 一套 RC 机器人竞赛系统的完整代码

本仓库包含同一套 RC 机器人的**上位机**与**下位机**两部分，放在同一个仓库里方便配套使用：

- `upper_computer/` — ROS2 视觉伺服上位机（YOLO 目标检测 → 自定义消息 → Action/PID 控制 → 串口下发）
- `lower_computer/` — STM32 下位机固件（串口解析上位机指令，驱动电机与 OLED 显示）

## 目录结构

```
rc-ros2-workspace/
├── README.md              # 本文件：系统总览
├── LICENSE                # MIT
├── .gitignore
├── upper_computer/        # ROS2 上位机（详见 upper_computer/README.md）
│   ├── src/
│   │   ├── vision_detect/ # YOLO 检测节点、Action 服务端/客户端、串口桥
│   │   └── rc_msgs/       # 自定义消息(.msg)与动作(.action)
│   └── README.md
└── lower_computer/        # STM32 下位机（详见 lower_computer/README.md）
    ├── Core/              # 用户代码（main.c / usart.c / oled.c ...）
    ├── MDK-ARM/           # Keil 工程文件
    └── rostele.ioc        # CubeMX 工程（可依据它重新生成 Drivers/）
```

## 系统架构

```mermaid
flowchart LR
    CAM[摄像头] --> YOLO[YOLO 目标检测]
    YOLO --> POS[position_data / topic]
    POS --> ACT[Action 服务端 + PID 控制]
    ACT --> CMD[/cmd_vel]
    CMD --> UART[串口 UART 115200]
    UART --> STM32[STM32 下位机]
    STM32 --> M[电机驱动]
    STM32 --> OLED[OLED 显示]
```

- **持续数据流**（每帧检测结果）用 ROS2 **topic**（`position_data`）传输；
- **启停/一次性指令**用 ROS2 **Action**（`MoveRobot`）传输，便于反馈执行状态；
- 控制量经 PID 解算后通过**串口帧**下发到下位机。

## 通信协议（上位机 ↔ 下位机）

串口帧格式：`AA 55` + `<int16 vx, int16 vy>` + 校验和 + `0D 0A`，115200 / 8N1。

| 字段 | 长度 | 说明 |
|---|---|---|
| 帧头 | 2 B | `AA 55` |
| 速度 X | 2 B | int16，左/右 |
| 速度 Y | 2 B | int16，前/后 |
| 校验和 | 1 B | 前面字节累加和 |
| 帧尾 | 2 B | `0D 0A` |

详细字段与下位机接收状态机见 `upper_computer/README.md` 与 `lower_computer/README.md`。

## 构建与运行

### 上位机（ROS2）

```bash
cd upper_computer
colcon build --packages-select rc_msgs vision_detect
source install/setup.bash
ros2 run vision_detect <节点名>
```

> ⚠️ 换机器必改 3 处硬编码：模型权重路径、`/dev/ttyUSB0` 串口设备名、HSV/PID 参数（详见 `upper_computer/README.md`）。

### 下位机（STM32）

1. 用 STM32CubeIDE 打开 `lower_computer/rostele.ioc` 重新生成代码（会重建 `Drivers/`）；
2. 用 Keil（`lower_computer/MDK-ARM/`）编译并下载到板子。

> `Drivers/` 不纳入版本库——它由 CubeMX 依据 `.ioc` 自动生成，重新生成即可还原。

## 许可证

[MIT](LICENSE) — Copyright (c) 2026 jiaolong
