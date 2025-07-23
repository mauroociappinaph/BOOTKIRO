"""
Script para indexar documentos en el sistema RAG.
"""
import os
import sys
import logging
import argparse
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Función principal para indexar documentos."""
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description='Indexar documentos para el sistema RAG')
    parser.add_argument('--dir', type=str, help='Directorio con documentos para indexar')
    parser.add_argument('--file', type=str, help='Archivo individual para indexar')
    parser.add_argument('--force', action='store_true', help='Forzar reindexación de documentos')
    args = parser.parse_args()

    if not args.dir and not args.file:
        parser.print_help()
        sys.exit(1)

    try:
        # Importar componentes RAG
        from personal_automation_bot.services.rag.vector_store import get_vector_store
        from personal_automation_bot.services.rag.indexer import DocumentIndexer
        from personal_automation_bot.services.rag.document_indexer import DocumentIndexingService

        # Crear vector store
        logger.info("Inicializando vector store...")
        vector_store = get_vector_store("faiss")

        # Crear indexer
        logger.info("Inicializando indexer...")
        indexer = DocumentIndexer(vector_store=vector_store)

        # Crear servicio de indexación
        logger.info("Inicializando servicio de indexación...")
        indexing_service = DocumentIndexingService(indexer=indexer)

        # Indexar directorio o archivo
        if args.dir:
            if os.path.isdir(args.dir):
                logger.info(f"Indexando documentos en {args.dir}...")
                results = indexing_service.index_directory(args.dir, force=args.force)
                logger.info(f"Indexados {len(results)} documentos")

                # Mostrar detalles de los documentos indexados
                for file_path, chunk_ids in results.items():
                    logger.info(f"  - {file_path}: {len(chunk_ids)} fragmentos")
            else:
                logger.error(f"El directorio {args.dir} no existe")

        if args.file:
            if os.path.isfile(args.file):
                logger.info(f"Indexando archivo {args.file}...")
                chunk_ids = indexing_service.index_document(args.file, force=args.force)
                logger.info(f"Archivo indexado en {len(chunk_ids)} fragmentos")
            else:
                logger.error(f"El archivo {args.file} no existe")

        logger.info("Indexación completada")

    except ImportError as e:
        logger.error(f"Error al importar módulos: {e}")
        logger.error("Asegúrate de haber instalado todas las dependencias con 'pip install -r requirements.txt'")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error al indexar documentos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
