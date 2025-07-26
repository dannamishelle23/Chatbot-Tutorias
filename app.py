#importar auth.py
import autenticacion  

#Importar las librerías necesarias
import streamlit as st
import json
import random
import pickle
import numpy as np
import tensorflow as tf
import re

st.set_page_config(layout="wide")
#Cargar el archivo CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

#Carga modelo y datos
model = tf.keras.models.load_model("chatbot_modelo.keras")
with open("chatbot_data.pkl", "rb") as f:
    all_words, tags, _, _ = pickle.load(f)

with open("intents.json", encoding="utf-8") as f:
    intents = json.load(f)

# Función simple para tokenizar y aplicar stemming ligero
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

def get_response(msg, rol_usuario):
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
    return "No entendí tu pregunta. ¿Puedes intentarlo de otra forma?"

# --- Interfaz Streamlit ---
st.title("Tutorías ESFOT Chatbot")

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
        "Actualizar contraseña",
        "Ver tutorías agendadas",
        "Crear una tutoría",
        "Reprogramar tutoría",
        "Cancelar tutoría",
        "Tutoría Premium",
    ],
    "Docente": [
        "Tutorías programadas para mí",
        "Actualizar perfil",
        "Ver perfil"
    ],
    "Administrador": [
        "Gestión de docentes",
        "Crear nuevo docente",
        "Ver docentes creados",
        "Actualizar la información del docente",
        "Eliminar docente del sistema"
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
        with st.chat_message("user" if remitente == "Tú" else "assistant"):
            st.markdown(texto)

    # Mostrar menú inicial solo una vez
    if st.session_state.mostrar_menu:
        st.markdown("---")
        st.markdown("### Opciones del menú:")
        for opcion in opciones_por_rol.get(st.session_state.rol_usuario, []):
            if st.button(opcion):
                st.session_state.chat.append(("Tú", opcion))
                respuesta = get_response(opcion, st.session_state.rol_usuario)
                st.session_state.chat.append(("Bot", respuesta))
                st.session_state.mostrar_menu = False  # Ocultar menú después de una selección
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

        #Mostrar menú si el usuario escribe "mostrar menú"
        if mensaje_usuario.strip().lower() in ["mostrar menú", "menu", "menú", "ver opciones"]:
            st.session_state.mostrar_menu = True
            st.session_state.chat.append(("Bot", "¿Qué opción deseas del menú?"))
        else:
            respuesta = get_response(mensaje_usuario, st.session_state.rol_usuario)
            st.session_state.chat.append(("Bot", respuesta))
        
        st.rerun()

    #Cerrar sesión
    if st.button("Cerrar sesión"):
        for var in ["estado", "nombre_usuario", "rol_usuario", "correo_usuario", "chat", "mostrar_menu"]:
            st.session_state[var] = "" if var in ["estado", "nombre_usuario", "rol_usuario", "correo_usuario"] else []
        st.session_state.estado = "auth"
        st.rerun()
