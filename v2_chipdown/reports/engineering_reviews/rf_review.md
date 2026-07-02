# RF Review

Verdict: **HOLD**.

- BLE/Wi-Fi spacing: current concept separates BLE left rear and Wi-Fi right rear, which is good.
- Keep-out: antenna windows must clear battery, copper, screws, speaker magnet, pogo magnets and boost current loops.
- Ground clearance: final FPC/PCB/LDS antenna vendor rules must drive the CAD/PCB no-copper area.
- Battery/metal interference: cells and shields detune antennas; worn-head tuning is mandatory.
- Coexistence: FCU760K shares Wi-Fi/BT antenna in selected ordering code; nRF BLE antenna coexistence requires test plan.
- Test method: tune in shell, with battery, speaker, pogo, glasses on phantom/head fixture and active Wi-Fi/BLE traffic.
