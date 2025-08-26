import tkinter as tk
from tkinterdnd2 import DND_FILES
from PIL import Image, ImageTk
import cv2
from src.ui_utils.ui_utils import clear_window, create_banner, create_dashboard_button
from src.ui.results_ui import ResultsUI


class UploadImageUI:
    """
    Clase para construir la interfaz para subir imágenes.

    Attributes:
        ui (UI): Instancia principal de la aplicación que contiene la ventana y estado global.
        window (tk.Tk):  Ventana principal de la aplicación.
        upload_frame (tk.Frame): Contenedor donde se muestra el botón para cargar imágenes.
        folder_icon (ImageTk.PhotoImage): Ícono para la carga de archivos.
    """

    def __init__(self, ui):
        """
        Inicializa la interfaz de carga de imágenes.

        Args:
            ui (UI): Instancia principal de la aplicación.
        """
        self.ui = ui
        self.window = ui.window

        self.upload_frame = None
        self.folder_icon = None

        self._build()


    def _build(self):
        """
        Construye la interfaz para la carga de imágenes.
        """
        clear_window(self.window)
        self.window.configure(bg="#E9F0EF")

        create_banner(self.window)
        create_dashboard_button(self.window, self.ui.create_dashboard)

        self._create_upload_frame()


    def _create_upload_frame(self):
        """
        Crea el contenedor con los elementos para subir una imagen.
        """
        self.upload_frame = tk.Frame(
            self.window,
            bg="white",
            highlightbackground="#D5D8DC",
            highlightthickness=1,
            width=500,
            height=260,
            relief="flat"
        )
        self.upload_frame.pack(pady=60)
        self.upload_frame.pack_propagate(False)

        self.folder_icon = ImageTk.PhotoImage(Image.open("icons/cloud.png").resize((64, 64)))

        icon_label = tk.Label(self.upload_frame, image=self.folder_icon, bg="white")
        icon_label.pack(pady=(20, 10))

        file_label = tk.Label(self.upload_frame, text="Arrastra tu archivo aquí o",
                              font=("Segoe UI", 12), bg="white", fg="#2C3E50")
        file_label.pack()

        browse_but = tk.Button(
            self.upload_frame,
            command=self._browse_image,
            text="📂 Explorar archivos",
            font=("Segoe UI", 11, "bold"),
            bg="#3498DB",
            fg="white",
            padx=12,
            pady=6,
            relief="flat",
            cursor="hand2"
        )
        browse_but.pack(pady=(10, 5))

        format_label = tk.Label(self.upload_frame, text="Formatos soportados: PNG, JPG, JPEG",
                                font=("Segoe UI", 9), bg="white", fg="#7F8C8D")
        format_label.pack()

        self.upload_frame.drop_target_register(DND_FILES)
        self.upload_frame.dnd_bind("<<Drop>>", self._drop_file)


    def _browse_image(self):
        """
        Abre el explorador de archivos para que el usuario seleccione una imagen.

        Si se selecciona un archivo válido, procesa la imagen y 
        llama a la interfaz de resultados.
        """
        path = tk.filedialog.askopenfilename(filetypes=[("Imagen", "*.png *.jpg *.jpeg")])
        if path:
            self._process_image(path)


    def _drop_file(self, event):
        """
        Maneja el evento de arrastrar y soltar un archivo para cargarlo.

        Args:
            event: Evento generado por tkinterdnd2 al soltar el archivo.
        """
        ruta = event.data.strip("{}")
        if ruta:
            self._process_image(ruta)


    def _process_image(self, ruta):
        if self.upload_frame:
            self.upload_frame.destroy()

        image_bgr = cv2.imread(ruta)
        if image_bgr is None:
            return

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        detections = self.ui.processor.process_frame(image_rgb)

        boxes = []
        confidences = []
        classes = []
        class_names = []

        for box, conf, category, subcategory in detections:
            boxes.append(box)
            confidences.append(conf)
            classes.append(len(class_names))  
            class_names.append(f"{category} → {subcategory}")

        ResultsUI(
            ui=self.ui,
            parent=self.window,
            image_rgb=image_rgb,
            boxes=boxes,
            confidences=confidences,
            classes=classes,
            class_names=class_names,
            image_path=ruta
        )

