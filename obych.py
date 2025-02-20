import os
from ultralytics import YOLO

current_dir = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(current_dir, 'data.yaml')
model = YOLO(os.path.join(current_dir, 'yolov8l.pt'))
epochs = 450
imgsz = 864


if __name__ == '__main__':
    results = model.train(data=data_path,
                      epochs=epochs,
                      imgsz=imgsz,
                      name='red',
                      device='cuda')
