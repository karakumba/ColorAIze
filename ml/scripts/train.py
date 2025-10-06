import torch
from pathlib import Path
import logging
from torch.utils.data import DataLoader

from .dataset import ColorizationDataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_training():
    logger.info("Setting up training environment")

    # Check for GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")

    # Create directories
    Path("models").mkdir(exist_ok=True)
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)

    return device


if __name__ == "__main__":
    device = setup_training()
    logger.info("Training setup completed")

    # Пробный DataLoader для sanity-check
    csv_path = Path(__file__).resolve().parents[1] / "data" / "metadata.csv"
    if csv_path.exists():
        try:
            train_ds = ColorizationDataset(csv_path=str(csv_path), split="train", image_size=512, input_mode="L3")
            train_loader = DataLoader(train_ds, batch_size=2, shuffle=True, num_workers=0)
            batch = next(iter(train_loader))
            gray, color, paths = batch
            logger.info(f"Sanity-check batch: gray={tuple(gray.shape)}, color={tuple(color.shape)}, n={len(paths)}")
        except Exception as e:
            logger.error(f"Sanity-check DataLoader failed: {e}")
    else:
        logger.warning(f"metadata.csv не найден: {csv_path}. Пропускаем sanity-check.")