# AI Glasses V2 Phase 1.5 Floorplan Fit Check

This report is generated from the current V2 schematic/BOM source of truth. It answers the mechanical placement question before formal PCB routing.

## Verdict

- A normal thin optical frame does **not** fit this V2 RK3576 chip-down architecture.
- A thick smart-glasses / sport-sunglasses frame can **conditionally fit** the current schematic if the frame provides the envelope below.
- The fit is not released for PCB layout yet: G00/G00F/G07/G10/G12/G14 remain open or HOLD until real CAD, battery, RF, FPC, speaker, camera, and package drawings are verified.
- Any real 3D envelope, component courtyard, battery swell zone, speaker cavity, or RF antenna keep-out overlap is a **fail**, unless CAD/EE explicitly proves it is a different Z-height feature with clearance, isolation, and thermal/RF sign-off.

## Minimum frame envelope for the current schematic

| Region | Minimum internal envelope | Why |
|---|---:|---|
| Right temple usable length | >=150 mm, with ~160+ mm preferred for a clean antenna/battery separation | RK3576 board + 70 mm cell + speaker/pogo + Wi-Fi antenna keep-out |
| Right front compute pod | >=72 x 20 x 8.5 mm | 62 x 18 mm compute PCB plus FPC strain relief and thermal stack |
| Right rear battery/RF/acoustic pod | >=78 x 16 x 8.5 mm | LP451165 max envelope 70 x 12.8 x 5.6 mm plus foam/swell, LS1 acoustic slot, pogo, RF window |
| Left temple usable length | >=145 mm | AON board + 70 mm cell + BLE keep-out + pogo |
| Left front AON pod | >=54 x 16 x 7.5 mm | 46 x 14 mm AON/power PCB plus FPC and shell clearance |
| Left rear battery/RF pod | >=82 x 16 x 7.5 mm | LP451165 max envelope plus BLE antenna region and service/charge area |
| Front sensor brow | >=32 x 8 x 5 mm | Custom IMX415 module, camera power, ESD, mic footprints and FPC exit |

## Frame style that can fit

Use a thick acetate/plastic smart-glasses frame, closer to Rokid/Xiaomi-style electronics temples than a normal thin prescription frame. The right temple needs a tall front compute pod, roughly 22-24 mm external vertical height and 10-11 mm external thickness after shell walls. The rear battery pods can taper but should still keep roughly 17-18 mm external vertical height and 8.5-9.5 mm external thickness.

A fixed-temple EVT frame is acceptable. Do not force a production folding hinge for EVT-A; keep the FPC/interconnect corridor and reserve bend/strain space for a later hinge version.

## Placement

| Location | Place here | Do not place here |
|---|---|---|
| Front brow / frame | U14 IMX415 custom module, MK1-MK4 mic footprints, camera ESD, J3 front FPC | RK3576, battery, hot regulators |
| Right temple front | U1 RK3576, U3 LPDDR4X, U2 RK806S, U4 eMMC, Y1 crystal, U6 TPS61088, L1, U11 FCU760K, U20/U21 audio electronics | Battery directly above/below RK3576/PMIC; antenna under copper or battery |
| Right temple rear | BT1 LP451165, LS1 speaker/acoustic slot, J7 Wi-Fi antenna keep-out/window, J1 pogo, J5 RF debug connector if EVT needs it | Speaker magnet inside antenna keep-out; battery swelling into FPC |
| Left temple front | U7 nRF54L15, U8 nPM1300, U9 NDP120, U10 BMI270, RS1, protection/current-sense options | High-current RK3576 boost loops |
| Left temple rear | BT2 LP451165, J6 BLE antenna keep-out/window, pogo/charge/service contacts, NTC/test pads | Battery/copper directly under BLE radiator |

## PCB stack recommendation

- Right compute PCB: one double-sided 8-10 layer HDI rigid island, not a board-on-board stack. Use the outer wall for RK3576 heat spreading.
- LPDDR4X must stay adjacent to RK3576; eMMC/PMIC/load switches can use the opposite side if height clears.
- Do not stack the battery over RK3576, RK806S, TPS61088, or the boost inductor.
- Left AON PCB: 4-layer rigid board is the starting point; use 6 layers only if RF/current-sense/noise review needs it.
- Front sensor board/FPC: 4-layer controlled-impedance rigid-flex for MIPI if the final camera module keeps CSI in the front frame.
- If the real CAD envelope is shorter than the table above, split into multiple rigid islands joined by FPC before routing instead of stacking hot boards over the battery.

## Interconnect map

| Link | Carries | Current schematic refs / nets |
|---|---|---|
| BT1/BT2 -> AON power path | 1S2P battery power, fuses, shunts, NTC | BT1/BT2 -> F1/F2 -> RS2/RS3 -> BAT_P -> RS1 -> U8 nPM1300/NPM_VBAT |
| Left AON -> right compute | VSYS/BAT_P distribution, AON UART, SOC/Wi-Fi/camera/audio enables, PGOOD/status, GND | J4/C039 hinge/interconnect placeholder; can be fixed-temple FPC/cable in EVT |
| nPM1300 -> AON loads | AON_1V8, AON_3V3, AON load-switch rail, I2C | U8 to U7/U9/U10 and current-sense options |
| Right compute power | VSYS -> SOC_IN -> SOC_5V -> RK806 rails | RS4, U6 TPS61088, U2 RK806S, U1/U3/U4 |
| Front camera -> right compute | MIPI CSI, CAM I2C, CAM MCLK/RST/PWDN, CAM_1V1/CAM_1V8/CAM_2V9, GND | J3/C038; U14/U15/U16/U17/U18/U19 to U1 |
| Front audio -> AON/compute | wake mic PDM to NDP120, array PDM to RK3576, I2S to amp | MK1 -> U9; MK2/MK3 -> U1; U20 -> LS1 |
| RF | Wi-Fi/BLE antenna feeds and debug coax | U11 -> J7/J5, U7 -> J6/J5; final antenna SKU/tune remains G14 |

## Render artifacts

- SVG: `v2_chipdown/reports/output/AI_Glasses_V2_Phase1_5_Floorplan.svg`
- PNG: `v2_chipdown/reports/output/AI_Glasses_V2_Phase1_5_Floorplan.png`
- PDF: `v2_chipdown/reports/output/AI_Glasses_V2_Phase1_5_Floorplan.pdf`

## Open gates before PCB layout

- G00/G00F: real CAD top/side envelope and no-route KiCad placement pass.
- G07: LP451165 datasheet, discharge curve, swelling, tabs, NTC, fusing, pairing/current-share proof.
- G10: custom IMX415 module dimensions, lens stack height, FPC pinout and rail current.
- G12: fixed-temple interconnect or folding hinge FPC pin count, impedance, bend radius and strain relief.
- G14: Wi-Fi/BLE antenna SKU, keep-out, matching, worn-state tuning and SAR/thermal interaction.
- Speaker/acoustic: final LS1 MPN, cavity size, magnet keep-out and leakage path.

## Source-of-truth sanity

- Current SoC: U1 / C001 / RK3576 / AI_Glasses_V2:VERIFY_FCCSP698L_16x17.
- Current Wi-Fi: U11 / C015 / FCU760KAAMD.
- Current IMU: U10 / C012 / BMI270.
- Current speaker: LS1 / C025 / 8 ohm 0.5-1 W speaker.
- Current battery: LP451165 300mAh (R) and LP451165 300mAh (L); mechanical max envelope uses 70 x 12.8 x 5.6 mm, not nominal pouch size.
