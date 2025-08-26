import os
import random
import shutil
from PIL import Image
from torchvision import transforms


augmentations = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.Resize((224, 224))
])

def balance_dataset(train_input_dir, train_output_dir, test_input_dir, test_output_dir, classes, max_images, special_class=None):
    """
    Crea un conjunto balanceado para el entrenamiento y copia el conjunto de test. 

    Args:
        train_input_dir (str): Carpeta de entrada del conjunto de entrenamiento.
        train_output_dir (str): Carpeta de salida para el conjunto de entrenamiento balanceado.
        test_input_dir (str): Carpeta de entrada del conjunto de test.
        test_output_dir (str): Carpeta de salida para el conjunto de test.
        classes (list[str]): Lista de clases a procesar.
        max_images (int): Máximo de imágenes por clase.
        special_class (str | None): Clase que tendrá un número máximo de imágenes diferente.
    """
    os.makedirs(train_output_dir, exist_ok=True)
    os.makedirs(test_output_dir, exist_ok=True)

    for cls in classes:
        _process_class_train(train_input_dir, train_output_dir, cls, special_class, max_images)
        _process_class_test(test_input_dir, test_output_dir, cls)


def _process_class_train(input_dir, output_dir, cls, special_class, max_images):
    """
    Balancea el conjunto de entrenamiento de una clase.

    Args:
        input_dir (str): Carpeta de entrada del conjunto de entrenamiento.
        output_dir (str): Carpeta de salida del conjunto de entrenamiento balanceado.
        cls (str): Nombre de la clase a procesar.
        special_class (str | None): Clase con límite especial de imágenes.
        max_images (int): Límite de imágenes para las demás clases.
    """
    src_dir = os.path.join(input_dir, cls)
    dst_dir = os.path.join(output_dir, cls)
    os.makedirs(dst_dir, exist_ok=True)

    for f in os.listdir(dst_dir):
        fp = os.path.join(dst_dir, f)
        if os.path.isfile(fp) and f.lower().endswith(('.jpg', '.jpeg', '.png')):
            os.remove(fp)

    if not os.path.isdir(src_dir):
        return

    images = [f for f in os.listdir(src_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not images:
        return

    target_max = 2000 if cls == special_class else max_images

    if len(images) > target_max:
        images = random.sample(images, target_max)

    for i, img_name in enumerate(images):
        try:
            img_path = os.path.join(src_dir, img_name)
            image = Image.open(img_path).convert("RGB")
            image.resize((224, 224)).save(os.path.join(dst_dir, f"{i}_orig.jpg"))

        except Exception:
            continue

    needed = target_max - len(images)
    for i in range(needed):
        try:
            img_name = random.choice(images)
            img_path = os.path.join(src_dir, img_name)
            image = Image.open(img_path).convert("RGB")
            aug_img = augmentations(image)
            aug_img.save(os.path.join(dst_dir, f"aug_{i}.jpg"))

        except Exception:
            continue


def _process_class_test(input_dir, output_dir, cls):
    """
    Copia las imágenes de test de una clase de la carpeta de entrada 
    a la carpeta de salida, manteniendo la estructura de clases.

     Args:
        input_dir (str): Carpeta de entrada.
        output_dir (str): Carpeta destino.
        cls (str): Nombre de la clase a procesar.
    """
    src_dir = os.path.join(input_dir, cls)
    dst_dir = os.path.join(output_dir, cls)
    os.makedirs(dst_dir, exist_ok=True)

    images = [f for f in os.listdir(src_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    for img_name in images:
        shutil.copy2(os.path.join(src_dir, img_name), os.path.join(dst_dir, img_name))
