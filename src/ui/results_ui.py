import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
import cv2
from src.ui_utils.ui_utils import create_scroll_window, create_dashboard_button, create_upload_button
from src.utils.recomendations import Recomendation
from src.utils.classes import TRANSLATIONS


class ResultsUI:
    """
    Interfaz de resultados tras analizar una imagen: muestra la imagen anotada y
    una lista de objetos detectados con miniaturas y recomendaciones.

    Attributes:
        ui (UI): Instancia principal de la aplicación.
        parent (tk.Frame | tk.Tk): Contenedor donde se dibuja la interfaz.
        image_rgb (numpy.ndarray): Imagen RGB procesada.
        boxes (list): Lista de bbox (x1, y1, x2, y2).
        confidences (list): Confianzas por detección.
        image_path (str): Ruta de la imagen analizada.
    """

    DETECTION_THRESHOLD = 0.4

    def __init__(self, ui, parent, image_rgb, boxes, confidences, classes, class_names, image_path):
        """
        Inicializa la interfaz de resultados.

        Args:
            ui (UI): Instancia principal de la aplicación.
            parent (tk.Frame | tk.Tk): Contenedor donde se construirá la interfaz.
            image_rgb (numpy.ndarray): Imagen en formato RGB.
            boxes (list): Coordenadas (x1, y1, x2, y2) de los objetos detectados.
            confidences (list): Valores de confianza de cada detección.
            classes (list): Identificadores de las clases detectadas.
            class_names (list): Nombres de las clases.
            image_path (str): Ruta del archivo de la imagen.
        """
        self.ui = ui
        self.parent = parent
        self.scrollable_frame = None
        self.image_rgb = image_rgb
        self.boxes = boxes
        self.confidences = confidences
        self.classes = classes
        self.class_names = class_names
        self.image_path = image_path

        self.results = []  
        self.frame = None

        self._load_results()
        self._build()


    def _load_results(self):
        """
        Calcula y guarda los resultados.
        """
        h, w = self.image_rgb.shape[:2]
        for i, (box, conf) in enumerate(zip(self.boxes, self.confidences)):
            if conf < self.DETECTION_THRESHOLD:
                continue

            x1, y1, x2, y2 = map(int, box)
            x1 = max(0, min(x1, w - 1))
            x2 = max(0, min(x2, w))
            y1 = max(0, min(y1, h - 1))
            y2 = max(0, min(y2, h))
            if x2 <= x1 or y2 <= y1:
                continue

            cropped_np = self.image_rgb[y1:y2, x1:x2]
            if cropped_np.size == 0:
                continue

            pil_image = Image.fromarray(cropped_np)
            category, subcategory = self.ui.processor.process_cropped_image(pil_image)

            self.ui.processor.save_result(
                image_path=self.image_path,
                objeto_id=i + 1,
                category=category,
                subcategory=subcategory
            )

            self.results.append({
                "idx": i,
                "box": (x1, y1, x2, y2),
                "conf": float(conf),
                "pil": pil_image,
                "categoria": category,
                "subcategoria": subcategory,
                "recomendacion": Recomendation.RECOMENDATIONS.get(subcategory, "No hay recomendación."),
                "nombre": TRANSLATIONS.get(subcategory, subcategory),
            })


    def _build(self):
        """
        Construye la interfaz principal de resultados.
        """
        main_frame = tk.Frame(self.parent, bg="#F4F7F5")
        main_frame.pack(fill="both", expand=True)

        create_dashboard_button(self.parent, self.ui.create_dashboard)
        create_upload_button(self.parent, self.ui.upload_image)

        self.scrollable_frame = create_scroll_window(main_frame, enable_mouse_scroll=True)

        if not self.results:
            frame = Label(self.scrollable_frame, text="No se detectó ningún objeto.", 
                          font=("Arial", 12), bg="#F4F7F5")
            frame.pack()
            return

        self.frame = tk.Frame(self.scrollable_frame, bg="#F4F7F5")
        self.frame.pack(pady=40)

        frame = Label(self.frame, text=f"Objetos detectados: {len(self.results)}",
                      font=("Arial", 12, "bold"), bg="#F4F7F5")
        frame.pack(pady=(0, 10))

        self._show_image()
        self._show_objects()


    def _show_image(self):
        """
        Dibuja los bounding boxes sobre una copia de la imagen y muestra el resultado.
        """
        img_draw = self.image_rgb.copy()
        for r in self.results:
            x1, y1, x2, y2 = r["box"]
            label_text = f'{r["categoria"]} - {r["subcategoria"]} ({r["conf"]:.2f})'
            cv2.rectangle(img_draw, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                img_draw, label_text,
                (x1, max(y1 - 5, 0)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA
            )

        img = Image.fromarray(img_draw)
        img.thumbnail((700, 700))
        img_tk = ImageTk.PhotoImage(img)

        label = Label(self.frame, image=img_tk, bg="#F4F7F5")
        label.image = img_tk  
        label.pack(pady=(0, 10))


    def _show_objects(self):
        """
        Muestra una miniatura de cada objeto detectado.
        """
        resultados_frame = tk.Frame(self.frame, bg="#F4F7F5")
        resultados_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title = tk.Label(resultados_frame, text="OBJETOS DETECTADOS:", 
                         font=("Arial", 11, "bold"), bg="#F4F7F5")
        title.pack(anchor="w", padx=10, pady=(0, 10))

        self.recorte_images = []
        for r in self.results:
            thumbnail_pil = r["pil"].copy()
            thumbnail_pil.thumbnail((80, 80))
            img_crop = ImageTk.PhotoImage(thumbnail_pil)
            self.recorte_images.append(img_crop)

            item_frame = tk.Frame(resultados_frame, bg="#F4F7F5")
            item_frame.pack(anchor="w", pady=5)

            icon = Label(item_frame, image=img_crop, bg="#F4F7F5")
            icon.pack(side="left", padx=10)

            cat = r["categoria"]
            subcat = r["subcategoria"]
            reco = r["recomendacion"]
            pil_for_popup = r["pil"].copy()
            icon.bind(
                "<Button-1>",
                lambda e, cat=cat, subcat=subcat, reco=reco, img=pil_for_popup:
                    self._show_popup(cat, subcat, reco, img)
            )

            text = Label(item_frame, text=r["nombre"], font=("Arial", 10), bg="#F4F7F5")
            text.pack(side="left", padx=10)


    def _show_popup(self, category, subcategory, recomendation, image_pil):
        """
        Muestra una ventana emergente con detalles de un objeto detectado.

        Args:
            categoria (str): Categoría del objeto.
            subcategoria (str): Subcategoría del objeto.
            recomendacion (str): Texto de recomendación asociado al objeto.
            imagen_pil (PIL.Image): Imagen recortada del objeto.
        """
        window = tk.Toplevel(self.parent)
        window.title("Detalles Objeto")
        window.configure(bg="white")
        window.geometry("500x350")

        container = tk.Frame(window, bg="white")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        image_pil = image_pil.copy()
        image_pil.thumbnail((150, 150))
        image_tk = ImageTk.PhotoImage(image_pil)

        icon = tk.Label(container, image=image_tk, bg="white")
        icon.image = image_tk
        icon.grid(row=0, column=0, rowspan=2, padx=10)

        categoria_trad = TRANSLATIONS.get(category, category)
        subcategoria_trad = TRANSLATIONS.get(subcategory, subcategory)

        label_category = tk.Label(container, text=f"Categoría: {categoria_trad}\nSubcategoría: {subcategoria_trad}",
                                  font=("Arial", 12), bg="white", justify="left")
        label_category.grid(row=0, column=1, sticky="w")

        label_title = tk.Label(container, text="RECOMENDACIONES", 
                               font=("Arial", 14, "bold"), bg="white", pady=10)
        label_title.grid(row=1, column=1, sticky="w")

        label_rec = tk.Label(container, text=recomendation, 
                             font=("Arial", 11), bg="white", wraplength=400, justify="left")
        label_rec.grid(row=2, column=0, columnspan=2, pady=(10, 20))

        close_but = tk.Button(
            window,
            text="Cerrar",
            command=window.destroy,
            bg="#3498db",
            fg="white",
            padx=10,
            pady=5
        )
        close_but.pack()

        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
