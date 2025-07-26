# Chatbot-Tutorias-Académicas

- Este proyecto es un chatbot educativo para estudiantes de la ESFOT. Este fue creado para implementar a futuro en la plataforma
de gestión de tutorías de la ESFOT.
- El chatbot fue desarrollado con **Python**, **TensorFlow/Keras** y una interfaz en **Streamlit**, con el objetivo de asistir a estudiantes respondiendo preguntas frecuentes sobre el sistema de tutorías académicas.

---

# Funcionalidades

- Entrenamiento de modelo usando `intents.json` con Keras
- Configuración de parámetros de entrenamiento
- Visualización de métricas
- Interfaz gráfica interactiva con Streamlit
- Respuestas automáticas a dudas de los usuarios.
- Posibilidad de agregar nuevas intenciones o reentrenar el modelo

## 📁 Estructura del Proyecto
chatbot_tutorias/
- app.py                              #Interfaz en Streamlit
- entrenamiento_modelo.py             #Entrenamiento del chatbot
- chatbot_modelo.keras                #Modelo entrenado
- intents.json                        #Datos de entrenamiento (intenciones y respuestas)
- usuarios.json                       #Guarda los usuarios registrados para el inicio de sesión
- Tokenizer.pickle                    #Tokenizador de texto (no se sube al repositorio, se genera automaticamente)
- labels.pickle                       #Etiquetas codificadas (no se sube al repositorio, se genera automaticamente)
- requirements.txt                    #Paquetes necesarios 
- .gitignore                          #Ignora entorno virtual y archivos pesados
- chatbot_env/                        #(No se sube al repositorio, es el entorno virtual donde se ejecuta la aplicación)

