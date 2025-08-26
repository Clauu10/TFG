import tkinter as tk

class Tooltip:
    """
    Clase para crear tooltips sobre un widget de Tkinter.

    Attributes:
        widget (tk.Widget): Widget asociado al tooltip.
        text (str): Texto del tooltip.
        delay (int): Tiempo de espera antes de mostrar el tooltip (ms).
    """

    def __init__(self, widget, text, delay=500):
        """
        Inicializa una instancia de Tooltip.

        Args:
            widget (tk.Widget): Widget asociado al tooltip.
            text (str): Texto del tooltip.
            delay (int, optional): Tiempo de espera antes de mostrar el tooltip (ms).
        """
        self.widget = widget
        self.text = text
        self.delay = delay  
        self.tooltip_window = None
        self.after_id = None
        self.last_mouse_pos = None

        self._bind_events()


    def _bind_events(self):
        """
        Asocia al widget los eventos de ratón necesarios para activar el tooltip.
        """
        self.widget.bind("<Enter>", self._schedule_tip)
        self.widget.bind("<Leave>", self._hide_tip)
        self.widget.bind("<Motion>", self._on_motion)


    def _schedule_tip(self, event=None):
        """
        Programa la aparición del tooltip tras un tiempo de espera.

        Args:
            event (tk.Event, optional): Evento de entrada del ratón.
        """
        self.last_mouse_pos = (event.x_root, event.y_root)
        self.after_id = self.widget.after(self.delay, lambda: self._show_tip(event))


    def _on_motion(self, event):
        """
       Reprograma el tooltip si cambia la posición del ratón.

        Args:
            event (tk.Event): Evento de movimiento del ratón.
        """
        current_pos = (event.x_root, event.y_root)
        if self.last_mouse_pos != current_pos:
            self.last_mouse_pos = current_pos

            if self.after_id:
                self.widget.after_cancel(self.after_id)

            self.after_id = self.widget.after(self.delay, lambda: self._show_tip(event))


    def _show_tip(self, event=None):
        """
        Crea y muestra la ventana del tooltip.

        Args:
            event (tk.Event, optional): Evento de posición del ratón.
        """
        if self.tooltip_window:
            return
        
        self.after_id = None  

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.configure(bg="black", padx=1, pady=1)

        label = tk.Label(tw, text=self.text, font=("Segoe UI", 9),
                         bg="white", fg="black", padx=8, pady=4)
        label.pack()

        x = event.x_root + 15
        y = event.y_root + 10

        tw.update_idletasks()
        width = tw.winfo_width()
        height = tw.winfo_height()
        screen_width = tw.winfo_screenwidth()
        screen_height = tw.winfo_screenheight()

        if x + width > screen_width:
            x = screen_width - width - 10
        if y + height > screen_height:
            y = screen_height - height - 10

        tw.wm_geometry(f"+{x}+{y}")


    def _hide_tip(self, event=None):
        """
        Cancela el tooltip programado y oculta el tooltip si está visible.

        Args:
            event (tk.Event, optional): Evento de salida del ratón.
        """
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None

        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
