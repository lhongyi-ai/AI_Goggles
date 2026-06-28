# IMX415 Bring-up on Official Radxa CM4 IO Board

Date: 2026-06-28

Goal: use the official Radxa CM4 IO Board as the first software bring-up platform for Radxa Camera 4K / Sony IMX415 before the custom carrier PCB is manufactured.

## Sources

- Radxa Camera 4K official page: https://docs.radxa.com/en/accessories/camera/camera-4k
- Radxa ROCK 5 ITX camera tutorial: https://docs.radxa.com/en/rock5/rock5itx/getting-started/interface-usage/camera
- Local camera pinout: `CM4_IMX415_design_files/Radxa_Camera_4K_31pin_pinout.csv`
- Local CM4 IO schematic: `CM4_IMX415_design_files/radxa_cm4_io_schematic_v1.10.pdf`
- Local CM4 pinout source: `data/radxa_cm4_pinout_v1.20.xlsx`

The ROCK 5 ITX tutorial is useful because it documents Radxa Camera 4K / IMX415 overlay enablement and GStreamer test commands. It is not proof that the same overlay applies unchanged to CM4.

## Official CM4 IO Overlay Now Confirmed

- Overlay file: `radxa-cm4-io-radxa-camera-4k.dtbo`
- `rsetup` menu title: `Enable Radxa Camera 4K`
- Official source target: `radxa,cm4-io`
- Sensor: IMX415
- I2C address: `0x1a`
- MIPI data lanes: 4
- CSI D-PHY endpoint: `csi2_dphy3`

This confirms that the official CM4 IO Board path exists. It does not close the custom carrier bring-up gate until we capture the actual `dmesg`, media graph and V4L2 node output on hardware.

## Bring-up Plan

1. Boot Radxa CM4 on the official CM4 IO Board with the latest supported Radxa OS image for this CM4 SKU.
2. Connect Radxa Camera 4K using the correct 31-pin camera path and contact orientation for the IO Board.
3. Use `rsetup` and enable `Enable Radxa Camera 4K`, which maps to `radxa-cm4-io-radxa-camera-4k.dtbo`.
4. Reboot, then inspect kernel, media graph, I2C and V4L2 state.
5. Capture 1080p first, then 4K modes.
6. Record the exact overlay name, kernel version, `/boot` DTBO path, detected I2C address, media graph, and `/dev/videoX` node.

## Commands to Run on the CM4 IO Board

```bash
uname -a
cat /etc/os-release

sudo rsetup

find /boot -iname '*imx415*' -o -iname '*camera*4k*' -o -iname '*cam*4k*'
find /usr/lib/firmware -iname '*imx415*' 2>/dev/null
find /usr/lib -iname '*imx415*' 2>/dev/null

modinfo imx415 2>/dev/null || true
sudo dmesg | grep -Ei 'imx415|rkisp|rkcif|csi|dphy|camera|mipi'

media-ctl -p
v4l2-ctl --list-devices
v4l2-ctl --list-formats-ext --device=/dev/videoX
```

Replace `/dev/videoX` with the actual node found from `v4l2-ctl --list-devices`.

Start with 1080p:

```bash
gst-launch-1.0 v4l2src device=/dev/videoX io-mode=4 \
  ! video/x-raw,width=1920,height=1080,framerate=30/1 \
  ! videoconvert ! autovideosink
```

Then test the Radxa tutorial style pipeline if the node and formats match:

```bash
gst-launch-1.0 v4l2src device=/dev/videoX io-mode=4 \
  ! videoconvert \
  ! video/x-raw,format=NV12,width=1920,height=1080 \
  ! xvimagesink
```

## Overlay Migration Notes for Our Carrier

The custom carrier overlay must match the schematic sources:

- I2C: `I2C0_M1`, CM4 pins 80/82, 1.8 V, board nets `CAM_I2C_SCL` / `CAM_I2C_SDA`.
- MCLK: `MIPI_CSI3_CAM_CLKOUT_1V8`, CM4 pin 59, function `CAM_CLK2_OUT_M0`, board net `CAM_MCLK`.
- Reset: `MIPI_CAM3_PDN_1V8`, CM4 pin 143, function `GPIO3_C5`, board net `CAM_RST_n`, active-low.
- CSI lanes: FPC `MDP1/MDN1` -> CSI3 D0, `MDP2/MDN2` -> CSI3 D1, `MDP3/MDN3` -> CSI3 D2, `MDP4/MDN4` -> CSI3 D3.
- Data-lane ordering in Device Tree must match `docs/csi3_imx415_audit_2026-06-28.md`.
- The local 31-pin Radxa Camera 4K pinout has RESET but no PWDN pin.

## Pass Criteria

- IMX415 probe succeeds on I2C without repeated NACK or timeout.
- Media graph shows a complete IMX415 -> CSI DPHY -> CIF/ISP path.
- D-PHY locks without persistent CRC/ECC errors in `dmesg`.
- 1080p30 runs for 30 minutes.
- Target 4K mode works at the required frame rate.
- Power measurements capture camera idle, streaming and mode-switch peaks.

## Information to Copy Back Into This Repo

- OS image name and kernel version.
- Exact overlay/DTBO filename and any edits.
- `dmesg` camera section.
- `media-ctl -p` output.
- `v4l2-ctl --list-devices` and format listing.
- First working GStreamer command.
- Whether reset GPIO polarity needed inversion.
