import os
import torch
import time
from loguru import logger
from PIL import Image
import io


class ImageColorizer:
    def __init__(self):
        self.model = None
        # DEVICE override via env (cpu/cuda), fallback to auto-detect
        device_env = os.getenv("DEVICE")
        if device_env in {"cpu", "cuda"}:
            self.device = torch.device(device_env)
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Render factor from env, default 35
        try:
            self.render_factor = int(os.getenv("RENDER_FACTOR", "35"))
        except ValueError:
            self.render_factor = 35

        logger.info(f"Using device: {self.device}, render_factor={self.render_factor}")
        self.load_model()

    def load_model(self):
        try:
            # DeOldify searches weights in local ./models by default (fastai convention)
            # Our Dockerfile ensures models/ColorizeArtistic_gen.pth is present.
            from deoldify.visualize import get_image_colorizer
            logger.info("Loading DeOldify model (artistic)...")
            self.model = get_image_colorizer(artistic=True)
            logger.info("✅ DeOldify model loaded successfully")
        except ImportError as e:
            logger.error(f"DeOldify not available: {e}")
            self.model = None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None

    def colorize(self, image_bytes: bytes, filename: str) -> str:
        try:
            if self.model is None:
                return self._mock_colorize(image_bytes, filename)

            file_ext = os.path.splitext(filename)[1] or '.jpg'
            output_filename = f"colorized_{int(time.time())}{file_ext}"
            output_path = os.path.join('storage/processed', output_filename)

            temp_input_path = os.path.join('storage/uploads', f"temp_{output_filename}")
            os.makedirs('storage/uploads', exist_ok=True)
            os.makedirs('storage/processed', exist_ok=True)

            with open(temp_input_path, "wb") as f:
                f.write(image_bytes)

            result_image = self.model.get_transformed_image(path=temp_input_path, render_factor=self.render_factor)
            result_image.save(output_path, quality=95)

            os.remove(temp_input_path)
            logger.info(f"Colorization completed: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Colorization error: {e}")
            return self._mock_colorize(image_bytes, filename)

    def _mock_colorize(self, image_bytes: bytes, filename: str) -> str:
        logger.info("Using mock colorization mode")
        file_ext = os.path.splitext(filename)[1] or '.jpg'
        output_filename = f"mock_{int(time.time())}{file_ext}"
        output_path = os.path.join('storage/processed', output_filename)

        os.makedirs('storage/processed', exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(image_bytes)

        time.sleep(2)
        return output_path

    def is_model_loaded(self) -> bool:
        return self.model is not None