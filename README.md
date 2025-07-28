# Chatbot-Tutorias-Académicas

- Este proyecto es un chatbot educativo para estudiantes de la ESFOT. Este fue creado para implementar a futuro en la plataforma
de gestión de tutorías de la ESFOT.
- El chatbot fue desarrollado con **Python**, **TensorFlow/Keras** y una interfaz en **Streamlit**, con el objetivo de asistir a estudiantes respondiendo preguntas frecuentes sobre el sistema de tutorías académicas.

---

# Funcionalidades

- Entrenamiento de modelo usando `intents.json` con Keras
- Configuración de parámetros de entrenamiento
- Visualización de métricas
- Interfaz gráfica interactiva con Streamlit para que el usuario pueda registrarse e iniciar sesión y tener su chatbot personalizado.
- Respuestas automáticas a dudas de los usuarios.
- Posibilidad de agregar nuevas intenciones o reentrenar el modelo

## 📁 Estructura del Proyecto
chatbot_tutorias/
- app.py                              #Interfaz en Streamlit
  
- tutorias.py                         #Codigo para guardar las tutorias en un archivo llamado tutorias.json y llamarlo en app.py

- autenticacion.py                    #Codigo para guardar y registrar usuarios en usuarios.json
  
- entrenamiento_modelo.py             #Entrenamiento del chatbot
  
- style.css                           #Archivo para darle estilos a la aplicación en Streamlit
  
- chatbot_modelo.keras                #Modelo entrenado
  
- chatbot_data.pkl                    #Contiene los datos preprocesados que se usaron para entrenar el modelo. Es decir, guarda la información que se transformó desde intents.json a un formato que TensorFlow/Keras puede entender.
  
- intents.json                        #Datos de entrenamiento (intenciones y respuestas)
  
- usuarios.json                       #Guarda los usuarios registrados para el inicio de sesión
  
- tutorias_guardadas.json             #Archivo .json de prueba para guardar las tutorias de los estudiantes
  
- Tokenizer.pickle                    #Tokenizador de texto (no se sube al repositorio, se genera automaticamente)
  
- labels.pickle                       #Etiquetas codificadas (no se sube al repositorio, se genera automaticamente)
  
- requirements.txt                    #Paquetes necesarios
  
- .gitignore                          #Ignora entorno virtual y archivos pesados
  
- chatbot_env/                        #(No se sube al repositorio, es el entorno virtual donde se ejecuta la aplicación)

Adicionalmente, dentro del proyecto se crea una carpeta llamada images donde se guarda la imagen de logo para la página.

## Instrucciones para Ejecutar 

### 1. Navegar a la ruta donde se encuentra la carpeta chatbot-tutorias

- Ejecutar el terminal como administrador
- Navegar a la ruta. Ej: cd C:\Users\Usuario\Downloads\chatbot-tutorias

### 2. Crear entorno virtual

Para instalar tensorflow, se necesita Python 3.9 - 3.10 - 3.11 o 3.12, dado que Tensorflow no es compatible con Python 3.13

Si se cuenta con Python 3.12 o versiones inferiores, se ejecuta el siguiente comando para crear el entorno virtual: python -m venv chatbot_env

### 3. Activar el entorno virtual

- Ejecutar el siguiente comando para activar el entorno virtual: chatbot_env\Scripts\activate
- Cuando se activa el entorno virtual, aparece de la siguiente manera:
  
<img width="538" height="58" alt="image" src="https://github.com/user-attachments/assets/a23c03ce-c02f-4e4e-bc09-2f70cd215176" />

Para instalar las dependencias que necesita el proyecto, hemos creado un archivo llamado requirements.txt con el propósito de que, cuando el proyecto se descargue en otro computador, no se tengan que instalar todas las dependencias de forma manual.
Esto se hizo al terminar de instalar todo lo necesario para el proyecto con el paquete PIP. Al final, ejecutamos el comando: pip freeze > requirements.txt 

### 4. Instalar dependencias

- Ejecutar el siguiente comando: pip install -r requirements.txt

### 5. Ejecutar el archivo entrenamiento_modelo.py 

- Ejecutar el comando: python entrenamiento_modelo.py
- Una vez entrenado el modelo, se recorren todas las épocas mostrando la precisión y la pérdida. Además, se generan las gráficas.
- Al final se guardará el modelo entrenado en formato .keras y se generan automáticamente dos archivos: tokenizer.pickle y labels.pickle

<img width="615" height="85" alt="image" src="https://github.com/user-attachments/assets/a383af08-6b88-4567-a34c-5447d84c8f0c" />


### 6. Ejecutar el chatbot con Streamlit

- Ejecutar el comando: streamlit run app.py y aparece el siguiente mensaje:

<img width="730" height="128" alt="image" src="https://github.com/user-attachments/assets/56ca9449-dd6a-4336-8082-50c0dd837bef" />

Esto indica que Streamlit está corriendo en el puerto 8501

### 7. Visualización de la interfaz del chatbot con Streamlit

## 7.1 PANTALLA DE LOGIN 

<img width="1319" height="556" alt="image" src="https://github.com/user-attachments/assets/97a24cd2-fd64-4b8d-a8f5-dd46a71dcd7b" />

Se hicieron validaciones para que el usuario ingrese con las credenciales guardadas en la BDD (archivo usuarios.json)

## 7.2 PANTALLA DE REGISTRO

Cuando el usuario se registra, le pide su correo institucional, una contraseña y el rol con el que quiere acceder. Una vez que se registra, sus datos se almacenan en usuarios.json

<img width="1318" height="552" alt="image" src="https://github.com/user-attachments/assets/922d9db0-514f-4ed8-abbf-2af19a8fed1f" />

## Nota: La funcionalidad de registro está habilitada solo para estudiantes y docentes.

## 7.3 PANTALLA DEL CHATBOT

<img width="1264" height="528" alt="image" src="https://github.com/user-attachments/assets/3b8c0fba-037b-49d2-95dc-6a6c202913b8" />

El chatbot tiene programado un saludo automático con un menú de opciones para que el usuario se familiarice más con la plataforma.
