# Fase 2: Event Bus y Logging

### Objetivo
Implementar sistema de eventos para comunicación entre módulos

### Componentes a Implementar

#### 2.1 Event Bus Core
- **Crear**: Sistema pub/sub con Redis
- **Referencia**: Sección 7.1 - Event Bus - Sistema Nervioso Central
- **Archivos**:
  - `core/event_bus.py`
- **Funcionalidad**:
  - Clase EventBus con métodos `publish()` y `subscribe()`
  - Conexión a Redis Pub/Sub
  - Sistema de serialización de eventos (JSON)

#### 2.2 Event Logger
- **Crear**: Sistema que guarda eventos en DB para auditoría
- **Referencia**: Sección 7.1 - Event Bus
- **Archivos**:
  - `database/models.py` (añadir modelo EventLog)
  - `database/migrations/002_create_event_logs.sql`
- **Campos**: event_id, event_type, event_data, timestamp

#### 2.3 Eventos Básicos de Usuario
- **Modificar**: Handlers existentes para publicar eventos
- **Referencia**: Sección 7.1 - Eventos Principales del Sistema
- **Archivos**:
  - `bot/handlers/start.py` (publicar evento `user.registered`)
  - `core/user_state.py` (publicar evento `user.command_executed`)
- **Eventos**:
  - `user.registered`
  - `user.command_executed`
  - `user.activity`

#### 2.4 Subscriber de Prueba
- **Crear**: Handler que escucha eventos y los registra
- **Referencia**: Sección 7.1 - Event Bus
- **Archivos**:
  - `core/event_handlers.py`
- **Funcionalidad**:
  - Suscribirse a eventos `user.*`
  - Loggear eventos recibidos
  - Actualizar `last_active` en DB

### Resultado de Fase 2
✓ Event Bus funcional con Redis
✓ Eventos se publican y registran en DB
✓ Sistema de comunicación entre módulos establecido

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

## Referencias
### 7.1 Event Bus - Sistema Nervioso Central

El Event Bus es el mecanismo que permite comunicación desacoplada entre módulos.

**Arquitectura del Event Bus**

Usamos Redis Pub/Sub como infraestructura del Event Bus por su velocidad y confiabilidad. La estructura es:

```python
class EventBus:
    def __init__(self):
        self.redis_client = redis.Redis()
        self.handlers = defaultdict(list)
    
    def publish(self, event_type, event_data):
        """Publica un evento para que otros módulos lo consuman"""
        event = {
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.now().isoformat(),
            'event_id': generate_event_id()
        }
        
        # Publicar en Redis
        self.redis_client.publish(
            f'dianabot:events:{event_type}', 
            json.dumps(event)
        )
        
        # También guardar en DB para auditoría
        EventLog.objects.create(
            event_type=event_type,
            event_data=event_data
        )
    
    def subscribe(self, event_type, handler_func):
        """Registra un handler para un tipo de evento"""
        self.handlers[event_type].append(handler_func)
        
        # Suscribirse al canal de Redis
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(f'dianabot:events:{event_type}')
        
        # Escuchar eventos en thread separado
        thread = pubsub.run_in_thread(sleep_time=0.01)
        return thread
```

**Eventos Principales del Sistema**

Eventos Narrativos:
- `narrative.fragment_started`: Usuario comenzó un fragmento
- `narrative.decision_made`: Usuario tomó una decisión
- `narrative.fragment_completed`: Usuario completó un fragmento
- `narrative.level_completed`: Usuario completó un nivel completo
- `narrative.secret_discovered`: Usuario descubrió contenido secreto

Eventos de Gamificación:
- `gamification.besitos_earned`: Usuario ganó besitos
- `gamification.besitos_spent`: Usuario gastó besitos
- `gamification.item_purchased`: Usuario compró item
- `gamification.item_used`: Usuario usó item consumible
- `gamification.achievement_unlocked`: Usuario desbloqueó achievement
- `gamification.mission_assigned`: Misión asignada a usuario
- `gamification.mission_completed`: Usuario completó misión
- `gamification.auction_won`: Usuario ganó subasta
- `gamification.trivia_answered`: Usuario respondió trivia

Eventos Administrativos:
- `admin.subscription_started`: Nueva suscripción VIP
- `admin.subscription_expiring`: Suscripción cerca de expirar
- `admin.subscription_expired`: Suscripción expiró
- `admin.user_joined_channel`: Usuario se unió a canal
- `admin.user_left_channel`: Usuario salió de canal
- `admin.content_published`: Nuevo contenido publicado