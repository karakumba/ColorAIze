"""
Скачивание COCO 2017 val (≈5k изображений ~1GB) и подготовка metadata.csv без хранения ч/б копий.

Что делает скрипт:
- скачивает и распаковывает COCO val2017 (JPEG)
- опционально: берёт подмножество из первых N файлов
- кладёт в data/raw/val (а train можно сформировать как большую часть, val — хвост)
- формирует ml/data/metadata.csv, где gray_path оставляем пустым (Dataset сгенерит L на лету)
"""

import zipfile
from pathlib import Path
import urllib.request
import csv


COCO_VAL_URL = "http://images.cocodataset.org/zips/val2017.zip"


def download(url: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"Exists: {dest}")
        return
    print(f"Downloading: {url}")
    urllib.request.urlretrieve(url, dest)
    print(f"Saved: {dest}")


def unzip(zip_path: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(out_dir)
    print(f"Extracted to: {out_dir}")


def build_metadata_from_folder(color_dir: Path, subset_size: int = 5000, split_ratio: float = 0.9):
    """Создаёт metadata.csv: gray_path пустой (генерим на лету), color_path указывает на val.

    split_ratio=0.9 означает ~90% строк пойдут в train, остаток — в val.
    """
    images = sorted(list(color_dir.glob("*.jpg")))
    if subset_size:
        images = images[:subset_size]
    n_train = int(len(images) * split_ratio)

    rows = []
    for i, color_path in enumerate(images):
        split = "train" if i < n_train else "val"
        # Путь в CSV должен быть относительно корня ml/
        rel_color = color_path.relative_to(Path.cwd()) if color_path.is_absolute() else color_path
        rows.append((
            "",  # gray_path пустой → Dataset генерирует L на лету
            str(rel_color).replace("\\", "/"),
            split,
            512,
            512,
        ))

    meta = Path("ml/data/metadata.csv")
    meta.parent.mkdir(parents=True, exist_ok=True)
    with meta.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["gray_path","color_path","split","height","width"])
        for r in rows:
            w.writerow(r)
    print(f"Wrote: {meta}, rows={len(rows)} train~{n_train} val~{len(rows)-n_train}")


def main():
    root = Path("ml")
    downloads = root / "downloads"
    raw_val = root / "data" / "raw" / "val"

    # 1) Скачиваем val2017.zip
    zip_path = downloads / "val2017.zip"
    download(COCO_VAL_URL, zip_path)

    # 2) Распаковываем
    unzip(zip_path, downloads)

    # 3) Переносим jpeg в ml/data/raw/val
    coco_val_dir = downloads / "val2017"
    raw_val.mkdir(parents=True, exist_ok=True)
    for img in coco_val_dir.glob("*.jpg"):
        target = raw_val / img.name
        if not target.exists():
            img.replace(target)

    # 4) Формируем metadata.csv (по умолчанию весь val → train/val по split_ratio)
    build_metadata_from_folder(raw_val, subset_size=5000, split_ratio=0.9)


if __name__ == "__main__":
    main()


