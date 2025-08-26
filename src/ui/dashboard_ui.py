import tkinter as tk
from PIL import Image, ImageTk
from src.ui_utils.ui_utils import clear_window, create_banner, create_logout_button
from src.ui.video_ui import VideoProcessorUI
from src.ui.upload_image_ui import UploadImageUI
from src.ui.statistics_ui import StatisticsUI
from src.ui.settings_ui import SettingsUI


class DashboardUI:
    """
    Clase para construir y mostrar la interfaz del Dashboard principal.

    Attributes:
        ui (UI): Instancia principal de la aplicación que contiene la ventana y estado global.
        window (tk.Tk): Ventana principal de la aplicación.
        icon_images (list[ImageTk.PhotoImage]): Lista de imágenes usadas como íconos en los botones.
    """
    
    def __init__(self, ui):
        """
        Inicializa la interfaz del Dashboard.

        Args:
            ui (UI): Instancia principal de la aplicación.
        """
        self.ui = ui
        self.window = ui.window
        self.icon_images = []

        self._build()


    def _build(self):
        """
        Crea y muestra la interfaz del Dashboard.
        """
        clear_window(self.window)
        self.window.configure(bg="#F4F7F5")

        create_banner(self.window)
        create_logout_button(self.window, command=self.ui.logout)

        self._load_icons()
        self._create_dashboard_buttons()


    def _load_icons(self):
        """
        Carga las imágenes de los íconos.
        """
        icon_paths = [
            "icons/camera.png",
            "icons/cloud.png",
            "icons/stats.png",
            "icons/settings.png"
        ]
        self.icon_images = [ImageTk.PhotoImage(Image.open(path).resize((48, 48))) for path in icon_paths]


    def _create_dashboard_buttons(self):
        """
        Crea y muestra los botones de navegación disponibles en el Dashboard.
        Las opciones dependen del rol del usuario actual [admin|worker].
        """
        container = tk.Frame(self.window, bg="#F4F7F5")
        container.pack()

        if self.ui.current_role == "admin":
            options = [
                ("Procesamiento\nen directo", lambda: VideoProcessorUI(self.ui)),
                ("Subir\nimagen", lambda: UploadImageUI(self.ui)),
                ("Estadísticas", lambda: StatisticsUI(self.ui)),
                ("Ajustes", lambda: SettingsUI(self.ui)),
            ]
        else:
            options = [
                ("Procesamiento\nen directo", lambda: UploadImageUI(self.ui)),
                ("Ajustes", lambda: SettingsUI(self.ui)),
            ]

        for i, (label_text, action) in enumerate(options):
            row = i // 2
            col = i % 2

            frame = tk.Frame(
                container,
                bg="#FFFFFF",
                highlightbackground="#49654E",
                highlightthickness=2,
                width=180,
                height=180,
                relief="flat"
            )
            frame.grid(row=row, column=col, padx=20, pady=20)
            frame.grid_propagate(False)
            frame.pack_propagate(False)

            frame.bind("<Enter>", lambda e, f=frame: f.config(bg="#E8F6F3"))
            frame.bind("<Leave>", lambda e, f=frame: f.config(bg="white"))

            icon = tk.Label(frame, image=self.icon_images[i], bg="#FFFFFF")
            icon.pack(pady=(30, 10))

            text_label = tk.Label(frame, text=label_text, bg="#FFFFFF", font=("Verdana", 15))
            text_label.pack(pady=(0, 30))

            hover_widgets = [frame, icon, text_label]

            for widget in hover_widgets:
                widget.bind("<Enter>", lambda e, w=hover_widgets: self._apply_hover(w, "#E8F6F3"))
                widget.bind("<Leave>", lambda e, w=hover_widgets: self._apply_hover(w, "#FFFFFF"))
                widget.bind("<Button-1>", lambda e, cmd=action: cmd())


    def _apply_hover(self, widgets, color):
        """
        Aplica un color de fondo a una lista de widgets para el efecto de hover.

        Args:
            widgets (list): Lista de widgets.
            color (str): Color de fondo.
        """
        for widget in widgets:
            widget.config(bg=color)
