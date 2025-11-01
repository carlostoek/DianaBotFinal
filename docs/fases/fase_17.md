#### 1. Arquitectura General
**Arquitectura modular basada en eventos** que integra tres patrones clave:
- **Event-Driven**: Comunicación asíncrona entre módulos (narrativa, gamificación, administración) mediante un **Event Bus** central (Pub/Sub). Ej.: Completar un fragmento narrativo publica un evento que activa recompensas en gamificación.
- **Capas Limpias**: Cada módulo es independiente, con interfaces claras para integración.
- **Repositorio Centralizado**: **Configuration Manager** unifica reglas, recompensas y desbloqueos, sincronizando cambios entre módulos.

**Componentes Principales**:
- **Event Bus**: Sistema nervioso central para publicación/suscripción de eventos.
- **Configuration Manager**: Abstracción para crear "experiencias" coordinadas (narrativa + gamificación).
- **User State Manager**: Mantiene consistencia del estado del usuario (progreso, besitos, inventario, suscripciones).

**Patrones de Diseño**:
- **Command**: Acciones de usuario encapsuladas (deshacer, historial, asíncronas).
- **Observer**: Módulos suscritos a eventos relevantes.
- **Strategy**: Condiciones de desbloqueo intercambiables.
- **Repository**: Acceso abstraído a datos.

#### 2. Plataforma y Tecnologías
**Framework del Bot**: **python-telegram-bot (PTB) v20+**, elegido por:
- Manejo nativo de handlers, **ConversationHandler** (narrativa ramificada), callbacks y reacciones.
- **JobQueue** integrada para misiones diarias, recordatorios VIP y scheduling.
- Excelente documentación y comunidad.

**Estructura Tecnológica**:
- Backend: Python 3.11+
- Web: FastAPI (panel admin, webhooks)
- Tareas: Celery + Redis
- Cache: Redis (sesiones, rate limiting)

**Base de Datos Híbrida**:
- **PostgreSQL (Principal)**: Datos relacionales/transaccionales (estado usuario, progreso narrativo, suscripciones). Garantías ACID, JSONB para flexibilidad, índices para consultas complejas.
- **MongoDB**: Configuración dinámica y estructuras variables (fragmentos narrativos con decisiones/minijuegos, plantillas de experiencias).
- **Redis**: Estado en tiempo real (conversaciones activas, rate limiting, locks distribuidos para subastas).

# Fase 17: API REST (FastAPI)

### Objetivo
API para panel administrativo

### Componentes a Implementar

#### 17.1 Setup de FastAPI
- **Crear**: Aplicación FastAPI
- **Referencia**: Sección 10.2 - Stack Tecnológico
- **Archivos**:
  - `api/main.py`
  - `api/__init__.py`
  - `requirements.txt` (añadir FastAPI, uvicorn)

#### 17.2 Sistema de Autenticación
- **Crear**: JWT auth para admins
- **Referencia**: Sección 9.3 - Sistema de Roles y Permisos
- **Archivos**:
  - `api/middleware/auth.py`
  - `database/models.py` (modelo AdminUser)
  - `database/migrations/014_create_admin_users.sql`
- **Funcionalidad**:
  - Login con username/password
  - Generar JWT token
  - Middleware de verificación
  - Roles y permisos

#### 17.3 Routers de Configuración
- **Crear**: Endpoints de config
- **Referencia**: Sección 6.4 - API de Configuración Centralizada
- **Archivos**:
  - `api/routers/config.py`
- **Endpoints**:
  - `POST /api/config/templates`
  - `GET /api/config/templates/{id}`
  - `POST /api/config/instances`
  - `PUT /api/config/instances/{id}`
  - `DELETE /api/config/instances/{id}`
  - `POST /api/config/validate`
  - `POST /api/config/propagate/{id}`

#### 17.4 Routers de Usuarios
- **Crear**: Endpoints de gestión de usuarios
- **Archivos**:
  - `api/routers/users.py`
- **Endpoints**:
  - `GET /api/users`
  - `GET /api/users/{id}`
  - `PUT /api/users/{id}/subscription`
  - `POST /api/users/{id}/grant-besitos`
  - `GET /api/users/{id}/stats`

#### 17.5 Routers de Contenido
- **Crear**: Endpoints de gestión de contenido
- **Archivos**:
  - `api/routers/content.py`
- **Endpoints**:
  - Narrativa: CRUD de fragmentos
  - Gamificación: CRUD de items, misiones, achievements
  - Canales: CRUD de posts programados

#### 17.6 Routers de Analíticas
- **Crear**: Endpoints de métricas
- **Referencia**: Sección 12 - Métricas de Éxito y KPIs
- **Archivos**:
  - `api/routers/analytics.py`
- **Endpoints**:
  - `GET /api/metrics/summary`
  - `GET /api/metrics/engagement`
  - `GET /api/metrics/monetization`
  - `GET /api/metrics/narrative`

#### 17.7 Rate Limiting
- **Crear**: Limitación de requests
- **Referencia**: Sección 8.1 - Seguridad
- **Archivos**:
  - `api/middleware/rate_limit.py`
- **Funcionalidad**:
  - Límites por endpoint
  - Tracking en Redis
  - Headers de rate limit

#### 17.8 Documentación Automática
- **Configurar**: OpenAPI/Swagger
- **Funcionalidad**:
  - FastAPI genera automáticamente
  - Disponible en `/docs`
  - Modelos Pydantic para request/response

### Resultado de Fase 17
✓ API REST funcional
✓ Autenticación JWT
✓ Endpoints de configuración
✓ Endpoints de gestión
✓ Documentación automática
✓ Rate limiting

## Referencias
### 6.4 API de Configuración Centralizada

La API expone endpoints para gestionar configuración programáticamente.

**Endpoints Principales**

```
POST /api/config/templates
GET /api/config/templates/{template_id}
POST /api/config/instances
PUT /api/config/instances/{instance_id}
DELETE /api/config/instances/{instance_id}
POST /api/config/validate
POST /api/config/propagate/{instance_id}
GET /api/config/dependencies/{instance_id}
```

**Validación antes de Guardar**

El endpoint `/api/config/validate` permite verificar configuración sin guardarla:

```python
{
  "template": "narrative_experience",
  "data": {
    "name": "Test Experience",
    "fragments": [...],
    "rewards": {...}
  }
}
```

Respuesta:

```python
{
  "valid": true,
  "warnings": [
    {
      "field": "rewards.besitos",
      "message": "Value is above recommended range",
      "severity": "warning"
    }
  ],
  "errors": [],
  "suggestions": [
    {
      "field": "fragments[2].decisions",
      "message": "Consider adding a third decision for more depth",
      "auto_fix_available": true
    }
  ]
}
```

**Propagación Controlada**

Cuando se actualiza una configuración, el administrador puede controlar qué cambios se propagan:

```python
PUT /api/config/instances/123
{
  "data": {
    "rewards": {
      "besitos": 150  // aumentado de 100
    }
  },
  "propagation_options": {
    "apply_to_existing_users": false,  // solo nuevos usuarios
    "notify_affected_users": true,
    "create_migration": true,  // guardar cambio como migración
    "rollback_on_error": true
  }
}
```

El sistema ejecuta la propagación y responde con reporte detallado:

```python
{
  "success": true,
  "changes_applied": [
    "Updated fragments table: 3 records",
    "Updated MongoDB narrative_content: 3 documents",
    "Scheduled notification to 45 affected users",
    "Created migration record: MIG_2025_10_28_001"
  ],
  "rollback_token": "RB_xyz789",  // para rollback manual si necesario
  "affected_systems": ["narrativa", "gamificación", "admin_canales"]
}
```

### 9.3 Sistema de Roles y Permisos

Más allá de Free/VIP, el sistema soporta roles granulares para gestión:

**Jerarquía de Roles**

```python
class Role(Enum):
    OWNER = 1000        # Acceso total
    ADMIN = 800         # Gestión de contenido y usuarios
    MODERATOR = 600     # Moderación de usuarios
    CONTENT_CREATOR = 400  # Crear contenido pero no publicar
    VIP_USER = 200      # Acceso a contenido VIP
    FREE_USER = 100     # Acceso básico
    BANNED = 0          # Sin acceso

class Permission(Enum):
    # Contenido
    CREATE_CONTENT = 'create_content'
    EDIT_CONTENT = 'edit_content'
    DELETE_CONTENT = 'delete_content'
    PUBLISH_CONTENT = 'publish_content'
    
    # Usuarios
    VIEW_USERS = 'view_users'
    MANAGE_SUBSCRIPTIONS = 'manage_subscriptions'
    BAN_USERS = 'ban_users'
    
    # Configuración
    EDIT_CONFIGURATION = 'edit_configuration'
    VIEW_ANALYTICS = 'view_analytics'
    
    # Gamificación
    GRANT_BESITOS = 'grant_besitos'
    CREATE_ITEMS = 'create_items'

# Mapeo de roles a permisos
ROLE_PERMISSIONS = {
    Role.OWNER: [perm for perm in Permission],  # todos los permisos
    Role.ADMIN: [
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT,
        Permission.DELETE_CONTENT,
        Permission.PUBLISH_CONTENT,
        Permission.VIEW_USERS,
        Permission.MANAGE_SUBSCRIPTIONS,
        Permission.BAN_USERS,
        Permission.VIEW_ANALYTICS,
        Permission.GRANT_BESITOS,
        Permission.CREATE_ITEMS
    ],
    Role.MODERATOR: [
        Permission.VIEW_USERS,
        Permission.BAN_USERS,
        Permission.VIEW_ANALYTICS
    ],
    Role.CONTENT_CREATOR: [
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT
    ]
}
```

**Verificación de Permisos**

```python
def has_permission(user_id, permission):
    """Verifica si usuario tiene permiso específico"""
    user_role = get_user_role(user_id)
    return permission in ROLE_PERMISSIONS.get(user_role, [])

def require_permission(permission):
    """Decorator para proteger funciones con permisos"""
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user_id = update.effective_user.id
            
            if not has_permission(user_id, permission):
                await update.message.reply_text(
                    "No tienes permisos para realizar esta acción."
                )
                return
            
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

# Uso
@require_permission(Permission.PUBLISH_CONTENT)
async def publish_fragment(update, context):
    """Solo admins y owners pueden publicar"""
    # lógica de publicación
    pass
```

### 8.1 Seguridad

**Protección de Datos de Usuario**

Los datos de usuarios deben protegerse rigurosamente:

Encriptación en reposo: Datos sensibles en la base de datos se encriptan usando AES-256. Esto incluye información de pago, información personal identificable, y mensajes privados.

Encriptación en tránsito: Todas las comunicaciones con la API de Telegram usan HTTPS/TLS 1.3.

Tokens y Secretos: El bot token de Telegram nunca se hardcodea, siempre se almacena en variables de entorno o servicios de gestión de secretos como AWS Secrets Manager o HashiCorp Vault.

**Prevención de Fraude en Besitos**

La economía virtual es vulnerable a explotación:

Rate Limiting por Usuario:
```python
def check_rate_limit(user_id, action, limit, window_seconds):
    """
    Verifica si el usuario ha excedido el límite de acciones
    """
    key = f'ratelimit:{user_id}:{action}'
    current = redis_client.incr(key)
    
    if current == 1:
        redis_client.expire(key, window_seconds)
    
    if current > limit:
        raise RateLimitExceeded(
            f"User {user_id} exceeded {action} limit: {limit}/{window_seconds}s"
        )
    
    return current

# Uso
check_rate_limit(user_id, 'trivia_answer', limit=20, window_seconds=3600)
check_rate_limit(user_id, 'purchase', limit=10, window_seconds=60)
```

### 12. Métricas de Éxito y KPIs

### 12.2 Métricas Técnicas

**Performance:**
- Response Time: Tiempo de respuesta promedio (objetivo: < 500ms)
- 95th Percentile Response Time: Tiempo de respuesta del 95% de requests (objetivo: < 1s)
- Error Rate: % de requests que fallan (objetivo: < 0.1%)
- Uptime: % de tiempo que el sistema está disponible (objetivo: > 99.9%)

**Escalabilidad:**
- Requests per Second: Capacidad de procesar requests
- Database Query Time: Tiempo promedio de queries (objetivo: < 100ms)
- Cache Hit Rate: % de requests servidos desde caché (objetivo: > 80%)
- Background Job Processing Time: Tiempo para procesar jobs en cola

**Recursos:**
- CPU Usage: Uso de CPU de servidores (objetivo: < 70% promedio)
- Memory Usage: Uso de RAM (objetivo: < 80%)
- Database Connections: Conexiones activas a DB (monitorear pool)
- Redis Memory: Memoria usada por Redis (objetivo: < 90%)

### 12.3 Dashboard de KPIs

Implementar dashboard que muestre métricas críticas en tiempo real:

```python
# Ejemplo de endpoint para métricas
@app.get('/api/metrics/summary')
async def get_metrics_summary():
    now = datetime.now()
    
    return {
        'engagement': {
            'dau': count_active_users(hours=24),
            'wau': count_active_users(days=7),
            'mau': count_active_users(days=30),
            'avg_session_length_minutes': get_avg_session_length()
        },
        'monetization': {
            'active_vip_subs': count_active_subscriptions(),
            'conversion_rate': calculate_conversion_rate(),
            'mrr': calculate_monthly_recurring_revenue(),
            'arpu': calculate_arpu()
        },
        'narrative': {
            'fragments_completed_today': count_completions(hours=24),
            'avg_level_completion': get_avg_level_completion(),
            'most_popular_decision': get_most_popular_decisions(limit=1)[0]
        },
        'gamification': {
            'besitos_in_circulation': get_total_besitos(),
            'transactions_today': count_transactions(hours=24),
            'missions_completed_today': count_mission_completions(hours=24),
            'achievements_unlocked_today': count_achievement_unlocks(hours=24)
        },
        'technical': {
            'avg_response_time_ms': get_avg_response_time(),
            'error_rate_percent': get_error_rate(),
            'uptime_percent': get_uptime(),
            'cache_hit_rate_percent': get_cache_hit_rate()
        }
    }
}
```