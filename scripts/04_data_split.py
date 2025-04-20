import numpy as np
from pathlib import Path
import shutil
# Load library

# YOLO directory archotecture
def yolo_dir(main_dir:str):
    Path(main_dir).mkdir(exist_ok=True)
    sub_dir1 = f"{main_dir}/datasets/images"
    sub_dir2 = f"{main_dir}/datasets/labels"
    Path(sub_dir1).mkdir(exist_ok=True, parents=True)
    Path(sub_dir2).mkdir(exist_ok=True, parents=True)

    split_dir = ["train", "test", "val"]

    sub_dir1 = [f"{sub_dir1}/{i}" for i in split_dir]
    sub_dir2 = [f"{sub_dir2}/{i}" for i in split_dir]

    all_sub_dir = sub_dir1
    all_sub_dir.extend(sub_dir2)

    for dr in all_sub_dir:
        Path(dr).mkdir(exist_ok=True, parents=True)


# Creat split for traning and test
def split_data(data_src:str, 
               label_dir:str, 
               split_type = [80, 20, 0], 
               seed = 123):

    if sum(split_type) > 100:
        Exception(f"Sum of split type must be 100, and not {sum(split_type)}")

    # Image path list
    img_path = list(Path(data_src).iterdir())
    ## Populate yolo architectir directory
    img_count = len(img_path)
    img_index = np.arange(start=0, stop=img_count)
    # select randomly some index
    np.random.seed(seed)
    # Select 80% for train
    train = np.random.choice(img_index, size=round(img_count*(split_type[0]/100)))
    remain = np.setdiff1d(img_index, train)
    # Selec 10% for val
    if split_type[0] + split_type[1] == 100:
        size = len(remain)#
    else:
        size = round(len(remain)*(split_type[1]/100))

    val =  np.random.choice(remain, size=size)
    if split_type[0] + split_type[1] < 100:
        # Select test 10% = ramin after val
        test = np.setdiff1d(remain, val)
        test_img = [img_path[i] for i in test]
        for img in test_img:
            shutil.copy(src=str(img), dst=f"datasets/images/train/{img.name}")
            label_path = f"{label_dir}/{img.stem}.txt"
            label_dst = f"datasets/labels/test/{img.stem}.txt"
            shutil.copy(label_path, label_dst)


    train_img = [img_path[i] for i in train]
    val_img = [img_path[i] for i in val]

    for img in train_img:
        shutil.copy(src=str(img), dst=f"datasets/images/train/{img.name}")
        label_path = f"{label_dir}/{img.stem}.txt"
        label_dst = f"datasets/labels/train/{img.stem}.txt"
        shutil.copy(label_path, label_dst)

    for img in val_img:
        shutil.copy(src=str(img), dst=f"datasets/images/val/{img.name}")
        label_path = f"{label_dir}/{img.stem}.txt"
        label_dst = f"datasets/labels/val/{img.stem}.txt"
        shutil.copy(label_path, label_dst)


yolo_dir(".")
split_data(data_src="images", label_dir="annotations")
