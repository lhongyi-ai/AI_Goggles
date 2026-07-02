# 1S2P Cross-Temple Safety Review

Verdict: **HOLD**.

- Cell matching: require same lot, same MPN, OCV window, capacity window and DCIR window before parallel connection.
- Equalization current: must be limited by branch resistance/fuse/PTC and verified before connecting cells across the frame.
- Fuse/protection: F1/F2 branch protection and one chosen pack protection scheme are mandatory; do not populate incompatible double-protection.
- NTC: one NTC per cell, thermally bonded to the cell body and read by nPM1300/AON ADC.
- FPC current capacity: J4/FPC copper width, thickness, pin count and temperature rise are not frozen.
- Connector resistance: contact resistance must be in the voltage-drop and heating budget.
- Voltage drop: RS1/RS2/RS3 plus FPC/contact resistance must not trip boost UVLO during RK3576 boot/AI bursts.
- Short-circuit path: worst case is one cell/FPC branch shorting into the other cell. Branch fuse/PTC must open before FPC damage.
- Single-cell disconnect: system must detect imbalance or branch loss and derate/stop charging.
