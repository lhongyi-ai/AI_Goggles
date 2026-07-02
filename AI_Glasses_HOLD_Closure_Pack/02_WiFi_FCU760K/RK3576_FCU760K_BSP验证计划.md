# RK3576 + FCU760K BSP 验证计划

## 已确认的硬件事实

Radxa CM4 V1.20 原理图第20页使用 `FCU760K`，接口包括 USB 2.0、PCM/SAI、CHIP_EN、VBAT/3.3 V 和 RF。当前资料包含 Quectel Short Spec。

## 仍需从 Quectel 取得

1. 对应具体 FCU760K 硬件版本的 Hardware Design。
2. Linux Wi-Fi driver source/package。
3. Bluetooth HCI driver/firmware。
4. Firmware blobs、NVRAM/校准文件、regulatory database。
5. 支持的 Linux kernel 版本矩阵。
6. USB VID/PID 与枚举说明。
7. DTS/设备电源控制示例。
8. Suspend/resume、WoWLAN、RF coexistence 指南。
9. 量产烧录、MAC 地址和校准流程。

Quectel 下载区部分文件需要账号或项目支持权限；应向 FAE 提交 RK3576/Linux 项目需求获取完整包。

## Bring-up 环境必须记录

- RK3576 BSP release / build ID。
- Linux kernel version 与 commit。
- U-Boot commit。
- Device Tree 文件与 patch。
- FCU760K driver commit/package version。
- firmware 文件校验值。
- 模块硬件版本、天线与供电版本。

## 验证步骤

### 1. 电源与 USB 枚举

- 先关闭 `WIFI_CHIP_EN`，确认供电漏电。
- 打开 3.3 V Buck/Load Switch，等待 PGOOD。
- 拉高 `WIFI_CHIP_EN`。
- 检查 `dmesg -w`、`lsusb -v`、USB 复位与重枚举。
- 连续做 100 次硬开关机。

### 2. 驱动和固件

- 编译并加载 Quectel 指定模块。
- 检查 firmware/NVRAM 加载日志。
- 确认 wlan interface、Bluetooth HCI interface。
- 检查国家码、2.4/5 GHz 信道和发射功率配置。

### 3. 功能与吞吐

| 测试 | 验收记录 |
|---|---|
| 2.4 GHz STA | RSSI、iperf3 TCP/UDP、丢包、功耗 |
| 5 GHz STA | RSSI、iperf3 TCP/UDP、丢包、功耗 |
| 1080p H.265 实时传输 | 码率、延迟、卡顿、温升 |
| Bluetooth | 扫描、连接、音频/控制接口 |
| Wi-Fi + BT 共存 | 吞吐下降、音频丢包 |
| Suspend/resume | 100次恢复成功率 |
| Hard power cycle | 100次重新枚举成功率 |
| 弱信号 | -70/-80 dBm 下稳定性 |

### 4. 低功耗

分别测量：

- Buck 开、模块关。
- Module on、未关联。
- 关联 idle。
- RX。
- TX 不同功率。
- WoWLAN（若支持）。
- 完全断电。

## HOLD 关闭门槛

- Quectel driver/firmware 包可合法用于产品。
- 在项目 RK3576 BSP 上完成可复现编译。
- 100次上电、枚举、连接和休眠恢复通过。
- 1080p 目标码率下稳定传输不少于2小时。
- Wi-Fi 关闭后电源岛漏电满足预算。
- 测试日志、patch 和固件版本进入项目仓库。
