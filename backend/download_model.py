import requests
import os
from pathlib import Path


def download_model():
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    model_url = "https://github.com/jantic/DeOldify/releases/download/v1.0/ColorizeArtistic_gen.pth"
    model_path = models_dir / "ColorizeArtistic_gen.pth"

    if model_path.exists():
        print("Model already exists")
        return

    print("Downloading model...")
    response = requests.get(model_url, stream=True)
    response.raise_for_status()

    with open(model_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print("Model downloaded successfully")


if __name__ == "__main__":
    download_model()