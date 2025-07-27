import json
import os

def guardar_tutoria(correo, docente, materia, horario):
    archivo = "tutorias_guardadas.json"

    # Cargar tutorías previas
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            tutorias = json.load(f)
    else:
        tutorias = {}

    # Agregar tutoría para el usuario
    if correo not in tutorias:
        tutorias[correo] = []

    tutorias[correo].append({
        "docente": docente,
        "materia": materia,
        "horario": horario
    })

    # Guardar
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(tutorias, f, indent=4, ensure_ascii=False)

def obtener_tutorias(correo):
    archivo = "tutorias_guardadas.json"
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            tutorias = json.load(f)
        return tutorias.get(correo, [])
    return []