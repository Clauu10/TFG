import tkinter as tk
from tkinter import ttk
from tkinter import messagebox 
from PIL import Image, ImageTk
import cv2
from src.ui_utils.ui_utils import create_scroll_window, create_banner, create_dashboard_button, clear_window


class VideoProcessorUI:
    """
    Crea la interfaz para reproducir y procesar videos con detección de objetos.

    Attributes:
        ui (UI): Instancia principal de la aplicación.
        window (tk.Tk): Ventana principal.
        cap (cv2.VideoCapture | None): Capturador de video actual.
        running (bool): Indica si el video está en reproducción.
        paused (bool): Indica si la reproducción está pausada.
        frame_delay (int): Retraso (ms) entre iteraciones del loop.
        frame_count (int): Contador de frames leídos.
        skip_rate (int): Procesa solo 1 de cada 'skip_rate' frames.
        video_label (tk.Label): Widget donde se muestra el frame actual.
        video_paths (list[str]): Rutas de videos disponibles.
        current_video_index (int): Índice del video actual.
        video_path (str): Ruta del video actual.
        scrollable_frame (tk.Frame): Contenedor con scroll para el contenido.
        pause_button (ttk.Button): Botón para pausar/reanudar.
    """
     
    def __init__(self, ui):
        """
        Inicializa la interfaz de procesamiento de video.

        Args:
            ui (UI): Instancia principal de la aplicación.
        """
        self.ui = ui
        self.window = ui.window

        self.cap = None
        self.running = False
        self.paused = False
        self.frame_delay = 10
        self.frame_count = 0
        self.skip_rate = 10

        self.video_label = None

        self.video_paths = [
            "video/camera1.mp4",
            "video/camera2.mp4",
            "video/camera3.mp4"
        ]
        self.current_video_index = 0
        self.video_path = self.video_paths[self.current_video_index]

        self._build()


    def _build(self):
        """
        Construye la interfaz e inicia la reproducción.
        """
        clear_window(self.window)
        self.window.configure(bg="#E9F0EF")

        create_banner(self.window)
        self.scrollable_frame = create_scroll_window(self.window, enable_mouse_scroll=True)
        
        create_dashboard_button(self.window, self.ui.create_dashboard)

        content_frame = tk.Frame(self.scrollable_frame, bg="#E9F0EF")
        content_frame.pack(pady=40)

        self.video_label = tk.Label(content_frame)
        self.video_label.pack()

        controls_frame = tk.Frame(content_frame, bg="#E9F0EF")
        controls_frame.pack(pady=10)

        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 10), padding=6)

        prev_button = ttk.Button(controls_frame, text="⏪ Anterior", command=self._previous_video)
        prev_button.pack(side=tk.LEFT, padx=5)

        pause_button = ttk.Button(controls_frame, text="⏸️ Pausar", command=self._toggle_pause)
        pause_button.pack(side=tk.LEFT, padx=5)
        self.pause_button = pause_button  

        next_button = ttk.Button(controls_frame, text="⏩ Siguiente", command=self._next_video)
        next_button.pack(side=tk.LEFT, padx=5)

        self._start_video()


    def _start_video(self):
        """
        Inicia la reproducción del video actual.
        """
        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(self.video_path)
        self.running = True
        self.paused = False
        self.frame_count = 0
        self._process_next_frame()


    def _process_next_frame(self):
        """
        Lee el siguiente frame, aplica detección, 
        dibuja las cajas/etiquetas y programa la siguiente iteración.
        """
        if not self.running or not self.cap or not self.cap.isOpened():
            return

        if self.paused:
            self.window.after(self.frame_delay, self._process_next_frame)
            return

        ret, frame = self.cap.read()
        if not ret:
            self.running = False
            self.cap.release()
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb, (800, 450))  

        self.frame_count += 1
        if self.frame_count % self.skip_rate != 0:
            self.window.after(self.frame_delay, self._process_next_frame)
            return

        detections = self.ui.processor.process_frame(frame_rgb)
        detections = sorted(detections, key=lambda x: x[1], reverse=True)[:3]

        annotated_frame = frame_rgb.copy()
        for box, conf, category, subcategory in detections:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                annotated_frame, f"{category}-{subcategory} ({conf:.2f})", (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
            )

        img = Image.fromarray(annotated_frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.configure(image=imgtk)
        self.video_label.image = imgtk

        self.window.after(self.frame_delay, self._process_next_frame)


    def _toggle_pause(self):
        """
        Pausar/Continuar la reproducción del vídeo.
        """
        self.paused = not self.paused
        self.pause_button.config(text="▶️ Reanudar" if self.paused else "⏸️ Pausar")


    def _next_video(self):
        """
        Cambia al siguiente video de la lista y reinicia la reproducción.
        """
        self.current_video_index = (self.current_video_index + 1) % len(self.video_paths)
        self.video_path = self.video_paths[self.current_video_index]
        messagebox.showinfo("Cambio de cámara", f"Reproduciendo: {self.video_path}")
        self._start_video()


    def _previous_video(self):
        """
        Cambia al video anterior de la lista y reinicia la reproducción.
        """
        self.current_video_index = (self.current_video_index - 1) % len(self.video_paths)
        self.video_path = self.video_paths[self.current_video_index]
        messagebox.showinfo("Cambio de cámara", f"Reproduciendo: {self.video_path}")
        self._start_video()

