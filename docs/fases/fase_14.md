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

# Fase 14: Reacciones Gamificadas

### Objetivo
Vincular reacciones en canales con recompensas

### Componentes a Implementar

#### 14.1 Configuración de Reacciones
- **Crear**: Sistema de rewards por reacción
- **Referencia**: Sección 5.3 - Sistema de Reacciones Vinculadas
- **Archivos**:
  - `database/models.py` (añadir campo reaction_rewards a ChannelPost)
  - `modules/admin/reactions.py`
- **Estructura**: Mapeo de emoji → recompensa + límite

#### 14.2 Handler de Reacciones
- **Crear**: Detector de reacciones en posts
- **Referencia**: Sección 5.3 - Configuración de Reacciones Gamificadas
- **Archivos**:
  - `bot/handlers/reactions.py`
- **Funcionalidad**:
  - Recibir `MessageReactionUpdated`
  - Identificar post y reacción
  - Verificar configuración de rewards
  - Verificar límites por usuario
  - Otorgar recompensas

#### 14.3 Tracking de Reacciones
- **Crear**: Registro de reacciones por usuario/post
- **Archivos**:
  - `database/models.py` (modelo UserReaction)
  - `database/migrations/011_create_reactions_tracking.sql`
- **Funcionalidad**:
  - Prevenir duplicados
  - Respetar límites configurados
  - Auditar reacciones para analíticas

#### 14.4 Integración con Misiones
- **Crear**: Misiones que requieren reacciones
- **Referencia**: Apéndice G - Ejemplo de Configuración de Misión
- **Modificar**: `modules/gamification/missions.py`
- **Funcionalidad**:
  - Tipo de tarea: "react_to_posts"
  - Tracking automático vía eventos
  - Contar solo reacciones válidas

#### 14.5 Eventos de Reacciones
- **Crear**: Publicar eventos de reacción
- **Referencia**: Sección 7.1 - Eventos Administrativos
- **Eventos**:
  - `admin.reaction_added`
  - Incluye: user_id, post_id, emoji, rewards_granted

### Resultado de Fase 14
✓ Reacciones otorgan recompensas
✓ Límites respetados
✓ Integrado con misiones
✓ Engagement en canales incentivado

## Referencias
### 5.3 Sistema de Reacciones Vinculadas

Las reacciones no son solo feedback, son parte del gameplay.

**Configuración de Reacciones Gamificadas**

Al publicar un post, el administrador puede configurar:

```json
{
  "post_id": 456,
  "reaction_rewards": {
    "❤️": {
      "besitos": 2,
      "limit_per_user": 1,
      "achievement_trigger": {
        "achievement_key": "romantic_soul",
        "condition": "react_heart_50_times"
      }
    },
    "🔥": {
      "besitos": 3,
      "limit_per_user": 1,
      "unlock_hint": "You seem passionate. Check your DMs."
    },
    "🤔": {
      "besitos": 1,
      "trigger_trivia": "trivia_about_this_post"
    }
  }
}
```

Cuando un usuario reacciona:
1. El bot recibe `MessageReactionUpdated`
2. Verifica configuración de reacciones para ese post
3. Verifica que el usuario no haya excedido límites
4. Otorga recompensas definidas
5. Dispara triggers especiales (enviar DM, activar trivia, etc.)

**Análisis de Engagement**

El sistema recopila métricas de reacciones:

Posts con más reacciones de cada tipo.
Usuarios más activos reaccionando.
Correlación entre tipo de contenido y reacciones recibidas.
Efectividad de reacciones gamificadas vs no gamificadas.

Estas métricas informan decisiones sobre qué tipo de contenido publicar.

### 7.1 Event Bus - Sistema Nervioso Central

Eventos Administrativos:
- `admin.subscription_started`: Nueva suscripción VIP
- `admin.subscription_expiring`: Suscripción cerca de expirar
- `admin.subscription_expired`: Suscripción expiró
- `admin.user_joined_channel`: Usuario se unió a canal
- `admin.user_left_channel`: Usuario salió de canal
- `admin.content_published`: Nuevo contenido publicado