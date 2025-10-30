# DianaBot

Sistema de Telegram con narrativa ramificada, gamificación y administración de contenido.

## Características

- **Narrativa Ramificada**: Sistema de fragmentos y decisiones interactivas
- **Gamificación**: Economía de "besitos", inventario, misiones y logros
- **Administración**: Gestión de canales VIP y contenido programado
- **Arquitectura Event-Driven**: Comunicación entre módulos vía Event Bus

## Estructura del Proyecto

```
bot/          # Entry point del bot y handlers
core/         # Componentes centrales (Event Bus, Config Manager)
modules/      # Módulos de narrativa, gamificación, administración
database/     # Modelos, migraciones, seeds
config/       # Configuración y settings
docker/       # Configuración de contenedores
api/          # API REST para panel administrativo
dashboard/     # Panel web administrativo
tasks/        # Tareas programadas (Celery)
utils/        # Utilidades comunes
```

## Instalación

1. Clonar el repositorio
2. Configurar variables de entorno en `.env`
3. Ejecutar `docker-compose up -d`
4. Ejecutar migraciones de base de datos

## Desarrollo

Seguir la [Hoja de Ruta](docs/HOJA_DE_RUTA.md) para implementación incremental.