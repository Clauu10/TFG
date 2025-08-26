from email.mime.text import MIMEText
import json
import random
import smtplib
import string
import bcrypt
import os
from datetime import datetime, timezone

# Ruta absoluta al archivo users.json
USERS = os.path.join(os.path.dirname(__file__), '..', '..', 'src/users_data', 'users.json')
USERS = os.path.abspath(USERS)


def _load_users():
    """
    Carga los datos de usuarios desde un archivo JSON.

    Returns:
        dict: Diccionario que contiene una lista de usuarios.
              Si el archivo no existe, devuelve {'users': []}.
    """
    if not os.path.exists(USERS):
        return {"users": []}

    with open(USERS, "r", encoding="utf-8") as file:
        return json.load(file)


def _save_users(data):
    """
    Guarda los datos de usuarios en un archivo JSON.

    Args:
        data (dict): Diccionario que contiene los datos de los usuarios.
    """
    directory = os.path.dirname(USERS)
    os.makedirs(directory, exist_ok=True)

    with open(USERS, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def _hash_password(password):
    """
    Genera un hash a partir de una contraseña en texto plano usando bcrypt.

    Args:
        password (str): Contraseña en texto plano.

    Returns:
        str: Contraseña hasheada en formato UTF-8.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def _verify_password(password, hash):
    """
    Comprueba si una contraseña coincide con un hash.

    Args:
        password (str): Contraseña en texto plano.
        hash (str): Hash con el que se compara la contraseña.

    Returns:
        bool: True si la contraseña coincide con el hash, False en caso contrario.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))


def register_user(username, fullname, email, password, role="worker"):
    """
    Registra un nuevo usuario.

    Args:
        username (str): Nombre de usuario.
        fullname (str): Nombre completo del usuario.
        email (str): Correo electrónico del usuario.
        password (str): Contraseña en texto plano.
        role (str, optional): Rol del usuario. Por defecto "worker".

    Returns:
        bool: True si el usuario fue registrado correctamente, False si el correo ya está registrado.
    """
    data = _load_users()

    if any(user["email"] == email for user in data["users"]):
        return False

    password_hash = _hash_password(password)
    user_data = {
        "username": username,
        "fullname": fullname,
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    data["users"].append(user_data)
    _save_users(data)
    return True


def _generate_password(length=10):
    """
    Genera una contraseña aleatoria segura.

    Args:
        length (int, optional): Longitud de la contraseña (por defecto 10 caracteres).

    Returns:
        str: Contraseña generada.
    """
    chars = string.ascii_letters + string.digits + "!@#$%&"
    return ''.join(random.choices(chars, k=length))


def _send_password_email(to_email, password):
    """
    Envía un correo electrónico con la contraseña temporal al nuevo usuario.

    Args:
        to_email (str): Dirección de correo electrónico del destinatario.
        password (str): Contraseña temporal generada.
    """
    from_email = "noreply.residuos@gmail.com"
    from_password = "difs memt ksvi qstd" 

    subject = "Contraseña temporal para tu cuenta"
    body = f"""
    Hola,

    Tu cuenta ha sido registrada exitosamente.
    Esta es tu contraseña temporal: {password}

    Por favor, cámbiala después de iniciar sesión.

    Saludos,
    Clasificador de Residuos
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, from_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Error al enviar correo: {e}")


def send_recovery_email(to_email, code):
    """
    Envía un correo con el código de recuperación de contraseña.

    Args:
        to_email (str): Dirección de correo electrónico del destinatario.
        code (str): Código de recuperación.
    """
    from_email = "noreply.residuos@gmail.com"
    from_password = "difs memt ksvi qstd"  

    subject = "Solicitud de recuperación de contraseña"
    body = f"""
    Hola,

    Hemos recibido tu solicitud para restablecer tu contraseña.
    Tu código de recuperación es: {code}

    Si no solicitaste esto, puedes ignorar este mensaje.

    Clasificador de Residuos
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, from_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Error al enviar correo: {e}")


def list_users():
    """
    Devuelve la lista de usuarios registrados.

    Returns:
        list: Lista de diccionarios de usuarios.
    """
    data = _load_users()
    return data.get("users", [])


def register_user_with_email(username, fullname, email, role="worker"):
    """
    Registra un nuevo usuario, genera contraseña aleatoria y la envía por correo.

    Args:
        username (str): Nombre de usuario.
        fullname (str): Nombre completo del usuario.
        email (str): Dirección de correo electrónico.
        role (str, optional): Rol del usuario (por defecto "worker").

    Returns:
        bool: True si el usuario se creó correctamente, False si el correo ya existe.
    """
    password = _generate_password()
    success = register_user(username, fullname, email, password, role)
    if success:
        _send_password_email(email, password)
    return success


def authenticate_user(email, password):
    """
    Autentica a un usuario con su correo y contraseña.

    Args:
        email (str): Correo electrónico del usuario.
        password (str): Contraseña en texto plano.

    Returns:
        dict|None: Diccionario del usuario si las credenciales son válidas, o None si no coinciden.
    """
    data = _load_users()

    for user in data["users"]:
        if user["email"] == email and _verify_password(password, user["password_hash"]):
            return user
    return None


def update_password(email, new_password):
    """
    Actualiza la contraseña del usuario.

    Args:
        email (str): Correo electrónico del usuario.
        new_password (str): Nueva contraseña en texto plano.

    Returns:
        bool: True si la contraseña se actualizó correctamente, False si el correo no fue encontrado.
    """
    data = _load_users()

    for user in data["users"]:
        if user["email"] == email:
            user["password_hash"] = _hash_password(new_password)
            _save_users(data)
            return True

    return False


def update_username(email, new_username):
    """
    Actualiza el nombre de usuario de un usuario identificado por su email.

    Args:
        email (str): Correo electrónico del usuario.
        new_username (str): Nuevo nombre de usuario.

    Returns:
        bool: True si se actualizó, False si no se encontró el usuario o el nombre ya existe.
    """
    data = _load_users()

    for u in data["users"]:
        if u["username"].strip().lower() == new_username.strip().lower() and u["email"] != email:
            return False

    for user in data["users"]:
        if user["email"] == email:
            user["username"] = new_username.strip()
            _save_users(data)
            return True

    return False


def delete_user(email):
    """
    Elimina un usuario por su correo electrónico.

    Args:
        email (str): Correo electrónico del usuario a eliminar.

    Returns:
        bool: True si el usuario fue eliminado, False se encontró.
    """
    data = _load_users()
    new_users = [u for u in data["users"] if u["email"] != email]

    if len(new_users) == len(data["users"]):
        return False

    data["users"] = new_users
    _save_users(data)
    return True

