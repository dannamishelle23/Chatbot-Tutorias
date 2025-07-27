#importar auth.py
import autenticacion  

#Importar el archivo de tutorias.py
from tutorias import guardar_tutoria, obtener_tutorias

#Importar las librerías necesarias
import streamlit as st
import json
import random
import pickle
import numpy as np
import tensorflow as tf
import re

st.set_page_config(layout="wide")

#Cargar el archivo CSS para personalizar la interfaz
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with st.container():
    st.image("images/logo_esfot.png", width=120)

#Carga modelo y datos
model = tf.keras.models.load_model("chatbot_modelo.keras")
with open("chatbot_data.pkl", "rb") as f:
    all_words, tags, _, _ = pickle.load(f)

with open("intents.json", encoding="utf-8") as f:
    intents = json.load(f)

#Función simple para tokenizar y aplicar stemming ligero
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

def agendar_tutoria():
    docentes = [
        {"nombre": "Ing. Ximena Sanchez", "materia": "Fundamentos de Matemática",
         "horarios": ["Lunes 10:00 - 11:00", "Martes 14:00 - 15:00"]},
        {"nombre": "Ing. Pedro Salinas", "materia": "Física",
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
    ]

    st.subheader("📚 Agendamiento de Tutoría Académica")

    nombres_docentes = [d["nombre"] for d in docentes]

    #Inicializar estado para docente seleccionado si no existe o no es válido
    if "docente_seleccionado" not in st.session_state or st.session_state.docente_seleccionado not in nombres_docentes:
        st.session_state.docente_seleccionado = nombres_docentes[0]

    #Mostrar selectbox para elegir docente, con índice del valor guardado
    seleccion_docente = st.selectbox(
        "Selecciona un docente:",
        nombres_docentes,
        index=nombres_docentes.index(st.session_state.docente_seleccionado)
    )
    st.session_state.docente_seleccionado = seleccion_docente

    #Obtener docente completo de acuerdo al que el usuario haya seleccionado
    docente = next(d for d in docentes if d["nombre"] == seleccion_docente)

    horarios_disponibles = docente["horarios"]

    # Inicializar estado para horario seleccionado si no existe o no es válido
    if "horario_seleccionado" not in st.session_state or st.session_state.horario_seleccionado not in horarios_disponibles:
        st.session_state.horario_seleccionado = horarios_disponibles[0]

    # Mostrar selectbox para elegir horario, con índice del valor guardado
    seleccion_horario = st.selectbox(
        f"Selecciona un horario disponible para {seleccion_docente}:",
        horarios_disponibles,
        index=horarios_disponibles.index(st.session_state.horario_seleccionado)
    )
    st.session_state.horario_seleccionado = seleccion_horario

    if st.button("Agendar tutoría"):
       # Guardamos la confirmación y mostramos resumen
        st.session_state.tutoria_agendada = True
        st.success("¡Tutoría agendada con éxito!")
        guardar_tutoria(st.session_state.correo_usuario, docente["nombre"], docente["materia"], seleccion_horario)
        st.markdown(f"Docente: {docente['nombre']}")
        st.markdown(f"Materia: {docente['materia']}")
        st.markdown(f"Horario: {seleccion_horario}")
        st.markdown("\u00bfDeseas ayuda en algo más?")

        if st.button("Volver al menú"):
            st.session_state.tutoria_agendada = False
            st.session_state.mostrar_agendamiento = False
            st.session_state.mostrar_menu = True
            st.rerun()

    elif "tutoria_agendada" in st.session_state and st.session_state.tutoria_agendada:
        docente = next(d for d in docentes if d["nombre"] == st.session_state.docente_seleccionado)
        st.success("¡Tutoría ya está agendada!")
        st.markdown(f"Docente: {docente['nombre']}")
        st.markdown(f"Materia: {docente['materia']}")
        st.markdown(f"Horario: {st.session_state.horario_seleccionado}")
        st.markdown("\u00bfDeseas ayuda en algo más?")

        if st.button("Volver al menú"):
            st.session_state.tutoria_agendada = False
            st.session_state.mostrar_agendamiento = False
            st.session_state.mostrar_menu = True
            st.rerun()

    else:
        st.info("Selecciona un docente y horario para agendar tu tutoría.")

def get_response(msg, rol_usuario):
    if msg.strip().lower() in ["crear una tutoría", "agendar tutoría", "nueva tutoría"]:
        st.session_state.mostrar_agendamiento = True
        return "Claro, vamos a agendar una tutoría. Selecciona un docente y luego el horario."

    elif msg.strip().lower() == "ver tutorías agendadas":
        tutorias = obtener_tutorias(st.session_state.correo_usuario)
        if tutorias:
            texto = "Estas son tus tutorías agendadas:\n\n"
            for t in tutorias:
                texto += f"- Docente: {t['docente']}, Materia: {t['materia']}, Horario: {t['horario']}\n"
            return texto
        else:
            return "No tienes tutorías agendadas aún."
        
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

#Interfaz de Streamlit para el usuario
st.title("Chatbot - Tutorías ESFOT")

# Inicializar estados
for var in ["estado", "nombre_usuario", "rol_usuario", "correo_usuario", "chat", "mostrar_menu"]:
    if var not in st.session_state:
        st.session_state[var] = "" if var in ["estado", "nombre_usuario", "rol_usuario", "correo_usuario"] else []

if st.session_state.estado == "":
    st.session_state.estado = "auth"

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

#Pantalla de autenticación
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
                    st.session_state.mostrar_menu = True  # Mostrar menú solo una vez
                    st.session_state.chat = [("Bot", f"Hola {usuario['nombre']}, gusto en saludarte! Te doy una cordial bienvenida al sistema de gestion de tutorias de la ESFOT! Soy un bot diseñado para asistir a estudiantes nuevos en la plataforma. ¿En qué puedo ayudarte?")]
                    st.rerun()
                else:
                    st.error("Correo o contraseña incorrectos.")

# Pantalla del chatbot
elif st.session_state.estado == "chat":
    st.write(f"Usuario: **{st.session_state.nombre_usuario}**")
    st.write(f"Rol: **{st.session_state.rol_usuario}**")

    # Mostrar historial
    for remitente, texto in st.session_state.chat:
        clase = "user-message" if remitente == "Tú" else "bot-message"
        st.markdown(f"<div class='chat-bubble {clase}'>{texto}</div>", unsafe_allow_html=True)

    if st.session_state.get("mostrar_agendamiento"):
        agendar_tutoria()
    #Evita que se muestre repetidamente una vez hecho
    if "tutoria_agendada" in st.session_state and st.session_state.tutoria_agendada:
        st.session_state.mostrar_agendamiento = False

    # Mostrar menú inicial solo una vez
    if st.session_state.mostrar_menu:
        st.markdown("---")
        st.markdown("Opciones del menú:")
        for opcion in opciones_por_rol.get(st.session_state.rol_usuario, []):
            if st.button(opcion):
                st.session_state.chat.append(("Tú", opcion))
                respuesta = get_response(opcion, st.session_state.rol_usuario)
                st.session_state.chat.append(("Bot", respuesta))
                st.session_state.mostrar_menu = False  #Ocultar menú después de una selección
                st.rerun()

    #Botón para volver a mostrar menú
    if st.button("Mostrar menú"):
        st.session_state.mostrar_menu = True
        st.session_state.chat.append(("Bot", "¿Qué opción deseas del menú?"))
        st.rerun()

    #Input del usuario
    mensaje_usuario = st.chat_input("Escribe tu mensaje...")
    if mensaje_usuario:
        st.session_state.chat.append(("Tú", mensaje_usuario))

        # Mostrar menú si el usuario escribe algo relacionado
        if mensaje_usuario.strip().lower() in ["mostrar menú", "menu", "menú", "ver opciones"]:
            st.session_state.mostrar_menu = True
            st.session_state.chat.append(("Bot", "¿Qué opción deseas del menú?"))
        else:
            # Ocultar menú si el usuario escribe manualmente una opción válida
            if mensaje_usuario in opciones_por_rol.get(st.session_state.rol_usuario, []):
                st.session_state.mostrar_menu = False

            respuesta = get_response(mensaje_usuario, st.session_state.rol_usuario)
            if respuesta: 
                st.session_state.chat.append(("Bot", respuesta))
        
        st.rerun()

    #Cerrar sesión
    if st.button("Cerrar sesión"):
        for var in ["estado", "nombre_usuario", "rol_usuario", "correo_usuario", "chat", "mostrar_menu"]:
            st.session_state[var] = "" if var in ["estado", "nombre_usuario", "rol_usuario", "correo_usuario"] else []
        st.session_state.estado = "auth"
        st.rerun()
