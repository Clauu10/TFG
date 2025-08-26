from tkinterdnd2 import TkinterDnD
from src.classification.validation import Validation
from src.utils.process_image import ImageProcessor
from src.ui.login_ui import LoginUI
from src.ui.register_ui import RegisterUI
from src.ui.dashboard_ui import DashboardUI
from src.ui.upload_image_ui import UploadImageUI


class UI:
    """
    Clase principal de la interfaz de la aplicación.

    Attributes:
        classifier (ResidueClassifier): Modelo para clasificar tipos de residuos.
        detector (YoloDetector): Modelo YOLOv5 para detectar objetos.
        window (tk.Tk): Ventana principal de la interfaz.
        scrollable_frame (tk.Frame | None): Ventana desplazable.
        current_email (str | None): Correo electrónico del usuario actual.
        current_role (str | None): Rol del usuario actual.
    """

    def __init__(self):
        """
        Inicializa los modelos y configura la ventana principal de la aplicación.
        """
        self.classifier = Validation()

        self.processor = ImageProcessor(
            yolo_model_path="runs/detect/yolo_model_v10/weights/best.pt",
            cnn1_model_path="models/cnn_1/modelo_multiclase_20250811_145535.pth"
        )
        
        self.window = TkinterDnD.Tk()
        self.window.title("Clasificador de Residuos")
        self.window.state('zoomed')

        self.scrollable_frame = None

        self.current_email = None
        self.current_role = None

        LoginUI(self)


    def logout(self):
        """
        Cierra sesión del usuario actual y muestra la vista de login.
        """
        LoginUI(self)


    def show_login(self):
        """
        Muestra la vista de inicio de sesión.
        """
        LoginUI(self)


    def show_register(self):
        """
        Muestra la vista de registro de usuario.
        """
        RegisterUI(self)


    def create_dashboard(self):
        """
        Muestra la interfaz del Dashboard.
        """
        DashboardUI(self)


    def upload_image(self):
        """
        Muestra la interfaz para subir una imagen.
        """
        UploadImageUI(self)


    def run(self):
        """
        Inicia el bucle principal de la aplicación.
        """
        self.window.mainloop()
