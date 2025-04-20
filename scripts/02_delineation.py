import numpy as np
import cv2 as cv
from pathlib import Path
import re
from tqdm import tqdm
# Load library
import rasterio as rio

def delineation(mask_dir:str, 
                annotation_dir:str, 
                exclude_pixel, 
                digits:int = 3):
    
    Path(annotation_dir).mkdir(exist_ok=True)
    
    mask_files = list(Path(mask_dir).iterdir())
    for msk in tqdm(mask_files, desc="Delineation"):
        full_txt_path = str(Path(annotation_dir, f"{msk.stem}.txt"))
        if Path(full_txt_path).exists():
            Path(full_txt_path).unlink()

        tif_img = cv.imread(str(msk), cv.IMREAD_UNCHANGED)
        ## Force binary format to BGR
        if exclude_pixel:
            if type(exclude_pixel) in (list, tuple):
                for i in exclude_pixel:
                    tif_img[tif_img == i] = np.nan
            else:
                tif_img[tif_img == exclude_pixel] = np.nan

        gray_image = cv.cvtColor(tif_img.astype(np.uint8), cv.COLOR_GRAY2BGR)
        ## From BGR to grayscale
        gray_image = cv.cvtColor(gray_image, cv.COLOR_BGR2GRAY)
        ## Acces different classes (diffrent pixel)
        species_classes = np.unique(gray_image)
        
        ## Select each class and convert to binnary mask
        for species in species_classes:
            new_array = gray_image.copy()  # create a copy to keep the original array
            if species == 0:
                new_array[new_array == 0] = 1
                new_array[new_array != 1] = 0
            else:
                new_array[new_array != species] = 0
            
            ## Find conture
            thres, mask_img = cv.threshold(src=new_array, type=cv.THRESH_BINARY, thresh=species/2, maxval=new_array.max())
            outlines, _ = cv.findContours(image=mask_img, mode=cv.RETR_EXTERNAL, method=cv.CHAIN_APPROX_SIMPLE)

            # Retrive image height and width of image
            img_height = mask_img.shape[0]; img_width = mask_img.shape[1]
            outl = 0
            for otl in outlines:
                outl += 1
                number_of_point = len(otl)
                plg_list = []
                for pt in range(number_of_point):
                    x = round(otl[pt][0][0]/img_width, digits)
                    y = round(otl[pt][0][1]/img_height, digits)
                    plg_list.append((x, y))
                if len(plg_list) < 3: # At leat 3 points to form polygon
                    continue
                plg_list.append((plg_list[0][0], plg_list[0][1])) # close with first point
                plg_str = f"{species} {plg_list}"
                
                plg_str = re.sub(",|\\[|\\(|\\]|\\)", "", plg_str)+"\n"

                with open(full_txt_path, "a") as f:
                    f.write(plg_str)


delineation(mask_dir="mask", 
            annotation_dir="annotations", 
            exclude_pixel=9999, digits=3)

