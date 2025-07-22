#!/usr/bin/env python3
"""
Configurador principal para compartir el bot con tu hermano.
"""

import os
import sys


def show_options():
    """Muestra las opciones disponibles."""
    print("🤖 Personal Automation Bot - Configurador para Hermano")
    print("=" * 60)
    print()
    print("Tienes dos opciones para que tu hermano use el bot:")
    print()
    print("📱 OPCIÓN 1: INSTANCIA SEPARADA (Recomendada)")
    print("   ✅ Tu hermano tiene su propio bot de Telegram")
    print("   ✅ Datos completamente separados")
    print("   ✅ No hay interferencia entre ustedes")
    print("   ✅ Cada uno puede personalizar su bot")
    print("   ❌ Requiere configurar Google Cloud Console separado")
    print("   ❌ Dos bots diferentes para mantener")
    print()
    print("👥 OPCIÓN 2: MULTI-USUARIO (Mismo bot)")
    print("   ✅ Un solo bot para ambos")
    print("   ✅ Datos separados por usuario")
    print("   ✅ Fácil de mantener")
    print("   ✅ Comparten configuración de Google Cloud")
    print("   ❌ Ambos ven el mismo bot")
    print("   ❌ Si el bot se cae, afecta a ambos")
    print()


def option_1_separate_instance():
    """Configura una instancia separada."""
    print("📱 Configurando instancia separada...")
    print()
    print("Esta opción creará una copia completa del bot para tu hermano.")
    print("Él tendrá su propio bot de Telegram y sus propios datos.")
    print()

    confirm = input("¿Continuar con instancia separada? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes', 'sí', 's']:
        return

    # Ejecutar script de instancia separada
    os.system("python3 setup_new_instance.py")


def option_2_multiuser():
    """Configura modo multi-usuario."""
    print("👥 Configurando modo multi-usuario...")
    print()
    print("Esta opción permite que ambos usen el mismo bot")
    print("pero con datos completamente separados.")
    print()

    confirm = input("¿Continuar con modo multi-usuario? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes', 'sí', 's']:
        return

    # Ejecutar script multi-usuario
    os.system("python3 setup_multiuser.py")


def get_telegram_id_help():
    """Muestra ayuda para obtener ID de Telegram."""
    print("🆔 Cómo obtener el ID de Telegram de tu hermano:")
    print()
    print("MÉTODO 1: Usando @userinfobot")
    print("1. Tu hermano debe agregar @userinfobot en Telegram")
    print("2. Enviar /start al bot")
    print("3. El bot le dará su ID numérico")
    print()
    print("MÉTODO 2: Usando tu bot actual")
    print("1. Agrega este código temporal a tu bot:")
    print("   - En cualquier comando, agrega: print(f'User ID: {update.effective_user.id}')")
    print("2. Tu hermano envía cualquier comando")
    print("3. Verás su ID en los logs")
    print()
    print("MÉTODO 3: Usando @RawDataBot")
    print("1. Tu hermano agrega @RawDataBot")
    print("2. Envía cualquier mensaje")
    print("3. El bot muestra toda la información, incluyendo el ID")
    print()


def create_quick_setup_guide():
    """Crea una guía rápida para tu hermano."""
    guide_content = """# 🤖 Personal Automation Bot - Guía Rápida para Hermano

## 🎯 ¿Qué es esto?

Es un bot de Telegram que te ayuda a:
- ✅ Leer y enviar emails desde Telegram
- ✅ Gestionar tu calendario de Google
- ✅ Generar contenido con IA
- ✅ Automatizar tareas repetitivas

## 🚀 Configuración Súper Rápida

### Paso 1: Crear tu bot de Telegram
1. Abre Telegram y busca @BotFather
2. Envía `/newbot`
3. Sigue las instrucciones (elige un nombre y username)
4. **GUARDA EL TOKEN** que te da (algo como: 123456:ABC-DEF...)

### Paso 2: Configurar Google
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea una cuenta si no tienes (es gratis)
3. Crea un nuevo proyecto
4. Busca "Gmail API" y actívala
5. Ve a "Credenciales" → "Crear credenciales" → "OAuth 2.0"
6. Descarga el archivo JSON como `credentials.json`

### Paso 3: Ejecutar el bot
```bash
# Si Mauro te dio una carpeta:
cd carpeta_del_bot
python3 setup.py
python3 start_hermano.py

# Si es modo multi-usuario:
# Solo envía un mensaje al bot de Mauro
```

## 🆘 Si algo no funciona

1. **Toma captura de pantalla del error**
2. **Copia el mensaje de error completo**
3. **Envíaselo a Mauro por WhatsApp**

## 🔒 Seguridad

- ✅ Tus datos están separados de los de Mauro
- ✅ Solo tú puedes ver tus emails
- ✅ Cada uno tiene su propia configuración
- ✅ Es seguro y privado

## 💡 Comandos Básicos

Una vez configurado:
- `/start` - Comenzar
- `/email` - Gestionar correos
- `/help` - Ayuda
- `/menu` - Menú principal

¡Disfruta tu nuevo asistente personal! 🎉
"""

    with open("GUIA_RAPIDA_HERMANO.md", "w") as f:
        f.write(guide_content)

    print("✅ Guía rápida creada: GUIA_RAPIDA_HERMANO.md")
    print("📤 Puedes enviar este archivo a tu hermano")


def main():
    """Función principal."""
    while True:
        show_options()

        print("¿Qué opción prefieres?")
        print("1. Instancia separada (recomendada)")
        print("2. Multi-usuario (mismo bot)")
        print("3. Ver cómo obtener ID de Telegram")
        print("4. Crear guía rápida para hermano")
        print("5. Salir")
        print()

        choice = input("Selecciona una opción (1-5): ").strip()

        if choice == "1":
            option_1_separate_instance()
        elif choice == "2":
            option_2_multiuser()
        elif choice == "3":
            get_telegram_id_help()
        elif choice == "4":
            create_quick_setup_guide()
        elif choice == "5":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")

        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
