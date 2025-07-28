#Importacion de las librerias necesarias
import json
import string
import random
import numpy as np
import pandas as pd
import pickle
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from nltk.stem import PorterStemmer

#Fijar la semilla para reproducibilidad: Obtener los mismos resultados cada vez que se entrena el modelo
seed = 42
random.seed(seed)
np.random.seed(seed)
tf.random.set_seed(seed)

#1. Cargar intents.json
with open("intents.json", encoding='utf-8') as file:
    data = json.load(file)

stemmer = PorterStemmer()

def tokenize(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.split()

#Diccionario simple de sinónimos para data augmentation
synonyms = {
    "quiero": ["deseo", "me gustaría", "necesito"],
    "tutoría": ["clase", "sesión", "asesoría"],
    "actualizar": ["modificar", "cambiar", "editar"],
    "contraseña": ["clave", "password"],
    "docente": ["profesor", "maestro", "educador"]
}

def augment_pattern(pattern):
    words = pattern.lower().split()
    augmented_patterns = []

    #Generar variantes reemplazando palabras por sinónimos uno por uno
    for i, word in enumerate(words):
        if word in synonyms:
            for syn in synonyms[word]:
                new_words = words.copy()
                new_words[i] = syn
                augmented_patterns.append(" ".join(new_words))
    return augmented_patterns

#2. Data augmentation: ampliar patrones de intents con nuevas frases
for intent in data["intents"]:
    new_patterns = []
    for pattern in intent["patterns"]:
        augmented = augment_pattern(pattern)
        new_patterns.extend(augmented)
    intent["patterns"].extend(new_patterns)

#3. Construcción de vocabulario y etiquetas
all_words = []
tags = []
xy = []

for intent in data["intents"]:
    tag = intent["tag"]
    tags.append(tag)
    for pattern in intent["patterns"]:
        words = tokenize(pattern)
        all_words.extend(words)
        xy.append((words, tag))

#Preprocesamiento
ignore_words = ["?", "!", ".", ","]
all_words = [stemmer.stem(w) for w in all_words if w not in ignore_words]
all_words = sorted(set(all_words))
tags = sorted(set(tags))

#4. Crear bolsa de palabras para cada patrón
x = []
y = []

for pattern_words, tag in xy:
    bag = [0] * len(all_words)
    stemmed_words = [stemmer.stem(w.lower()) for w in pattern_words]
    for sw in stemmed_words:
        for i, w in enumerate(all_words):
            if w == sw:
                bag[i] = 1
    x.append(bag)
    label = tags.index(tag)
    y.append(label)

x = np.array(x)
y = np.array(y)

#Mostrar cantidad de ejemplos por intent para aplicar data augmentation
for intent in data["intents"]:
    print(f"Intent: {intent['tag']}, ejemplos: {len(intent['patterns'])}")

#5. Dividir datos en entrenamiento y prueba
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=seed, stratify=y)

#6. Guardar vocabulario y etiquetas en un archivo .pkl que sera utilizado en la interfaz
with open("chatbot_data.pkl", "wb") as f:
    pickle.dump((all_words, tags, x, y), f)

#7. Creacion y compilacion del modelo
model = Sequential()
model.add(Dense(128, input_shape=(len(x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(tags), activation='softmax'))

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

#8. Entrenar modelo
history = model.fit(
    x_train, y_train,
    epochs=50,
    batch_size=8,
    validation_data=(x_test, y_test),
    verbose=2
)

#9. Evaluar modelo
train_loss, train_acc = model.evaluate(x_train, y_train, verbose=0)
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)

print(f"Precisión en entrenamiento: {train_acc:.2f}")
print(f"Precisión en prueba: {test_acc:.2f}")

#10. Guardar modelo
model.save("chatbot_modelo.keras")
print("Modelo guardado como chatbot_modelo.keras")

#11. Guardar un CSV con los datos de precision y perdida para ser analizados
df_resultados = pd.DataFrame(history.history)

#Agregar la columna de época
df_resultados["epoch"] = df_resultados.index + 1

#Guardar como CSV
df_resultados.to_csv("resultados_entrenamiento.csv", index=False)
print("Archivo CSV guardado con éxito")

#12. Graficar curvas
plt.figure(figsize=(12, 4))

#Visualizar el aprendizaje del modelo
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Entrenamiento')
plt.plot(history.history['val_accuracy'], label='Validación')
plt.title('Precisión')
plt.xlabel('Épocas')
plt.ylabel('Precisión')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Entrenamiento')
plt.plot(history.history['val_loss'], label='Validación')
plt.title('Pérdida')
plt.xlabel('Épocas')
plt.ylabel('Pérdida')
plt.legend()
plt.grid(True)

#Guardar la grafica en un archivo .png y mostrar
plt.tight_layout()
print("Imagen guardada con éxito como: chatbot_entrenamiento.png")
plt.savefig('chatbot_entrenamiento.png')
plt.show()
