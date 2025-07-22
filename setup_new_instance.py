#!/usr/bin/env python3
"""
Script para configurar una nueva instancia del Personal Automation Bot
para otro usuario (ej: hermano) sin afectar la instancia actual.
"""

import os
import shutil
import json
from pathlib import Path


def create_new_instance(instance_name, telegram_token=None):
    """
    Crea una nueva instancia del bot para otro usuario.

    Args:
        instance_name: Nombre de la nueva instancia (ej: "hermano")
        telegram_token: Token del nuevo bot de Telegram
    """
    print(f"🚀 Configurando nueva instancia: {instance_name}")
    print("=" * 50)

    # 1. Crear directorio para la nueva instancia
    instance_dir = f"instances/{instance_name}"
    os.makedirs(instance_dir, exist_ok=True)
    print(f"✅ Directorio creado: {instance_dir}")

    # 2. Copiar código fuente (sin datos personales)
    source_files = [
        "personal_automation_bot/",
        "requirements.txt",
        "main.py",
        "docs/",
        ".kiro/specs/"
    ]

    for item in source_files:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.copytree(item, f"{instance_dir}/{item}", dirs_exist_ok=True)
            else:
                shutil.copy2(item, f"{instance_dir}/{item}")

    print("✅ Código fuente copiado")

    # 3. Crear archivo .env personalizado
    env_content = f"""# Telegram Bot Token para {instance_name}
TELEGRAM_BOT_TOKEN={telegram_token or 'TU_TOKEN_AQUI'}

# Google API Credentials (cada usuario necesita su propio credentials.json)
GOOGLE_CLIENT_SECRETS_PATH=credentials.json

# OpenAI API Key (opcional - puede compartirse o ser diferente)
OPENAI_API_KEY=your_openai_api_key

# Notion API Key (opcional)
NOTION_API_KEY=your_notion_api_key

# Buffer API Key (opcional)
BUFFER_API_KEY=your_buffer_api_key

# Metricool API Key (opcional)
METRICOOL_API_KEY=your_metricool_api_key

# Development Settings
DEBUG=False
LOG_LEVEL=INFO

# Data Directory (separado por instancia)
DATA_DIR=./data_{instance_name}
"""

    with open(f"{instance_dir}/.env", "w") as f:
        f.write(env_content)

    print(f"✅ Archivo .env creado para {instance_name}")

    # 4. Crear script de inicio personalizado
    start_script = f"""#!/usr/bin/env python3
\"\"\"
Script de inicio para la instancia de {instance_name}
\"\"\"

import os
import sys
from pathlib import Path

# Cambiar al directorio de la instancia
instance_dir = Path(__file__).parent
os.chdir(instance_dir)

# Agregar al path de Python
sys.path.insert(0, str(instance_dir))

# Ejecutar el bot
if __name__ == "__main__":
    from main import main
    main()
"""

    with open(f"{instance_dir}/start_{instance_name}.py", "w") as f:
        f.write(start_script)

    os.chmod(f"{instance_dir}/start_{instance_name}.py", 0o755)
    print(f"✅ Script de inicio creado: start_{instance_name}.py")

    # 5. Crear README de configuración
    readme_content = f"""# Personal Automation Bot - Instancia de {instance_name.title()}

## 🚀 Configuración Rápida

### 1. Crear Bot de Telegram
1. Habla con @BotFather en Telegram
2. Usa `/newbot` y sigue las instrucciones
3. Copia el token y pégalo en el archivo `.env`

### 2. Configurar Google Cloud Console
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto (diferente al de Mauro)
3. Habilita Gmail API
4. Crea credenciales OAuth 2.0
5. Descarga el archivo como `credentials.json`

### 3. Instalar Dependencias
```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 4. Ejecutar el Bot
```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar
python3 start_{instance_name}.py
```

## 📁 Estructura de Datos

Todos los datos de {instance_name} se guardan en:
- `data_{instance_name}/` - Datos del usuario
- `credentials.json` - Credenciales de Google (propias)
- `.env` - Configuración (propia)

## 🔒 Seguridad

- ✅ Datos completamente separados de otras instancias
- ✅ Credenciales propias de Google
- ✅ Bot de Telegram propio
- ✅ No hay interferencia con otros usuarios

## 🆘 Soporte

Si tienes problemas, contacta a Mauro con:
- Capturas de pantalla del error
- Logs del bot (si los hay)
- Descripción de lo que estabas haciendo
"""

    with open(f"{instance_dir}/README_{instance_name}.md", "w") as f:
        f.write(readme_content)

    print(f"✅ README creado: README_{instance_name}.md")

    # 6. Crear script de configuración automática
    config_script = f"""#!/usr/bin/env python3
\"\"\"
Script de configuración automática para {instance_name}
\"\"\"

import os
import subprocess
import sys

def setup():
    print("🔧 Configuración automática para {instance_name}")
    print("=" * 40)

    # Verificar Python
    print("✅ Python encontrado:", sys.version)

    # Crear entorno virtual si no existe
    if not os.path.exists("venv"):
        print("📦 Creando entorno virtual...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        print("✅ Entorno virtual creado")

    # Activar entorno virtual e instalar dependencias
    if os.name == 'nt':  # Windows
        pip_path = "venv\\\\Scripts\\\\pip"
        python_path = "venv\\\\Scripts\\\\python"
    else:  # Unix/Linux/Mac
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"

    print("📦 Instalando dependencias...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    print("✅ Dependencias instaladas")

    # Verificar configuración
    print("\\n🔍 Verificando configuración...")

    if os.path.exists(".env"):
        print("✅ Archivo .env encontrado")
    else:
        print("❌ Archivo .env no encontrado")

    if os.path.exists("credentials.json"):
        print("✅ Archivo credentials.json encontrado")
    else:
        print("❌ Archivo credentials.json no encontrado")
        print("   👉 Descárgalo de Google Cloud Console")

    print("\\n🚀 Configuración completada!")
    print(f"Para ejecutar el bot: python3 start_{instance_name}.py")

if __name__ == "__main__":
    setup()
"""

    with open(f"{instance_dir}/setup.py", "w") as f:
        f.write(config_script)

    os.chmod(f"{instance_dir}/setup.py", 0o755)
    print(f"✅ Script de configuración creado: setup.py")

    print("\n" + "=" * 50)
    print(f"🎉 ¡Instancia '{instance_name}' creada exitosamente!")
    print(f"📁 Ubicación: {instance_dir}/")
    print(f"📖 Instrucciones: {instance_dir}/README_{instance_name}.md")
    print(f"⚙️  Configuración: {instance_dir}/setup.py")

    return instance_dir


def create_deployment_package(instance_name):
    """Crea un paquete ZIP para enviar a tu hermano."""
    import zipfile

    instance_dir = f"instances/{instance_name}"
    zip_path = f"{instance_name}_bot_package.zip"

    print(f"📦 Creando paquete de despliegue: {zip_path}")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(instance_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, instance_dir)
                zipf.write(file_path, arc_path)

    print(f"✅ Paquete creado: {zip_path}")
    print(f"📤 Envía este archivo a tu hermano")

    return zip_path


def main():
    """Función principal."""
    print("🤖 Personal Automation Bot - Configurador de Instancias")
    print("=" * 60)

    instance_name = input("📝 Nombre de la instancia (ej: hermano): ").strip()
    if not instance_name:
        instance_name = "hermano"

    telegram_token = input("🤖 Token del bot de Telegram (opcional): ").strip()

    # Crear instancia
    instance_dir = create_new_instance(instance_name, telegram_token)

    # Preguntar si crear paquete
    create_package = input("\\n📦 ¿Crear paquete ZIP para enviar? (y/n): ").strip().lower()
    if create_package in ['y', 'yes', 'sí', 's']:
        create_deployment_package(instance_name)

    print("\\n🎯 Próximos pasos:")
    print(f"1. Ve a la carpeta: {instance_dir}")
    print(f"2. Lee las instrucciones: README_{instance_name}.md")
    print("3. Configura el bot de Telegram y Google Cloud Console")
    print("4. Ejecuta: python3 setup.py")
    print(f"5. Inicia el bot: python3 start_{instance_name}.py")


if __name__ == "__main__":
    main()
