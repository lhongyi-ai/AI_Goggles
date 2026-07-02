# Thermal Review

Verdict: **HOLD**.

- RK3576: heat must go to the outer temple wall/heat spreader, not skin side and not into the cell.
- RK806S: PMIC heat and inductor/cap placement need thermal current budget.
- TPS61088/boost: high-current loop and L1 can become local hot spots.
- Wi-Fi: FCU760K transmit bursts add local heat and RF keep-out constraints.
- Amplifier/speaker: peak audio power is acoustic/thermal dependent; speaker magnet must clear antenna.
- Battery isolation: no hot component or heat spreader should directly press or radiate into LP451165 envelope.
- Skin-side path: add NTC at hot spreader and skin side; firmware throttles record/AI burst.
