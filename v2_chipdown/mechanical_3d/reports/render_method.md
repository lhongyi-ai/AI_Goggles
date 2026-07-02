# Render method

- Units: millimeters.
- Source of truth: `v2_chipdown/scripts/chipdown_bom.py`, current generated schematic, and the supplied V2.2 hardware-dimensions PDF.
- Rendering method on this machine: deterministic matplotlib engineering drawings plus ASCII STL envelope export.
- AutoCAD handoff method: dependency-free ASCII DXF. `autocad_floorplan_2d.dxf` contains 2D engineering floorplans; `autocad_envelopes_3d.dxf` contains 3D `3DFACE` envelope solids.
- Labeling method: short IDs on geometry, details in side tables/CSV to avoid text overlap.
- Frozen dimensions use solid edges; TBD or target-only envelopes use orange transparent/dashed/hatch styling and are marked `TBD - NOT RELEASED FOR TOOLING`.
- Native FreeCAD `.FCStd`, STEP and Blender `.blend` exports require installing the missing tools listed in `setup_requirements.md`.

Generated outputs:
- renders/01_transparent_overview.png: PASS (3840x2160 px)
- renders/02_external_view.png: PASS (3840x2160 px)
- renders/03_right_top.png: PASS (3840x2160 px)
- renders/04_right_side.png: PASS (3840x2160 px)
- renders/05_left_top.png: PASS (3840x2160 px)
- renders/06_left_side.png: PASS (3840x2160 px)
- renders/07_camera_detail.png: PASS (3840x2160 px)
- renders/08_soc_thermal_section.png: PASS (3840x2160 px)
- renders/09_battery_section.png: PASS (3840x2160 px)
- renders/10_camera_z_section.png: PASS (3840x2160 px)
- renders/11_speaker_section.png: PASS (3840x2160 px)
- renders/12_pogo_section.png: PASS (3840x2160 px)
- renders/13_rf_keepout.png: PASS (3840x2160 px)
- renders/14_exploded_view.png: PASS (3840x2160 px)
- models/glasses_assembly_model.json: PASS (editable JSON parameter model)
- models/compute_board_model.json: PASS (editable JSON parameter model)
- models/aon_board_model.json: PASS (editable JSON parameter model)
- models/camera_module_model.json: PASS (editable JSON parameter model)
- models/battery_pack_model.json: PASS (editable JSON parameter model)
- models/speaker_chamber_model.json: PASS (editable JSON parameter model)
- export/glasses_assembly.stl: PASS (ASCII STL envelope model, units documented as mm)
- export/autocad_floorplan_2d.dxf: PASS (AutoCAD ASCII DXF 2D floorplan, INSUNITS=mm)
- export/autocad_envelopes_3d.dxf: PASS (AutoCAD ASCII DXF 3D 3DFACE envelope model, INSUNITS=mm)
- reports/autocad_import_notes.md: PASS (AutoCAD handoff notes)
- blender/ai_glasses_render.blend: BLOCKED (blender command not found)
