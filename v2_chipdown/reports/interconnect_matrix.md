# V2.3 Interconnect Matrix

Generated: 2026-07-01

Source of truth: `chipdown_bom.py` component pin lists normalized by `net_meta()`. This is schematic-aligned audit evidence, not a released harness or FPC fabrication drawing.

## Summary

| Metric | Count |
|---|---|
| total schematic nets | 127 |
| cross-domain / cross-board signals | 50 |
| high-speed / RF focus nets | 16 |

## Cross-Domain Signals

| Net | Kind | Domain | Direction | Boards | Isolation / close condition |
|---|---|---|---|---|---|
| SOC_SHUTDOWN_REQ | control | 1.8V | nRF->RK3576 | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| SOC_SAFE_TO_OFF | control | 1.8V | RK3576->nRF | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| SOC_ALIVE | control | 1.8V | RK3576->nRF | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| SOC_FAULT | control | 1.8V | RK3576->nRF | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| AON_UART_TX | bus | 1.8V | nRF->RK3576 | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| AON_UART_RX | bus | 1.8V | RK3576->nRF | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| CSI_CLK_P | diff | 1.2V | camera->RK3576 | Front Sensor Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| CSI_CLK_N | diff | 1.2V | camera->RK3576 | Front Sensor Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| CSI_D0_P | diff | 1.2V | camera->RK3576 | Front Sensor Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| CSI_D0_N | diff | MIPI D-PHY | camera->RK3576 | Front Sensor Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| CSI_D1_P | diff | 1.2V | camera->RK3576 | Front Sensor Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| CSI_D1_N | diff | MIPI D-PHY | camera->RK3576 | Front Sensor Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| CAM_I2C_SCL | bus | 1.8V unless final pinmux says otherwise | controller->targets | Front Sensor Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| CAM_I2C_SDA | bus | 1.8V unless final pinmux says otherwise | bidirectional open-drain | Front Sensor Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| CAM_RST_L | control | 1.8V | RK3576->cam | Front Sensor Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| CAM_PWDN_L | control | 1.8V | RK3576->cam | Front Sensor Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| CAM_MCLK | control | 1.8V | RK3576->cam | Front Sensor Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| PDM_ARRAY_CLK | bus | AON | RK3576->mic | Front Sensor Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| PDM_ARRAY_D0 | bus | 1.8V unless final pinmux says otherwise | array mics->RK3576 | Front Sensor Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| PDM_ARRAY_D1 | bus | 1.8V unless final pinmux says otherwise | array mics->RK3576 | Front Sensor Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| USB2_DP | diff | 3.3V | bidirectional | EVT Debug Tail; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| USB2_DM | diff | 3.3V | bidirectional | EVT Debug Tail; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| SOC_MASKROM_L | control | 1.8V unless final pinmux says otherwise | see endpoints | EVT Debug Tail; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| SOC_RESET_L | control | 1.8V | nRF/btn->RK3576 | EVT Debug Tail; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| SOC_PWRKEY | control | 1.8V unless final pinmux says otherwise | see endpoints | EVT Debug Tail; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| PMIC_PWRON | control | 1.8V | nRF->RK806 | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| SOC_PWR_EN | control | 1.8V | nRF->boost | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| SOC_5V_PGOOD | control | 1.8V | boost->nRF | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| WIFI_CHIP_EN | control | 3.3V | nRF->FCU760K | L-Temple AON/Power Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| WIFI_ANT | analog | RF | see endpoints | R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| WIFI_BUCK_EN | control | 1.8V | nRF->buck | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| WIFI_LS_EN | control | 1.8V | nRF->LSW | L-Temple AON/Power Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| BLE_ANT | analog | RF | see endpoints | L-Temple AON/Power Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| CAM_1V1_EN | control | 1.8V | nRF->buck | Front Sensor Board; L-Temple AON/Power Board | required: default-safe pull + leakage/reverse-feed check |
| CAM_1V8_EN | control | 1.8V | nRF->LSW | Front Sensor Board; L-Temple AON/Power Board | required: default-safe pull + leakage/reverse-feed check |
| CAM_2V9_EN | control | 1.8V | nRF->LDO | Front Sensor Board; L-Temple AON/Power Board | required: default-safe pull + leakage/reverse-feed check |
| AUDIO_LS_EN | control | 1.8V | nRF->LSW | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| AUDIO_AMP_SD | control | Vbat | nRF->amp | L-Temple AON/Power Board; R-Temple Compute Board | required: default-safe pull + leakage/reverse-feed check |
| I2C_AON_SCL | bus | 1.8V | controller->targets | Front Sensor Board; L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| I2C_AON_SDA | bus | 1.8V | bidirectional open-drain | Front Sensor Board; L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| NRF_SWDIO | bus | 1.8V unless final pinmux says otherwise | see endpoints | EVT Debug Tail; L-Temple AON/Power Board | required: default-safe pull + leakage/reverse-feed check |
| NRF_SWDCLK | bus | 1.8V unless final pinmux says otherwise | see endpoints | EVT Debug Tail; L-Temple AON/Power Board | required: default-safe pull + leakage/reverse-feed check |
| NTC_R | analog | analog | see endpoints | L-Temple AON/Power Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| NTC_L | analog | analog | see endpoints | L-Temple AON/Power Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| PDM_WAKE_CLK | bus | AON | NDP120->mic | Front Sensor Board; L-Temple AON/Power Board | required: default-safe pull + leakage/reverse-feed check |
| PDM_WAKE_DATA | bus | 1.8V unless final pinmux says otherwise | wake mic->NDP120 | Front Sensor Board; L-Temple AON/Power Board | required: default-safe pull + leakage/reverse-feed check |
| SPK_P | diff | TBD | see endpoints | R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| SPK_N | diff | TBD | see endpoints | R-Temple Compute Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| HAPTIC_P | diff | TBD | see endpoints | L-Temple AON/Power Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |
| HAPTIC_N | diff | TBD | see endpoints | L-Temple AON/Power Board; Temple Rears (batt/spkr/ant) | required: default-safe pull + leakage/reverse-feed check |

## High-Speed And RF Nets

| Net | Kind | Diff mate | Boards | Layout rule | ESD |
|---|---|---|---|---|---|
| CSI_CLK_P | diff | CSI_CLK_N | Front Sensor Board; R-Temple Compute Board | 100 ohm diff, length match, continuous ground, no stubs, ESD at FPC | yes, low-cap at FPC entry (U18/U19) |
| CSI_CLK_N | diff | CSI_CLK_P | Front Sensor Board; R-Temple Compute Board | 100 ohm diff, length match, continuous ground, no stubs, ESD at FPC | yes, low-cap at FPC entry (U18/U19) |
| CSI_D0_P | diff | CSI_D0_N | Front Sensor Board; R-Temple Compute Board | 100 ohm diff, length match, continuous ground, no stubs, ESD at FPC | yes, low-cap at FPC entry (U18/U19) |
| CSI_D0_N | diff | CSI_D0_P | Front Sensor Board; R-Temple Compute Board | 100 ohm diff, length match, continuous ground, no stubs, ESD at FPC | yes, low-cap at FPC entry (U18/U19) |
| CSI_D1_P | diff | CSI_D1_N | Front Sensor Board; R-Temple Compute Board | 100 ohm diff, length match, continuous ground, no stubs, ESD at FPC | yes, low-cap at FPC entry (U18/U19) |
| CSI_D1_N | diff | CSI_D1_P | Front Sensor Board; R-Temple Compute Board | 100 ohm diff, length match, continuous ground, no stubs, ESD at FPC | yes, low-cap at FPC entry (U18/U19) |
| WIFI_USB_DP | diff | WIFI_USB_DM | R-Temple Compute Board | 90 ohm diff, pair route, no stubs, continuous ground | module-internal side; add only if HW Design requires |
| WIFI_USB_DM | diff | WIFI_USB_DP | R-Temple Compute Board | 90 ohm diff, pair route, no stubs, continuous ground | module-internal side; add only if HW Design requires |
| USB2_DP | diff | USB2_DM | EVT Debug Tail; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | 90 ohm diff, pair route, no stubs, continuous ground | yes, low-cap at connector (U24) |
| USB2_DM | diff | USB2_DP | EVT Debug Tail; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | 90 ohm diff, pair route, no stubs, continuous ground | yes, low-cap at connector (U24) |
| WIFI_ANT | analog | no | R-Temple Compute Board; Temple Rears (batt/spkr/ant) | 50 ohm controlled impedance, pi-match, antenna keep-out | RF-approved only if required |
| BLE_ANT | analog | no | L-Temple AON/Power Board; Temple Rears (batt/spkr/ant) | 50 ohm controlled impedance, pi-match, antenna keep-out | RF-approved only if required |
| SPK_P | diff | SPK_N | R-Temple Compute Board; Temple Rears (batt/spkr/ant) | standard layout; verify at pinmux/placement | no / TBD |
| SPK_N | diff | SPK_P | R-Temple Compute Board; Temple Rears (batt/spkr/ant) | standard layout; verify at pinmux/placement | no / TBD |
| HAPTIC_P | diff | HAPTIC_N | L-Temple AON/Power Board; Temple Rears (batt/spkr/ant) | standard layout; verify at pinmux/placement | no / TBD |
| HAPTIC_N | diff | HAPTIC_P | L-Temple AON/Power Board; Temple Rears (batt/spkr/ant) | standard layout; verify at pinmux/placement | no / TBD |

## FPC / Board-Crossing Focus

| Net | Direction | Boards | Endpoints |
|---|---|---|---|
| SOC_SHUTDOWN_REQ | nRF->RK3576 | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U1.SHUTDOWN_REQ=RK3576; U7.SOC_SHDN_REQ=nRF54L15-QFN48; J4.SOC_SHDN_REQ=Custom hinge FPC 6-10mm |
| SOC_SAFE_TO_OFF | RK3576->nRF | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U1.SAFE_TO_OFF=RK3576; U7.SOC_SAFE_OFF=nRF54L15-QFN48; J4.SOC_SAFE_OFF=Custom hinge FPC 6-10mm |
| SOC_ALIVE | RK3576->nRF | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U1.ALIVE=RK3576; U7.SOC_ALIVE=nRF54L15-QFN48; J4.SOC_ALIVE=Custom hinge FPC 6-10mm |
| SOC_FAULT | RK3576->nRF | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U1.FAULT=RK3576; U7.SOC_FAULT=nRF54L15-QFN48; J4.SOC_FAULT=Custom hinge FPC 6-10mm |
| AON_UART_TX | nRF->RK3576 | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U1.AON_UART_RX=RK3576; U7.AON_UART_TX=nRF54L15-QFN48; J4.AON_UART_TX=Custom hinge FPC 6-10mm |
| AON_UART_RX | RK3576->nRF | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U1.AON_UART_TX=RK3576; U7.AON_UART_RX=nRF54L15-QFN48; J4.AON_UART_RX=Custom hinge FPC 6-10mm |
| CSI_CLK_P | camera->RK3576 | Front Sensor Board; R-Temple Compute Board | U1.CSI_CLK_P=RK3576; U14.CSI_CLK_P=IMX415-AAQR module (custom FPC); U18.CLK_P=TPD4E05U06; J3.CSI_CLK_P=Hirose FH26W 0.3mm FPC |
| CSI_CLK_N | camera->RK3576 | Front Sensor Board; R-Temple Compute Board | U1.CSI_CLK_N=RK3576; U14.CSI_CLK_N=IMX415-AAQR module (custom FPC); U18.CLK_N=TPD4E05U06; J3.CSI_CLK_N=Hirose FH26W 0.3mm FPC |
| CSI_D0_P | camera->RK3576 | Front Sensor Board; R-Temple Compute Board | U1.CSI_D0_P=RK3576; U14.CSI_D0_P=IMX415-AAQR module (custom FPC); U18.D0_P=TPD4E05U06; J3.CSI_D0_P=Hirose FH26W 0.3mm FPC |
| CSI_D0_N | camera->RK3576 | Front Sensor Board; R-Temple Compute Board | U1.CSI_D0_N=RK3576; U14.CSI_D0_N=IMX415-AAQR module (custom FPC); U18.D0_N=TPD4E05U06; J3.CSI_D0_N=Hirose FH26W 0.3mm FPC |
| CSI_D1_P | camera->RK3576 | Front Sensor Board; R-Temple Compute Board | U1.CSI_D1_P=RK3576; U14.CSI_D1_P=IMX415-AAQR module (custom FPC); U19.D1_P=TPD4E05U06; J3.CSI_D1_P=Hirose FH26W 0.3mm FPC |
| CSI_D1_N | camera->RK3576 | Front Sensor Board; R-Temple Compute Board | U1.CSI_D1_N=RK3576; U14.CSI_D1_N=IMX415-AAQR module (custom FPC); U19.D1_N=TPD4E05U06; J3.CSI_D1_N=Hirose FH26W 0.3mm FPC |
| CAM_I2C_SCL | controller->targets | Front Sensor Board; R-Temple Compute Board | U1.CAM_I2C_SCL=RK3576; U14.SCL=IMX415-AAQR module (custom FPC); J3.CAM_I2C_SCL=Hirose FH26W 0.3mm FPC; R5.B=2.2k 1% |
| CAM_I2C_SDA | bidirectional open-drain | Front Sensor Board; R-Temple Compute Board | U1.CAM_I2C_SDA=RK3576; U14.SDA=IMX415-AAQR module (custom FPC); J3.CAM_I2C_SDA=Hirose FH26W 0.3mm FPC; R6.B=2.2k 1% |
| CAM_RST_L | RK3576->cam | Front Sensor Board; R-Temple Compute Board | U1.CAM_RST_L=RK3576; U14.XCLR_L=IMX415-AAQR module (custom FPC); U19.RST=TPD4E05U06; J3.CAM_RST_L=Hirose FH26W 0.3mm FPC |
| CAM_PWDN_L | RK3576->cam | Front Sensor Board; R-Temple Compute Board | U1.CAM_PWDN_L=RK3576; U14.PWDN_L=IMX415-AAQR module (custom FPC); J3.CAM_PWDN_L=Hirose FH26W 0.3mm FPC |
| CAM_MCLK | RK3576->cam | Front Sensor Board; R-Temple Compute Board | U1.CAM_MCLK=RK3576; U14.INCK=IMX415-AAQR module (custom FPC); U19.MCLK=TPD4E05U06; J3.CAM_MCLK=Hirose FH26W 0.3mm FPC |
| PDM_ARRAY_CLK | RK3576->mic | Front Sensor Board; R-Temple Compute Board | U1.PDM_ARR_CLK=RK3576; MK2.CLK=T5837 (array mic 1); MK3.CLK=T5837 (array mic 2); MK4.CLK=T5837 (4th mic); J3.PDM_ARR_CLK=Hirose FH26W 0.3mm FPC |
| PDM_ARRAY_D0 | array mics->RK3576 | Front Sensor Board; R-Temple Compute Board | U1.PDM_ARR_D0=RK3576; MK2.DATA=T5837 (array mic 1); J3.PDM_ARR_D0=Hirose FH26W 0.3mm FPC |
| PDM_ARRAY_D1 | array mics->RK3576 | Front Sensor Board; R-Temple Compute Board | U1.PDM_ARR_D1=RK3576; MK3.DATA=T5837 (array mic 2); MK4.DATA=T5837 (4th mic); J3.PDM_ARR_D1=Hirose FH26W 0.3mm FPC |
| USB2_DP | bidirectional | EVT Debug Tail; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U1.USB2_DP=RK3576; J1.DP=Magnetic pogo 4-6p; J2.DP=USB-C 16p USB2-only; U24.DP=TPD2E001 |
| USB2_DM | bidirectional | EVT Debug Tail; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U1.USB2_DM=RK3576; J1.DM=Magnetic pogo 4-6p; J2.DM=USB-C 16p USB2-only; U24.DM=TPD2E001 |
| SOC_MASKROM_L | see endpoints | EVT Debug Tail; R-Temple Compute Board | U1.MASKROM_n=RK3576; SW3.A=MaskROM/Recovery |
| SOC_RESET_L | nRF/btn->RK3576 | EVT Debug Tail; R-Temple Compute Board | U1.RESET_n=RK3576; U2.RESET_n=RK806S-5; SW2.A=Reset |
| SOC_PWRKEY | see endpoints | EVT Debug Tail; R-Temple Compute Board | U1.PWRKEY=RK3576; SW1.A=Power/PWRKEY |
| PMIC_PWRON | nRF->RK806 | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U2.PWRON=RK806S-5; U7.PMIC_PWRON=nRF54L15-QFN48; J4.PMIC_PWRON=Custom hinge FPC 6-10mm; R12.A=100k |
| SOC_PWR_EN | nRF->boost | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U6.EN=TPS61088; U7.SOC_PWR_EN=nRF54L15-QFN48; J4.SOC_PWR_EN=Custom hinge FPC 6-10mm; R11.A=100k |
| SOC_5V_PGOOD | boost->nRF | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U6.PG=TPS61088; U7.SOC_5V_PGOOD=nRF54L15-QFN48; J4.SOC_5V_PGOOD=Custom hinge FPC 6-10mm |
| WIFI_CHIP_EN | nRF->FCU760K | L-Temple AON/Power Board; R-Temple Compute Board | U11.CHIP_EN=FCU760KAAMD; U7.WIFI_CHIP_EN=nRF54L15-QFN48; R18.A=100k |
| WIFI_ANT | see endpoints | R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U11.ANT_WIFI_BT=FCU760KAAMD; J7.ANT=Wi-Fi 2.4/5 GHz FPC ant; J5.SIG=U.FL / I-PEX MHF |
| WIFI_BUCK_EN | nRF->buck | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U12.EN=TPS62825; U7.WIFI_BUCK_EN=nRF54L15-QFN48; J4.WIFI_BUCK_EN=Custom hinge FPC 6-10mm; R16.A=100k |
| WIFI_LS_EN | nRF->LSW | L-Temple AON/Power Board; R-Temple Compute Board | U13.EN=TPS22917DBVR; U7.WIFI_LS_EN=nRF54L15-QFN48; R17.A=100k |
| BLE_ANT | see endpoints | L-Temple AON/Power Board; Temple Rears (batt/spkr/ant) | U7.ANT=nRF54L15-QFN48; J6.ANT=BLE 2.4 GHz FPC/PCB ant |
| CAM_1V1_EN | nRF->buck | Front Sensor Board; L-Temple AON/Power Board | U7.CAM_1V1_EN=nRF54L15-QFN48; U15.EN=TPS62840; J3.CAM_1V1_EN=Hirose FH26W 0.3mm FPC; R13.A=100k |
| CAM_1V8_EN | nRF->LSW | Front Sensor Board; L-Temple AON/Power Board | U7.CAM_1V8_EN=nRF54L15-QFN48; U17.EN=TPS22917DBVR; J3.CAM_1V8_EN=Hirose FH26W 0.3mm FPC; R14.A=100k |
| CAM_2V9_EN | nRF->LDO | Front Sensor Board; L-Temple AON/Power Board | U7.CAM_2V9_EN=nRF54L15-QFN48; U16.EN=TLV75529PDRVR; J3.CAM_2V9_EN=Hirose FH26W 0.3mm FPC; R15.A=100k |
| AUDIO_LS_EN | nRF->LSW | L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U7.AUDIO_LS_EN=nRF54L15-QFN48; U21.EN=TPS22917DBVR; J4.AUDIO_LS_EN=Custom hinge FPC 6-10mm; R19.A=100k |
| AUDIO_AMP_SD | nRF->amp | L-Temple AON/Power Board; R-Temple Compute Board | U7.AMP_SD=nRF54L15-QFN48; U20.SD_MODE=MAX98360A; R20.A=100k |
| I2C_AON_SCL | controller->targets | Front Sensor Board; L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U7.I2C_SCL=nRF54L15-QFN48; U8.I2C_SCL=nPM1300; U10.SCL=BMI270; U22.SCL=DRV2605L; U25.SCL=INA238 (I_BAT_TOTAL); U26.SCL=INA238 (I_CELL_L); U27.SCL=INA238 (I_CELL_R); U28.SCL=INA238 (I_SOC_5V); U29.SCL=INA238 (I_WIFI); U30.SCL=INA238 (I_AUDIO); U31.SCL=INA238 (I_CAM_1V1); U32.SCL=INA238 (I_CAM_1V8); U33.SCL=INA238 (I_CAM_2V9); R3.B=2.2k 1% |
| I2C_AON_SDA | bidirectional open-drain | Front Sensor Board; L-Temple AON/Power Board; R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U7.I2C_SDA=nRF54L15-QFN48; U8.I2C_SDA=nPM1300; U10.SDA=BMI270; U22.SDA=DRV2605L; U25.SDA=INA238 (I_BAT_TOTAL); U26.SDA=INA238 (I_CELL_L); U27.SDA=INA238 (I_CELL_R); U28.SDA=INA238 (I_SOC_5V); U29.SDA=INA238 (I_WIFI); U30.SDA=INA238 (I_AUDIO); U31.SDA=INA238 (I_CAM_1V1); U32.SDA=INA238 (I_CAM_1V8); U33.SDA=INA238 (I_CAM_2V9); R4.B=2.2k 1% |
| NRF_SWDIO | see endpoints | EVT Debug Tail; L-Temple AON/Power Board | U7.SWDIO=nRF54L15-QFN48; TP1.SWDIO=UART/SWD pogo pads |
| NRF_SWDCLK | see endpoints | EVT Debug Tail; L-Temple AON/Power Board | U7.SWDCLK=nRF54L15-QFN48; TP1.SWDCLK=UART/SWD pogo pads |
| NTC_R | see endpoints | L-Temple AON/Power Board; Temple Rears (batt/spkr/ant) | U8.NTC_R=nPM1300; RT1.A=10k NTC (R cell); TP2.NTC_R=Battery test points |
| NTC_L | see endpoints | L-Temple AON/Power Board; Temple Rears (batt/spkr/ant) | U8.NTC_L=nPM1300; RT2.A=10k NTC (L cell); TP2.NTC_L=Battery test points |
| PDM_WAKE_CLK | NDP120->mic | Front Sensor Board; L-Temple AON/Power Board | U9.PDM_CLK=NDP120; MK1.CLK=T5837 (wake mic); J3.PDM_WAKE_CLK=Hirose FH26W 0.3mm FPC |
| PDM_WAKE_DATA | wake mic->NDP120 | Front Sensor Board; L-Temple AON/Power Board | U9.PDM_DATA=NDP120; MK1.DATA=T5837 (wake mic); J3.PDM_WAKE_DATA=Hirose FH26W 0.3mm FPC |
| SPK_P | see endpoints | R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U20.OUT_P=MAX98360A; LS1.P=8 ohm 0.5-1 W speaker |
| SPK_N | see endpoints | R-Temple Compute Board; Temple Rears (batt/spkr/ant) | U20.OUT_N=MAX98360A; LS1.N=8 ohm 0.5-1 W speaker |
| HAPTIC_P | see endpoints | L-Temple AON/Power Board; Temple Rears (batt/spkr/ant) | U22.OUT_P=DRV2605L; M1.P=LRA/ERM motor |
| HAPTIC_N | see endpoints | L-Temple AON/Power Board; Temple Rears (batt/spkr/ant) | U22.OUT_N=DRV2605L; M1.N=LRA/ERM motor |

Full endpoint-level matrix is exported as `v2_chipdown/reports/interconnect_matrix.csv`.
