# 📂 Estructura del Proyecto — DianaBot

## Organización de Directorios

```
.
├── api/                 # API REST con FastAPI
│   └── main.py          # Punto de entrada de la API
├── bot/                 # Componentes del bot de Telegram
│   ├── main.py          # Punto de entrada del bot
│   └── handlers/        # Handlers para comandos y mensajes
├── config/              # Configuración del proyecto
│   └── settings.py      # Configuración centralizada con Pydantic
├── core/                # Componentes centrales del sistema
│   ├── event_bus.py     # Implementación del Event Bus con Redis
│   ├── event_handlers.py # Handlers para eventos del sistema
│   └── config_manager.py # Gestor centralizado de configuración
├── modules/             # Módulos funcionales del sistema
│   ├── narrative/       # Sistema de narrativa ramificada
│   ├── gamification/    # Sistemas de gamificación (besitos, items, misiones, logros)
│   ├── admin/           # Funcionalidades de administración
│   └── shop/            # Sistema de tienda virtual
├── database/            # Componentes relacionados con la base de datos
│   ├── models.py        # Modelos de SQLAlchemy
│   ├── connection.py    # Configuración de conexiones a bases de datos
│   ├── migrations/      # Scripts de migración de la base de datos
│   └── seeds/           # Datos de ejemplo para inicialización
├── dashboard/           # Panel administrativo web
│   ├── templates/       # Templates HTML para el dashboard
│   ├── static/          # Archivos estáticos (CSS, JS)
│   └── views.py         # Vistas del dashboard
├── tasks/               # Tareas programadas y asincrónicas
│   └── celery_app.py    # Configuración de Celery
├── utils/               # Utilidades comunes
├── docs/                # Documentación del proyecto
├── tests/               # Suite de tests
└── docker/              # Configuración de contenedores
```

## Convenciones de Nomenclatura

- **Archivos**: snake_case para módulos Python (main.py, event_bus.py), kebab-case para archivos de configuración
- **Variables**: snake_case (user_profile, is_vip)
- **Constantes**: UPPER_SNAKE_CASE (MAX_RETRY_ATTEMPTS)
- **Clases**: PascalCase (EventBus, UserManager)

## Estilo de Código
- **Indentación**: 4 espacios
- **Líneas**: Límite de 88 caracteres por línea (según Black)
- **Imports**: Agrupados en estándar, externos e internos con isort
- **Docstrings**: Formato Google para documentación de funciones y clases

## Testing
- **Unit Tests**: Cobertura de lógica de negocio y utilidades
- **Integration Tests**: Verificación de integraciones entre módulos
- **E2E Tests**: Simulación de flujos completos de usuario
- **Ubicación**: `tests/unit/`, `tests/integration/`, `tests/e2e/`

## Documentación
- **Type hints**: Obligatorios en funciones públicas y de negocio
- **Docstrings**: En todas las funciones, clases y módulos
- **README.md**: Descripción general del proyecto, setup y arquitectura
- **docs/**: Documentación detallada por secciones (API, arquitectura, deployment)