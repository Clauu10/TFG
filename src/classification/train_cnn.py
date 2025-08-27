import argparse
import torch
import torch.nn as nn
from torchvision import models
from src.utils.classes import CLASSES
from src.utils.tranforms import TRANSFORMS_CONFIG
from src.classification.training_data import load_datasets, get_class_weights
from src.classification.cnn_trainer import train_model


def get_resnet_model(num_classes, checkpoint_path=None, device="cpu"):
    """
    Crea un modelo ResNet18 con una nueva capa 
    totalmente conectada adaptada al número de clases.

    Args:
        num_classes (int): Número de clases de salida.
        checkpoint_path (str): Ruta al modelo (.pth) para cargar pesos preentrenados.
        device (str): Dispositivo donde mapear los pesos del checkpoint ("cpu" o "cuda").

    Returns:
        torch.nn.Module: Modelo ResNet-18 con la cabeza personalizada.
    """
    model = models.resnet18(weights="IMAGENET1K_V1")
    in_features = model.fc.in_features

    with_bn_head = False
    if checkpoint_path and torch.cuda.is_available():
        state_dict = torch.load(checkpoint_path, map_location=device, weights_only=True)
        if any(k.startswith("fc.1.") for k in state_dict.keys()):
            with_bn_head = True

    if with_bn_head:
        model.fc = nn.Sequential(
            nn.Linear(in_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
    else:
        model.fc = nn.Sequential(
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )

    if checkpoint_path:
        model.load_state_dict(torch.load(checkpoint_path, map_location=device, weights_only=True))

    return model


def _run(type, batch_size, epochs, lr, device):
    """
    Ejecuta un entrenamiento completo para una clase del dataset.

    Args:
        type (str): Tipo a entrenar ("multiclase" o una de CLASSES).
        batch_size (int): Tamaño de batch.
        epochs (int): Número de épocas de entrenamiento.
        lr (float): Tasa de aprendizaje.
        device (torch.device): Dispositivo (CPU o GPU).
    """
    print(f"\nEntrenando modelo ResNet para '{type}'...")

    if type == "multiclase":
        data_path = "cnn1_archive_balanced"
        output_dir = "models/cnn_1"
    else:
        data_path = f"cnn2_archive_balanced/{type}"
        output_dir = f"models/cnn_2/{type}"

    transforms_train = TRANSFORMS_CONFIG[type]["train"]
    transforms_test  = TRANSFORMS_CONFIG[type]["test"]

    train_loader, test_loader, num_classes, train_dataset = load_datasets(
        data_path,
        batch_size=batch_size,
        transforms_train=transforms_train,
        transforms_test=transforms_test
    )

    model = get_resnet_model(num_classes, checkpoint_path=None, device=str(device)).to(device)
    class_weights = get_class_weights(train_dataset, device)

    train_model(
        model, device, train_loader, test_loader, class_weights,
        output_dir, type=type, epochs=epochs, lr=lr, patience=15
    )


if __name__ == "__main__":
    torch.backends.cudnn.benchmark = True
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    parser = argparse.ArgumentParser(description="Entrenamiento CNN por tipo")
    parser.add_argument("--type", "-t", required=True, 
                        help=f"Tipo: 'multiclase' o una de {CLASSES}")
    parser.add_argument("--batch-size", "-b", type=int, default=32)
    parser.add_argument("--epochs", "-e", type=int, default=100)
    parser.add_argument("--lr", "-l", type=float, default=1e-4)
    args = parser.parse_args()

    allowed = ["multiclase"] + CLASSES
    if args.type not in allowed:
        raise ValueError(f"Tipo '{args.type}' no válido. Usa uno de: {allowed}")

    _run(args.type, args.batch_size, args.epochs, args.lr, device)