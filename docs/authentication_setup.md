# Sistema de Autenticación OAuth

## Configuración de Google Cloud Console

Para usar las funcionalidades de Gmail, Calendar y Drive, necesitas configurar OAuth 2.0 en Google Cloud Console.

### 1. Crear Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita las APIs necesarias:
   - Gmail API
   - Google Calendar API
   - Google Drive API

### 2. Configurar OAuth 2.0

1. Ve a "APIs y servicios" > "Credenciales"
2. Haz clic en "Crear credenciales" > "ID de cliente de OAuth 2.0"
3. Selecciona "Aplicación web"
4. Configura:
   - **Nombre**: Personal Automation Bot
   - **URIs de origen autorizados**: `http://localhost:8080`
   - **URIs de redirección autorizados**: `http://localhost:8080/`

### 3. Descargar Credenciales

1. Después de crear las credenciales OAuth, haz clic en el botón de descarga
2. Descarga el archivo JSON de credenciales
3. Guarda el archivo como `credentials.json` en la raíz del proyecto
4. **Importante**: Nunca subas este archivo a control de versiones

### 4. Configurar Variables de Entorno

Agrega la ruta del archivo de credenciales a tu archivo `.env`:

```bash
# Google OAuth Credentials
GOOGLE_CLIENT_SECRETS_PATH=credentials.json

# Opcional: Para configuración avanzada
GOOGLE_CLIENT_ID=tu_client_id_aqui
GOOGLE_CLIENT_SECRET=tu_client_secret_aqui
GOOGLE_REDIRECT_URI=http://localhost:8080/
```

## Uso del Sistema de Autenticación

### Comandos Disponibles

- `/auth` - Gestionar autenticación con Google
- Botón "🔐 Autenticación" en el menú principal

### Proceso de Autenticación

1. **Iniciar autenticación**: Usa `/auth` o el botón del menú
2. **Seguir enlace**: Haz clic en el enlace de autenticación
3. **Autorizar permisos**: Acepta los permisos solicitados en Google
4. **Copiar código**: Copia el código de autorización
5. **Enviar código**: Envía el código como mensaje al bot

### Permisos Solicitados

El bot solicita los siguientes permisos mínimos:

#### Gmail

- `gmail.readonly` - Leer correos
- `gmail.send` - Enviar correos
- `gmail.compose` - Componer correos

#### Google Calendar

- `calendar` - Acceso completo al calendario
- `calendar.events` - Gestionar eventos

#### Google Drive

- `drive.file` - Acceso a archivos creados por la app
- `drive.readonly` - Leer archivos existentes

## Seguridad

### Almacenamiento de Tokens

- Los tokens se almacenan **encriptados** localmente
- Cada usuario tiene sus propios tokens
- Los tokens se renuevan automáticamente
- Puedes revocar el acceso en cualquier momento

### Mejores Prácticas

1. **Revoca el acceso** si no usas el bot por mucho tiempo
2. **Verifica los permisos** en tu cuenta de Google regularmente
3. **Mantén seguras** tus credenciales de OAuth
4. **No compartas** tu archivo `.env`

### Revocar Autenticación

Puedes revocar la autenticación de dos formas:

1. **Desde el bot**: Usa `/auth` y selecciona "Revocar Autenticación"
2. **Desde Google**: Ve a [Cuenta de Google](https://myaccount.google.com/permissions) > "Aplicaciones de terceros"

## Solución de Problemas

### Error: "OAuth credentials not configured"

- Verifica que `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET` estén en tu `.env`
- Asegúrate de que el archivo `.env` esté en la raíz del proyecto

### Error: "Invalid authorization code"

- El código puede haber expirado (válido por 10 minutos)
- Asegúrate de copiar el código completo
- Intenta el proceso de autenticación de nuevo

### Error: "Failed to refresh tokens"

- Los tokens pueden haber sido revocados
- Inicia el proceso de autenticación de nuevo
- Verifica que las credenciales OAuth sigan siendo válidas

### Error: "Redirect URI mismatch"

- Verifica que `GOOGLE_REDIRECT_URI` coincida con la configuración en Google Cloud Console
- Asegúrate de que la URI esté exactamente igual (incluyendo la barra final)

## Desarrollo y Testing

### Variables de Entorno para Testing

```bash
# Para testing local
GOOGLE_REDIRECT_URI=http://localhost:8080/

# Para producción (ajustar según tu dominio)
GOOGLE_REDIRECT_URI=https://tu-dominio.com/auth/callback
```

### Comandos de Testing

```bash
# Probar el sistema de autenticación
python test_auth_system.py

# Probar importaciones
python -c "from personal_automation_bot.utils.auth import google_auth_manager; print('Auth system OK')"
```

## Limitaciones

### Cuotas de API

Google tiene límites en las APIs gratuitas:

- **Gmail API**: 1,000,000,000 unidades de cuota por día
- **Calendar API**: 1,000,000 solicitudes por día
- **Drive API**: 1,000 solicitudes por 100 segundos por usuario

### Tokens de Actualización

- Los tokens de actualización pueden expirar si no se usan por 6 meses
- Google puede revocar tokens si detecta uso sospechoso
- Los tokens se invalidan si cambias la configuración OAuth

## Próximas Funcionalidades

- [ ] Autenticación con múltiples cuentas de Google
- [ ] Soporte para otros proveedores OAuth (Microsoft, etc.)
- [ ] Interfaz web para gestión de autenticación
- [ ] Notificaciones de expiración de tokens
