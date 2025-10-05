import requests
import os
from pathlib import Path


def download_file(url, filename):
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Downloaded: {filename}")


def main():
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    model_urls = {
        "ColorizeArtistic_gen.pth": "https://github.com/jantic/DeOldify/releases/download/v1.0/ColorizeArtistic_gen.pth",
    }

    for filename, url in model_urls.items():
        filepath = models_dir / filename
        if not filepath.exists():
            download_file(url, filepath)
        else:
            print(f"Model already exists: {filename}")


if __name__ == "__main__":
    main()