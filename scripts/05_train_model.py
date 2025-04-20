from ultralytics import YOLO

mdl = YOLO(model="yolov8m-seg.pt")
mdl.train(epochs = 120, lr0 = 0.01, imgsz = (800, 800), data = "data.yaml")