import os
import torch
import gc
from ultralytics import YOLO


class YOLOTrainer:
    """
    Clase para entrenar, validar y realizar predicciones con un modelo YOLOv8.

    Attributes:
        model_path (str): Ruta al archivo .pt que se cargará (modelo base o best.pt anterior).
        device (str): Dispositivo (CPU o GPU).
        model (YOLO): Instancia del modelo YOLO cargado.
    """

    def __init__(self, model_path=None, device="cuda"):
        """
        Inicializa el trainer cargando un modelo YOLO.

        Args:
            model_path (str): Ruta al archivo .pt del modelo. 
                        Si es None, se usa un modelo base (por defecto yolov8m.pt).
            device (str): Dispositivo (CPU o GPU).
        """
        self.model_path = model_path
        self.device = device
        self._clear_memory()

        if self.model_path is None:
            base_model = "yolov8m.pt"
            self.model = YOLO(base_model)
        else:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"No se encontró un modelo en: {self.model_path}")
            self.model = YOLO(self.model_path)


    def _clear_memory(self):
        """
        Libera memoria y vacía la caché de CUDA.
        """
        gc.collect()
        torch.cuda.empty_cache()


    def train(self, config_path="src/detection/yolov8_config.yaml"):
        """
        Inicia un entrenamiento desde cero usando un archivo de configuración YAML.

        Args:
            config_path (str): Ruta al archivo YAML de configuración.

        Returns:
            Resultados generados por Ultralytics.
        """
        results = self.model.train(cfg=config_path)
        return results


    def resume_training(self, config_path="src/detection/yolov8_config.yaml"):
        """
        Continúa el entrenamiento desde el último checkpoint disponible.

        Args:
            config_path (str): Ruta al archivo YAML de configuración.

        Returns:
            Resultados generados por Ultralytics.
        """
        results = self.model.train(cfg=config_path, resume=True)
        return results


    def generate_plots(self, data_yaml="settings.yaml", conf=0.15, iou=0.5):
        """
        Genera y guarda gráficas de validación del modelo.

        Args:
            config_path (str): Ruta al archivo YAML de configuración.
            conf (float): Umbral de confianza mínimo.
            iou (float): Umbral IoU.
        """
        self.model.val(
            data=data_yaml,
            conf=conf,
            iou=iou,
            plots=True
        )


if __name__ == "__main__":
    model = YOLO("runs/detect/yolo_model_v10/weights/best.pt")

    model.train(cfg="src/detection/yolov8_config.yaml", freeze=10, epochs=20)
    model.train(cfg="src/detection/yolov8_config.yaml", freeze=0, epochs=80)

    model.val(data="settings.yaml", conf=0.001, iou=0.5, plots=True)
