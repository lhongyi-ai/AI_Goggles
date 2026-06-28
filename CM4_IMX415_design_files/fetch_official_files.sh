#!/usr/bin/env bash
set -euo pipefail
mkdir -p official_downloads
cd official_downloads

curl -fL -O https://dl.radxa.com/accessories/camera-4k/radxa_camera_4k_product_brief_Revision_1.0.pdf
curl -fL -O https://dl.radxa.com/accessories/camera-4k/IMX415-AAQR-C_Datasheet_E19504.pdf
curl -fL -O https://dl.radxa.com/cm4/docs/hw/radxa_cm4_schematic_v1.20.pdf
curl -fL -O https://dl.radxa.com/cm4/docs/hw/radxa_cm4_components_placement_map_v1.20.pdf
curl -fL -O https://dl.radxa.com/cm4/docs/hw/radxa_cm4_pinout_v1.20.xlsx
curl -fL -O https://dl.radxa.com/cm4/docs/hw/radxa_cm4_2d_dxf_v1.20.zip
curl -fL -O https://dl.radxa.com/cm4/docs/hw/radxa_cm4_3d_stp_v1.20.zip
curl -fL -O https://dl.radxa.com/cm4/cm4-io-board/docs/hw/radxa_cm4_io_schematic_v1.10.pdf
curl -fL -O https://dl.radxa.com/cm4/cm4-io-board/docs/hw/radxa_cm4_io_components_placement_map_v1.10.pdf
curl -fL -O https://dl.radxa.com/cm4/cm4-io-board/docs/hw/radxa_cm4_io_2d_dxf_v1.10.zip
curl -fL -O https://dl.radxa.com/cm4/cm4-io-board/docs/hw/radxa_cm4_io_3d_stp_v1.10.zip

echo 'Radxa files downloaded. Download the two DF40C 2D drawings and STEP models manually from the Hirose product pages listed in README_文件索引.md.'
