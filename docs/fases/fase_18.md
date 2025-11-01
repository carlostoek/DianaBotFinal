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

# Fase 18: Dashboard Web Básico

### Objetivo
Panel administrativo web

### Componentes a Implementar

#### 18.1 Setup de Frontend
- **Crear**: Estructura HTML/CSS/JS
- **Referencia**: Sección 10.2 - Frontend (Dashboard Admin)
- **Archivos**:
  - `dashboard/templates/base.html`
  - `dashboard/static/css/style.css`
  - `dashboard/static/js/app.js`
- **Tech Stack**: HTML5, Alpine.js, Tailwind CSS

#### 18.2 Vista de Login
- **Crear**: Página de autenticación
- **Archivos**:
  - `dashboard/templates/login.html`
  - `dashboard/views.py`
- **Funcionalidad**:
  - Form de login
  - Llamar API de auth
  - Guardar JWT en localStorage
  - Redirect a dashboard

#### 18.3 Dashboard Principal
- **Crear**: Vista de métricas principales
- **Referencia**: Sección 6.5 - Panel de Administración Unificado
- **Archivos**:
  - `dashboard/templates/dashboard.html`
- **Contenido**:
  - KPIs en tiempo real
  - Usuarios activos
  - Suscripciones VIP
  - Besitos en circulación
  - Alertas del sistema

#### 18.4 Vista de Usuarios
- **Crear**: Gestión de usuarios
- **Archivos**:
  - `dashboard/templates/users.html`
- **Funcionalidad**:
  - Lista de usuarios con filtros
  - Búsqueda
  - Ver detalles de usuario
  - Editar suscripción
  - Otorgar besitos manualmente

#### 18.5 Vista de Configuración Simple
- **Crear**: Interface básica de config
- **Referencia**: Sección 6.2 - Flujos de Configuración Unificada
- **Archivos**:
  - `dashboard/templates/config.html`
- **Funcionalidad**:
  - Lista de configuraciones
  - Crear nueva (forms básicos)
  - Editar existente
  - Ver historial de versiones

#### 18.6 Vista de Contenido
- **Crear**: Gestión de narrativa y gamificación
- **Archivos**:
  - `dashboard/templates/content.html`
- **Funcionalidad**:
  - CRUD de fragmentos narrativos
  - CRUD de items
  - CRUD de misiones
  - CRUD de achievements

#### 18.7 Vista de Publicaciones
- **Crear**: Gestión de posts en canales
- **Archivos**:
  - `dashboard/templates/posts.html`
- **Funcionalidad**:
  - Calendario de publicaciones
  - Crear nuevo post
  - Editar posts programados
  - Ver posts publicados

#### 18.8 Vista de Analíticas
- **Crear**: Dashboards de métricas
- **Referencia**: Sección 12.3 - Dashboard de KPIs
- **Archivos**:
  - `dashboard/templates/analytics.html`
  - `dashboard/static/js/charts.js`
- **Contenido**:
  - Gráficas de engagement
  - Gráficas de monetización
  - Gráficas de progreso narrativo
  - Usar Chart.js

### Resultado de Fase
✓ Dashboard web funcional
✓ Autenticación JWT implementada
✓ Vista de métricas principales
✓ Gestión de usuarios
✓ Interface de configuración básica
✓ Vista de contenido y publicaciones

## Referencias
### 6.5 Panel de Administración Unificado

**Dashboard Principal**

El dashboard muestra vista holística del sistema:

```
┌─────────────────────────────────────────────────────┐
│  DianaBot - Dashboard Administrativo                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📊 Métricas en Tiempo Real                        │
│  ├─ Usuarios activos (últimas 24h): 1,247         │
│  ├─ Suscriptores VIP: 156 (↑ 12 esta semana)      │
│  ├─ Besitos en circulación: 3,456,789             │
│  └─ Fragmentos completados hoy: 3,421              │
│                                                     │
│  ⚠️ Alertas del Sistema                            │
│  ├─ 3 suscripciones expiran en 24h                │
│  ├─ Misión "Búsqueda Semanal" completada por 78%  │
│  └─ Item "Espada Legendaria" sin stock en tienda  │
│                                                     │
│  🎯 Acciones Rápidas                               │
│  ├─ [+ Crear Experiencia]                         │
│  ├─ [📅 Programar Evento]                         │
│  ├─ [🎁 Lanzar Recompensa Masiva]                 │
│  └─ [📊 Ver Analíticas Detalladas]                │
│                                                     │
│  📝 Configuraciones Recientes                      │
│  ├─ "El Misterio del Jardín" - hace 2 horas       │
│  │   Status: Activo | Usuarios: 89               │
│  ├─ "Misión Halloween" - hace 5 horas             │
│  │   Status: Programado para 31/10 00:00         │
│  └─ "Subasta Corona Dorada" - hace 1 día          │
│      Status: Completado | Ganador: @usuario123   │
└─────────────────────────────────────────────────────┘
```

**Navegación Contextual**

El panel usa navegación inteligente que comprende relaciones:

Al ver un fragmento narrativo, el panel muestra enlaces directos a:
- Items que desbloquea
- Misiones que activa
- Posts de canal asociados
- Usuarios que lo han completado
- Analíticas específicas de ese fragmento

Al ver una misión, muestra:
- Fragmentos narrativos relacionados
- Items como recompensa
- Usuarios con la misión activa/completada
- Tasa de completación histórica

Esto elimina la necesidad de navegar por múltiples secciones para entender cómo un elemento se relaciona con el resto del sistema.

**Editor Visual de Flujos**

Para experiencias complejas, el panel incluye editor visual de flujos:

```
[Fragmento 1: Entrada] 
    ├─[Decisión A]─→ [Fragmento 2A: Confianza]
    │                    ├─[Obtiene: Medallón]
    │                    └─[Activa: Misión "Buscar Verdad"]
    │
    └─[Decisión B]─→ [Fragmento 2B: Cautela]
                         ├─[Obtiene: 50 besitos]
                         └─[Desbloquea: Fragmento Secreto]
```

El administrador puede:
- Arrastrar y conectar fragmentos visualmente
- Ver condiciones de desbloqueo en cada conexión
- Identificar caminos huérfanos o sin salida
- Simular recorridos de usuario

### 6.2 Flujos de Configuración Unificada

**Flujo: Crear Experiencia Narrativa-Gamificada Completa**

El administrador accede al panel unificado y selecciona "Crear Nueva Experiencia". El asistente guía paso a paso:

Paso 1 - Información Básica:
- Nombre de la experiencia: "El Secreto del Ático"
- Descripción: "Descubre lo que Lucien oculta en el ático prohibido"
- Tipo: Narrativa con Gamificación
- Requisitos: VIP, 50 besitos, poseer "Llave Maestra"

Paso 2 - Contenido Narrativo:
- Editor visual para crear 3-5 fragmentos interconectados
- Para cada fragmento:
  - Texto narrativo con preview
  - Decisiones con consecuencias
  - Media asociada (subir imágenes/audio)
  - Variables narrativas afectadas

Paso 3 - Recompensas Integradas:
Panel unificado que muestra todas las recompensas en un solo lugar:

```
Recompensas al Completar Experiencia:
├── Besitos: [100] ✓
├── Items Desbloqueados:
│   ├── [Seleccionar existente ▼] o [Crear nuevo +]
│   └── "Diario del Ático" (nuevo)
│       ├── Descripción: ...
│       ├── Categoría: Narrativo
│       └── Efecto: Desbloquea fragmento secreto F_SECRET_05
├── Achievements:
│   └── [✓] "Explorador del Ático" (existente)
│       └── Rewards: 50 besitos adicionales
└── Misiones Activadas:
    └── [Crear nueva +]
        └── "Investiga los hallazgos"
            ├── Descripción: ...
            └── Recompensa: Item "Fotografía Antigua"
```

El administrador define TODO en esta pantalla sin navegar a otras secciones.

Paso 4 - Programación de Publicación:
- ¿Publicar en qué canal? [VIP ▼]
- ¿Cuándo? [Inmediato / Programado: 2025-11-01 20:00]
- ¿Notificar usuarios? [✓ Sí]
- Plantilla de notificación: "¡Nueva experiencia disponible! El Secreto del Ático te espera..."

Paso 5 - Validación y Vista Previa:
El sistema valida automáticamente:
- ✓ Todos los fragmentos tienen al menos una decisión
- ✓ Items referenciados existen o serán creados
- ✓ Recompensas de besitos están en rango razonable (0-500)
- ⚠ Advertencia: Esta experiencia no tiene misiones recurrentes
- ✓ Coherencia narrativa verificada

Vista previa muestra cómo los usuarios experimentarán el contenido.

Paso 6 - Confirmación y Propagación:
Al confirmar, el sistema ejecuta en una transacción:

```python
def create_narrative_experience(config_data):
    with transaction.atomic():
        # 1. Crear nivel narrativo si no existe
        level = create_or_get_level(config_data['level_number'])
        
        # 2. Crear fragmentos en PostgreSQL
        fragments = []
        for frag_data in config_data['fragments']:
            fragment = NarrativeFragment.objects.create(
                level=level,
                fragment_key=generate_key(frag_data['title']),
                title=frag_data['title'],
                unlock_conditions=config_data['requirements'],
                rewards=config_data['rewards']
            )
            fragments.append(fragment)
            
            # 3. Crear contenido detallado en MongoDB
            mongo_db.narrative_content.insert_one({
                'fragment_key': fragment.fragment_key,
                'content': frag_data['content'],
                'decisions': frag_data['decisions']
            })
        
        # 4. Crear items nuevos
        created_items = []
        for item_data in config_data['new_items']:
            item = Item.objects.create(**item_data)
            created_items.append(item)
        
        # 5. Vincular achievements existentes
        for achievement_key in config_data['achievements']:
            achievement = Achievement.objects.get(achievement_key=achievement_key)
            # Vincular al primer fragmento de la experiencia
            fragments[0].rewards['achievements'].append(achievement.achievement_id)
            fragments[0].save()
        
        # 6. Crear misiones activadas
        for mission_data in config_data['activated_missions']:
            mission = Mission.objects.create(
                **mission_data,
                requirements={'completed_fragments': [f.fragment_id for f in fragments]}
            )
        
        # 7. Programar publicación en canal
        if config_data['publish_immediately']:
            publish_to_channel(config_data['channel'], fragments[0])
        else:
            schedule_post(
                channel=config_data['channel'],
                content=fragments[0],
                scheduled_for=config_data['publish_at']
            )
        
        # 8. Guardar config instance para historial
        ConfigInstance.objects.create(
            template=config_data['template'],
            instance_data=config_data,
            created_by=config_data['admin_id'],
            status='active'
        )
        
        # 9. Publicar evento para otros sistemas
        event_bus.publish('narrative_experience_created', {
            'experience_name': config_data['name'],
            'fragments': [f.fragment_key for f in fragments],
            'items': [i.item_key for i in created_items]
        })
        
        return {
            'success': True,
            'fragments_created': len(fragments),
            'items_created': len(created_items),
            'experience_id': fragments[0].fragment_id
        }
```

Todo esto sucede en una sola operación atómica. Si cualquier paso falla, nada se guarda (rollback automático).

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