import tkinter as tk
from PIL import Image, ImageTk
from src.auth.auth import update_password
from src.ui_utils.tooltip_ui import Tooltip


def clear_window(window):
    """
    Elimina todos los widgets hijos de una ventana.

    Args:
        window (tk.Widget): Ventana de la que se eliminan los widgets.
    """
    for widget in window.winfo_children():
        widget.destroy()


def create_scroll_window(window, bg="#F4F7F5", enable_mouse_scroll=True):
    """
    Crea un contenedor con scroll vertical.
    
    Args:
        window (tk.Widget): Contenedor padre.
        bg (str): Color de fondo del área scrollable.
        enable_mouse_scroll (bool): Si True, habilita el scroll con la rueda del ratón.

    Returns:
        tk.Frame: Frame interno sobre el que se añaden los widgets.
    """
    container = tk.Frame(window, bg=bg)
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container, bg=bg, highlightthickness=0)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    scrollable_frame = tk.Frame(canvas, bg=bg)
    window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")

    canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    if enable_mouse_scroll:
        def on_mousewheel(event):
            if canvas.winfo_exists():
                direction = int(-1 * (event.delta / 120))
                current_top = canvas.yview()[0]
                if direction < 0 and current_top <= 0:
                    return 
    
                canvas.yview_scroll(direction, "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        def on_destroy(_):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Destroy>", on_destroy)

    return scrollable_frame


def create_banner(parent):
    """
    Crea un banner superior en la ventana.

    Args:
        parent (tk.Widget): Contenedor en el que se creará el banner.
    """
    banner = tk.Frame(parent, bg="#49654E", height=80)
    banner.pack(fill="x", side="top")

    title = tk.Label(banner, text="Clasificador de Residuos",
                     font=("Poppins", 18, "bold"), bg="#49654E", fg="#F4F7F5")
    title.pack(pady=20)


def create_dashboard_button(parent, command):
    """
    Crea un botón para volver al Dashboard.

    Args:
        parent (tk.Widget): Contenedor donde se crea el botón.
        command (callable): Función que se ejecuta al hacer clic en el botón.
    """
    icon = Image.open("icons/home.png")
    icon = icon.resize((16, 16))
    icon_image = ImageTk.PhotoImage(icon)

    button = tk.Button(
        parent,
        command=command,
        image=icon_image,
        text=f"  { "Volver al Dashboard"}", 
        font=("Segoe UI", 12),
        bg="white",
        fg="black",
        relief="flat",
        compound="left"
    )
    button.image = icon_image  
    button.place(x=10, y=90)


def create_upload_button(parent, command):
    """
    Crea un botón para subir otra imagen.

    Args:
        parent (tk.Widget): Contenedor donde se crea el botón.
        command (callable): Función que se ejecuta al hacer clic en el botón.
    """
    icon = Image.open("icons/arrow.png").resize((16, 16))  
    icon_image = ImageTk.PhotoImage(icon)

    button = tk.Button(
        parent,
        command=command,
        image=icon_image,
        text="  Subir otra imagen",
        font=("Segoe UI", 12),
        bg="white",
        fg="black",
        relief="flat",
        compound="left"
    )
    button.image = icon_image 
    button.place(x=200, y=90) 


def create_logout_button(parent, command):
    """
    Crea un botón para cerrar sesión.

    Args:
        parent (tk.Widget): Contenedor donde se coloca el botón.
        command (callable): Función que se ejecuta al hacer clic en el botón.
    """
    icon = Image.open("icons/logout.png").resize((32, 32))
    icon_image = ImageTk.PhotoImage(icon)

    container = tk.Frame(parent, bg="#F4F7F5")
    container.pack(fill="x", pady=(10, 30))

    button = tk.Button(
        container,
        command=command,
        image=icon_image,
        bg="#F4F7F5",
        bd=0,
        cursor="hand2",
        activebackground="#F4F7F5"
    )
    button.image = icon_image
    button.pack(side="right", padx=20)

    Tooltip(button, "Cerrar sesión")


def show_popup(parent, title, message):
    """
    Muestra una ventana popup con título, mensaje y botón de "Aceptar".

    Args:
        parent (tk.Widget): Ventana a la que pertenece el popup.
        title (str): Título del popup.
        message (str): Mensaje a mostrar.
    """
    popup = tk.Toplevel(parent)
    popup.title(title)
    popup.configure(bg="white")
    popup.resizable(False, False)

    title = tk.Label(popup, text=title, font=("Segoe UI", 14, "bold"),
                     bg="white", fg="#2C3E50")
    title.pack(pady=(20, 5))

    message = tk.Label(popup, text=message, font=("Segoe UI", 10), 
                       bg="white", wraplength=350, justify="center")
    message.pack(padx=20)

    ok_btn = tk.Button(
        popup, 
        text="Aceptar", 
        command=popup.destroy,
        font=("Segoe UI", 10, "bold"), 
        bg="#2980B9", 
        fg="white",
        relief="flat", 
        padx=10, 
        pady=5, 
        width=12
    )
    ok_btn.pack(pady=20)

    popup.update_idletasks()
    w = popup.winfo_width()
    h = popup.winfo_height()
    x = (popup.winfo_screenwidth() // 2) - (w // 2)
    y = (popup.winfo_screenheight() // 2) - (h // 2)
    popup.geometry(f"{w}x{h}+{x}+{y}")

    popup.transient(parent)
    popup.grab_set()
    parent.wait_window(popup)


def _create_entry(parent, show="*"):
    """
    Crea un campo de entrada personalizado.

    Args:
        parent (tk.Widget): Contenedor padre.
        show (str): Carácter para ocultar el texto (por defecto '*').

    Returns:
        tk.Entry: Campo de entrada creado.
    """
    entry = tk.Entry(parent, show=show, width=35, font=("Segoe UI", 10), bg="#F4F7F5", relief="flat")
    entry.pack(pady=(0, 10), ipady=5)
    return entry


def create_labeled_entry(self, parent, label_text, attr_name):
    """
    Crea un campo de entrada etiquetado y lo guarda como atributo de la clase.

    Args:
        parent (tk.Widget): Contenedor del campo.
        label_text (str): Texto del campo.
        attr_name (str): Atributo del campo.
    """
    label = tk.Label(parent,text=label_text, font=("Segoe UI", 10),
                     bg="white", anchor="w")
    label.pack(fill="x", padx=5)

    entry = tk.Entry(parent, width=40, font=("Segoe UI", 10), bg="#F4F7F5", relief="flat")
    entry.pack(pady=(0, 15), ipady=6, ipadx=4)
    setattr(self, attr_name, entry)


def create_password_field(parent, label_text, instance, attr_name):
    """
    Crea un campo de entrada de contraseña con botón para mostrar/ocultar.

    Args:
        parent (tk.Widget): Contenedor donde se añadirá el campo.
        label_text (str): Texto de la etiqueta del campo.
        instance (object): Instancia donde se guardará la referencia del Entry.
        attr_name (str): Nombre del atributo donde se guarda el Entry.
    """
    label = tk.Label(parent, text=label_text, bg="white", 
                     anchor="w", font=("Segoe UI", 10))
    label.pack(fill="x", padx=5)

    frame = tk.Frame(parent, bg="white")
    frame.pack(fill="x", expand=True, pady=(0, 10))

    entry = tk.Entry(frame, font=("Segoe UI", 10), show="*",
                     bg="#F4F7F5", relief="flat")
    entry.grid(row=0, column=0, sticky="ew", ipady=6, padx=(0, 4))

    toggle_btn = tk.Button(
        frame,
        text="Mostrar",
        font=("Segoe UI", 9, "underline"),
        bg="white",
        fg="#2980B9",
        relief="flat",
        cursor="hand2"
    )
    toggle_btn.grid(row=0, column=1, sticky="e")

    frame.grid_columnconfigure(0, weight=1)

    def toggle():
        if entry.cget("show") == "":
            entry.config(show="*")
            toggle_btn.config(text="Mostrar")
        else:
            entry.config(show="")
            toggle_btn.config(text="Ocultar")

    toggle_btn.config(command=toggle)
    setattr(instance, attr_name, entry)


def _handle_password_update(popup, parent_window, email, new_pw, confirm_pw, on_success):
    """
    Validar y actualizar la contraseña.

    Args:
        popup (tk.Toplevel): Popup actual que se cerrará si la actualización es correcta.
        parent_window (tk.Widget): Ventana principal para mostrar mensajes de error/éxito.
        email (str): Correo del usuario cuya contraseña se quiere actualizar.
        new_pw (tk.Entry): Campo de entrada con la nueva contraseña.
        confirm_pw (tk.Entry): Campo de entrada para confirmar la nueva contraseña.
        on_success (callable | None): Callback opcional que se ejecuta tras una actualización exitosa.
    """
    pw1 = new_pw.get()
    pw2 = confirm_pw.get()

    if not pw1 or not pw2:
        show_popup(parent_window, "Error", "Completa ambos campos.")
        return
    if pw1 != pw2:
        show_popup(parent_window, "Error", "Las contraseñas no coinciden.")
        return

    if update_password(email, pw1):
        show_popup(parent_window, "Éxito", "Contraseña actualizada.")
        popup.destroy()
        if on_success:
            on_success()
    else:
        show_popup(parent_window, "Error", "No se pudo actualizar la contraseña.")


def create_password_change_popup(parent_window, email, on_success):
    """
    Muestra un popup para cambiar la contraseña.

    Args:
        parent_window (tk.Widget): Ventana principal desde la que se abre el popup.
        email (str): Email del usuario que va a actualizar la contraseña.
        on_success (callable | None): Callback opcional al completar con éxito.
    """
    popup = tk.Toplevel(parent_window)
    popup.title("Verificar código")

    width, height = 350, 230
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()

    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))

    popup.geometry(f"{width}x{height}+{x}+{y}")
    popup.resizable(False, False)
    popup.configure(bg="white")

    tk.Label(popup, text="Nueva contraseña:", font=("Segoe UI", 10), bg="white").pack(pady=(20, 5))
    new_pw = _create_entry(popup)

    tk.Label(popup, text="Confirmar contraseña:", font=("Segoe UI", 10), bg="white").pack()
    confirm_pw = _create_entry(popup)

    button = tk.Button(
        popup,
        text="Cambiar contraseña",
        font=("Segoe UI", 10, "bold"),
        bg="#2980B9",
        fg="white",
        relief="flat",
        padx=10,
        pady=5,
        command=lambda: _handle_password_update(popup, parent_window, email, new_pw, confirm_pw, on_success)
    )
    button.pack()
