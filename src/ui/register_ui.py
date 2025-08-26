import re
import tkinter as tk
from tkinter import Button, ttk
import random
import string
from email.mime.text import MIMEText
import smtplib
from src.ui_utils.ui_utils import clear_window, create_banner, show_popup, create_labeled_entry
from src.auth.auth import register_user_with_email
from src.ui_utils.tooltip_ui import Tooltip


class RegisterUI:
    """
    Clase que construye la interfaz de registro de nuevos usuarios.

    Attributes:
        ui (UI): Instancia principal de la aplicación que contiene la ventana y estado global.
        window (tk.Tk): Ventana principal de la aplicación.
    """

    def __init__(self, ui):
        """
        Inicializa de la interfaz de registro.

        Args:
            ui (UI): Instancia principal de la aplicación.
        """
        self.ui = ui
        self.window = ui.window
        self._build_ui()


    def _build_ui(self):
        """
        Construye la interfaz gráfica del formulario de registro.
        """
        clear_window(self.window)
        self.window.configure(bg="#E9F0EF")
        create_banner(self.window)

        center_frame = tk.Frame(self.window, bg="#E9F0EF")
        center_frame.pack(expand=True)

        container = tk.Frame(center_frame, bg="white", bd=1, relief="flat", padx=40, pady=30)
        container.pack(pady=60)

        title = tk.Label(container, text="Registrar nuevo usuario",
                         font=("Segoe UI", 18, "bold"), bg="white", fg="#2C3E50")
        title.pack(pady=(10, 25))

        create_labeled_entry(self, container, "Nombre de usuario:", "username")
        create_labeled_entry(self, container, "Nombre completo:", "fullname")
        create_labeled_entry(self, container, "Correo electrónico:", "email")

        role_label = tk.Label(container, text="Rol:",
                              font=("Segoe UI", 10), bg="white", anchor="w")
        role_label.pack(fill="x", padx=5)

        self.role = tk.StringVar(value="worker")
        self.role_combobox = ttk.Combobox(
            container,
            textvariable=self.role,
            values=["worker", "admin"],
            font=("Segoe UI", 10),
            state="readonly"
        )
        self.role_combobox.pack(pady=(0, 20), ipady=6, ipadx=4, fill="x")
        self.role_combobox.configure(width=38)

        register_btn = Button(
            container,
            text="Registrar",
            command=self._register,
            font=("Segoe UI", 11, "bold"),
            bg="#3498DB",
            fg="white",
            relief="flat",
            width=30,
            pady=6,
            cursor="hand2"
        )
        register_btn.pack(pady=(0, 12))
        Tooltip(register_btn, "Registrarse")

        back_btn = Button(
            container,
            text="Volver",
            command=self._go_back,
            font=("Segoe UI", 10, "bold"),
            bg="#BDC3C7",
            fg="white",
            relief="flat",
            width=30,
            pady=6,
            cursor="hand2"
        )
        back_btn.pack()
        Tooltip(back_btn, "Volver")


    def _is_valid_email(self, email):
        """
        Verifica si el correo tiene un formato válido.

        Args:
            email: Correo electrónico a validar.

        Returns:
            bool: True si el formato es válido, False si no lo es.
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


    def _register(self):
        username = self.username.get()
        fullname = self.fullname.get()
        email = self.email.get()
        role = self.role.get()

        if not self._is_valid_email(email):
            show_popup(self.window, "Error", "El correo electrónico no es válido.")
            return

        success = register_user_with_email(username, fullname, email, role)
        if success:
            show_popup(self.window, "Éxito", "Usuario registrado correctamente. La contraseña se ha enviado a su correo.")
            self._go_back()
        else:
            show_popup(self.window, "Error", "El usuario ya existe.")


    def _go_back(self):
        """
        Vuelve a la pantalla de inicio de sesión.
        """
        self.ui.show_login()
    