import streamlit as st
import random
import pickle
import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Cargar modelo y utilidades
modelo = load_model("chatbot_modelo.keras")
with open("tokenizer.pickle", "rb") as handle:
    tokenizer = pickle.load(handle)
with open("labels.pickle", "rb") as enc:
    lbl_encoder = pickle.load(enc)
with open("intents.json", encoding="utf-8") as file:
    intents = json.load(file)

# Inicializar estado para manejar diálogo con nombre y mensaje
if "chat" not in st.session_state:
    st.session_state.chat = []

if "estado" not in st.session_state:
    st.session_state.estado = "normal"  # normal o esperando_nombre

if "nombre_usuario" not in st.session_state:
    st.session_state.nombre_usuario = ""

if "saludo_realizado" not in st.session_state:
    st.session_state.saludo_realizado = False  # Aquí guardamos si ya saludó o no

# Mostrar título
st.title("Chatbot Tutorías Académicas")
st.write("Escribe tu mensaje aquí...")

# Input del usuario
mensaje = st.chat_input("Tú:")

if mensaje:
    if st.session_state.estado == "normal":
        #Procesar mensaje y predecir tag
        secuencia = tokenizer.texts_to_sequences([mensaje])
        padded = pad_sequences(secuencia, maxlen=modelo.input_shape[1], padding='post')
        prediccion = modelo.predict(padded)[0]
        tag_predicho = lbl_encoder.inverse_transform([np.argmax(prediccion)])[0]

        if tag_predicho == "saludo" and not st.session_state.nombre_usuario:
            respuesta = "Hola, bienvenido a la plataforma de Tutorías ESFOT. ¿Cómo te llamas?"
            st.session_state.estado = "esperando_nombre"
            st.session_state.saludo_realizado = True
        else:
            # Buscar respuesta en intents
            respuesta = None
            for intent in intents["intents"]:
                if intent["tag"] == tag_predicho:
                    respuesta = random.choice(intent["responses"])
                    break
            if respuesta is None:
                respuesta = "Lo siento, no entiendo tu pregunta. ¿Podrías ser más específico?"

    elif st.session_state.estado == "esperando_nombre":
        # Guardar el nombre del usuario
        nombre = mensaje.strip().title()
        st.session_state.nombre_usuario = nombre
        respuesta = f"¡Mucho gusto, {nombre}! ¿En qué puedo ayudarte?"
        st.session_state.estado = "normal"

    # Guardar mensajes en el chat para mostrar
    st.session_state.chat.append(("Tú", mensaje))
    st.session_state.chat.append(("Bot", respuesta))

# Mostrar historial tipo chat
st.markdown("---")
for remitente, texto in st.session_state.chat:
    if remitente == "Tú":
        with st.chat_message("user"):
            st.markdown(texto)
    else:
        with st.chat_message("assistant"):
            st.markdown(texto)
