import os
import random
from datetime import datetime

from tqdm import tqdm
import torch
import torch.nn.functional as F
from dataset import ThoraxCBCTDataset
from torch.utils.data import DataLoader

import icon_registration as icon
import icon_registration.networks as networks
from icon_registration.losses import ICONLoss, to_floats

from unigradicon import make_network

# Determine the available device
device = "cpu"  # Default to CPU
if torch.backends.mps.is_available():
    device = "mps"  # Use MPS on macOS
elif torch.cuda.is_available():
    device = "cuda"  # Use CUDA if available

print(f"Using device: {device}")

def write_stats(writer, stats: ICONLoss, ite, prefix=""):
    for k, v in to_floats(stats)._asdict().items():
        writer.add_scalar(f"{prefix}{k}", v, ite)

input_shape = [1, 1, 175, 175, 175]

BATCH_SIZE = 4
EXP_DIR = "./output/ucenje/"
DATASET_DIR = "./input/Release_06_12_23"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_train_dataset():
    return ThoraxCBCTDataset(
        data_path=os.path.join(SCRIPT_DIR, f"../{DATASET_DIR}"),
        phase="train",
        desired_shape=input_shape[2:],
        device=device,
        paired=True,
    )

def get_val_dataset():
    return ThoraxCBCTDataset(
        data_path=os.path.join(SCRIPT_DIR, f"../{DATASET_DIR}"),
        phase="val",
        desired_shape=input_shape[2:],
        device=device,
        paired=True,
    )

def augment(image_A, image_B):
    identity_list = []
    for i in range(image_A.shape[0]):
        identity = torch.zeros((1, 3, 4), device=image_A.device)
        for j in range(3):
            k = random.choice(range(3))
            identity[0, j, k] = random.choice([-1, 1])
        identity_list.append(identity)

    identity = torch.cat(identity_list)
    noise = torch.randn((image_A.shape[0], 3, 4), device=image_A.device)
    forward = identity + 0.05 * noise

    grid_shape = list(image_A.shape)
    grid_shape[1] = 3
    forward_grid = F.affine_grid(forward, grid_shape)

    warped_A = F.grid_sample(image_A, forward_grid, padding_mode='border')
    warped_B = F.grid_sample(image_B, forward_grid, padding_mode='border')

    return warped_A, warped_B

def train_kernel(optimizer, net, moving_image, fixed_image, writer, ite):
    optimizer.zero_grad()
    loss_object = net(moving_image, fixed_image)
    loss = torch.mean(loss_object.all_loss)
    loss.backward()
    optimizer.step()
    write_stats(writer, loss_object, ite, prefix="train/")

def train(
    net,
    optimizer,
    data_loader,
    val_data_loader,
    epochs=200,
    eval_period=-1,
    save_period=-1,
    step_callback=(lambda net: None),
    unwrapped_net=None,
    data_augmenter=None,
):
    from torch.utils.tensorboard import SummaryWriter

    if unwrapped_net is None:
        unwrapped_net = net

    writer = SummaryWriter(EXP_DIR + "/logs/" + datetime.now().strftime("%Y%m%d-%H%M%S"), flush_secs=30)

    iteration = 0
    for epoch in tqdm(range(epochs)):
        for moving_image, fixed_image in data_loader:
            moving_image, fixed_image = moving_image.to(device), fixed_image.to(device)
            if data_augmenter is not None:
                with torch.no_grad():
                    moving_image, fixed_image = data_augmenter(moving_image, fixed_image)
            train_kernel(optimizer, net, moving_image, fixed_image, writer, iteration)
            iteration += 1

            step_callback(unwrapped_net)

def train_two_stage(input_shape, data_loader, val_data_loader, epochs, eval_period, save_period, resume_from):
    net = make_network(input_shape, include_last_step=False)

    if resume_from:
        print("Resume from:", resume_from)
        net.regis_net.load_state_dict(torch.load(resume_from, map_location="cpu"))

    net = net.to(device)
    optimizer = torch.optim.Adam(net.parameters(), lr=0.00005)

    print("Start training.")
    train(net, optimizer, data_loader, val_data_loader, epochs[0], eval_period, save_period)

    torch.save(net.regis_net.state_dict(), EXP_DIR + "checkpoints/Step_1_final.trch")

    net_2 = make_network(input_shape, include_last_step=True)
    net_2.regis_net.netPhi.load_state_dict(net.regis_net.state_dict())

    del net
    optimizer = torch.optim.Adam(net_2.parameters(), lr=0.00005)
    net_2 = net_2.to(device)

    train(net_2, optimizer, data_loader, val_data_loader, epochs[1], eval_period, save_period)
    torch.save(net_2.regis_net.state_dict(), EXP_DIR + "checkpoints/Step_2_final.trch")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--resume_from", required=False, default="")
    args = parser.parse_args()
    resume_from = args.resume_from

    os.makedirs(EXP_DIR + "checkpoints", exist_ok=True)

    train_dataset = get_train_dataset()
    val_dataset = get_val_dataset()

    train_dataloader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4, drop_last=True)
    val_dataloader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4, drop_last=True)

    train_two_stage(input_shape, train_dataloader, val_dataloader, [801, 201], 20, 20, resume_from)