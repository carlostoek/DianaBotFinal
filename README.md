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

## Sistema Administrativo

El bot incluye un sistema de comandos administrativos accesible mediante `/admin`.

### Configuración de Administradores

Para configurar usuarios administradores, agregar sus IDs de Telegram a la variable de entorno:

```bash
ADMIN_USER_IDS=123456789,987654321
```

### Funcionalidades del Panel Admin

- **Gestión de Canales**: VIP y Free
- **Gamificación**: Misiones, insignias, niveles
- **Tienda**: Productos y desbloqueos
- **Narrativa**: Fragmentos y árbol de decisiones
- **Estadísticas**: Métricas del sistema
- **Configuración**: Ajustes del bot

## Desarrollo

Seguir la [Hoja de Ruta](docs/HOJA_DE_RUTA.md) para implementación incremental.