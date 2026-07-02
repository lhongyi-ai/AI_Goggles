# Setup requirements

Input PDF requested: `/mnt/data/AI_Glasses_Hardware_Dimensions_V2.2 (3).pdf`
Input PDF used: `/Users/stanley/AI Glasses/v2_chipdown/reports/output/AI_Glasses_Hardware_Dimensions_V2.2 (3).pdf`

| Tool | Path | Version/status | Impact | Install command |
|---|---|---|---|---|
| blender | - | MISSING | .blend and native Blender renders blocked | `brew install --cask blender` |
| freecad | - | MISSING | .FCStd and STEP exports blocked | `brew install --cask freecad` |
| kicad-cli | - | MISSING | ERC/PDF export from KiCad CLI blocked | `brew install --cask kicad` |
| python3 | /opt/anaconda3/bin/python3 | Python 3.12.4 | all generation blocked | `brew install python@3.12` |
| pdftotext | /opt/homebrew/bin/pdftotext | pdftotext version 26.06.0 | PDF dimension extraction blocked | `brew install poppler` |
| magick | - | MISSING | image montage via ImageMagick blocked | `brew install imagemagick` |
| convert | - | MISSING | image montage via ImageMagick blocked | `brew install imagemagick` |
| git | /usr/bin/git | git version 2.39.3 (Apple Git-145) | version control operations blocked | `brew install git` |

Python package status: current environment has numpy/pandas/Pillow/matplotlib/PyYAML; reportlab/trimesh/shapely/ezdxf/pypdf are not installed.
Because this environment lacks FreeCAD/Blender/KiCad CLI, native FreeCAD/Blender deliverables are recorded as blocked files, while AutoCAD DXF, PNG, CSV, JSON and STL outputs were generated.
