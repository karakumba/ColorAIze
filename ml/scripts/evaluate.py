import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def evaluate_model():
    logger.info("Model evaluation script")

    models_dir = Path("models")
    if not models_dir.exists():
        logger.error("Models directory not found")
        return

    models = list(models_dir.glob("*.pth"))
    logger.info(f"Found {len(models)} models for evaluation")


if __name__ == "__main__":
    evaluate_model()