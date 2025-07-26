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
def registrar_usuario(correo, password, rol):
    usuarios = cargar_usuarios()
    #Verificar que no existan espacios en blanco
    if not correo or not password or not rol:
        return False
    #Verificar si el correo ya está registrado
    if any(u["correo"] == correo for u in usuarios):
        return False  #Usuario ya existe
    #Agregar nuevo usuario
    usuarios.append({"Correo": correo, "Contraseña": password, "Rol": rol})
    guardar_usuarios(usuarios)
    return True

#Login del usuario
def login_usuario(correo, password):
    usuarios = cargar_usuarios()
    for u in usuarios:
        if u["correo"] == correo and u["password"] == password:
            return u["rol"]
    return None