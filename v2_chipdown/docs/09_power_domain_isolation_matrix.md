# 09 — Power-domain isolation matrix (generated)

> Generated 2026-07-01 from `scripts/chipdown_bom.py`. This is the pre-layout reverse-feed checklist.

## Domain map

| Domain | Rails / nets | Owner | Default state | Closure gate |
|---|---|---|---|---|
| Battery / pack | BATR_P, BATL_P, BATR_F, BATL_F, BAT_P, NPM_VBAT, CELL_NEG | LP451165 1S2P + F1/F2/RS1-RS3 | live | G07 pack + protection closure |
| AON | AON_1V8, AON_3V3, AON_LSW2 | nPM1300 BUCK1/BUCK2/LSW2 | on in normal standby | G08 AON <=25/50 mW |
| RK3576 compute | SOC_IN, SOC_5V, VDD_*, VCC_* | RS4 -> TPS61088 -> RK806S | off until SOC_PWR_EN + PMIC_PWRON | G01/G02/G03/G06/G09 |
| Wi-Fi | WIFI_IN, WIFI_3V3, WIFI_VBAT_3V3 | RS5 -> TPS62825 -> TPS22917 | off until WIFI_*_EN + CHIP_EN | G05/G06 |
| Camera | CAM_1V1, CAM_1V8_SW, CAM_2V9 and *_S | front-board buck/LDO/load switch + RS7-RS9 | off until CAM_*_EN | G10/G12 |
| Audio | AUDIO_IN, AUDIO_PWR | RS6 -> TPS22917 -> MAX98360A | off/muted until AUDIO_* asserted | speaker/acoustic gate |
| RF | WIFI_ANT, BLE_ANT | antenna feeds | passive | worn-state tune + keep-out |
| Debug / charge | USB_5V, USB2_DP/DM, USB_CC1/2, SWD/UART pads | EVT tail / pogo | lab-use only | connector/mechanical gate |

## Cross-domain signals

| Net | Kind | Domain | Board crossing | Default | Off-high allowed | Isolation / leakage rule | Endpoints |
|---|---|---|---|---|---|---|---|
| `SOC_SHUTDOWN_REQ` | control | 1.8V | R-Temple Compute Board -> L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | low | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.SHUTDOWN_REQ; U7.SOC_SHDN_REQ; J4.SOC_SHDN_REQ |
| `SOC_SAFE_TO_OFF` | control | 1.8V | R-Temple Compute Board -> L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | low | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.SAFE_TO_OFF; U7.SOC_SAFE_OFF; J4.SOC_SAFE_OFF |
| `SOC_ALIVE` | control | 1.8V | R-Temple Compute Board -> L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | low | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.ALIVE; U7.SOC_ALIVE; J4.SOC_ALIVE |
| `SOC_FAULT` | control | 1.8V | R-Temple Compute Board -> L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | low | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.FAULT; U7.SOC_FAULT; J4.SOC_FAULT |
| `AON_UART_TX` | bus | 1.8V | R-Temple Compute Board -> L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | idle high | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.AON_UART_RX; U7.AON_UART_TX; J4.AON_UART_TX |
| `AON_UART_RX` | bus | 1.8V | R-Temple Compute Board -> L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | idle high | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.AON_UART_TX; U7.AON_UART_RX; J4.AON_UART_RX |
| `CSI_CLK_P` | diff | 1.2V | R-Temple Compute Board -> Front Sensor Board | hi-Z | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.CSI_CLK_P; U14.CSI_CLK_P; U18.CLK_P; J3.CSI_CLK_P |
| `CSI_CLK_N` | diff | 1.2V | R-Temple Compute Board -> Front Sensor Board | hi-Z | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.CSI_CLK_N; U14.CSI_CLK_N; U18.CLK_N; J3.CSI_CLK_N |
| `CSI_D0_P` | diff | 1.2V | R-Temple Compute Board -> Front Sensor Board | hi-Z | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.CSI_D0_P; U14.CSI_D0_P; U18.D0_P; J3.CSI_D0_P |
| `CSI_D0_N` | diff | MIPI D-PHY | R-Temple Compute Board -> Front Sensor Board | hi-Z when source domain is off | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.CSI_D0_N; U14.CSI_D0_N; U18.D0_N; J3.CSI_D0_N |
| `CSI_D1_P` | diff | 1.2V | R-Temple Compute Board -> Front Sensor Board | hi-Z | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.CSI_D1_P; U14.CSI_D1_P; U19.D1_P; J3.CSI_D1_P |
| `CSI_D1_N` | diff | MIPI D-PHY | R-Temple Compute Board -> Front Sensor Board | hi-Z when source domain is off | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.CSI_D1_N; U14.CSI_D1_N; U19.D1_N; J3.CSI_D1_N |
| `CAM_I2C_SCL` | bus | 1.8V unless final pinmux says otherwise | R-Temple Compute Board -> Front Sensor Board | pulled high | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.CAM_I2C_SCL; U14.SCL; J3.CAM_I2C_SCL; R5.B |
| `CAM_I2C_SDA` | bus | 1.8V unless final pinmux says otherwise | R-Temple Compute Board -> Front Sensor Board | pulled high | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.CAM_I2C_SDA; U14.SDA; J3.CAM_I2C_SDA; R6.B |
| `CAM_RST_L` | control | 1.8V | R-Temple Compute Board -> Front Sensor Board | low (XCLR held) | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.CAM_RST_L; U14.XCLR_L; U19.RST; J3.CAM_RST_L |
| `CAM_PWDN_L` | control | 1.8V | R-Temple Compute Board -> Front Sensor Board | low | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.CAM_PWDN_L; U14.PWDN_L; J3.CAM_PWDN_L |
| `CAM_MCLK` | control | 1.8V | R-Temple Compute Board -> Front Sensor Board | off | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.CAM_MCLK; U14.INCK; U19.MCLK; J3.CAM_MCLK |
| `PDM_ARRAY_CLK` | bus | AON | R-Temple Compute Board -> Front Sensor Board | off | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.PDM_ARR_CLK; MK2.CLK; MK3.CLK; MK4.CLK; J3.PDM_ARR_CLK |
| `PDM_ARRAY_D0` | bus | 1.8V unless final pinmux says otherwise | R-Temple Compute Board -> Front Sensor Board | TBD at pinmux freeze | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.PDM_ARR_D0; MK2.DATA; J3.PDM_ARR_D0 |
| `PDM_ARRAY_D1` | bus | 1.8V unless final pinmux says otherwise | R-Temple Compute Board -> Front Sensor Board | TBD at pinmux freeze | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.PDM_ARR_D1; MK3.DATA; MK4.DATA; J3.PDM_ARR_D1 |
| `USB2_DP` | diff | 3.3V | R-Temple Compute Board -> Temple Rears (batt/spkr/ant) -> EVT Debug Tail | hi-Z | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.USB2_DP; J1.DP; J2.DP; U24.DP |
| `USB2_DM` | diff | 3.3V | R-Temple Compute Board -> Temple Rears (batt/spkr/ant) -> EVT Debug Tail | hi-Z | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.USB2_DM; J1.DM; J2.DM; U24.DM |
| `SOC_MASKROM_L` | control | 1.8V unless final pinmux says otherwise | R-Temple Compute Board -> EVT Debug Tail | low or pulled to safe state until firmware owns it | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.MASKROM_n; SW3.A |
| `SOC_RESET_L` | control | 1.8V | R-Temple Compute Board -> EVT Debug Tail | low (reset) | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.RESET_n; U2.RESET_n; SW2.A |
| `SOC_PWRKEY` | control | 1.8V unless final pinmux says otherwise | R-Temple Compute Board -> EVT Debug Tail | TBD at pinmux freeze | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U1.PWRKEY; SW1.A |
| `PMIC_PWRON` | control | 1.8V | R-Temple Compute Board -> L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | low (OFF) | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U2.PWRON; U7.PMIC_PWRON; J4.PMIC_PWRON; R12.A |
| `SOC_PWR_EN` | control | 1.8V | R-Temple Compute Board -> L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | low (OFF) | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U6.EN; U7.SOC_PWR_EN; J4.SOC_PWR_EN; R11.A |
| `SOC_5V_PGOOD` | control | 1.8V | R-Temple Compute Board -> L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | low | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U6.PG; U7.SOC_5V_PGOOD; J4.SOC_5V_PGOOD |
| `WIFI_CHIP_EN` | control | 3.3V | R-Temple Compute Board -> L-Temple AON/Power Board | low (OFF) | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U11.CHIP_EN; U7.WIFI_CHIP_EN; R18.A |
| `WIFI_ANT` | analog | RF | R-Temple Compute Board -> Temple Rears (batt/spkr/ant) | - | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U11.ANT_WIFI_BT; J7.ANT; J5.SIG |
| `WIFI_BUCK_EN` | control | 1.8V | R-Temple Compute Board -> L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | low (OFF) | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U12.EN; U7.WIFI_BUCK_EN; J4.WIFI_BUCK_EN; R16.A |
| `WIFI_LS_EN` | control | 1.8V | R-Temple Compute Board -> L-Temple AON/Power Board | low (OFF) | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U13.EN; U7.WIFI_LS_EN; R17.A |
| `BLE_ANT` | analog | RF | L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | - | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U7.ANT; J6.ANT |
| `CAM_1V1_EN` | control | 1.8V | L-Temple AON/Power Board -> Front Sensor Board | low (OFF) | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U7.CAM_1V1_EN; U15.EN; J3.CAM_1V1_EN; R13.A |
| `CAM_1V8_EN` | control | 1.8V | L-Temple AON/Power Board -> Front Sensor Board | low (OFF) | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U7.CAM_1V8_EN; U17.EN; J3.CAM_1V8_EN; R14.A |
| `CAM_2V9_EN` | control | 1.8V | L-Temple AON/Power Board -> Front Sensor Board | low (OFF) | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U7.CAM_2V9_EN; U16.EN; J3.CAM_2V9_EN; R15.A |
| `AUDIO_LS_EN` | control | 1.8V | L-Temple AON/Power Board -> R-Temple Compute Board -> Temple Rears (batt/spkr/ant) | low (OFF) | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U7.AUDIO_LS_EN; U21.EN; J4.AUDIO_LS_EN; R19.A |
| `AUDIO_AMP_SD` | control | Vbat | L-Temple AON/Power Board -> R-Temple Compute Board | low (muted) | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U7.AMP_SD; U20.SD_MODE; R20.A |
| `I2C_AON_SCL` | bus | 1.8V | L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) -> R-Temple Compute Board -> Front Sensor Board | pull-up 2.2k | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U7.I2C_SCL; U8.I2C_SCL; U10.SCL; U22.SCL; U25.SCL; U26.SCL; U27.SCL; U28.SCL; U29.SCL; U30.SCL; U31.SCL; U32.SCL; U33.SCL; R3.B |
| `I2C_AON_SDA` | bus | 1.8V | L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) -> R-Temple Compute Board -> Front Sensor Board | pull-up 2.2k | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U7.I2C_SDA; U8.I2C_SDA; U10.SDA; U22.SDA; U25.SDA; U26.SDA; U27.SDA; U28.SDA; U29.SDA; U30.SDA; U31.SDA; U32.SDA; U33.SDA; R4.B |
| `NRF_SWDIO` | bus | 1.8V unless final pinmux says otherwise | L-Temple AON/Power Board -> EVT Debug Tail | TBD at pinmux freeze | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U7.SWDIO; TP1.SWDIO |
| `NRF_SWDCLK` | bus | 1.8V unless final pinmux says otherwise | L-Temple AON/Power Board -> EVT Debug Tail | TBD at pinmux freeze | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U7.SWDCLK; TP1.SWDCLK |
| `NTC_R` | analog | analog | L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | - | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U8.NTC_R; RT1.A; TP2.NTC_R |
| `NTC_L` | analog | analog | L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | - | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U8.NTC_L; RT2.A; TP2.NTC_L |
| `PDM_WAKE_CLK` | bus | AON | L-Temple AON/Power Board -> Front Sensor Board | off | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U9.PDM_CLK; MK1.CLK; J3.PDM_WAKE_CLK |
| `PDM_WAKE_DATA` | bus | 1.8V unless final pinmux says otherwise | L-Temple AON/Power Board -> Front Sensor Board | TBD at pinmux freeze | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U9.PDM_DATA; MK1.DATA; J3.PDM_WAKE_DATA |
| `SPK_P` | diff | TBD | R-Temple Compute Board -> Temple Rears (batt/spkr/ant) | hi-Z when source domain is off | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U20.OUT_P; LS1.P |
| `SPK_N` | diff | TBD | R-Temple Compute Board -> Temple Rears (batt/spkr/ant) | hi-Z when source domain is off | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U20.OUT_N; LS1.N |
| `HAPTIC_P` | diff | TBD | L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | hi-Z when source domain is off | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U22.OUT_P; M1.P |
| `HAPTIC_N` | diff | TBD | L-Temple AON/Power Board -> Temple Rears (batt/spkr/ant) | hi-Z when source domain is off | No; prove no reverse-feed or add isolation | required: default-safe pull + leakage/reverse-feed check | U22.OUT_N; M1.N |

## Hardware default-OFF proof

| Ref | Net | Value | Board | Effect |
|---|---|---|---|---|
| R11 | `SOC_PWR_EN` | 100k | R-Temple Compute Board | SOC_PWR_EN pull-down — RK3576 boost default OFF (main SoC off at boot). |
| R12 | `PMIC_PWRON` | 100k | R-Temple Compute Board | PMIC_PWRON pull-down — RK806 stays off until AON MCU sequences it. |
| R13 | `CAM_1V1_EN` | 100k | Front Sensor Board | CAM_1V1_EN pull-down — camera core buck default OFF. |
| R14 | `CAM_1V8_EN` | 100k | Front Sensor Board | CAM_1V8_EN pull-down — camera I/O load switch default OFF. |
| R15 | `CAM_2V9_EN` | 100k | Front Sensor Board | CAM_2V9_EN pull-down — camera analog LDO default OFF. |
| R16 | `WIFI_BUCK_EN` | 100k | R-Temple Compute Board | WIFI_BUCK_EN pull-down — Wi-Fi buck default OFF. |
| R17 | `WIFI_LS_EN` | 100k | R-Temple Compute Board | WIFI_LS_EN pull-down — Wi-Fi load switch default OFF. |
| R18 | `WIFI_CHIP_EN` | 100k | R-Temple Compute Board | WIFI_CHIP_EN pull-down — FCU760K held off until AON MCU enables it (pack §9). |
| R19 | `AUDIO_LS_EN` | 100k | R-Temple Compute Board | AUDIO_LS_EN pull-down — audio amp load switch default OFF. |
| R20 | `AUDIO_AMP_SD` | 100k | R-Temple Compute Board | AUDIO_AMP_SD pull-down — MAX98360A shutdown default (amp muted at boot). |

## Layout-entry requirements

- RK3576, camera, Wi-Fi and audio domains must remain off with nRF reset or firmware hung.
- Any signal into a powered-down RK3576/camera/Wi-Fi domain needs measured leakage or isolation.
- Load switches with quick-output-discharge must prove the off-domain rail collapses fast enough.
- FPC crossings need the same default-state review as board-local crossings.
