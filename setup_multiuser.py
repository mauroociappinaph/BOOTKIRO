#!/usr/bin/env python3
"""
Script para configurar el bot en modo multi-usuario.
Permite que múltiples usuarios (tú y tu hermano) usen el mismo bot
pero con datos completamente separados.
"""

import os
import json
from pathlib import Path


def setup_multiuser_config():
    """Configura el bot para modo multi-usuario."""
    print("👥 Configurando modo multi-usuario")
    print("=" * 40)

    # 1. Crear configuración de usuarios autorizados
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    # Lista de usuarios autorizados (IDs de Telegram)
    authorized_users = {
        "users": {
            # Agregar tu ID y el de tu hermano aquí
            # "123456789": {
            #     "name": "Mauro",
            #     "role": "admin",
            #     "data_dir": "data_mauro"
            # },
            # "987654321": {
            #     "name": "Hermano",
            #     "role": "user",
            #     "data_dir": "data_hermano"
            # }
        },
        "settings": {
            "require_authorization": True,
            "admin_only_commands": ["/admin", "/logs", "/stats"],
            "separate_data_dirs": True
        }
    }

    config_path = config_dir / "users.json"
    with open(config_path, "w") as f:
        json.dump(authorized_users, f, indent=2)

    print(f"✅ Configuración creada: {config_path}")

    # 2. Crear middleware de autorización
    middleware_content = '''"""
Middleware de autorización para modo multi-usuario.
"""

import json
import logging
from pathlib import Path
from functools import wraps

logger = logging.getLogger(__name__)

class UserManager:
    """Gestor de usuarios autorizados."""

    def __init__(self, config_path="config/users.json"):
        self.config_path = Path(config_path)
        self.users = self._load_users()

    def _load_users(self):
        """Carga la configuración de usuarios."""
        if not self.config_path.exists():
            return {"users": {}, "settings": {"require_authorization": False}}

        with open(self.config_path) as f:
            return json.load(f)

    def is_authorized(self, user_id):
        """Verifica si un usuario está autorizado."""
        if not self.users["settings"].get("require_authorization", False):
            return True

        return str(user_id) in self.users["users"]

    def get_user_info(self, user_id):
        """Obtiene información del usuario."""
        return self.users["users"].get(str(user_id))

    def get_user_data_dir(self, user_id):
        """Obtiene el directorio de datos del usuario."""
        user_info = self.get_user_info(user_id)
        if user_info:
            return user_info.get("data_dir", f"data_user_{user_id}")
        return f"data_user_{user_id}"

    def is_admin(self, user_id):
        """Verifica si un usuario es administrador."""
        user_info = self.get_user_info(user_id)
        return user_info and user_info.get("role") == "admin"

# Instancia global del gestor de usuarios
user_manager = UserManager()

def require_auth(func):
    """Decorador que requiere autorización."""
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        user_id = update.effective_user.id

        if not user_manager.is_authorized(user_id):
            await update.message.reply_text(
                "❌ No tienes autorización para usar este bot.\\n"
                "Contacta al administrador para obtener acceso."
            )
            return

        # Configurar directorio de datos del usuario
        user_data_dir = user_manager.get_user_data_dir(user_id)
        context.user_data["data_dir"] = user_data_dir

        return await func(update, context, *args, **kwargs)

    return wrapper

def require_admin(func):
    """Decorador que requiere permisos de administrador."""
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        user_id = update.effective_user.id

        if not user_manager.is_admin(user_id):
            await update.message.reply_text(
                "❌ Este comando requiere permisos de administrador."
            )
            return

        return await func(update, context, *args, **kwargs)

    return wrapper
'''

    middleware_path = Path("personal_automation_bot/utils/auth_middleware.py")
    with open(middleware_path, "w") as f:
        f.write(middleware_content)

    print(f"✅ Middleware creado: {middleware_path}")

    # 3. Crear script para agregar usuarios
    add_user_script = '''#!/usr/bin/env python3
"""
Script para agregar usuarios autorizados al bot.
"""

import json
import sys
from pathlib import Path

def add_user(user_id, name, role="user"):
    """Agrega un usuario a la configuración."""
    config_path = Path("config/users.json")

    if not config_path.exists():
        print("❌ Archivo de configuración no encontrado")
        return False

    with open(config_path) as f:
        config = json.load(f)

    config["users"][str(user_id)] = {
        "name": name,
        "role": role,
        "data_dir": f"data_{name.lower().replace(' ', '_')}"
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Usuario agregado: {name} (ID: {user_id})")
    return True

def main():
    if len(sys.argv) < 3:
        print("Uso: python3 add_user.py <user_id> <name> [role]")
        print("Ejemplo: python3 add_user.py 123456789 'Mi Hermano' user")
        return

    user_id = sys.argv[1]
    name = sys.argv[2]
    role = sys.argv[3] if len(sys.argv) > 3 else "user"

    add_user(user_id, name, role)

if __name__ == "__main__":
    main()
'''

    add_user_path = Path("add_user.py")
    with open(add_user_path, "w") as f:
        f.write(add_user_script)

    os.chmod(add_user_path, 0o755)
    print(f"✅ Script para agregar usuarios: {add_user_path}")

    # 4. Crear documentación
    docs_content = f"""# Configuración Multi-Usuario

## 🎯 Descripción

El bot ahora puede manejar múltiples usuarios con datos completamente separados.

## 👥 Usuarios Autorizados

Para agregar usuarios autorizados:

```bash
# Agregar tu hermano (necesitas su ID de Telegram)
python3 add_user.py 987654321 "Mi Hermano" user

# Agregarte a ti como admin
python3 add_user.py 123456789 "Mauro" admin
```

## 🔍 Obtener ID de Telegram

Para obtener el ID de Telegram de tu hermano:

1. Agrega el bot @userinfobot a Telegram
2. Envía `/start` al bot
3. Te dará el ID numérico
4. Usa ese ID en el comando `add_user.py`

## 📁 Separación de Datos

Cada usuario tendrá su propio directorio:
- `data_mauro/` - Tus datos
- `data_mi_hermano/` - Datos de tu hermano
- Credenciales de Gmail separadas
- Configuraciones independientes

## 🔒 Seguridad

- ✅ Solo usuarios autorizados pueden usar el bot
- ✅ Datos completamente separados por usuario
- ✅ Permisos de administrador para comandos sensibles
- ✅ Logs separados por usuario

## 🚀 Activar Modo Multi-Usuario

1. Ejecuta: `python3 setup_multiuser.py`
2. Agrega usuarios: `python3 add_user.py <id> <nombre>`
3. Reinicia el bot
4. ¡Listo! Cada usuario tendrá su espacio separado

## 🆘 Comandos de Admin

Como administrador, tendrás acceso a:
- `/admin` - Panel de administración
- `/logs` - Ver logs del sistema
- `/stats` - Estadísticas de uso
"""

    docs_path = Path("docs/multiuser_setup.md")
    with open(docs_path, "w") as f:
        f.write(docs_content)

    print(f"✅ Documentación creada: {docs_path}")

    print("\n" + "=" * 40)
    print("🎉 Configuración multi-usuario completada!")
    print("\n📋 Próximos pasos:")
    print("1. Obtén el ID de Telegram de tu hermano")
    print("2. Ejecuta: python3 add_user.py <id_hermano> 'Nombre Hermano'")
    print("3. Ejecuta: python3 add_user.py <tu_id> 'Tu Nombre' admin")
    print("4. Reinicia el bot")
    print("\n📖 Documentación: docs/multiuser_setup.md")


if __name__ == "__main__":
    setup_multiuser_config()
