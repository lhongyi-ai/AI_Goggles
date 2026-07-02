# PCB Routability Review

Verdict: **HOLD**.

- Estimated layer count: right compute island likely 8-10 layer HDI, not a simple 4-layer wearable board.
- DDR escape: unproven until RK3576/LPDDR ball maps and selected LPDDR MPN exist.
- BGA via technology: expect microvia/via-in-pad or very tight fanout rules; must be quoted by PCB fab early.
- Controlled impedance: MIPI CSI, USB2, Wi-Fi USB and any RF/coax transitions need stack-up from layout/fab.
- High-speed corridor: RK3576-LPDDR, RK3576-eMMC and front FPC corridors must be reserved before placing battery/speaker.
- Power planes: SOC_5V, RK806 rails and GND return must not be fragmented by cosmetic temple shape.
