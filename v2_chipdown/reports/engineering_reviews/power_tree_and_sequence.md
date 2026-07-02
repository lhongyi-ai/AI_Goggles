# Power Tree And Sequence Review

Verdict: **PASS WITH CONDITIONS** for architecture, **HOLD** for timing/measurement.

- Always-on power: BT1/BT2 -> branch protection/shunts -> BAT_P -> RS1 -> nPM1300 -> AON_1V8/AON_3V3.
- Main boost: nRF54L15 asserts SOC_PWR_EN, TPS61088 generates SOC_5V, SOC_5V_PGOOD returns to AON.
- RK3576 rails: RK806S generates CPU/GPU/NPU/logic/DDR/IO rails; exact sequencing requires RK806S/RK3576 HDG.
- Wake sequence: BLE/IMU/NDP/button event -> nRF -> enable boost -> RK806 PWRON -> RK3576 alive/status.
- Shutdown: RK3576 requests/acknowledges safe off -> nRF cuts camera/Wi-Fi/audio then SOC_5V.
- Brownout: boost UVLO and nPM1300 thresholds must be coordinated with battery sag and branch-current imbalance.
