import os
import json

#Ruta del archivo de usuarios.json
archivo_usuarios = "usuarios.json"

#Cargar usuarios si existe
def cargar_usuarios():
    if os.path.exists(archivo_usuarios):
        with open(archivo_usuarios, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

#Guardar usuarios en usuarios.json
def guardar_usuarios(usuarios):
    with open(archivo_usuarios, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=4)

#Registrar nuevo usuario
def registrar_usuario(nombre, correo, password, rol):
    usuarios = cargar_usuarios()

    if not correo or not password or not rol:
        return {"error": True, "mensaje": "Campos vacíos"}

    #Verificar si el correo ya está registrado
    for u in usuarios:
        if u.get("correo") == correo:
            return {
                "error": True,
                "mensaje": "Correo ya registrado",
                "usuario_existente": u
            }

    nuevo_usuario = {
        "nombre": nombre,
        "correo": correo,
        "password": password,
        "rol": rol
    }
    usuarios.append(nuevo_usuario)
    guardar_usuarios(usuarios)
    return {"error": False}

# Login del usuario
def login_usuario(correo, password):
    usuarios = cargar_usuarios()
    for u in usuarios:
        if u["correo"] == correo and u["password"] == password:
            return u    #Retorna el dict completo
    return None
