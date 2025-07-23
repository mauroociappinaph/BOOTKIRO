#!/bin/bash
# Script para configurar el entorno para el sistema RAG con Telegram

echo "🔧 Configurando el entorno para el sistema RAG con Telegram..."

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔌 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Crear directorios necesarios
echo "📁 Creando directorios para almacenamiento..."
mkdir -p data/vector_store/faiss
mkdir -p data/temp
mkdir -p data/document_cache

echo "✅ Configuración completada. Ahora puedes ejecutar el bot con:"
echo "source venv/bin/activate && python main.py"
echo ""
echo "⚠️ Recuerda configurar las variables de entorno necesarias:"
echo "export TELEGRAM_BOT_TOKEN=\"tu_token_de_telegram\""
echo "export OPENAI_API_KEY=\"tu_clave_api_de_openai\" # Si usas OpenAI"
