#!/usr/bin/env python3
"""
Modelo de Licencias para Personal Automation Bot
Venta de licencias de software con diferentes niveles de acceso.
"""

from enum import Enum
from datetime import datetime


class LicenseType(Enum):
    PERSONAL = "personal"
    COMMERCIAL = "commercial"
    ENTERPRISE = "enterprise"
    DEVELOPER = "developer"


class LicensingModel:
    """Modelo de licencias para el bot."""

    LICENSES = {
        LicenseType.PERSONAL: {
            "name": "Licencia Personal",
            "price": 49.99,
            "currency": "USD",
            "type": "one_time",
            "description": "Para uso personal únicamente",
            "includes": [
                "Código fuente completo",
                "Documentación de instalación",
                "Soporte por email (30 días)",
                "Actualizaciones menores (6 meses)"
            ],
            "restrictions": [
                "Solo uso personal",
                "No redistribución",
                "No uso comercial",
                "Máximo 1 instalación"
            ],
            "support_level": "basic"
        },

        LicenseType.COMMERCIAL: {
            "name": "Licencia Comercial",
            "price": 299.99,
            "currency": "USD",
            "type": "one_time",
            "description": "Para uso comercial en pequeñas empresas",
            "includes": [
                "Todo lo de la licencia personal",
                "Uso comercial permitido",
                "Soporte prioritario (90 días)",
                "Actualizaciones mayores (1 año)",
                "Personalización básica incluida"
            ],
            "restrictions": [
                "Máximo 10 usuarios",
                "Una empresa únicamente",
                "No reventa del software"
            ],
            "support_level": "priority"
        },

        LicenseType.ENTERPRISE: {
            "name": "Licencia Empresarial",
            "price": 999.99,
            "currency": "USD",
            "type": "one_time",
            "description": "Para grandes empresas y organizaciones",
            "includes": [
                "Todo lo de la licencia comercial",
                "Usuarios ilimitados",
                "Personalización completa",
                "Soporte 24/7 (1 año)",
                "Instalación asistida",
                "Integración personalizada",
                "Actualizaciones de por vida"
            ],
            "restrictions": [
                "Una organización únicamente",
                "Requiere acuerdo de confidencialidad"
            ],
            "support_level": "premium"
        },

        LicenseType.DEVELOPER: {
            "name": "Licencia de Desarrollador",
            "price": 199.99,
            "currency": "USD",
            "type": "one_time",
            "description": "Para desarrolladores que quieren crear productos derivados",
            "includes": [
                "Código fuente con comentarios detallados",
                "Documentación técnica completa",
                "Derecho a crear productos derivados",
                "Soporte técnico especializado",
                "Acceso al repositorio privado"
            ],
            "restrictions": [
                "Debe dar crédito al proyecto original",
                "No puede usar la marca 'Personal Automation Bot'",
                "Debe compartir mejoras significativas"
            ],
            "support_level": "technical"
        }
    }


def create_licensing_documentation():
    """Crea documentación completa de licencias."""

    doc = """# 📜 Licencias - Personal Automation Bot

## 🎯 Tipos de Licencia Disponibles

### 👤 Licencia Personal - $49.99
**Para uso personal únicamente**

✅ **Incluye:**
- Código fuente completo
- Documentación de instalación paso a paso
- Soporte por email durante 30 días
- Actualizaciones menores por 6 meses
- Guía de configuración personalizada

❌ **Restricciones:**
- Solo para uso personal (no comercial)
- No se puede redistribuir
- Máximo 1 instalación
- No se puede modificar para reventa

🎯 **Ideal para:** Profesionales independientes, estudiantes, uso doméstico

---

### 🏢 Licencia Comercial - $299.99
**Para pequeñas y medianas empresas**

✅ **Incluye:**
- Todo lo de la licencia personal
- Derecho de uso comercial
- Soporte prioritario por 90 días
- Actualizaciones mayores por 1 año
- Personalización básica incluida
- Instalación para hasta 10 usuarios

❌ **Restricciones:**
- Máximo 10 usuarios simultáneos
- Una empresa únicamente
- No se puede revender el software

🎯 **Ideal para:** Startups, pequeñas empresas, equipos de trabajo

---

### 🏭 Licencia Empresarial - $999.99
**Para grandes organizaciones**

✅ **Incluye:**
- Todo lo de la licencia comercial
- Usuarios ilimitados
- Personalización completa del bot
- Soporte 24/7 durante 1 año
- Instalación asistida por expertos
- Integración con sistemas existentes
- Actualizaciones de por vida
- SLA garantizado

❌ **Restricciones:**
- Una organización únicamente
- Requiere acuerdo de confidencialidad

🎯 **Ideal para:** Corporaciones, organizaciones gubernamentales, grandes equipos

---

### 👨‍💻 Licencia de Desarrollador - $199.99
**Para crear productos derivados**

✅ **Incluye:**
- Código fuente con comentarios detallados
- Documentación técnica completa
- Derecho a crear productos derivados
- Soporte técnico especializado
- Acceso al repositorio privado de desarrollo
- Ejemplos de extensiones

❌ **Restricciones:**
- Debe dar crédito al proyecto original
- No puede usar la marca registrada
- Debe compartir mejoras significativas (open source)

🎯 **Ideal para:** Desarrolladores, consultores, empresas de software

## 💳 Proceso de Compra

### 1. Selección de Licencia
- Elige la licencia que mejor se adapte a tus necesidades
- Revisa las restricciones y términos

### 2. Pago Seguro
- Pagos procesados por Stripe
- Aceptamos tarjetas de crédito/débito
- PayPal disponible
- Facturación automática

### 3. Entrega Inmediata
- Acceso instantáneo al código fuente
- Descarga desde portal seguro
- Documentación incluida
- Licencia digital firmada

### 4. Soporte Incluido
- Email de soporte dedicado
- Documentación técnica
- Comunidad de usuarios
- Actualizaciones automáticas

## 🔒 Términos de Licencia

### Derechos Otorgados
- Uso del software según el tipo de licencia
- Modificación para uso interno
- Integración con otros sistemas (según licencia)

### Restricciones Generales
- No ingeniería inversa maliciosa
- No eliminación de avisos de copyright
- No uso para actividades ilegales
- Cumplimiento de leyes locales

### Garantías
- Software entregado "tal como está"
- Garantía de funcionamiento básico
- Soporte técnico incluido según plan
- Reembolso en 30 días si no funciona

## 🛡️ Protección Anti-Piratería

### Medidas Técnicas
- Licencias firmadas digitalmente
- Verificación de autenticidad
- Watermarks en el código
- Tracking de instalaciones

### Medidas Legales
- Términos de uso claros
- DMCA takedown notices
- Acciones legales cuando sea necesario
- Colaboración con plataformas

## 📊 Comparación de Licencias

| Característica | Personal | Comercial | Empresarial | Desarrollador |
|----------------|----------|-----------|-------------|---------------|
| **Precio** | $49.99 | $299.99 | $999.99 | $199.99 |
| **Usuarios** | 1 | 10 | Ilimitado | 1 |
| **Uso Comercial** | ❌ | ✅ | ✅ | ✅ |
| **Soporte** | 30 días | 90 días | 1 año | Especializado |
| **Actualizaciones** | 6 meses | 1 año | De por vida | Acceso repo |
| **Personalización** | Básica | Incluida | Completa | Total |
| **Código Fuente** | ✅ | ✅ | ✅ | ✅ + Docs |

## 🚀 Upgrades y Renovaciones

### Upgrade de Licencia
- Paga solo la diferencia
- Migración automática
- Sin pérdida de datos
- Soporte en la transición

### Renovación de Soporte
- Extiende el período de soporte
- Acceso a nuevas actualizaciones
- Precios preferenciales
- Sin interrupción del servicio

## 📞 Contacto de Ventas

- **Email:** sales@personalautomationbot.com
- **WhatsApp:** +1 (555) 123-4567
- **Horario:** Lunes a Viernes, 9AM - 6PM EST
- **Respuesta:** Dentro de 24 horas

¿Necesitas una licencia personalizada? ¡Contáctanos!
"""

    return doc


def create_license_generator():
    """Crea un generador de licencias digitales."""

    generator = '''#!/usr/bin/env python3
"""
Generador de licencias digitales para Personal Automation Bot.
"""

import json
import hashlib
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet


class LicenseGenerator:
    """Generador de licencias digitales."""

    def __init__(self, secret_key=None):
        if secret_key:
            self.cipher = Fernet(secret_key)
        else:
            self.cipher = Fernet(Fernet.generate_key())

    def generate_license(self, license_type, customer_info, duration_days=None):
        """Genera una licencia digital."""

        license_data = {
            "license_id": self._generate_license_id(),
            "license_type": license_type,
            "customer": customer_info,
            "issued_date": datetime.now().isoformat(),
            "expires_date": (datetime.now() + timedelta(days=duration_days)).isoformat() if duration_days else None,
            "features": self._get_features_for_license(license_type),
            "restrictions": self._get_restrictions_for_license(license_type)
        }

        # Encriptar la licencia
        license_json = json.dumps(license_data)
        encrypted_license = self.cipher.encrypt(license_json.encode())

        # Codificar en base64 para fácil distribución
        license_key = base64.b64encode(encrypted_license).decode()

        return {
            "license_key": license_key,
            "license_data": license_data
        }

    def verify_license(self, license_key):
        """Verifica una licencia digital."""
        try:
            # Decodificar y desencriptar
            encrypted_license = base64.b64decode(license_key.encode())
            decrypted_data = self.cipher.decrypt(encrypted_license)
            license_data = json.loads(decrypted_data.decode())

            # Verificar expiración
            if license_data.get("expires_date"):
                expires = datetime.fromisoformat(license_data["expires_date"])
                if datetime.now() > expires:
                    return {"valid": False, "reason": "License expired"}

            return {"valid": True, "data": license_data}

        except Exception as e:
            return {"valid": False, "reason": f"Invalid license: {str(e)}"}

    def _generate_license_id(self):
        """Genera un ID único para la licencia."""
        timestamp = str(datetime.now().timestamp())
        return hashlib.md5(timestamp.encode()).hexdigest()[:16].upper()

    def _get_features_for_license(self, license_type):
        """Obtiene las características según el tipo de licencia."""
        features_map = {
            "personal": ["email", "calendar", "basic_ai"],
            "commercial": ["email", "calendar", "advanced_ai", "workflows", "multi_user"],
            "enterprise": ["all_features", "custom_integrations", "priority_support"],
            "developer": ["source_code", "documentation", "modification_rights"]
        }
        return features_map.get(license_type, [])

    def _get_restrictions_for_license(self, license_type):
        """Obtiene las restricciones según el tipo de licencia."""
        restrictions_map = {
            "personal": ["no_commercial_use", "single_user", "no_redistribution"],
            "commercial": ["max_10_users", "single_organization"],
            "enterprise": ["single_organization", "nda_required"],
            "developer": ["attribution_required", "share_improvements"]
        }
        return restrictions_map.get(license_type, [])


def main():
    """Ejemplo de uso del generador de licencias."""
    generator = LicenseGenerator()

    # Generar licencia personal
    customer = {
        "name": "Juan Pérez",
        "email": "juan@example.com",
        "company": "Freelancer"
    }

    license_info = generator.generate_license("personal", customer, 365)

    print("🔑 Licencia generada:")
    print(f"ID: {license_info['license_data']['license_id']}")
    print(f"Tipo: {license_info['license_data']['license_type']}")
    print(f"Cliente: {license_info['license_data']['customer']['name']}")
    print(f"Clave: {license_info['license_key'][:50]}...")

    # Verificar licencia
    verification = generator.verify_license(license_info['license_key'])
    print(f"\\nVerificación: {'✅ Válida' if verification['valid'] else '❌ Inválida'}")


if __name__ == "__main__":
    main()
'''

    return generator


def main():
    """Genera documentación del modelo de licencias."""

    print("📜 Generando modelo de licencias...")

    # Crear documentación de licencias
    with open("docs/licensing_model.md", "w") as f:
        f.write(create_licensing_documentation())

    # Crear generador de licencias
    with open("tools/license_generator.py", "w") as f:
        f.write(create_license_generator())

    # Crear configuración de licencias
    with open("config/license_types.json", "w") as f:
        licenses_data = {license.value: config for license, config in LicensingModel.LICENSES.items()}
        json.dump(licenses_data, f, indent=2)

    print("✅ Documentación de licencias generada:")
    print("   📄 docs/licensing_model.md")
    print("   🔑 tools/license_generator.py")
    print("   ⚙️  config/license_types.json")

    print("\n💰 Proyección de ingresos (licencias):")
    print("   Personal (100/mes): $4,999/mes")
    print("   Comercial (20/mes): $5,999/mes")
    print("   Empresarial (5/mes): $4,999/mes")
    print("   Desarrollador (10/mes): $1,999/mes")
    print("   TOTAL ESTIMADO: $17,996/mes")


if __name__ == "__main__":
    main()
