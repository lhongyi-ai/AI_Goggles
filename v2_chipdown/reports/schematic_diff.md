# Phase 1 Schematic Diff

No KiCad schematic edits were made in this audit phase.

Required future schematic decisions before Phase 4:

- Decide whether U14 stays `IMX415-AAQR module (custom FPC)` or changes to Radxa Camera 4K AS001 mechanical baseline.
- Add/verify any NOT_FOR_FAB markings for VERIFY/HOLD/TBD packages once actual KiCad footprint libraries exist.
- Freeze J3/J4 pin counts and update interconnect matrix before any PCB placement.
- Freeze RK806S, LPDDR4X, eMMC and FCU760K official package/land patterns before assigning release footprints.
