import json
import numpy as np
import pickle
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from nltk.stem import PorterStemmer
import string

# 1. Cargar intents.json
with open("intents.json", encoding='utf-8') as file:
    data = json.load(file)

stemmer = PorterStemmer()

def tokenize(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.split()

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

# Entrenamiento
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

# 2. Dividir en entrenamiento/prueba
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42, stratify=y)

# 3. Guardar vocabulario y etiquetas
with open("chatbot_data.pkl", "wb") as f:
    pickle.dump((all_words, tags, x, y), f)

#4. Crear el modelo
model = Sequential()
model.add(Dense(128, input_shape=(len(x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(tags), activation='softmax'))

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# 5. Entrenar modelo
history = model.fit(
    x_train, y_train,
    epochs=100,
    batch_size=8,
    validation_data=(x_test, y_test),
    verbose=1
)

# 6. Evaluar modelo
train_loss, train_acc = model.evaluate(x_train, y_train, verbose=0)
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)

print(f"Precisión en entrenamiento: {train_acc:.2f}")
print(f"Precisión en prueba: {test_acc:.2f}")

# 7. Guardar modelo
model.save("chatbot_modelo.keras")
print("Modelo guardado como chatbot_modelo.keras")

# 8. Graficar curvas de entrenamiento
plt.figure(figsize=(12, 4))

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

plt.tight_layout()
plt.savefig('chatbot_entrenamiento.png')
plt.show()
