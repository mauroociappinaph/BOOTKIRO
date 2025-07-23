# Personal Automation Bot

Un sistema de automatización personal gratuito que centraliza tareas de productividad y creación de contenido a través de un bot de Telegram.

## Características

- Control desde Telegram para gestionar Gmail y Google Calendar
- Generación de contenido con IA gratuita
- Integración con sistemas de almacenamiento como Notion o Google Drive
- Publicación de contenido en redes sociales
- Sistema RAG para generar contenido personalizado
- Automatización de flujos de trabajo

## Requisitos

- Python 3.8 o superior
- Cuenta de Telegram
- Cuenta de Google (para Gmail y Calendar)
- Cuenta de Notion (opcional)
- Cuenta de Buffer o Metricool (opcional)

## Instalación

1. Clonar el repositorio:

   ```
   git clone https://github.com/mauroociappinaph/BOOTKIRO.git
   cd BOOTKIRO
   ```

2. Crear y activar entorno virtual:

   ```
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:

   ```
   pip install -r requirements.txt
   ```

   Las dependencias están organizadas en los siguientes grupos:

   - Bot y API: python-telegram-bot, requests, python-dotenv, cryptography
   - Google API: google-api-python-client y relacionados
   - Vector database: faiss-cpu, chromadb, sentence-transformers
   - Document processing: pypdf, python-docx, beautifulsoup4, pdfminer.six
   - Content generation: openai, transformers, torch
   - RAG y LLM: langchain, llama-index

4. Configurar variables de entorno:

   ```
   cp .env.example .env
   # Editar .env con tus credenciales
   ```

5. Ejecutar el bot:
   ```
   python main.py
   ```

## Uso

1. Inicia una conversación con el bot en Telegram
2. Usa el comando `/start` para ver las opciones disponibles
3. Sigue las instrucciones para autenticarte con los servicios necesarios

## Desarrollo

Este proyecto sigue una arquitectura modular basada en microservicios. Consulta la documentación en la carpeta `docs/` para más detalles.

## Licencia

Este proyecto es software libre y se distribuye bajo la licencia MIT.
