import json
import numpy as np
import random
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

#Cargar el archivo intents.json
with open("intents.json", encoding="utf-8") as archivo:
    datos = json.load(archivo)

#Extraer datos
tags = []
entradas = []
respuestas = {}

for intent in datos["intents"]:
    for pattern in intent["patterns"]:
        entradas.append(pattern)
        tags.append(intent["tag"])
    respuestas[intent["tag"]] = intent["responses"]

#Codificar etiquetas
lbl_encoder = LabelEncoder()
lbl_encoder.fit(tags)
etiquetas = lbl_encoder.transform(tags)

#Tokenizar texto
tokenizer = Tokenizer(num_words=1000, oov_token="<OOV>")
tokenizer.fit_on_texts(entradas)
secuencias = tokenizer.texts_to_sequences(entradas)
padded = pad_sequences(secuencias, padding="post")

#Crear modelo
modelo = Sequential()
modelo.add(Dense(128, input_shape=(padded.shape[1],), activation='relu'))
modelo.add(Dropout(0.5))
modelo.add(Dense(64, activation='relu'))
modelo.add(Dropout(0.3))
modelo.add(Dense(len(set(tags)), activation='softmax'))

modelo.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(learning_rate=0.01), metrics=['accuracy'])

#Entrenar el modelo
x_train, x_val, y_train, y_val = train_test_split(padded, etiquetas, test_size=0.2, random_state=42)
history = modelo.fit(x_train, y_train, 
                    validation_data=(x_val, y_val),
                    epochs=100, 
                    verbose=1)

#Guardar modelo y utilidades
modelo.save("chatbot_modelo.keras", save_format="keras")              #Guardar el modelo en formato .keras
with open("tokenizer.pickle", "wb") as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open("labels.pickle", "wb") as enc:
    pickle.dump(lbl_encoder, enc, protocol=pickle.HIGHEST_PROTOCOL)

print("Modelo guardado.")

#Graficar la Precisión
plt.plot(history.history['accuracy'], label='Entrenamiento')
plt.plot(history.history['val_accuracy'], label='Validación')
plt.title('Precisión del modelo')
plt.xlabel('Épocas')
plt.ylabel('Precisión')
plt.legend()
plt.show()

#Graficar la Pérdida
plt.plot(history.history['loss'], label='Entrenamiento')
plt.plot(history.history['val_loss'], label='Validación')
plt.title('Pérdida del modelo')
plt.xlabel('Épocas')
plt.ylabel('Pérdida')
plt.legend()
plt.show()
