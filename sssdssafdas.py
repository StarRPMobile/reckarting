import os
path = 'dataset'

train_images_path = os.path.join(path, 'train', 'images')
train_labels_path = os.path.join(path, 'train', 'labels')

images = [f for f in os.listdir(train_images_path)]
labels = [f for f in os.listdir(train_labels_path)]

print(len(images), len(labels))

for i in images:
    try:
        print(labels.index(i.replace(i.split('.').pop(), "") + "txt"))
    except Exception as e:
        print(e)