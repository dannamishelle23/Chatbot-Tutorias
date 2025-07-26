import streamlit as st
import random
import pickle
import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

#Importar el archivo autenticacion.py
import autenticacion  

#Cargar modelo y utilidades
modelo = load_model("chatbot_modelo.keras")
with open("tokenizer.pickle", "rb") as handle:
    tokenizer = pickle.load(handle)
with open("labels.pickle", "rb") as enc:
    lbl_encoder = pickle.load(enc)
with open("intents.json", encoding="utf-8") as file:
    intents = json.load(file)

#Inicializar estados
if "estado" not in st.session_state:
    st.session_state.estado = "auth" 

if "correo_usuario" not in st.session_state:
    st.session_state.correo_usuario = ""

if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = ""

if "nombre_usuario" not in st.session_state:
    st.session_state.nombre_usuario = ""

if "chat" not in st.session_state:
    st.session_state.chat = []

def obtener_respuesta(texto_usuario):
    secuencia = tokenizer.texts_to_sequences([texto_usuario])
    padded = pad_sequences(secuencia, maxlen=modelo.input_shape[1], padding='post')
    prediccion = modelo.predict(padded)[0]
    tag = lbl_encoder.inverse_transform([np.argmax(prediccion)])[0]

    for intent in intents["intents"]:
        if intent["tag"] == tag:
            return random.choice(intent["responses"])
    return "Lo siento, no entiendo tu pregunta. ¿Podrías ser más específico?"

st.title("Plataforma de Tutorías ESFOT")

if st.session_state.estado == "auth":
    opcion = st.selectbox("Selecciona una opción:", ["Iniciar sesión", "Registrarse"])

    correo = st.text_input("Correo")
    password = st.text_input("Contraseña", type="password")

    if opcion == "Registrarse":
        nombre = st.text_input("Nombre completo")
        rol = st.selectbox("Rol", ["estudiante", "docente", "administrador"])
        if st.button("Registrarse"):
            if autenticacion.registrar_usuario(correo, password, rol, nombre):
                st.success("Cuenta registrada! Ahora puedes iniciar sesión.")
            else:
                st.error("Error al registrar. Verifica los datos o el correo ya existe.")

    elif opcion == "Iniciar sesión":
        if st.button("Iniciar sesión"):
            usuario = autenticacion.login_usuario(correo, password)
            if usuario:
                st.success(f"Has iniciado sesión con éxito, {usuario['nombre']} ({usuario['rol']})")
                st.session_state.estado = "chatbot"
                st.session_state.correo_usuario = correo
                st.session_state.rol_usuario = usuario['rol']
                st.session_state.nombre_usuario = usuario['nombre']
                st.session_state.chat = [
            ("Bot", f"Hola {usuario['nombre']}, bienvenido a la plataforma de tutorías de la ESFOT. ¿En qué puedo ayudarte?")
        ]
            else:
                st.error("Correo o contraseña incorrectos.")

elif st.session_state.estado == "chatbot":
    st.write(f"Usuario: **{st.session_state.nombre_usuario}** | Rol: **{st.session_state.rol_usuario}**")

    mensaje = st.chat_input("Escribe tu pregunta aquí...")

    if mensaje:
        st.session_state.chat.append(("Tú", mensaje))

        saludo_inicial = f"Hola, {st.session_state.nombre_usuario}. "

        if st.session_state.rol_usuario.lower() == "Administrador":
            respuesta = saludo_inicial + obtener_respuesta(mensaje)
        elif st.session_state.rol_usuario.lower() == "Docente":
            respuesta = saludo_inicial + obtener_respuesta(mensaje)
        else:
            respuesta = obtener_respuesta(mensaje)

        st.session_state.chat.append(("Bot", respuesta))

    #Mostrar historial de conversaciones
    st.markdown("--------")
    for remitente, texto in st.session_state.chat:
        if remitente == "Tú":
            with st.chat_message("user"):
                st.markdown(texto)
        else:
            with st.chat_message("assistant"):
                st.markdown(texto)
