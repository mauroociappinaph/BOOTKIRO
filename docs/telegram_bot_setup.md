# Configuración del Bot de Telegram

## Crear un Bot en Telegram

Para usar este sistema, necesitas crear un bot en Telegram y obtener su token API. Sigue estos pasos:

### 1. Contactar a BotFather

1. Abre Telegram y busca `@BotFather`
2. Inicia una conversación con BotFather enviando `/start`

### 2. Crear el Bot

1. Envía el comando `/newbot` a BotFather
2. BotFather te pedirá un nombre para tu bot (ej: "Mi Bot de Automatización Personal")
3. Luego te pedirá un username único que termine en "bot" (ej: "mi_automatizacion_bot")

### 3. Obtener el Token

Una vez creado el bot, BotFather te enviará un mensaje con:

- Un token API único (algo como: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
- Un enlace para acceder a tu bot

### 4. Configurar el Token

1. Copia el archivo `.env.example` a `.env`:

   ```bash
   cp .env.example .env
   ```

2. Edita el archivo `.env` y reemplaza `your_telegram_bot_token` con tu token real:
   ```
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### 5. Configuraciones Adicionales del Bot (Opcional)

Puedes configurar tu bot enviando estos comandos a BotFather:

- `/setdescription` - Establecer una descripción del bot
- `/setabouttext` - Establecer texto "Acerca de"
- `/setuserpic` - Establecer foto de perfil
- `/setcommands` - Configurar lista de comandos

#### Comandos Sugeridos para `/setcommands`:

```
start - Iniciar el bot
help - Mostrar ayuda y comandos disponibles
email - Gestionar correos electrónicos
calendar - Gestionar eventos del calendario
content - Generar contenido con IA
storage - Gestionar documentos y almacenamiento
publish - Publicar en redes sociales
rag - Generar contenido basado en documentos
flow - Gestionar flujos de trabajo automatizados
```

## Seguridad del Token

⚠️ **IMPORTANTE**:

- Nunca compartas tu token API
- No lo subas a repositorios públicos
- Mantenlo seguro en tu archivo `.env`
- Si crees que tu token ha sido comprometido, usa `/revoke` en BotFather para generar uno nuevo

## Probar el Bot

Una vez configurado:

1. Ejecuta el bot:

   ```bash
   python main.py
   ```

2. Busca tu bot en Telegram usando el username que creaste
3. Envía `/start` para probar que funciona

¡Tu bot debería responder con un mensaje de bienvenida!
