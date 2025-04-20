from pathlib import Path
import numpy as np
import rasterio as rio
from tqdm import tqdm
import cv2

# Tiff to JPEG to have true color
def raster_to(source:str, 
           dst_dir:str = 'images', 
           suffix:str = "jpeg",
           normalize:bool = False):
    # Ceate a directory to store image in true color into jpeg from instead of tif
    Path(f"{dst_dir}").mkdir(exist_ok=True)

    ext = ('jpeg', 'jpg', 'png', 'tif')
    if not suffix in ext:
        raise ValueError(f"suffix must be on of {ext}, not {suffix}")

    # Apply for loop to convert each tif file and save inti jpeg format
    if Path(source).is_dir():
        img_list = [str(img) for ext in ("*.tif", "*.tiff") for img in Path(source).glob(ext)]
    else:
        img_list = [Path(source)]

    for img in tqdm(img_list, desc='Converting'):
        img_path = Path(img)
        jpeg_file = f"{dst_dir}/{img_path.stem}.{suffix}"

        with rio.open(img) as rst:
            if rst.count < 3:
                continue
            band1 = rst.read(3)
            band2 = rst.read(2)
            band3 = rst.read(1)

            new_img = np.array([band1, band2, band3])
            new_img = np.transpose(new_img, (1, 2, 0))
            if normalize:
                 # Normalize to 0–255 (based on max value in image)
                max_val = np.percentile(new_img, 95)  # Better than raw max (avoids bright outliers)
                new_img = np.clip((new_img / max_val) * 255, 0, 255)
            # Convert to uint8 and save
            new_img = new_img.astype(np.uint8)
            cv2.imwrite(jpeg_file, new_img)


raster_to(source="cropped", 
       dst_dir='images', normalize=True,
       suffix='jpeg')