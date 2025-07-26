import streamlit as st
import random
import pickle
import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

#1. Importar el archivo autenticacion.py
import autenticacion  

#2. Cargar modelo y utilidades
modelo = load_model("chatbot_modelo.keras")
with open("tokenizer.pickle", "rb") as handle:
    tokenizer = pickle.load(handle)
with open("labels.pickle", "rb") as enc:
    lbl_encoder = pickle.load(enc)
with open("intents.json", encoding="utf-8") as file:
    intents = json.load(file)

#3. Inicializar estados
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

#4. Funcion para obtener la respuesta que el usuario escriba en el chat
def obtener_respuesta(texto_usuario):
    secuencia = tokenizer.texts_to_sequences([texto_usuario])
    padded = pad_sequences(secuencia, maxlen=modelo.input_shape[1], padding='post')
    prediccion = modelo.predict(padded)[0]
    tag = lbl_encoder.inverse_transform([np.argmax(prediccion)])[0]

    for intent in intents["intents"]:
        if intent["tag"] == tag:
            return random.choice(intent["responses"])
    return "Lo siento, no entiendo tu pregunta. ¿Podrías ser más específico?"

#Añadir un titulo a la interfaz
st.title("Plataforma de Tutorías ESFOT")

#5. Mostrar la interfaz para que el usuario inicie sesion o se registre
if st.session_state.estado == "auth":
    opcion = st.selectbox("Selecciona una opción:", ["Iniciar sesión", "Registrarse"])

    #Si el usuario elige "Registro"
    if opcion == "Registrarse":
        nombre = st.text_input("Nombre completo")
        correo = st.text_input("Correo")
        password = st.text_input("Contraseña", type="password")
        rol = st.selectbox("Rol", ["Estudiante", "Docente", "Administrador"])
        if st.button("Registrarse"):
            if not nombre or not correo or not password or not rol:
                st.warning("Todos los campos son obligatorios!")
            elif "@" not in correo or "." not in correo:
                st.warning("Introduce un correo electrónico válido.")
            else:
                respuesta = autenticacion.registrar_usuario(nombre, correo, password, rol)
                if not respuesta["error"]:
                    st.success("Cuenta registrada! Ahora puedes iniciar sesión.")
                    st.session_state.estado = "auth"
                else:
                    if "usuario_existente" in respuesta:
                        u = respuesta["usuario_existente"]
                        st.error(f"Ya existe una cuenta registrada con ese correo ({u['correo']}) con rol de **{u['rol']}**.")
                    else:
                        st.error("No se pudo registrar. Verifica los campos.")

    #Si el usuario ya tiene cuenta creada
    elif opcion == "Iniciar sesión":
        correo = st.text_input("Correo")
        password = st.text_input("Contraseña", type="password")
        if st.button("Iniciar sesión"):
            if not correo or not password:
                st.warning("Completa todos los campos para iniciar sesión.")
            else:
                usuario = autenticacion.login_usuario(correo, password)
                if usuario:
                    st.success(f"Has iniciado sesión con éxito, {usuario['nombre']} ({usuario['rol']})")
                    st.session_state.estado = "chatbot"
                    st.session_state.nombre_usuario = usuario['nombre']
                    st.session_state.correo_usuario = correo
                    st.session_state.rol_usuario = usuario['rol']
                    st.session_state.chat = [
                ("Bot", f"Hola {usuario['nombre']}, bienvenido a la plataforma de tutorías de la ESFOT. ¿En qué puedo ayudarte?")
            ]
                else:
                    st.error("Correo o contraseña incorrectos.")

#6. Mostrar al usuario la interfaz del chatbot luego de iniciar sesion
elif st.session_state.estado == "chatbot":
    st.write(f"Usuario: **{st.session_state.nombre_usuario}**")
    st.write(f"Rol: **{st.session_state.rol_usuario}**")
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
    
    #Mostrar el historial de conversaciones
    st.markdown("--------")
    for remitente, texto in st.session_state.chat:
        if remitente == "Tú":
            with st.chat_message("user"):
                st.markdown(texto)
        else:
            with st.chat_message("assistant"):
                st.markdown(texto)
