# AutoCAD import notes

- Primary CAD exchange files:
  - `export/autocad_floorplan_2d.dxf`: model-space 2D floorplan, units in millimeters.
  - `export/autocad_envelopes_3d.dxf`: 3D envelope model using DXF `3DFACE` entities, units in millimeters.
- In AutoCAD, open the DXF directly or use `INSERT`; verify `INSUNITS=4` / millimeters.
- Layers: COMPUTE, POWER, RF, AUDIO, BATTERY, TBD, KEEP_OUT, SHELL, DIM, TEXT.
- TBD layer means target/control envelope only and `NOT RELEASED FOR TOOLING`.
- DWG was not generated because the environment has no DWG-capable converter. AutoCAD can save the opened DXF as DWG.
