import os
import numpy as np
import torch
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision.datasets import ImageFolder
from sklearn.utils.class_weight import compute_class_weight


def load_datasets(data_path, transforms_train, transforms_test, batch_size=32):
    """
    Carga los datasets de entrenamiento y test desde carpetas
    y aplica transformaciones.

    Args:
        data_path (str): Ruta base con las carpetas "train" y "test".
        transform: Transformaciones a aplicar a las imágenes.
        batch_size (int): Tamaño del batch.

    Returns:
        tuple:
            - train_loader (DataLoader): DataLoader para el entrenamiento.
            - test_loader (DataLoader): DataLoader para la evaluación.
            - num_classes (int): Número total de clases.
            - train_dataset (Dataset): Dataset de entrenamiento.
    """
    train_dataset = ImageFolder(os.path.join(data_path, "train"), transform=transforms_train)
    test_dataset = ImageFolder(os.path.join(data_path, "test"), transform=transforms_test)

    targets = [label for _, label in train_dataset.samples]
    class_sample_count = np.bincount(targets)
    weights = 1. / class_sample_count
    sample_weights = [weights[t] for t in targets]

    sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights), replacement=True)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, sampler=sampler, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=2)

    num_classes = len(train_dataset.classes)
    print(f"Clases detectadas en '{data_path}': {num_classes}")

    return train_loader, test_loader, num_classes, train_dataset


def get_class_weights(train_dataset, device):
    """
    Calcula los pesos de cada clase a partir del conjunto de entrenamiento
    para corregir el desbalance durante el entrenamiento del modelo.

    Args:
        train_dataset (torch.utils.data.Dataset): Dataset de entrenamiento.
        device (torch.device): Dispositivo (CPU o GPU).

    Returns:
        torch.Tensor: Tensor con los pesos por clase.
    """
    labels = [label for _, label in train_dataset.samples]

    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(labels),
        y=labels
    )

    return torch.tensor(class_weights, dtype=torch.float).to(device)
