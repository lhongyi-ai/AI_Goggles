# 02 — Power State Machine

"RK3576 fully powered down" and "respond in a few hundred ms" cannot both be true — a full Linux cold boot is not sub-second. So V2 defines **two distinct standby levels** plus the active states. The numbers here are the *design targets*; `config/power_budget_v2.yaml` holds the modelled per-subsystem estimate that must land inside each target band, and bench EVT replaces both.

| State | RK3576 | Target power | Wake time | Use case |
|---|---|--:|---|---|
| **Deep Off** | fully powered down | whole device **20–50 mW** | ~2–5 s (TBM*) | long standby, ordinary wear |
| **Quick Standby** | DDR retention / light sleep | **80–200 mW** (validation target) | <500 ms (TBM*) | active hazard-detection window (cycling) |
| **Record Active** | ISP + encode running | **1.0–1.5 W** | already running | continuous recording |
| **AI Burst** | NPU + encode + Wi-Fi | **1.5–2.5 W** peak | already running | vehicle ID, upload, STT |
| **Return to Sleep** | save state, close domains | falling | — | event finished |

*TBM = to be measured on bench; do not treat wake times as verified.*

Two extra "average-use" scenarios are modelled for battery sizing (they are duty-cycle *blends* of the states above, not hardware states):

| Scenario | Target avg power | Target runtime |
|---|--:|--:|
| Phone-assisted safety ID | **250–450 mW** | 3–5 h |
| Mixed motion use | **<=500–800 mW** | 3–4 h |

> Note: the external mixed-use target is **≤500–800 mW**; the current model is **450 mW**, which is deliberately below that band. At the high end of 500–800 mW, 4 h still needs a larger cell than a slim temple can usually absorb, so duty-cycle control remains mandatory.

## Decision behavior

```
Ordinary wear .................. Deep Off
Cycling started ................ Quick Standby
Motion/voice command detected .. Record / AI Burst
Event finished ................. close Wi-Fi + camera + RK3576 → Deep Off
```

## Two runtimes must be quoted, never one

Do not spec "4 h battery." Spec the pair:

| Usage mode | V2 target |
|---|--:|
| Standby (BLE + IMU + wake word) | 12–24 h |
| Mixed motion use | 3–4 h |
| Continuous 1080p record | 45–90 min |
| Continuous 1080p + local AI | 30–60 min |
| Short safety ID + phone link | 3–5 h |

Commercial "8 h / 2 days" claims are *also* mixed-mode, not continuous camera+AI. Quote V2 the same way.
