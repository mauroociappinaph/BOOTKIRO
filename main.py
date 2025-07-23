"""
Script principal para iniciar el bot de Telegram.
"""
import os
import logging
import sys
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log")
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal para iniciar el bot."""
    try:
        # Importar el setup_bot después de configurar logging
        from personal_automation_bot.bot.core import setup_bot

        # Obtener token del bot
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN no está configurado. Por favor, configura esta variable de entorno.")
            sys.exit(1)

        logger.info("Iniciando bot de Telegram...")

        # Configurar y ejecutar el bot
        app = setup_bot(token)

        # Mostrar información del bot
        logger.info("Bot configurado correctamente. Iniciando polling...")

        # Iniciar el bot
        app.run_polling()

    except ImportError as e:
        logger.error(f"Error al importar módulos: {e}")
        logger.error("Asegúrate de haber instalado todas las dependencias con 'pip install -r requirements.txt'")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error al iniciar el bot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
