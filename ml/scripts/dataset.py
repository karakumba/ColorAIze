import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

from PIL import Image
import torch
from torch.utils.data import Dataset
import torchvision.transforms as T


@dataclass
class SampleRecord:
    """Описание одной пары путей для задачи колоризации.

    Ожидается CSV с колонками: gray_path,color_path,split,height,width
    Пути могут быть относительными от корня каталога ml/ (рекомендуется).
    """

    gray_path: Path
    color_path: Path
    split: str
    height: Optional[int] = None
    width: Optional[int] = None


def _build_transforms(is_train: bool, image_size: int = 512) -> T.Compose:
    """Формируем пайплайн препроцессинга/аугментаций.

    - Resize по длинной стороне до image_size
    - Центр-кроп image_size×image_size
    - Для train: горизонтальный флип p=0.5
    - Преобразование в тензор и нормализация в [0,1]
    """

    resize = T.Resize(image_size)
    center_crop = T.CenterCrop(image_size)

    ops: List[torch.nn.Module] = [
        T.Lambda(lambda img: _resize_long_side(img, image_size)),
        center_crop,
    ]

    if is_train:
        ops.append(T.RandomHorizontalFlip(p=0.5))

    ops.extend([
        T.ToTensor(),  # превращает в [0,1]
    ])

    return T.Compose(ops)


def _resize_long_side(img: Image.Image, target_long_side: int) -> Image.Image:
    """Меняет размер так, чтобы длинная сторона стала target_long_side, сохраняя пропорции."""
    w, h = img.size
    if w >= h:
        new_w = target_long_side
        new_h = int(h * (target_long_side / w))
    else:
        new_h = target_long_side
        new_w = int(w * (target_long_side / h))
    return img.resize((new_w, new_h), Image.BICUBIC)


class ColorizationDataset(Dataset):
    """Dataset для пар: вход (grayscale) → цель (color RGB).

    Параметры:
    - csv_path: путь к CSV с колонками gray_path,color_path,split,height,width
    - split: "train" | "val" | "test"
    - image_size: целевой размер по короткой стороне после кропа (квадрат)
    - input_mode: "L3" — вход как 3 одинаковых канала из gray; "L1" — один канал
    """

    def __init__(self, csv_path: str, split: str = "train", image_size: int = 512, input_mode: str = "L3"):
        self.csv_path = Path(csv_path)
        self.root_dir = self.csv_path.parent.parent  # предполагаем, что пути в CSV от корня ml/
        self.split = split
        self.image_size = image_size
        self.input_mode = input_mode

        self.records: List[SampleRecord] = self._read_csv()
        self.transform_train = _build_transforms(is_train=True, image_size=image_size)
        self.transform_eval = _build_transforms(is_train=False, image_size=image_size)

    def _read_csv(self) -> List[SampleRecord]:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV не найден: {self.csv_path}")

        items: List[SampleRecord] = []
        with self.csv_path.open("r", newline="") as f:
            reader = csv.DictReader(f)
            required_cols = {"gray_path", "color_path", "split"}
            if not required_cols.issubset(reader.fieldnames or {}):
                raise ValueError(f"CSV должен содержать колонки: {sorted(required_cols)}")

            for row in reader:
                if row.get("split") != self.split:
                    continue
                gray = (self.root_dir / row["gray_path"]).resolve()
                color = (self.root_dir / row["color_path"]).resolve()
                h = int(row.get("height")) if row.get("height") else None
                w = int(row.get("width")) if row.get("width") else None

                if not gray.exists() or not color.exists():
                    # Пропускаем битые записи
                    continue

                items.append(SampleRecord(gray, color, self.split, h, w))

        if not items:
            raise ValueError(f"В CSV для split='{self.split}' не найдено валидных записей")

        return items

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, str]:
        rec = self.records[idx]

        # Загружаем целевое цветное изображение
        color_img = Image.open(rec.color_path).convert("RGB")
        # Если путь к серому отсутствует или файла нет — генерируем L из color (экономия диска)
        if rec.gray_path and Path(rec.gray_path).exists():
            gray_img = Image.open(rec.gray_path).convert("L")
        else:
            gray_img = color_img.convert("L")

        # Выбираем набор трансформаций
        transform = self.transform_train if self.split == "train" else self.transform_eval

        # Применяем к целевому RGB
        color_tensor: torch.Tensor = transform(color_img)

        # Для входа: либо один канал, либо продублированный в 3 канала
        if self.input_mode == "L1":
            gray_tensor: torch.Tensor = transform(gray_img)  # shape: 1xHxW
        else:
            # Превращаем L → 3 канала копированием
            gray_rgb = Image.merge("RGB", (gray_img, gray_img, gray_img))
            gray_tensor = transform(gray_rgb)  # shape: 3xHxW

        return gray_tensor, color_tensor, str(rec.gray_path)


