import torch
import os
import itk
from torch.utils.data import Dataset
import json
from tqdm import tqdm

class ThoraxCBCTDataset(Dataset):
    def __init__(self, data_path, phase="train", paired=True, data_num=-1, desired_shape=None, device="cpu"):
        """
        Initialize the ThoraxCBCTDataset.

        Args:
            data_path (str): Path to the directory containing the dataset.
            phase (str): Phase of the dataset - 'train', 'val', or 'test'.
            paired (bool): If True, load paired data for registration tasks.
            data_num (int): Limit on the number of samples to load (-1 for all).
            desired_shape (tuple): Desired shape for resizing images.
            device (str): Device to use ('cpu' or 'cuda').
        """
        self.device = device
        self.desired_shape = desired_shape

        # Load dataset metadata
        with open(os.path.join(data_path, "ThoraxCBCT_dataset.json"), "r") as f:
            dataset_info = json.load(f)
        
        if phase == "train":
            data_list = dataset_info["training_paired_images"] if paired else dataset_info["training"]
        elif phase == "val":
            data_list = dataset_info["registration_val"]
        elif phase == "test":
            data_list = dataset_info["registration_test"]
        else:
            raise ValueError("Invalid phase. Choose from 'train', 'val', or 'test'.")

        # Load the specified number of samples
        if data_num > 0:
            data_list = data_list[:data_num]

        self.img_pairs = [
            (os.path.join(data_path, pair["moving"]), os.path.join(data_path, pair["fixed"]))
            for pair in data_list
        ]

    def load_image(self, img_path):
        """
        Load and preprocess a single image.
        """
        img = torch.tensor(itk.GetArrayFromImage(itk.imread(img_path))).float()
        img = (torch.clamp(img, -1000, 1000) + 1000) / 2000  # Normalize to [0, 1]
        if self.desired_shape:
            img = torch.nn.functional.interpolate(
                img[None, None, ...], size=self.desired_shape, mode="trilinear", align_corners=False
            ).squeeze(0)
        return img.to(self.device)

    def __len__(self):
        return len(self.img_pairs)

    def __getitem__(self, idx):
        moving_path, fixed_path = self.img_pairs[idx]
        moving_img = self.load_image(moving_path)
        fixed_img = self.load_image(fixed_path)
        return moving_img, fixed_img
    

if __name__ == "__main__":
    from torch.utils.data import DataLoader

    dataset_path = "./input/Release_06_12_23"
    thorax_dataset = ThoraxCBCTDataset(data_path=dataset_path, phase="train", paired=True, desired_shape=(64, 64, 64))
    dataloader = DataLoader(thorax_dataset, batch_size=2, shuffle=True)

    for moving, fixed in dataloader:
        print(f"Moving image shape: {moving.shape}")
        print(f"Fixed image shape: {fixed.shape}")
        break