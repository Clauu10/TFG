import tkinter as tk
from tkinter import ttk  
from src.auth.auth import authenticate_user, delete_user, list_users, update_password, update_username
from src.ui_utils.ui_utils import clear_window, create_banner, create_labeled_entry, create_password_field, show_popup
from src.auth.auth import register_user_with_email
from src.ui_utils.tooltip_ui import Tooltip


class SettingsUI:
    """
    Crea la ventana de ajustes del usuario.

    Attributes:
        ui (UI): Instancia principal de la aplicación.
        window (tk.Tk): Ventana principal.
        content_frame (tk.Frame): Contenedor lateral derecho donde se cargan los ajustes.
    """

    def __init__(self, ui):
        """
        Inicializa la vista de ajustes y construye la interfaz.

        Args:
            ui (UI): Instancia principal de la aplicación.
        """
        self.ui = ui
        self.window = ui.window
        self.content_frame = None 
        self._build_settings()


    def _build_settings(self):
        """
        Construye la ventana de ajustes:
        """
        clear_window(self.window)
        self.window.configure(bg="#E9F0EF")
        create_banner(self.window)

        main_frame = tk.Frame(self.window, bg="#E9F0EF")
        main_frame.pack(expand=True, fill="both")

        sidebar = tk.Frame(main_frame, bg="white", width=250, relief="flat")
        sidebar.pack(side="left", fill="y", padx=(20, 0), pady=20)
        sidebar.pack_propagate(False)

        home_btn = tk.Button(
            sidebar,
            text="Volver al Dashboard",
            command=self.ui.create_dashboard,
            font=("Segoe UI", 10, "bold"),
            bg="#E9F0EF",
            fg="black",
            relief="flat",
            width=25,
            cursor="hand2"
        )
        home_btn.pack(padx=20, pady=(0, 15))
        Tooltip(home_btn, "Volver al Dashboard")

        tk.Button(sidebar, text="Cambiar nombre de usuario", command=self._load_username_form,
                  font=("Segoe UI", 10), bg="#E9F0EF", relief="flat", width=25).pack(padx=20, pady=5)
        
        tk.Button(sidebar, text="Cambiar contraseña", command=self._load_password_form,
                  font=("Segoe UI", 10), bg="#E9F0EF", relief="flat", width=25).pack(padx=20, pady=5)
        
        if self.ui.current_role == "admin":
            tk.Button(sidebar, text="Crear usuario", command=self._load_create_user_form,
                    font=("Segoe UI", 10), bg="#E9F0EF", relief="flat", width=25).pack(padx=20, pady=5)

            tk.Button(sidebar, text="Eliminar usuario", command=self._load_delete_user_form,
                    font=("Segoe UI", 10), bg="#E9F0EF", relief="flat", width=25).pack(padx=20, pady=5)

        self.content_frame = tk.Frame(main_frame, bg="white", bd=1, relief="flat", padx=40, pady=30)
        self.content_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        self._load_password_form()


    def _load_password_form(self):
        """
        Carga el formulario para actualizar la contraseña del usuario actual.
        """
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        change_pw_label = tk.Label(self.content_frame, text="Cambiar contraseña",
                 font=("Segoe UI", 18, "bold"), bg="white", fg="#2C3E50")
        change_pw_label.pack(pady=(0, 25))

        form_frame = tk.Frame(self.content_frame, bg="white")
        form_frame.pack(padx=0, pady=10)

        create_password_field(form_frame, "Contraseña actual:", self, "current_pw")
        create_password_field(form_frame, "Nueva contraseña:", self, "new_pw")
        create_password_field(form_frame, "Repetir nueva contraseña:", self, "repeat_pw")

        update_but = tk.Button(
            self.content_frame,
            command=self._submit_password,
            text="Actualizar contraseña",
            font=("Segoe UI", 11, "bold"),
            bg="#3498DB",
            fg="white",
            relief="flat",
            padx=10,
            pady=6,
            width=30,
            cursor="hand2"
        )
        update_but.pack(pady=(15, 10))
        Tooltip(update_but, "Actualizar contraseña")

        go_back_but = tk.Button(
            self.content_frame,
            command=self.ui.create_dashboard,
            text="Volver",
            font=("Segoe UI", 10, "bold"),
            bg="#BDC3C7",
            fg="white",
            relief="flat",
            padx=10,
            pady=6,
            width=30,
            cursor="hand2"
        )
        go_back_but.pack()
        Tooltip(go_back_but, "Volver")


    def _submit_password(self):
        """
        Comprueba las contraseñas y actualiza la contraseña del usuario.
        """
        current_pw = self.current_pw.get()
        new_pw = self.new_pw.get()
        repeat_pw = self.repeat_pw.get()
        email = self.ui.current_email

        if not current_pw or not new_pw or not repeat_pw:
            show_popup(self.window, "Error", "Todos los campos son obligatorios.")
            return

        user = authenticate_user(email, current_pw)
        if not user:
            show_popup(self.window, "Error", "La contraseña actual no es correcta.")
            return

        if new_pw != repeat_pw:
            show_popup(self.window, "Error", "Las nuevas contraseñas no coinciden.")
            return

        if current_pw == new_pw:
            show_popup(self.window, "Error", "La nueva contraseña no puede ser igual a la actual.")
            return

        success = update_password(email, new_pw)
        if success:
            show_popup(self.window, "Éxito", "Contraseña actualizada correctamente.")
            self._load_password_form()
        else:
            show_popup(self.window, "Error", "No se pudo actualizar la contraseña.")


    def _load_username_form(self):
        """
        Carga el formulario para actualizar el nombre de usuario.
        """
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        user_label = tk.Label(self.content_frame, text="Cambiar nombre de usuario", 
                 font=("Segoe UI", 18, "bold"), bg="white", fg="#2C3E50")
        user_label.pack(pady=(0, 25))

        form_frame = tk.Frame(self.content_frame, bg="white")
        form_frame.pack()

        create_labeled_entry(self, form_frame, "Nuevo nombre de usuario:", "new_username")

        update_btn = tk.Button(
            self.content_frame,
            command=self._submit_username,
            text="Actualizar nombre de usuario",
            font=("Segoe UI", 11, "bold"),
            bg="#3498DB",
            fg="white",
            relief="flat",
            width=30,
            pady=6,
            cursor="hand2"
        )
        update_btn.pack(pady=(15, 10))
        Tooltip(update_btn, "Actualizar nombre de usuario")

        go_back_btn = tk.Button(
            self.content_frame,
            command=self.ui.create_dashboard,
            text="Volver",
            font=("Segoe UI", 10, "bold"),
            bg="#BDC3C7",
            fg="white",
            relief="flat",
            width=30,
            pady=6,
            cursor="hand2"
        )
        go_back_btn.pack()
        Tooltip(go_back_btn, "Volver")


    def _submit_username(self):
        """
        Valida y actualiza el nombre de usuario del usuario actual.
        """
        new_username = self.new_username.get().strip()
        email = self.ui.current_email

        if not new_username:
            show_popup(self.window, "Error", "El nuevo nombre de usuario no puede estar vacío.")
            return

        success = update_username(email, new_username)
        if success:
            show_popup(self.window, "Éxito", "Nombre de usuario actualizado correctamente.")
            self.ui.current_username = new_username 
            self._load_username_form()
        else:
            show_popup(self.window, "Error", "No se pudo actualizar. El nombre ya existe o el usuario no fue encontrado.")


    def _load_create_user_form(self):
        """
        Carga el formulario para crear un nuevo usuario.
        """
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text="Crear nuevo usuario",
                font=("Segoe UI", 18, "bold"), bg="white", fg="#2C3E50").pack(pady=(0, 25))

        form_frame = tk.Frame(self.content_frame, bg="white")
        form_frame.pack()

        create_labeled_entry(self, form_frame, "Nombre de usuario:", "new_username_reg")
        create_labeled_entry(self, form_frame, "Nombre completo:", "new_fullname")
        create_labeled_entry(self, form_frame, "Email:", "new_email")

        tk.Label(form_frame, text="Rol:", bg="white", anchor="w").pack(fill="x", padx=5)

        self.new_role = tk.StringVar(value="worker")
        role_combobox = ttk.Combobox(
            form_frame,
            textvariable=self.new_role,
            values=["worker", "admin"],
            font=("Segoe UI", 10),
            state="readonly"
        )
        role_combobox.pack(pady=(0, 20), ipady=6, ipadx=4, fill="x")
        role_combobox.configure(width=38)

        reg_but = tk.Button(
            self.content_frame, 
            command=self._submit_create_user, 
            text="Crear usuario",
            font=("Segoe UI", 11, "bold"), 
            bg="#3498DB", 
            fg="white",
            relief="flat", width=30
        )
        reg_but.pack(pady=(15, 10))

        go_back_but = tk.Button(
            self.content_frame,
            command=self._build_settings,
            text="Volver",
            font=("Segoe UI", 10, "bold"),
            bg="#BDC3C7",
            fg="white",
            relief="flat",
            width=30,
            pady=6,
            cursor="hand2"
        )
        go_back_but.pack()
        Tooltip(go_back_but, "Volver")


    def _submit_create_user(self):
        """
        Valida y registra un nuevo usuario desde los datos introducidos en el formulario.
        """
        username = self.new_username_reg.get().strip()
        fullname = self.new_fullname.get().strip()
        email = self.new_email.get().strip()
        role = self.new_role.get()

        if not username or not fullname or not email:
            show_popup(self.window, "Error", "Todos los campos son obligatorios.")
            return

        success = register_user_with_email(username, fullname, email, role)
        if success:
            show_popup(self.window, "Éxito", "Usuario creado correctamente. La contraseña se ha enviado al correo.")
            self._load_create_user_form()
        else:
            show_popup(self.window, "Error", "El email ya está registrado.")


    def _load_delete_user_form(self):
        """
        Carga la vista para eliminar usuarios existentes.
        """
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text="Eliminar usuario",
                font=("Segoe UI", 18, "bold"), bg="white", fg="#2C3E50").pack(pady=(0, 25))

        users = list_users()

        for user in users:
            email = user["email"]
            row = tk.Frame(self.content_frame, bg="white")
            row.pack(fill="x", pady=2)

            tk.Label(row, text=f"{user['username']} ({email}) - {user['role']}",
                    bg="white", anchor="w").pack(side="left", padx=5)

            del_but = tk.Button(
                row, 
                command=lambda e=email: self._submit_delete_user(e),
                text="Eliminar",
                bg="#3498DB", 
                fg="white", 
                relief="flat"
            )
            del_but.pack(side="right", padx=5)

        go_back_but = tk.Button(
            self.content_frame,
            command=self._build_settings,
            text="Volver",
            font=("Segoe UI", 10, "bold"),
            bg="#BDC3C7",
            fg="white",
            relief="flat",
            width=30,
            pady=6,
            cursor="hand2"
        )
        go_back_but.pack(pady=(20, 0))
        Tooltip(go_back_but, "Volver")


    def _submit_delete_user(self, email):
        """
        Elimina un usuario del sistema.

        Args:
            email (str): Correo electrónico del usuario a eliminar.
        """
        if email == self.ui.current_email:
            show_popup(self.window, "Error", "No puedes eliminar tu propio usuario.")
            return

        if delete_user(email):
            show_popup(self.window, "Éxito", f"Usuario {email} eliminado.")
            self._load_delete_user_form()
        else:
            show_popup(self.window, "Error", "No se pudo eliminar el usuario.")
