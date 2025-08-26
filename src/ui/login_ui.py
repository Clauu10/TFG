import tkinter as tk
from tkinter import Button, messagebox
import random
import string
from src.ui_utils.ui_utils import clear_window, create_banner, show_popup, create_labeled_entry, create_password_field, create_password_change_popup
from src.auth.auth import authenticate_user, send_recovery_email
from src.ui_utils.tooltip_ui import Tooltip


class LoginUI:
    """
    Clase que construye la interfaz de inicio de sesión y recuperación de contraseña.

    Attributes:
        ui (UI): Instancia principal de la aplicación que contiene la ventana y estado global.
        window (tk.Tk): Ventana principal.
        recovery_codes (dict): Diccionario que asocia correos con sus códigos de recuperación.
    """

    def __init__(self, ui):
        """
        Inicializa la interfaz de Login.

        Args:
            ui (UI): Instancia principal de la aplicación.
        """
        self.ui = ui
        self.window = ui.window
        self.recovery_codes = {}

        self._build_ui()


    def _build_ui(self):
        """
        Construye la interfaz gráfica del inicio de sesión.
        """
        clear_window(self.window)
        self.window.configure(bg="#E9F0EF")
        create_banner(self.window)

        center_frame = tk.Frame(self.window, bg="#E9F0EF")
        center_frame.pack(expand=True)

        container = tk.Frame(center_frame, bg="white", bd=1, relief="flat", padx=40, pady=30)
        container.pack(pady=60)

        title = tk.Label(container, text="Iniciar sesión", 
                         font=("Segoe UI", 18, "bold"), bg="white", fg="#2C3E50")
        title.pack(pady=(10, 25))

        create_labeled_entry(self, container, "Correo electrónico:", "login_email")
        create_password_field(container, "Contraseña:", self, "login_password")

        forgot_btn = tk.Button(
            container,
            text="¿Olvidaste tu contraseña?",
            font=("Segoe UI", 9, "underline"),
            bg="white",
            fg="#2980B9",
            relief="flat",
            cursor="hand2",
            command=self._forgot_password
        )
        forgot_btn.pack(anchor="e", padx=5, pady=(0, 15))

        login_btn = Button(
            container,
            text="Iniciar sesión",
            command=self._login,
            font=("Segoe UI", 11, "bold"),
            bg="#2980B9",
            fg="white",
            relief="flat",
            width=30,
            pady=6,
            cursor="hand2"
        )
        login_btn.pack(pady=(0, 12))
        Tooltip(login_btn, "Iniciar sesión")

        register_btn = Button(
            container,
            text="Registrarse",
            command=self._go_to_register,
            font=("Segoe UI", 10, "bold"),
            bg="#BDC3C7",
            fg="white",
            relief="flat",
            width=30,
            pady=6,
            cursor="hand2"
        )
        register_btn.pack()
        Tooltip(register_btn, "Registrarse")


    def _forgot_password(self):
        """
        Muestra una ventana para que el usuario introduzca su correo
        y reciba un código de recuperación por email.
        """
        popup = tk.Toplevel(self.window)
        popup.title("Recuperar contraseña")

        width, height = 350, 160
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()

        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))

        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.resizable(False, False)
        popup.configure(bg="white")

        label = tk.Label(popup, text="Introduce tu correo electrónico:", 
                         font=("Segoe UI", 10), bg="white")
        label.pack(pady=(20, 5))

        email_entry = tk.Entry(
            popup,
            width=35,
            font=("Segoe UI", 10),
            bg="#F4F7F5",
            relief="flat"
        )
        email_entry.pack(pady=(0, 15), ipady=5)

        send_btn = tk.Button(
            popup,
            text="Enviar código",
            bg="#2980B9",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            command=lambda: self._handle_send_code(email_entry.get().strip(), popup)
        )
        send_btn.pack()


    def _login(self):
        """
        Verifica las credenciales (correo, contraseña) introducidas.
        Si son válidas, se va al dashboard. Si no, se muestra un mensaje de error.
        """
        email = self.login_email.get()
        pw = self.login_password.get()
        user = authenticate_user(email, pw)

        if user:
            self.ui.current_email = user["email"]
            self.ui.current_role = user["role"]
            self.ui.create_dashboard()
        else:
            show_popup(self.window, "Error", "Credenciales incorrectas")


    def _go_to_register(self):
        """
        Cambia a la ventana de registro.
        """
        self.ui.show_register()


    def _handle_send_code(self, email, popup):
        """
        Maneja el envío del código de recuperación por correo.

        Args:
            email (str): Correo electrónico del usuario.
            popup (tk.Toplevel): Ventana emergente que se cerrará tras enviar el código.
        """
        if not email:
            messagebox.showwarning("Campo vacío", "Por favor ingresa tu correo.")
            return

        code = self._generate_code()
        self.recovery_codes[email] = code
        send_recovery_email(email, code)

        popup.destroy()
        self._show_code_popup(email)


    def _generate_code(self, length=6):
        """
        Genera un código de recuperación alfanumérico aleatorio.

        Args:
            length (int): Longitud del código. Por defecto 6.

        Returns:
            str: Código generado.
        """
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    

    def _show_code_popup(self, email):
        """
        Muestra una ventana para que el usuario introduzca el código recibido por correo.
        Si el código es correcto, permite cambiar la contraseña.

        Args:
            email (str): Correo electrónico del usuario.
        """
        popup = tk.Toplevel(self.window)
        popup.title("Verificar código")

        width, height = 350, 160
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()

        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))

        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.resizable(False, False)
        popup.configure(bg="white")

        label = tk.Label(popup, text="Ingresa el código enviado a tu correo:", 
                         font=("Segoe UI", 10), bg="white")
        label.pack(pady=(20, 5))

        code_entry = tk.Entry(
            popup,
            width=20,
            font=("Segoe UI", 10),
            bg="#F4F7F5",
            relief="flat"
        )
        code_entry.pack(pady=(0, 15), ipady=5)

        verify_btn = tk.Button(
            popup,
            text="Verificar",
            font=("Segoe UI", 10, "bold"),
            bg="#2980B9",
            fg="white",
            relief="flat",
            padx=10,
            pady=5,
            command=lambda: self._handle_code_verification(email, code_entry.get().strip(), popup)
        )
        verify_btn.pack()

    
    def _handle_code_verification(self, email, code, popup):
        """
        Verifica si el código ingresado es correcto.
        Si es válido, muestra el formulario para cambiar la contraseña.

        Args:
            email (str): Correo electrónico del usuario.
            code (str): Código introducido por el usuario.
            popup (tk.Toplevel): Ventana actual.
        """
        if self.recovery_codes.get(email) == code:
            popup.destroy()
            create_password_change_popup(self.window, email, on_success=None)
        else:
            messagebox.showerror("Código incorrecto", "El código ingresado no es válido.")

