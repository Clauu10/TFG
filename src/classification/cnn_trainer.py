import os
import datetime
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F


class FocalLoss(nn.Module):
    """
    Implementación de Focal Loss para la clasificación.

    Args:
        alpha (torch.Tensor | None): Ponderaciones por clase: mismo tamaño que el nº de clases o None.
        gamma (float): Controla cuánto se reduce la pérdida de ejemplos fáciles.
        reduction (str): Tipo de reducción a aplicar: "mean", "sum" o "none".
    """
    def __init__(self, alpha=None, gamma=2.0, reduction="mean"):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction


    def forward(self, logits, target):
        """
        Calcula la Focal Loss.

        Args:
            logits (torch.Tensor): Logits sin normalizar de forma [batch, num_classes].
            target (torch.Tensor): Etiquetas verdaderas de forma [batch], con índices de clase.

        Returns:
            torch.Tensor: Escalar o tensor por elemento con la pérdida.
        """
        ce = F.cross_entropy(logits, target, weight=self.alpha, reduction="none")
        pt = torch.exp(-ce)
        loss = (1 - pt) ** self.gamma * ce
        
        if self.reduction == "mean":
            return loss.mean()
        elif self.reduction == "sum":
            return loss.sum()
        return loss


def train_model(model, device, train_loader, test_loader, class_weights, output_dir, type, epochs=100, lr=0.001, patience=10):
    """
    Entrena un modelo con Focal Loss y early stopping.

    Args:
        model (nn.Module): Modelo a entrenar.
        device (torch.device): Dispositivo (CPU o GPU).
        train_loader (torch.utils.data.DataLoader): Cargador de datos de entrenamiento.
        test_loader (torch.utils.data.DataLoader): Cargador de datos de test.
        class_weights (torch.Tensor): Pesos por clase.
        output_dir (str): Carpeta de salida.
        type (str): Tipo de modelo.
        epochs (int): Máximo de épocas de entrenamiento.
        lr (float): Tasa de aprendizaje.
        patience (int): Número de épocas sin mejora antes de activar early stopping.
    """
    class_weights = class_weights.clone()

    criterion = FocalLoss(alpha=class_weights, gamma=1.5)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

    best_accuracy = 0.0
    epochs_no_improve = 0

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        avg_loss = running_loss / len(train_loader)
        print(f"\nEpoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")

        accuracy = evaluate_model(model, device, test_loader)

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            print(f"Sin mejora por {epochs_no_improve}/{patience} epochs.")
            if epochs_no_improve >= patience:
                print("Early stopping.")
                break

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    torch.save(model.state_dict(), os.path.join(output_dir, f"modelo_{type}_{timestamp}.pth"))
    print("Entrenamiento completado.")


def evaluate_model(model, device, test_loader):
    """
    Evalúa la precisión del modelo sobre el conjunto de test.

    Args:
        model (nn.Module): Modelo ya entrenado a evaluar.
        device (torch.device): Dispositivo (CPU o GPU).
        test_loader (torch.utils.data.DataLoader): Cargador del conjunto de test.

    Returns:
        float: Precisión del modelo en porcentaje.
    """
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total
    print(f"Precisión en test: {accuracy:.2f}%")
    return accuracy
