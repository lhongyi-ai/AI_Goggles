# 01 — V2 System Architecture

## Two islands

V2 splits the system into an **always-on (AON) island** and a **demand-started RK3576 compute island**. The AON island owns system state and the *power switches* for everything expensive.

```
                        GLASSES ALWAYS-ON (AON) SYSTEM
┌───────────────────────────────────────────────────────────┐
│ Low-power BLE MCU (nRF-class)                              │
│  ├─ BLE link + alerting                                    │
│  ├─ IMU + motion detection (interrupt-driven)             │
│  ├─ Buttons / touch                                       │
│  ├─ Fuel gauge / NTC / charge status                      │
│  ├─ System state machine                                  │
│  └─ Controls power to RK3576, camera, Wi-Fi  ◄── key role │
│                                                           │
│ Audio DSP / wake-word processor                           │
│  ├─ Always-listening voice wake                           │
│  └─ Light audio pre-processing                            │
└───────────────────────────┬───────────────────────────────┘
              event / voice / button / motion trigger
                            ▼
┌───────────────────────────────────────────────────────────┐
│ RK3576 COMPUTE ISLAND (off by default)                    │
│  ├─ Camera / ISP                                          │
│  ├─ NPU recognition (6 TOPS)                              │
│  ├─ H.264/H.265 hardware encode                           │
│  ├─ Wi-Fi transmit                                        │
│  ├─ Local STT/TTS or heavy audio                          │
│  └─ On task done: return to sleep or power down           │
└───────────────────────────────────────────────────────────┘
```

RK3576 is capable enough (ISP, 3× MIPI CSI, PDM, SAI/I²S, hardware video encode, 6 TOPS NPU) — the problem was never capability, it was **keeping the 8-core CPU + DDR + PMIC + radio alive 24/7**. So it becomes a burst accelerator, not the always-on host.

## Split of responsibility (do not merge these)

| Function | Owner |
|---|---|
| System state machine + power sequencing | **BLE MCU** |
| Always-listening wake word + audio pre-proc | **Audio DSP** |
| Vision / NPU / encode / Wi-Fi upload | **RK3576 (burst)** |

The Architecture-Brief NDP120-class wake coprocessor direction is retained, but the DSP only *listens*; the BLE MCU owns the whole system state and the supply rails.

## Physical partition — four boards, not one carrier

See [05_hardware_partition.md](05_hardware_partition.md). Summary:

```
                     FRONT FRAME
                Camera + Mic Array (FPC)
                         │
        ┌────────────────┴────────────────┐
   RIGHT TEMPLE                       LEFT TEMPLE
   RK3576 Compute                  AON MCU + DSP + Power
        │                                 │
  R battery + Speaker              L battery + Speaker
        │                                 │
   Wi-Fi antenna                   BLE antenna / charging
```

This distributes heat, weight, and battery volume instead of stacking compute + battery + charging + audio on one board (the V1 mistake). RF split follows the V1 requirement: Wi-Fi carries video, BLE carries control + alerts.

## Standalone vs Tethered = software routing, not two boards

- **Standalone:** more tasks run on RK3576.
- **Tethered:** phone does GNSS, cloud ASR/TTS, networking, some AI.

Both run on the *same* hardware; the difference is where work is routed. GNSS defaults to the phone; an on-glasses GNSS module (e.g. MAX-M10S) becomes an *option*, not a default fit.
