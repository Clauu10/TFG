import os
import shutil
from src.utils.organizer import group_by_class, group_by_subclass
from src.utils.balancer import balance_dataset
from src.utils.classes import CLASSES, SUBCLASSES


def prepare_dataset():
    """
    Organiza y balancea los datasets para la clasificación.

    1) Agrupa por clases (cnn1_archive_balanced)
    2) Agrupa por subclases (cnn2_archive_balanced).
    3) Balancea el dataset de clases.
    4) Balancea datasets de subclases.
    """
    group_by_class(
        input_base_dir="archive/Warp-C",
        output_base_dir="cnn1_archive",
        splits=["train", "test"],
    )

    group_by_subclass(
        input_base_dir="archive/Warp-C",
        output_base_dir="cnn2_archive",
        splits=["train", "test"],
    )

    balance_dataset(
        train_input_dir="cnn1_archive/train",
        train_output_dir="cnn1_archive_balanced/train",
        test_input_dir="cnn1_archive/test",
        test_output_dir="cnn1_archive_balanced/test",
        classes=CLASSES,
        special_class="plastic",
        max_images=1000,
    )

    balance_dataset(
        train_input_dir="cnn2_archive/plastic/train",
        train_output_dir="cnn2_archive_balanced/plastic/train",
        test_input_dir="cnn2_archive/plastic/test",
        test_output_dir="cnn2_archive_balanced/plastic/test",
        classes=SUBCLASSES["plastic"],
        max_images=450,
    )

    balance_dataset(
        train_input_dir="cnn2_archive/detergent/train",
        train_output_dir="cnn2_archive_balanced/detergent/train",
        test_input_dir="cnn2_archive/detergent/test",
        test_output_dir="cnn2_archive_balanced/detergent/test",
        classes=SUBCLASSES["detergent"],
        max_images=400,
    )

    balance_dataset(
        train_input_dir="cnn2_archive/cardboard/train",
        train_output_dir="cnn2_archive_balanced/cardboard/train",
        test_input_dir="cnn2_archive/cardboard/test",
        test_output_dir="cnn2_archive_balanced/cardboard/test",
        classes=SUBCLASSES["cardboard"],
        max_images=400,
    )

    balance_dataset(
        train_input_dir="cnn2_archive/glass/train",
        train_output_dir="cnn2_archive_balanced/glass/train",
        test_input_dir="cnn2_archive/glass/test",
        test_output_dir="cnn2_archive_balanced/glass/test",
        classes=SUBCLASSES["glass"],
        max_images=170,
    )

    for folder in ["cnn1_archive", "cnn2_archive"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)


if __name__ == "__main__":
    prepare_dataset()
