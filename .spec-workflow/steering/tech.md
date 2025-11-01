# ⚙️ Estándares Técnicos — DianaBot

## Stack Tecnológico

### Backend
- Lenguaje: Python 3.11
- Framework Bot: python-telegram-bot 20.7
- Framework API: FastAPI 0.104.1
- ORM: SQLAlchemy 2.0.23
- Validación: Pydantic 2.5.0 + Pydantic Settings 2.1.0

### Base de Datos
- PostgreSQL 15: Almacenamiento relacional (usuarios, misiones, logros, etc.)
- MongoDB 6: Almacenamiento de contenido narrativo detallado
- Redis 7: Caché, pub/sub para Event Bus, sesiones y contadores

### Herramientas
- Contenedores: Docker + Docker Compose
- Tareas Asíncronas: Celery 5.3.4
- Servidor ASGI: Uvicorn 0.24.0
- Gestión de dependencias: pip
- Linting y formateo: Black 23.11.0, isort 5.13.2

## Decisiones Técnicas Clave
- **Arquitectura basada en eventos**: Uso de Event Bus con Redis para comunicar módulos
- **Base de datos híbrida**: PostgreSQL para relaciones estructuradas, MongoDB para contenido narrativo flexible
- **Desacoplamiento de módulos**: Comunicación a través de eventos en lugar de dependencias directas
- **Configuración centralizada**: Gestión de configuración con Pydantic Settings
- **Procesamiento asíncrono**: Uso de Celery para tareas que no requieren respuesta inmediata

## Restricciones y Políticas
- **Seguridad**: Variables de entorno para secrets, validación de entradas, protección contra inyección SQL
- **Escalabilidad**: Uso de Redis para caché y colas de tareas, índices en bases de datos
- **Compatibilidad**: Aplicación Dockerizada para despliegue consistente en diferentes entornos
- **Dependencias**: Uso de librerías maduras y mantenidas con buena documentación

## Servicios Externos
- **Telegram API**: Para comunicación con usuarios y manejo de interacciones en el bot
- **Posible integración futura**: Proveedores de pago (Stripe, posiblemente Telegram Stars)