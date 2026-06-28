# J2 FH35C Footprint Check

Date: 2026-06-28

## Source

- Official drawing copied into repo:
  `hardware/datasheets/FH35C-31S-0.3SHW_50_CL0580-2923-7-50_2DDrawing_0001002002.pdf`
- Original user-provided file:
  `/Users/stanley/Downloads/FH35C-31S-0.3SHW(50)_CL0580-2923-7-50_2DDrawing_0001002002.pdf`
- Drawing no.: `EDC3-338903-01`
- Code no.: `CL0580-2923-7-50`
- Part: `FH35C-31S-0.3SHW(50)`

Text extraction note:

```bash
pdftotext -layout /Users/stanley/Downloads/FH35C-31S-0.3SHW\(50\)_CL0580-2923-7-50_2DDrawing_0001002002.pdf /private/tmp/fh35c_2d.txt
```

Result: exit code 0, but the extracted text contained only watermark/copyright text and no usable dimension table. Dimensions were read from rendered pages using:

```bash
pdftoppm -png -r 200 /Users/stanley/Downloads/FH35C-31S-0.3SHW\(50\)_CL0580-2923-7-50_2DDrawing_0001002002.pdf /private/tmp/fh35c_page
```

## Drawing Dimensions Applied

For 31 contacts, the drawing table gives:

| Dimension | Value mm |
| --- | ---: |
| A | 10.9 |
| B | 8.4 |
| C | 9.0 |
| D | 9.63 |
| E | 10.33 |
| F | 9.6 |

Recommended PCB mounting pattern:

| Item | Value |
| --- | --- |
| Same-row pitch | 0.6 mm |
| Odd/even row X offset | 0.3 mm |
| Contact No.2 / even row | 15 pads, B = 8.4 mm span |
| Contact No.1 / odd row | 16 pads, C = 9.0 mm span |
| Even pad size | 0.20 x 0.65 mm |
| Odd pad size | 0.20 x 0.80 mm |

This corrected the previous temporary single-row footprint. The generated footprint now uses the official odd/even two-row mounting pattern.

## Files Generated

- Footprint source config: `config/j2_fh35c_footprint.yaml`
- Generator: `scripts/generate_j2_footprint.py`
- KiCad footprint: `hardware/AI_Glasses.pretty/FH35C-31S-0.3SHW_50.kicad_mod`
- 1:1 check PCB: `hardware/j2_fh35c_1to1_check.kicad_pcb`
- 1:1 check PDF: `generated/reports/j2_fh35c_1to1_check.pdf`

## Physical Gate Status

The drawing-based footprint check is complete. These items are **not** part of the
schematic electrical gate; they are explicitly marked `DEFERRED_TO_PRE_LAYOUT`:

| Item | Status |
| --- | --- |
| AC006 physical validation | `DEFERRED_TO_PRE_LAYOUT` |
| FPC contact side | `DEFERRED_TO_PRE_LAYOUT` |
| Insertion direction | `DEFERRED_TO_PRE_LAYOUT` |
| Pin 1 physical check | `DEFERRED_TO_PRE_LAYOUT` |
| 1:1 print | `DEFERRED_TO_PRE_LAYOUT` |
| Coupon test | `DEFERRED_TO_PRE_LAYOUT` |
| FPC bend and enclosure path | `DEFERRED_TO_PRE_LAYOUT` |

Pre-layout closure still requires printing `generated/reports/j2_fh35c_1to1_check.pdf`
at exactly 100%, placing a real FH35C-31S-0.3SHW(50) connector on the print,
checking AC006 contact side/orientation, and documenting continuity/photo evidence
before fabrication.
