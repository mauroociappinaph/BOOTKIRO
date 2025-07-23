# Configuración del Sistema RAG con Telegram

Este documento explica cómo configurar y ejecutar el sistema RAG (Retrieval-Augmented Generation) integrado con Telegram.

## Requisitos previos

- Python 3.8 o superior
- Pip (gestor de paquetes de Python)
- Token de bot de Telegram (obtenido a través de [@BotFather](https://t.me/botfather))
- Opcionalmente, una clave API de OpenAI para generación de texto de alta calidad

## Pasos de configuración

### 1. Configurar el entorno

Ejecuta el script de configuración para crear un entorno virtual e instalar todas las dependencias:

```bash
# Dar permisos de ejecución al script
chmod +x setup_rag.sh

# Ejecutar el script
./setup_rag.sh
```

### 2. Configurar variables de entorno

Crea un archivo `.env` basado en el ejemplo proporcionado:

```bash
cp .env.example .env
```

Edita el archivo `.env` y añade tus credenciales:

```bash
# Abre el archivo con tu editor favorito
nano .env

# Añade tu token de Telegram y otras credenciales
```

### 3. Indexar documentos iniciales

Para que el sistema RAG sea útil, necesitas indexar algunos documentos:

```bash
# Activar el entorno virtual
source venv/bin/activate

# Indexar un directorio completo
python index_documents.py --dir path/to/your/documents

# O indexar un archivo específico
python index_documents.py --file path/to/your/document.pdf
```

### 4. Iniciar el bot

Una vez configurado todo, puedes iniciar el bot:

```bash
# Activar el entorno virtual
source venv/bin/activate

# Iniciar el bot
python main.py
```

## Uso del bot

Una vez que el bot esté en funcionamiento, puedes interactuar con él en Telegram:

1. Busca tu bot por su nombre de usuario en Telegram
2. Envía el comando `/start` para iniciar
3. Usa el comando `/rag` para acceder al sistema RAG
4. Sigue las instrucciones en pantalla para:
   - Hacer preguntas sobre tus documentos
   - Ver documentos indexados
   - Subir nuevos documentos para indexar

## Solución de problemas

### El bot no responde

- Verifica que el token de Telegram sea correcto
- Asegúrate de que el bot esté en ejecución (`python main.py`)
- Revisa los logs en `bot.log` para ver posibles errores

### Errores de generación de texto

- Si usas OpenAI, verifica que la clave API sea correcta
- Si usas modelos locales, asegúrate de tener suficiente memoria RAM

### Errores de indexación

- Verifica que los formatos de archivo sean soportados (PDF, DOCX, TXT, HTML)
- Asegúrate de tener permisos de escritura en los directorios `data/`
- Revisa los logs para ver errores específicos

## Formatos de archivo soportados

El sistema RAG puede procesar los siguientes formatos de archivo:

- Texto plano (`.txt`, `.md`, `.csv`, `.json`)
- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- HTML (`.html`, `.htm`)

## Configuración avanzada

Para configuración avanzada, puedes editar los siguientes archivos:

- `personal_automation_bot/services/content/text_generator.py` - Para configurar los generadores de texto
- `personal_automation_bot/services/rag/vector_store.py` - Para configurar el almacenamiento de vectores
- `personal_automation_bot/bot/conversations/rag_conversation.py` - Para modificar la conversación RAG
