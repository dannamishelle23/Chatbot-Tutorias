import json
import os
import streamlit as st

def guardar_tutoria(correo, nombre_docente, materia, horario):
    nueva_tutoria = {
        "correo": correo,
        "docente": nombre_docente,
        "materia": materia,
        "horario": horario
    }

    tutorias = []

    if os.path.exists("tutorias_guardadas.json"):
        try:
            with open("tutorias_guardadas.json", "r") as f:
                contenido = f.read().strip()
                if contenido:
                    tutorias = json.loads(contenido)
        except json.JSONDecodeError:
            tutorias = []

    #Evitar duplicados exactos
    for t in tutorias:
        if t["correo"] == correo and t["horario"] == horario:
            st.warning("Ya tienes una tutoría agendada en ese horario.")
            return  #Si ya existe, no guardar de nuevo

    tutorias.append(nueva_tutoria)

    with open("tutorias_guardadas.json", "w") as f:
        json.dump(tutorias, f, indent=4)

def obtener_tutorias(correo):
    archivo = "tutorias_guardadas.json"
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            tutorias = json.load(f)
        # Filtrar solo las tutorías del estudiante con ese correo
        return [t for t in tutorias if t["correo"] == correo]
    return []
