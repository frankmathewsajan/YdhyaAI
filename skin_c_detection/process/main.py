import os
import shutil
import pandas as pd
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import torchvision
import tensorflow.keras.utils.image_dataset_from_directory
from torchvision import transforms
import torch.utils.data as data

# Define paths
data_dir = 'data/HAM10000/'  # Path to the folder containing all images
metadata_path = 'data/HAM10000/HAM10000_metadata.csv'  # Metadata CSV file
reorganized_dir = 'data/reorganized/'  # Destination folder for reorganized data

# Step 1: Load Metadata
skin_df = pd.read_csv(metadata_path)

# Step 2: Map Image Paths
image_paths = {
    os.path.splitext(os.path.basename(x))[0]: x for x in glob(os.path.join(data_dir, '*', '*.jpg'))
}
skin_df['path'] = skin_df['image_id'].map(image_paths.get)

# Step 3: Reorganize Images by Labels
if not os.path.exists(reorganized_dir):
    os.makedirs(reorganized_dir)

for label in skin_df['dx'].unique():
    label_dir = os.path.join(reorganized_dir, label)
    os.makedirs(label_dir, exist_ok=True)

    for _, row in skin_df[skin_df['dx'] == label].iterrows():
        shutil.copy(row['path'], label_dir)

# Step 4: Data Loader with Keras
image_size = (32, 32)
datagen = image_dataset_from_directory(rescale=1. / 255)

train_data_keras = datagen.flow_from_directory(
    directory=reorganized_dir,
    target_size=image_size,
    batch_size=16,
    class_mode='categorical'
)

# Step 5: Data Loader with PyTorch
transform = transforms.Compose([
    transforms.Resize(32),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

train_data_torch = torchvision.datasets.ImageFolder(root=reorganized_dir, transform=transform)
train_loader = data.DataLoader(train_data_torch, batch_size=16, shuffle=True)

print("Keras DataLoader Classes:", train_data_keras.class_indices)
print("PyTorch DataLoader Classes:", train_data_torch.class_to_idx)


# Step 6: Visualization
def plot_images_keras(data_generator):
    x, y = next(data_generator)
    plt.figure(figsize=(12, 12))
    for i in range(9):
        plt.subplot(3, 3, i + 1)
        plt.imshow(x[i])
        plt.title(f"Class: {y[i].argmax()}")
        plt.axis('off')
    plt.show()


def plot_images_torch(data_loader):
    batch = next(iter(data_loader))
    images, labels = batch
    plt.figure(figsize=(12, 12))
    for i in range(9):
        plt.subplot(3, 3, i + 1)

