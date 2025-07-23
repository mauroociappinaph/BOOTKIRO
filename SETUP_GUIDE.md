# 🚀 Guía de Configuración - Personal Automation Bot

## ✅ Estado Actual

El bot está **completamente configurado** y listo para usar con funcionalidad de calendario completa.

## 📋 Requisitos Previos

### 1. Variables de Entorno (.env)

Crea un archivo `.env` en la raíz del proyecto con:

```env
# Telegram Bot Token (obligatorio)
TELEGRAM_BOT_TOKEN=tu_token_de_telegram_bot

# Google OAuth Credentials (obligatorio para calendario)
GOOGLE_CLIENT_ID=tu_google_client_id
GOOGLE_CLIENT_SECRET=tu_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8080/

# Opcional - para otras funcionalidades
OPENAI_API_KEY=tu_openai_api_key
NOTION_API_KEY=tu_notion_api_key
```

### 2. Cómo Obtener las Credenciales

#### **Telegram Bot Token:**

1. Habla con [@BotFather](https://t.me/botfather) en Telegram
2. Usa `/newbot` para crear un nuevo bot
3. Sigue las instrucciones y guarda el token

#### **Google OAuth Credentials:**

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita las APIs:
   - Google Calendar API
   - Gmail API
4. Ve a "Credenciales" → "Crear credenciales" → "ID de cliente OAuth 2.0"
5. Configura:
   - Tipo: Aplicación web
   - URIs de redirección: `http://localhost:8080/`
6. Descarga las credenciales y extrae `client_id` y `client_secret`

## 🚀 Iniciar el Bot

```bash
# Instalar dependencias (si no están instaladas)
pip install -r requirements.txt

# Iniciar el bot
python main.py

# Para desarrollo con auto-reload
python main.py --dev
```

## 📱 Uso en Telegram

### **Comandos Principales:**

- `/start` - Iniciar el bot y ver menú principal
- `/calendar` - Acceder directamente a funciones de calendario
- `/auth` - Gestionar autenticación con Google
- `/help` - Ver ayuda completa

### **Funcionalidades de Calendario:**

1. **Ver eventos** - Próximos, de hoy, de la semana
2. **Crear eventos** - Con fechas flexibles (hoy, mañana, DD/MM, etc.)
3. **Actualizar eventos** - Modificar título, fecha, hora, descripción, ubicación
4. **Eliminar eventos** - Con confirmación de seguridad
5. **Buscar eventos** - Por texto en títulos y descripciones

### **Formatos de Fecha/Hora Soportados:**

- **Fechas:** `hoy`, `mañana`, `25/12`, `25/12/2024`
- **Horas:** `todo el día`, `14:30`, `14:30-16:00`, `14`

## 🔐 Proceso de Autenticación

1. Usa `/auth` en Telegram
2. Sigue el enlace proporcionado
3. Autoriza el acceso a Google Calendar
4. Regresa a Telegram - ¡listo!

## 🧪 Verificar Configuración

```bash
# Ejecutar tests para verificar que todo funciona
python test_bot_startup.py
python test_calendar_service_improved.py
python test_calendar_integration.py
```

## 📁 Estructura del Proyecto

```
personal_automation_bot/
├── main.py                     # Punto de entrada
├── .env                        # Variables de entorno (crear)
├── bot/
│   ├── core.py                 # Configuración del bot
│   ├── commands/calendar.py    # Comandos de calendario
│   └── conversations/calendar_conversation.py
├── services/calendar/          # Servicio de calendario
└── utils/auth.py              # Autenticación Google
```

## 🎯 Flujo de Uso Típico

1. **Iniciar:** `/start` → Ver menú principal
2. **Autenticar:** Botón "🔐 Autenticación" → Seguir proceso OAuth
3. **Calendario:** Botón "📅 Calendario" → Seleccionar acción
4. **Crear evento:** Seguir flujo conversacional guiado
5. **Gestionar:** Ver, actualizar o eliminar eventos existentes

## 🔧 Solución de Problemas

### **Error: "No estás autenticado con Google"**

- Usa `/auth` para autenticarte
- Verifica que las credenciales de Google estén correctas en `.env`

### **Error: "Token inválido"**

- Verifica que `TELEGRAM_BOT_TOKEN` esté correcto en `.env`
- Asegúrate de que el bot esté activo en BotFather

### **Error: "API no habilitada"**

- Habilita Google Calendar API en Google Cloud Console
- Espera unos minutos para que se propague

### **Fechas en el pasado**

- El bot no permite crear eventos en fechas pasadas
- Usa fechas futuras o `hoy`/`mañana`

## 🎉 ¡Listo para Usar!

Una vez configurado, el bot estará completamente funcional con:

- ✅ Gestión completa de eventos de calendario
- ✅ Interfaz conversacional intuitiva
- ✅ Autenticación segura con Google
- ✅ Validación robusta de datos
- ✅ Manejo de errores completo

**¡Disfruta tu asistente de automatización personal!** 🤖📅
