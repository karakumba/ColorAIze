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


def try_download_with_fallbacks(filename: str, dest: Path):
    """Пробуем несколько источников скачивания весов.

    Если все источники недоступны, выводим понятное сообщение и выходим без ошибки
    (инференс DeOldify сможет подтянуть веса самостоятельно при первом запуске,
    если будет доступ в интернет).
    """
    # Список возможных зеркал. Первый — исторический релиз, далее — альтернативы.
    candidate_urls = [
        "https://github.com/jantic/DeOldify/releases/download/v1.0/ColorizeArtistic_gen.pth",
        # Зеркала/альтернативы можно дополнять по мере необходимости:
        # Пример: зеркальный хостинг или артефакты вашей команды/облака.
        # "https://your-mirror.example.com/deoldify/ColorizeArtistic_gen.pth",
    ]

    for url in candidate_urls:
        try:
            print(f"Trying: {url}")
            download_file(url, dest)
            return
        except requests.HTTPError as e:
            print(f"Failed: {e}")
        except Exception as e:
            print(f"Failed: {e}")

    print("Не удалось скачать веса ни из одного источника. Пропускаем скачивание.")
    print("DeOldify попытается загрузить веса автоматически при первом запуске, если есть интернет.")


def main():
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    filename = "ColorizeArtistic_gen.pth"
    filepath = models_dir / filename
    if filepath.exists():
        print("Model already exists: ColorizeArtistic_gen.pth")
        return

    try_download_with_fallbacks(filename, filepath)


if __name__ == "__main__":
    main()