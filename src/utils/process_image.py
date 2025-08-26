import os
import cv2
import torch
from PIL import Image
from torchvision import transforms
from ultralytics import YOLO
import pandas as pd
from datetime import datetime
from src.classification.validation import get_resnet_model
from src.utils.classes import CLASSES, SUBCLASSES


class ImageProcessor:
    """
    Procesador principal: detecta objetos con YOLO y los clasifica (categoría/subcategoría).

    Attributes:
        device (torch.device): Dispositivo (CPU o GPU).
        yolo_model (YOLO): Modelo YOLO para detección de objetos.
        cnn1 (torch.nn.Module): Clasificador de categorías.
        transform (torchvision.transforms.Compose): Transformaciones de entrada para las CNN.
    """
      
    CNN2_PATHS = {
        "plastic": "models/cnn_2/plastic/modelo_plastic_20250817_002837.pth",
        "glass": "models/cnn_2/glass/model_glass_20250808_000648.pth",
        "cardboard": "models/cnn_2/cardboard/modelo_cardboard_20250815_145417.pth",
        "detergent": "models/cnn_2/detergent/modelo_detergent_20250808_003450.pth",
    }

    def __init__(self, yolo_model_path, cnn1_model_path, device=None):
        """
        Inicializa los modelos y las transformaciones.

        Args:
            yolo_model_path (str): Ruta al archivo del modelo YOLO.
            cnn1_model_path (str): Ruta al modelo del clasificador de categorías.
            device (torch.device | None): Dispositivo (CPU o GPU).
        """
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.yolo_model = YOLO(yolo_model_path)

        self.cnn1 = get_resnet_model(
            num_classes=len(CLASSES),
            checkpoint_path=cnn1_model_path,
            device=self.device
        )
        self.cnn1.to(self.device).eval()

        self.cnn1.load_state_dict(torch.load(cnn1_model_path, map_location=self.device))
        self.cnn1.to(self.device).eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.RandomResizedCrop(224, scale=(0.9, 1.1)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                std=[0.229, 0.224, 0.225])
        ])


    def load_subclassifier(self, category):
        """
        Carga el clasificador de subcategorías para una categoría determinada.

        Args:
            category (str): Categoría principal ('plastic', 'glass', 'cardboard', 'detergent', 'cans').

        Returns:
            torch.nn.Module | None: Modelo de subclasificación para la categoría,
            o None si la categoría no requiere subclasificador ('cans').
        """
        if category == "cans":
            return None

        checkpoint = self.CNN2_PATHS[category]
        model = get_resnet_model(
            num_classes=len(SUBCLASSES[category]),
            checkpoint_path=checkpoint,
            device=self.device
        )
        model.to(self.device).eval()
        return model
    

    def process_image(self, image_path):
        """
        Detecta objetos en una imagen del disco, clasifica cada recorte y guarda resultados.

        Args:
            image_path (str): Ruta a la imagen a procesar.

        Returns:
            None
        """
        image_bgr = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results = self.yolo_model(image_rgb, conf=0.2, iou=0.5)

        boxes = results[0].boxes.xyxy.cpu().numpy()
        confidences = results[0].boxes.conf.cpu().numpy()

        for i, (box, conf) in enumerate(zip(boxes, confidences)):
            if conf < 0.4:
                continue

            x1, y1, x2, y2 = map(int, box)
            cropped = image_rgb[y1:y2, x1:x2]
            pil_image = Image.fromarray(cropped)

            category, subcategory = self.process_cropped_image(pil_image)
            self.save_result(image_path, i + 1, category, subcategory)


    def process_cropped_image(self, pil_image):
        """
        Clasifica un recorte de imagenprimero en categoría y luego en subcategoría.

        Args:
            pil_image (PIL.Image.Image): Imagen recortada del objeto en formato PIL.

        Returns:
            tuple[str, str]: (categoria, subcategoria) predichas.
        """
        input_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.cnn1(input_tensor)
            category_idx = torch.argmax(output).item()
            category = CLASSES[category_idx]

        submodel = self.load_subclassifier(category)
        if submodel is None:
            return category, "cans"

        with torch.no_grad():
            sub_output = submodel(input_tensor)
            sub_idx = torch.argmax(sub_output).item()
            subclass_names = SUBCLASSES[category]
            subcategory = subclass_names[sub_idx] if sub_idx < len(subclass_names) else f"Clase {sub_idx}"

        return category, subcategory
    

    def process_frame(self, frame_rgb):
        """
        Detecta objetos en un frame RGB, clasifica los recortes y devuelve las detecciones.

        Args:
            frame_rgb (numpy.ndarray): Frame en formato RGB.

        Returns:
            list[tuple]: Lista de detecciones en forma (box, conf, category, subcategory),
                         donde 'box' es (x1, y1, x2, y2) en coordenadas de píxel y 'conf' es float.
        """
        results = self.yolo_model(frame_rgb)

        boxes = results[0].boxes.xyxy.cpu().numpy()
        confidences = results[0].boxes.conf.cpu().numpy()

        detections = []
        for i, (box, conf) in enumerate(zip(boxes, confidences)):
            if conf < 0.4:
                continue

            x1, y1, x2, y2 = map(int, box)
            cropped = frame_rgb[y1:y2, x1:x2]
            pil_image = Image.fromarray(cropped)
            category, subcategory = self.process_cropped_image(pil_image)

            detections.append((box, conf, category, subcategory))

        return detections
    

    def save_result(self, image_path, objeto_id, category, subcategory):
        """
        Añade una fila al archivo CSV de resultados con información del objeto.

        Args:
            image_path (str): Ruta de la imagen procesada.
            objeto_id (int): Identificador del objeto en la imagen.
            category (str): Categoría predicha.
            subcategory (str): Subcategoría predicha.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nombre_imagen = os.path.basename(image_path)

        fila = pd.DataFrame([{
            "timestamp": now,
            "imagen": nombre_imagen,
            "objeto_id": objeto_id,
            "categoria": category,
            "subcategoria": subcategory
        }])

        archivo = "resultados.csv"
        header = not os.path.exists(archivo)
        fila.to_csv(archivo, mode='a', index=False, header=header)
