# Phase 2 Supplier Data Freeze Status

Generated: 2026-07-01

Verdict: **HOLD**. Local source documents were reviewed and folded into the mechanical database, but the supplier-data set is not sufficient to freeze layout or release footprints.

## Local Source Review

| Item | Source | Freeze status | Reason |
|---|---|---|---|
| RK3576 | RK3576 Brief Datasheet file | HOLD | brief datasheet only; HDG/ball map/land pattern missing |
| FCU760K | Quectel FCU760K Short Specification | HOLD | outline and basic electrical data present; hardware design guide/land pattern missing |
| NDP120 | Syntiant NDP120 Product Brief | HOLD | product brief only; full datasheet/rail map/package drawing missing |
| IMX415 | Sony IMX415-AAQR-C Datasheet E19504 | HOLD | bare sensor source present; final custom module/lens/FPC drawing missing |
| BQ2970 | TI BQ297xx Datasheet SLUSBU9I | DNP | valid fallback IC source; pack PCM scheme still must be chosen |
| LP451165 | LP451165 Battery Bay Fit Check | HOLD | project fit envelope present; supplier max drawing/certs/tabs/NTC missing |

## P0 Supplier Questions Blocking PCB Layout

| Item | Missing document | Closure condition |
|---|---|---|
| RK806S-5 package / height | Rockchip/Radxa PMIC drawing | Official package drawing + land pattern + rail sequence reviewed |
| LPDDR4X exact MPN / size / ball map | LPDDR vendor datasheet + ball map | MPN + package + ball map + DDR topology + length report |
| eMMC exact MPN / package | eMMC datasheet/package drawing | MPN + package + BSP boot validation |
| IMX415 lens / PCB / FPC / total Z | final module drawing and pinout | Approved module drawing + lens/FPC/mounting + schematic/BOM update if changed |
| Wi-Fi antenna | antenna vendor drawing + tune report | Worn-state antenna tune + keep-out in CAD/PCB |
| BLE antenna | antenna vendor drawing + tune report | Antenna SKU + keep-out + matching + tune report |
| main speaker | speaker datasheet + acoustic cavity drawing | Speaker MPN + cavity + antenna magnet clearance passed |
| magnetic pogo connector | pogo supplier drawing | MPN + pinout + current/fault/ESD validation |
| hinge FPC | FPC vendor stack-up and impedance report | Pinout + current rating + impedance + bend test |
| Boost inductor | inductor datasheet | Selected MPN passes peak/droop/thermal |
| FH26W exact pin count | Hirose drawing + interconnect matrix | Pin count/contact orientation + impedance checked |
| battery pack drawing | cell/pack drawing + certs | Supplier drawing + dummy/real-cell fit test |
| battery tab and cable exit | battery pack drawing | Pack drawing + strain-relief CAD |
| battery NTC | NTC datasheet + charger config | Curve + nPM1300 config + per-cell placement |
| battery protection | pack PCM spec or BQ2970 suffix/MOSFET | One protection scheme selected and tested |
| all connector mating heights | connector drawings | All connector 3D envelopes in CAD |

No online supplier data was promoted to frozen status in this phase. Per the project rule, only official datasheets, package drawings, land patterns and verified CAD/STEP files can close these items.
