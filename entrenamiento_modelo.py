import json
import numpy as np
import random
import pickle
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from nltk.stem import PorterStemmer
import string

#Cargar archivo intents.json
with open("intents.json", encoding='utf-8') as file:
    data = json.load(file)

stemmer = PorterStemmer()

def tokenize(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.split()

#Listas para almacenar datos
all_words = []
tags = []
xy = []

# Procesar intents.json
for intent in data["intents"]:
    tag = intent["tag"]
    tags.append(tag)
    for pattern in intent["patterns"]:
        words = tokenize(pattern)
        all_words.extend(words)  # Acumular palabras para el vocabulario
        xy.append((words, tag))  # Guardar pares (tokens, etiqueta)

# Filtrar palabras ignoradas
ignore_words = ["?", "!", ".", ","]
all_words = [stemmer.stem(w) for w in all_words if w not in ignore_words]
all_words = sorted(set(all_words))
tags = sorted(set(tags))

#Entrenar el modelo
X_train = []
y_train = []

for pattern_words, tag in xy:
    bag = [0] * len(all_words)
    stemmed_words = [stemmer.stem(w.lower()) for w in pattern_words]
    for sw in stemmed_words:
        for i, w in enumerate(all_words):
            if w == sw:
                bag[i] = 1
    X_train.append(bag)

    label = tags.index(tag)
    y_train.append(label)

X_train = np.array(X_train)
y_train = np.array(y_train)

#Guardar datos necesarios
with open("chatbot_data.pkl", "wb") as f:
    pickle.dump((all_words, tags, X_train, y_train), f)

#Crear el modelo
model = Sequential()
model.add(Dense(128, input_shape=(len(X_train[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(tags), activation='softmax'))

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

#Entrenar el modelo
history = model.fit(X_train, y_train, epochs=100, batch_size=8, verbose=1)

#Guardar el modelo
model.save("chatbot_modelo.keras")
print("Modelo guardado con éxito: chatbot_modelo.keras")

#Graficar precisión y pérdida
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Precisión')
plt.title('Precisión durante el entrenamiento')
plt.xlabel('Épocas')
plt.ylabel('Precisión')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Pérdida', color='red')
plt.title('Pérdida durante el entrenamiento')
plt.xlabel('Épocas')
plt.ylabel('Pérdida')
plt.legend()
plt.grid(True)

plt.tight_layout()
#Guardar las graficas en un archivo png
plt.savefig('chatbot_entrenamiento.png')
plt.show()
