import autenticacion  
from tutorias import guardar_tutoria, obtener_tutorias
import streamlit as st
import json
import random
import pickle
import numpy as np
import tensorflow as tf
import re
import os

st.set_page_config(layout="wide")

# Cargar CSS para estilos
if os.path.exists("style.css"):
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with st.container():
    st.image("images/logo_esfot.png", width=120)

# Carga modelo y datos
model = tf.keras.models.load_model("chatbot_modelo.keras")
with open("chatbot_data.pkl", "rb") as f:
    all_words, tags, _, _ = pickle.load(f)

with open("intents.json", encoding="utf-8") as f:
    intents = json.load(f)

# Funciones tokenización y stemming
def tokenize(sentence):
    return re.findall(r'\b\w+\b', sentence.lower())

def stem(word):
    return word.lower().rstrip("ing").rstrip("ed").rstrip("s")

def bag_of_words(sentence):
    words = tokenize(sentence)
    words = [stem(w) for w in words]
    bag = [0] * len(all_words)
    for s in words:
        for i, w in enumerate(all_words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

# Función para agendar tutoría
def agendar_tutoria():
    docentes = [
        {"nombre": "Ing. Ximena Sanchez", "materia": "Fundamentos de Matemática",
         "horarios": ["Lunes 10:00 - 11:00", "Martes 14:00 - 15:00"]},
        {"nombre": "Ing. Alan Cuenca", "materia": "Introduccion a las TIC",
         "horarios": ["Lunes 10:00 - 13:00", "Viernes 15:00 - 16:00"]},
        {"nombre": "Ing. Carlos Yunga", "materia": "Física",
         "horarios": ["Miércoles 08:00 - 09:00", "Viernes 09:00 - 10:00"]},
        {"nombre": "Ing. Edgar Lincango", "materia": "Geometría",
         "horarios": ["Lunes 13:00 - 14:00", "Jueves 10:00 - 11:00"]},
        {"nombre": "Ing. Kleber Sánchez", "materia": "Química",
         "horarios": ["Martes 09:00 - 10:00", "Viernes 11:00 - 12:00"]},
        {"nombre": "Ing. Verónica Caicedo", "materia": "Lenguaje y Comunicación",
         "horarios": ["Miércoles 10:00 - 11:00", "Jueves 14:00 - 15:00"]},
        {"nombre": "Ing. Walter Salas", "materia": "Física I",
         "horarios": ["Lunes 09:00 - 10:00", "Viernes 13:00 - 14:00"]},
        {"nombre": "Ing. Gabriela Cevallos", "materia": "Introducción a las TIC",
         "horarios": ["Martes 11:00 - 12:00", "Jueves 09:00 - 10:00"]},
        {"nombre": "Ing. Ana Torres", "materia": "Estadística",
         "horarios": ["Miércoles 09:00 - 11:00", "Jueves 10:00 - 11:00"]},
    ]

    st.subheader("📚 Agendamiento de Tutoría Académica")

    nombres_docentes = [d["nombre"] for d in docentes]

    if "docente_seleccionado" not in st.session_state or st.session_state.docente_seleccionado not in nombres_docentes:
        st.session_state.docente_seleccionado = nombres_docentes[0]

    seleccion_docente = st.selectbox(
        "Selecciona un docente:",
        nombres_docentes,
        index=nombres_docentes.index(st.session_state.docente_seleccionado)
    )
    st.session_state.docente_seleccionado = seleccion_docente

    docente = next(d for d in docentes if d["nombre"] == seleccion_docente)

    horarios_disponibles = docente["horarios"]

    if "horario_seleccionado" not in st.session_state or st.session_state.horario_seleccionado not in horarios_disponibles:
        st.session_state.horario_seleccionado = horarios_disponibles[0]

    seleccion_horario = st.selectbox(
        f"Selecciona un horario disponible para {seleccion_docente}:",
        horarios_disponibles,
        index=horarios_disponibles.index(st.session_state.horario_seleccionado)
    )
    st.session_state.horario_seleccionado = seleccion_horario

    if st.button("Agendar tutoría"):
        guardar_tutoria(st.session_state.correo_usuario, docente['nombre'], docente['materia'], st.session_state.horario_seleccionado)
        st.session_state.tutoria_agendada = True
        st.success("¡Tutoría agendada con éxito!")
        st.rerun()

    if st.session_state.get("tutoria_agendada"):
        st.markdown(f"Docente: {docente['nombre']}")
        st.markdown(f"Materia: {docente['materia']}")
        st.markdown(f"Horario: {st.session_state.horario_seleccionado}")
        st.text("¿Deseas ayuda en algo más?")

    if st.session_state.get("mostrar_agendamiento") or st.session_state.get("tutoria_agendada"):
        if st.button("Volver al menú", key="volver_menu_agendar"):
            st.session_state.tutoria_agendada = False
            st.session_state.mostrar_agendamiento = False
            st.session_state.mostrar_menu = True
            st.rerun()

# Mostrar tutorías agendadas del usuario
def mostrar_tutorias_agendadas():
    st.subheader("Tus tutorías agendadas")
    tutorias = obtener_tutorias(st.session_state.correo_usuario)

    if not tutorias:
        st.info("No tienes tutorías agendadas.")
    else:
        for i, t in enumerate(tutorias, 1):
            st.markdown(f"**{i}. Docente:** {t['docente']}")
            st.markdown(f"   - Materia: {t['materia']}")
            st.markdown(f"   - Horario: {t['horario']}")
            st.markdown("---")

    if st.button("Volver al menú", key="volver_menu_tutorias"):
        st.session_state.mostrar_tutorias = False
        st.session_state.mostrar_menu = True
        st.session_state.chat.append(("Bot", "¿Qué opción deseas del menú?"))
        st.rerun()

# Procesar respuesta chatbot o comandos
def get_response(msg, rol_usuario):
    if msg.strip().lower() in ["crear una tutoría", "agendar tutoría", "nueva tutoría"]:
        st.session_state.mostrar_agendamiento = True
        st.session_state.tutoria_agendada = False
        st.session_state.mostrar_tutorias = False
        return "Perfecto, te ayudaré a reservar una tutoría de acuerdo a la disponibilidad de tu docente. ¿Con qué profesor quieres agendar la tutoría?"

    # Manejo con modelo
    bow = bag_of_words(msg)
    result = model.predict(np.array([bow]))[0]
    idx = np.argmax(result)
    tag = tags[idx]
    confidence = result[idx]

    if confidence > 0.7:
        for intent in intents["intents"]:
            if intent["tag"] == tag:
                intent_rol = intent.get("rol", "Todos")
                if intent_rol == "Todos" or intent_rol.lower() == rol_usuario.lower():
                    return random.choice(intent["responses"])
                else:
                    return "No estás autorizado para esta acción."

    return "No entendí tu pregunta. ¿Podrías ser más específico?"

# Opciones por rol
opciones_por_rol = {
    "Estudiante": [
        "Actualizar perfil",
        "Ver tutorías agendadas",
        "Crear una tutoría",
        "Reprogramar tutoría",
        "Cancelar tutoría",
        "Tutoría Premium",
        "Acceder a tutoría premium",
        "Pago tutoria premium",
        "Pagos realizados"
    ],
    "Docente": [
        "Tutorías programadas para mí",
        "Actualizar perfil",
        "Ver perfil",
    ],
    "Administrador": [
        "Gestión de docentes",
        "Crear nuevo docente",
        "Ver docentes creados",
        "Actualizar la información del docente",
        "Eliminar docente del sistema",
        "Actualizar perfil",
        "Actualizar contraseña",
    ]
}

# Inicializar estados
for var in ["estado", "nombre_usuario", "rol_usuario", "correo_usuario", "chat", "mostrar_menu", "mostrar_agendamiento", "tutoria_agendada", "mostrar_tutorias"]:
    if var not in st.session_state:
        if var == "chat":
            st.session_state[var] = []
        else:
            st.session_state[var] = False if var != "estado" else ""

if st.session_state.estado == "":
    st.session_state.estado = "auth"

# Título general
st.title("Chatbot - Tutorías ESFOT")

# Pantalla autenticación
if st.session_state.estado == "auth":
    opcion = st.selectbox("Inicia sesión o regístrate para acceder a la plataforma", ["Iniciar sesión", "Registrarse"])

    if opcion == "Registrarse":
        nombre = st.text_input("Nombre completo")
        correo = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        rol = st.selectbox("Rol", ["Estudiante", "Docente"])

        if st.button("Registrarse"):
            if not nombre or not correo or not password or not rol:
                st.warning("¡Por favor completa todos los campos!")
            elif "@" not in correo or "." not in correo:
                st.warning("Introduce un correo válido.")
            else:
                resultado = autenticacion.registrar_usuario(nombre, correo, password, rol)
                if resultado["error"]:
                    if "usuario_existente" in resultado:
                        u = resultado["usuario_existente"]
                        st.error(f"Correo ya registrado para {u['nombre']} con rol {u['rol']}.")
                    else:
                        st.error("Error al registrar.")
                else:
                    st.success("Registro exitoso. Ahora puedes iniciar sesión.")
                    st.rerun()

    elif opcion == "Iniciar sesión":
        correo = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")

        if st.button("Iniciar sesión"):
            if not correo or not password:
                st.warning("Completa ambos campos.")
            else:
                usuario = autenticacion.login_usuario(correo, password)
                if usuario:
                    st.success(f"Has iniciado sesión como {usuario['nombre']} ({usuario['rol']})")
                    st.session_state.estado = "chat"
                    st.session_state.nombre_usuario = usuario["nombre"]
                    st.session_state.rol_usuario = usuario["rol"]
                    st.session_state.correo_usuario = usuario["correo"]
                    st.session_state.mostrar_menu = True
                    st.session_state.mostrar_agendamiento = False
                    st.session_state.mostrar_tutorias = False
                    st.session_state.tutoria_agendada = False
                    st.session_state.chat = [("Bot", f"Hola {usuario['nombre']}, gusto en saludarte! Te doy una cordial bienvenida al sistema de gestion de tutorias de la ESFOT! Soy un bot diseñado para asistir a estudiantes nuevos en la plataforma. ¿En qué puedo ayudarte?")]
                    st.rerun()
                else:
                    st.error("Correo o contraseña incorrectos.")

# Pantalla chatbot
elif st.session_state.estado == "chat":
    st.write(f"Usuario: **{st.session_state.nombre_usuario}**")
    st.write(f"Rol: **{st.session_state.rol_usuario}**")

    # Mostrar historial
    for remitente, texto in st.session_state.chat:
        clase = "user-message" if remitente == "Tú" else "bot-message"
        st.markdown(f"<div class='chat-bubble {clase}'>{texto}</div>", unsafe_allow_html=True)

    # Mostrar tutorías agendadas si está activo
    if st.session_state.get("mostrar_tutorias", False):
        mostrar_tutorias_agendadas()

    # Mostrar agendamiento si está activo
    elif st.session_state.get("mostrar_agendamiento", False):
        agendar_tutoria()

    else:
        # Mostrar botón para mostrar menú si no está visible
        if not st.session_state.get("mostrar_menu", False):
            if st.button("Mostrar menú"):
                st.session_state.mostrar_menu = True
                st.session_state.chat.append(("Bot", "¿Qué opción deseas del menú?"))
                st.rerun()

        # Mostrar menú si está visible
        if st.session_state.get("mostrar_menu", False):
            st.markdown("---")
            st.markdown("Opciones del menú:")
            for opcion in opciones_por_rol.get(st.session_state.rol_usuario, []):
                if st.button(opcion):
                    st.session_state.chat.append(("Tú", opcion))
                    # Si es "Ver tutorías agendadas", mostrar tutorías
                    if opcion == "Ver tutorías agendadas":
                        st.session_state.mostrar_tutorias = True
                        st.session_state.mostrar_menu = False
                        st.session_state.mostrar_agendamiento = False
                    elif opcion == "Crear una tutoría":
                        st.session_state.mostrar_agendamiento = True
                        st.session_state.mostrar_menu = False
                        st.session_state.mostrar_tutorias = False
                    else:
                        respuesta = get_response(opcion, st.session_state.rol_usuario)
                        if respuesta:
                            st.session_state.chat.append(("Bot", respuesta))
                        st.session_state.mostrar_menu = False
                        st.session_state.mostrar_tutorias = False
                        st.session_state.mostrar_agendamiento = False
                    st.rerun()

    #Input de usuario
    mensaje_usuario = st.chat_input("Escribe tu mensaje...")
    if mensaje_usuario:
        st.session_state.chat.append(("Tú", mensaje_usuario))

        #Mostrar menú con texto
        if mensaje_usuario.strip().lower() in ["mostrar menú", "menu", "menú", "ver opciones"]:
            st.session_state.mostrar_menu = True
            st.session_state.mostrar_tutorias = False
            st.session_state.mostrar_agendamiento = False
            st.session_state.chat.append(("Bot", "¿Qué opción deseas del menú?"))

        #Mostrar tutorías con texto
        elif mensaje_usuario.strip().lower() in ["ver tutorías agendadas", "ver tutorias agendadas"]:
            st.session_state.mostrar_tutorias = True
            st.session_state.mostrar_menu = False
            st.session_state.mostrar_agendamiento = False

        else:
            #Si el usuario escribe alguna opción del menú manualmente
            if mensaje_usuario in opciones_por_rol.get(st.session_state.rol_usuario, []):
                st.session_state.mostrar_menu = False
                st.session_state.mostrar_tutorias = False
                st.session_state.mostrar_agendamiento = False

            respuesta = get_response(mensaje_usuario, st.session_state.rol_usuario)
            if respuesta:
                st.session_state.chat.append(("Bot", respuesta))

        st.rerun()

    #Botón cerrar sesión
    if st.button("Cerrar sesión"):
        for var in ["estado", "nombre_usuario", "rol_usuario", "correo_usuario", "chat", "mostrar_menu", "mostrar_tutorias", "mostrar_agendamiento", "tutoria_agendada"]:
            st.session_state[var] = "" if var in ["estado", "nombre_usuario", "rol_usuario", "correo_usuario"] else False if var != "chat" else []
        st.session_state.estado = "auth"
        st.rerun()
