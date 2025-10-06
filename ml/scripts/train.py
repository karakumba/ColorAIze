import torch
from pathlib import Path
import logging
from torch.utils.data import DataLoader

from .dataset import ColorizationDataset
from .model_unet import UNet

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
            # Датасеты
            train_ds = ColorizationDataset(csv_path=str(csv_path), split="train", image_size=512, input_mode="L3")
            val_ds = ColorizationDataset(csv_path=str(csv_path), split="val", image_size=512, input_mode="L3")

            # Даталоадеры
            train_loader = DataLoader(train_ds, batch_size=4, shuffle=True, num_workers=0)
            val_loader = DataLoader(val_ds, batch_size=4, shuffle=False, num_workers=0)

            # Модель
            model = UNet(in_channels=3, out_channels=3).to(device)
            optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
            criterion = torch.nn.L1Loss()

            # Простейший цикл на 1 эпоху (sanity)
            model.train()
            for step, (gray, color, _) in enumerate(train_loader):
                gray = gray.to(device)
                color = color.to(device)
                optimizer.zero_grad(set_to_none=True)
                pred = model(gray)
                loss = criterion(pred, color)
                loss.backward()
                optimizer.step()
                if step % 10 == 0:
                    logger.info(f"train step={step} loss={loss.item():.4f}")

            # Сохранение чекпоинта
            ckpt_dir = Path("models")
            ckpt_dir.mkdir(exist_ok=True)
            ckpt_path = ckpt_dir / "unet_colorizer_sanity.pth"
            torch.save({"model_state": model.state_dict()}, ckpt_path)
            logger.info(f"Saved checkpoint: {ckpt_path}")

        except Exception as e:
            logger.error(f"Training loop failed: {e}")
    else:
        logger.warning(f"metadata.csv не найден: {csv_path}. Пропускаем sanity-check.")