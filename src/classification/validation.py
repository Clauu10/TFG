import argparse
import os
import glob
import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
from torchvision.datasets import ImageFolder
from torchvision import transforms
from src.utils.classes import CLASSES
from src.classification.train_cnn import get_resnet_model


def save_confusion_matrix(cm, class_names, path, title, fmt="d"):
    """
    Guarda una matriz de confusión como imagen.

    Args:
        cm (numpy.ndarray): Matriz de confusión (N x N).
        class_names (list[str]): Nombres de clase.
        path (str): Ruta de salida.
        title (str): Título de la figura.
        fmt (str): Formato de anotación ('d' o '.2f').
    """
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt=fmt, xticklabels=class_names, yticklabels=class_names, cmap="Blues")
    plt.xlabel("Predicción")
    plt.ylabel("Clase real")
    plt.title(title)
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()


def per_class_results(y_true, y_pred, class_names, red_name):
    """
    Calcula precision por clase.

    Args:
        y_true (list[str]): Etiquetas reales.
        y_pred (list[str]): Etiquetas predichas.
        class_names (list[str]): Nombres de las clases.
        red_name (str): Identificador del modelo.

    Returns:
        pandas.DataFrame: Columnas ['red', 'clase', 'accuracy'].
    """
    cm = confusion_matrix(y_true, y_pred, labels=class_names)
    accs = cm.diagonal() / cm.sum(axis=1)
    return pd.DataFrame({
        "red": red_name,
        "clase": class_names,
        "accuracy": accs
    })


class Validation:
    """
    Clase con métodos para validar un modelo de clasificación.

    Atributos:
        device (torch.device): Dispositivo (CPU o GPU).
        class_names (list[str] | None): Nombres de las clases.
        num_classes (int | None): Número de clases.
        model (torch.nn.Module | None): Modelo cargado.
        transform (callable): Transformaciones aplicadas a cada imagen de entrada.
    """

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.class_names = None
        self.num_classes = None
        self.model = None
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])


    def _setup(self, model_dir, test_dir):
        """
        Configura los archivos para la validación.

        Args:
            model_dir (str): Carpeta donde está el modelo (.pth).
            test_dir (str): Carpeta del conjunto de test.
        """
        self.test_dir = test_dir
        dataset = ImageFolder(test_dir)
        self.class_names = dataset.classes
        self.num_classes = len(self.class_names)
        self.model = self._load_model(model_dir)


    def _load_model(self, model_dir):
        """
        Carga el checkpoint más reciente de la carpeta dada y prepara el modelo.

        Args:
            model_dir (str): Carpeta con ficheros .pth.

        Returns:
            torch.nn.Module: Modelo.
        """
        modelos = glob.glob(os.path.join(model_dir, "*.pth"))
        if not modelos:
            raise FileNotFoundError("No se encontró ningún modelo en la ruta especificada.")

        modelos.sort(key=os.path.getmtime)
        modelo_reciente = modelos[-1]
        print(f"Cargando modelo: {modelo_reciente}")

        model = get_resnet_model(self.num_classes, checkpoint_path=modelo_reciente, device=self.device)
        model.to(self.device)
        model.eval()
        return model


    def predict_image(self, image_path):
        """
        Predice la clase de una imagen.

        Args:
            image_path (str): Ruta a la imagen.

        Returns:
            str: Nombre de la clase predicha.
        """
        image = Image.open(image_path).convert("RGB")
        image = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(image)
            _, predicted_class = torch.max(output, 1)
        return self.class_names[predicted_class.item()]


    def predict_image_from_tensor(self, tensor):
        """
        Predice la clase a partir de un tensor ya transformado.

        Args:
            tensor (torch.Tensor): Tensor de forma [1, C, H, W] en rango y norma esperada.

        Returns:
            int: Índice de la clase predicha.
        """
        tensor = tensor.to(self.device)
        with torch.no_grad():
            output = self.model(tensor)
            _, predicted = torch.max(output, 1)
        return predicted.item()


    def evaluate_model(self):
        """
        Evalúa el modelo a partir del test e indica aciertos por categoría y totales.
        """
        categories = sorted(os.listdir(self.test_dir))
        total_correct = 0
        total_images = 0

        for category in categories:
            category_path = os.path.join(self.test_dir, category)
            image_files = [f for f in os.listdir(category_path) if f.endswith(".jpg")]

            correct_predictions = 0
            total_category_images = len(image_files)

            if total_category_images > 0:
                for image_file in image_files:
                    image_path = os.path.join(category_path, image_file)
                    predicted_class = self.predict_image(image_path)
                    if predicted_class == category:
                        correct_predictions += 1

                print(f"Categoría: {category} - Correctas: {correct_predictions}/{total_category_images} "
                      f"({(correct_predictions / total_category_images) * 100:.2f}%)")

                total_correct += correct_predictions
                total_images += total_category_images
            else:
                print(f"No se encontraron imágenes en {category}")

        if total_images > 0:
            print("")
            print(f"Total de imágenes clasificadas: {total_images}")
            print(f"Total de aciertos: {total_correct}")
        else:
            print("No se encontraron imágenes en ninguna categoría.")


    def evaluation_metrics(self, output_dir):
        """
        Calcula métricas globales y por clase, y guarda:
        - metrics.txt con precision/recall/F1 y macro
        - confusion_matrix.png y confusion_matrix_normalized.png
        - per_class_accuracy.csv con accuracy por clase

        Args:
            output_dir (str): Carpeta donde guardar los archivos de métricas.

        Returns:
            pandas.DataFrame: DataFrame con la precisión por clase.
        """
        os.makedirs(output_dir, exist_ok=True)

        y_true, y_pred = [], []
        class_names = sorted(os.listdir(self.test_dir))

        for class_name in class_names:
            class_dir = os.path.join(self.test_dir, class_name)
            image_files = [f for f in os.listdir(class_dir) if f.endswith(".jpg")]

            for image_file in image_files:
                image_path = os.path.join(class_dir, image_file)
                predicted = self.predict_image(image_path)
                y_true.append(class_name)
                y_pred.append(predicted)

        acc = accuracy_score(y_true, y_pred)
        prec_macro = precision_score(y_true, y_pred, average="macro", zero_division=0)
        rec_macro = recall_score(y_true, y_pred, average="macro", zero_division=0)
        f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)

        print(f"Precisión global: {acc*100:.2f}%")
        metrics_path = os.path.join(output_dir, "metrics.txt")
        with open(metrics_path, "w") as f:
            f.write(f"Precisión global: {acc*100:.2f}%\n")
            f.write(f"Macro precision:  {prec_macro*100:.2f}%\n")
            f.write(f"Macro recall:     {rec_macro*100:.2f}%\n")
            f.write(f"Macro F1-score:   {f1_macro*100:.2f}%\n")
        print(f"Métricas guardadas en {metrics_path}")

        cm = confusion_matrix(y_true, y_pred, labels=class_names)
        cm_path = os.path.join(output_dir, "confusion_matrix.png")
        save_confusion_matrix(cm, class_names, cm_path, "Matriz de Confusión", fmt="d")

        cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
        cm_norm_path = os.path.join(
            output_dir, "confusion_matrix_normalized.png")
        save_confusion_matrix(cm_norm, class_names, cm_norm_path, "Matriz de Confusión Normalizada", fmt=".2f")

        print(f"Matriz de confusión guardada en {cm_path}")
        print(f"Matriz de confusión normalizada guardada en {cm_norm_path}")

        df_per_class = per_class_results(y_true, y_pred, class_names, red_name="CNN_" + str(self.num_classes) + "clases")
        csv_path = os.path.join(output_dir, "per_class_accuracy.csv")
        df_per_class.to_csv(csv_path, index=False)
        print(f"Precisión por clase guardada en {csv_path}")

        return df_per_class


if __name__ == "__main__":
    torch.backends.cudnn.benchmark = True
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    parser = argparse.ArgumentParser(description="Validación de CNN por tipo")
    parser.add_argument("--type", "-t", required=True,
                        help=f"Tipo: 'multiclase' o una de {CLASSES}")
    parser.add_argument("--metrics-dir", "-m", type=str, default=None,
                        help="Carpeta para guardar las métricas (por defecto: metrics/<type>)")
    args = parser.parse_args()

    type = args.type
    allowed = ["multiclase"] + CLASSES
    if type not in allowed:
        raise ValueError(f"Tipo '{type}' no válido. Usa uno de: {allowed}")

    classifier = Validation()

    if type == "multiclase":
        classifier._setup(
            model_dir="models/cnn_1/",
            test_dir="cnn1_archive_balanced/test"
        )
    else:
        classifier._setup(
            model_dir=f"models/cnn_2/{type}/",
            test_dir=f"cnn2_archive_balanced/{type}/test"
        )

    output_dir = args.metrics_dir or f"metrics/{type}"
    os.makedirs(output_dir, exist_ok=True)

    classifier.evaluate_model()
    df_per_class = classifier.evaluation_metrics(output_dir=output_dir)
