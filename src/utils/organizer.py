import os
import shutil
from src.utils.classes import SUBCLASSES


def group_by_class(input_base_dir, output_base_dir, splits):
    """
    Reorganiza las imágenes desde carpetas de subclases a carpetas por clase.

    Args:
        input_base_dir (str): Carpeta con imágenes organizadas por subclase.
        output_base_dir (str): Carpeta destino con la organización por clases.
        splits (list): Lista de conjuntos (train, test).
    """
    for split in splits:
        for general_class in SUBCLASSES:
            os.makedirs(os.path.join(output_base_dir, split, general_class), exist_ok=True)

    for split in splits:
        for general_class, specific_classes in SUBCLASSES.items():
            for specific_class in specific_classes:
                input_dir = os.path.join(input_base_dir, split, specific_class)
                output_dir = os.path.join(output_base_dir, split, general_class)

                if not os.path.exists(input_dir):
                    continue

                for img_file in os.listdir(input_dir):
                    if not img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        continue

                    new_name = f"{specific_class}_{img_file}"
                    src = os.path.join(input_dir, img_file)
                    dst = os.path.join(output_dir, new_name)
                    shutil.copy2(src, dst)


def group_by_subclass(input_base_dir, output_base_dir, splits):
    """
    Reorganiza las imágenes desde carpetas de clases a carpetas por subclase.

    Args:
        input_base_dir (str): Carpeta con imágenes organizadas por clase.
        output_base_dir (str): Carpeta destino con la organización por subclases.
        splits (list): Lista de conjuntos (train, test).
    """
    for general_class, subclasses in SUBCLASSES.items():
        for split in splits:
            for subclass in subclasses:
                os.makedirs(os.path.join(output_base_dir, general_class, split, subclass), exist_ok=True)

    for split in splits:
        for general_class, subclasses in SUBCLASSES.items():
            for subclass in subclasses:
                src_dir = os.path.join(input_base_dir, split, subclass)
                dst_dir = os.path.join(output_base_dir, general_class, split, subclass)

                if not os.path.isdir(src_dir):
                    continue

                for file_name in os.listdir(src_dir):
                    src = os.path.join(src_dir, file_name)
                    dst = os.path.join(dst_dir, file_name)
                    shutil.copy2(src, dst)
