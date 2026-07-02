# Mechanical conflicts and blockers

- PASS: No 2D projection overlap between right battery and RK3576/RK806/TPS61088/boost inductor.
- PASS: RF02 antenna keep-out is separated from battery, main speaker and shield in this envelope model.
- WARN: LPDDR4X package body/height and ball map are still supplier/Rockchip HOLD despite EVT MPN selection.
- WARN: IMX415 camera module is an orange TBD target envelope, not released tooling geometry.
- WARN: Battery 70x12.8x5.6 is a control envelope; supplier pack drawing, tab/cable exit and dummy-cell fit test remain required.
- BLOCKED: Missing tools prevent native CAD exports: blender, freecad, kicad-cli, magick, convert
