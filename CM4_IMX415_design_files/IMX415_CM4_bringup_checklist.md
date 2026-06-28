# IMX415 on Radxa CM4 Bring-up Checklist

## 1. Hardware evidence
- [x] Camera module is confirmed as Radxa Camera 4K, not only a generic IMX415 board.
- [x] 31-pin FPC pinout saved in repository.
- [x] Four MIPI data pairs and one clock pair mapped to one valid 4-lane CM4 CSI receiver.
- [x] I2C bus, MCLK and RESET mapped to real CM4 pins; no PWDN pin exists in the Radxa Camera 4K 31-pin pinout.
- [x] Control-signal voltage domain confirmed as 1.8 V in the schematic plan.
- [x] J2 3.3 V and 5 V supply pins are connected in the schematic.
- [ ] DEFERRED_TO_PRE_LAYOUT: Pin 1 physical side and FPC contact side confirmed from real hardware/mechanical drawing.
- [ ] DEFERRED_TO_PRE_LAYOUT: AC006 physical validation, insertion direction, 1:1 print, coupon test, and FPC bend/enclosure path.
- [ ] EVT: 3.3 V and 5 V module power current budget measured on hardware.

## 2. Device Tree evidence
Required camera node properties normally include:
- compatible = "sony,imx415"
- reg / I2C address
- clocks / clock-names
- reset-gpios and optional pwdn-gpios
- power supplies if controlled by Linux
- port / endpoint
- data-lanes = <1 2 3 4> or board-specific ordering
- remote-endpoint to CSI2 DPHY / CIF / ISP path

Do not copy a ROCK 5 ITX overlay unchanged. Adapt its I2C controller, GPIOs, clock source, CSI endpoint and lane order to CM4.

Official CM4 IO overlay now confirmed:
- file: radxa-cm4-io-radxa-camera-4k.dtbo
- menu: Enable Radxa Camera 4K
- compatible board target: radxa,cm4-io
- sensor: IMX415
- I2C address: 0x1a
- data lanes: 4
- D-PHY endpoint: csi2_dphy3

## 3. Image-side verification commands
```bash
modinfo imx415 2>/dev/null || true
find /boot -iname '*imx415*' -o -iname '*camera*4k*'
find /usr/lib/firmware -iname '*imx415*' 2>/dev/null
find /usr/lib -iname '*imx415*' 2>/dev/null
sudo dmesg | grep -Ei 'imx415|rkisp|rkcif|csi|dphy|camera'
media-ctl -p
v4l2-ctl --list-devices
```

## 4. Functional test
Start with 1080p30 rather than immediately demanding 4K:
```bash
gst-launch-1.0 v4l2src device=/dev/videoX io-mode=4 \
  ! video/x-raw,width=1920,height=1080,framerate=30/1 \
  ! videoconvert ! autovideosink
```

Then test capture, encoding, frame drops, temperature and power.

## 5. Pass criteria
- [ ] Sensor identified by I2C without repeated timeout/NACK.
- [ ] MIPI D-PHY locks with no persistent CRC/ECC errors.
- [ ] 1080p30 stable for at least 30 minutes.
- [ ] 4K mode stable at required frame rate.
- [ ] ISP IQ/tuning file loaded or documented as missing.
- [ ] No lane-order workaround left undocumented.
