import logging
from pathlib import Path
import torch
import torchvision
from math import log10

from .dataset import ColorizationDataset
from .model_unet import UNet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def psnr(pred: torch.Tensor, target: torch.Tensor) -> float:
    """PSNR по батчу (среднее), вход в [0,1]."""
    mse = torch.mean((pred - target) ** 2, dim=[1, 2, 3]) + 1e-8
    psnr_vals = 10 * torch.log10(1.0 / mse)
    return psnr_vals.mean().item()


def ssim(pred: torch.Tensor, target: torch.Tensor) -> float:
    """Простейшая SSIM через torchvision (approx)."""
    return torchvision.metrics.structural_similarity_index_measure(pred, target).item()


def evaluate_model():
    logger.info("Model evaluation script")

    ckpt_path = Path("models/unet_colorizer_sanity.pth")
    if not ckpt_path.exists():
        logger.error(f"Checkpoint not found: {ckpt_path}")
        return

    csv_path = Path("data/metadata.csv")
    if not csv_path.exists():
        logger.error(f"CSV not found: {csv_path}")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    val_ds = ColorizationDataset(csv_path=str(csv_path), split="val", image_size=512, input_mode="L3")
    val_loader = torch.utils.data.DataLoader(val_ds, batch_size=4, shuffle=False, num_workers=0)

    model = UNet(in_channels=3, out_channels=3).to(device)
    state = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(state["model_state"])    
    model.eval()

    psnr_vals = []
    ssim_vals = []
    with torch.no_grad():
        for gray, color, _ in val_loader:
            gray = gray.to(device)
            color = color.to(device)
            pred = model(gray)
            psnr_vals.append(psnr(pred, color))
            ssim_vals.append(ssim(pred, color))

    if psnr_vals and ssim_vals:
        logger.info(f"PSNR(среднее)={sum(psnr_vals)/len(psnr_vals):.2f} dB")
        logger.info(f"SSIM(среднее)={sum(ssim_vals)/len(ssim_vals):.3f}")
    else:
        logger.warning("Нет данных для метрик (проверьте CSV и val split)")


if __name__ == "__main__":
    evaluate_model()