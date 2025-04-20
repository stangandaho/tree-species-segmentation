
# 🌳 Tree Species Segmentation from Aerial Imagery using YOLO
This project is an experimental pipeline that applies **deep learning (YOLO architecture)** to detect and classify individual tree species from **high-resolution aerial imagery**. The data includes 31 tree species, raster canopy masks, and multispectral input images.

> ⚠️ **Disclaimer:**  
> This project is for **testing and prototyping only**. It is not optimized for high accuracy and may perform inconsistently across all species due to factors like class imbalance and spectral similarity.


## 📌 Project Overview
- Extract canopy polygons and associate them with tree species
- Tile aerial imagery and generate YOLO-compatible masks
- Convert data into training-ready image and label files
- Split into train/val/test datasets
- Prepare for object detection training using YOLOv5 or YOLOv8


## 🧱 Pipeline Overview

### ✅ 1. Preprocessing & Tiling  
**Script:** `01_clip_image.R`  
- Import canopy and species shapefiles
- Create a spatial grid and clip to the Area Of Interest (AOI)
- Generate raster masks (`mask/`) and cropped imagery (`cropped/`)
- Assign class IDs and export class labels (`class_names.txt`)


### ✅ 2. Generate YOLO Annotations  
**Script:** `02_delineation.py`  
- Convert raster masks to polygon outlines
- Format outlines into YOLO label format
- Save to `annotations/` folder


### ✅ 3. Convert TIF to JPEG  
**Script:** `03_to_jpeg.py`  
- Convert 3-band `.tif` files into RGB `.jpeg`
- Normalize for better contrast
- Save to `images/` directory

### ✅ 4. Prepare for Training (Split & Organize)  
**Script:** `04_data_split.py`  
- Create YOLO-style folder structure
  ```
  datasets/
    └── images/ └── train/, test/, val/
    └── labels/ └── train/, test/, val/
  ```
- Randomly split images into training, validation, and testing sets
- Copy both images and labels to appropriate folders


## 📁 Final Folder Structure

```bash
.
├── images/                   # JPEG tiles (from TIF)
├── mask/                     # Raster masks with species IDs
├── annotations/              # YOLO polygon annotations (txt)
├── cropped/                  # Raw TIF tiles
├── datasets/
│   ├── images/
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   └── labels/
│       ├── train/
│       ├── val/
│       └── test/
├── shapefiles/               # Input canopy and AOI shapefiles
├── Pansharpen.Band.tiff      # Aerial multispectral image
├── class_names.txt           # ID to species name mapping
├── scripts/
│   ├── 01_clip_images.R
│   ├── 02_delineation.py
│   ├── 03_to_jpeg.py
│   ├── 04_data_split.py
└── README.md                 # ← You're here!
```


## 🧪 Requirements
- R and Dependencies
```r
install.packages(c("sf", "terra", "dplyr"))
```
- Python and Dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Ready for YOLO Training
You can now train YOLO with implementation:

```bash
yolo detect train data=data.yaml model=yolo11m.pt epochs=100 imgsz=640
```
For this project, we train model in Google Colab. The notebook can be accessed [here](https://drive.google.com/file/d/1-V3pXUukGJ8qukAxDnlVNNA-GyRMh2op/view?usp=sharing)