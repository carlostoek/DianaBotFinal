# FASE 2: REACCIONES Y ANALYTICS BÁSICO (Semanas 5-6)

## Especificación de la Fase

### SPRINT 3: Sistema de Reacciones (Semana 5-6)

#### Objetivos
- Implementar sistema completo de reacciones
- Integrar con besitos para recompensas
- Habilitar tracking de engagement

#### Análisis de Brecha
- **Referencia:** Sección 2.2 - BRECHA CRÍTICA 1 (Ausencia de Sistema de Reacciones)

#### Componentes a Crear
1. **Módulo de Reacciones**
   - **Ubicación:** `modules/gamification/reactions.py`
   - **Especificación:** Sección 2.2 - BRECHA CRÍTICA 1
   - **Clase principal:** `ReactionProcessor`

2. **Modelos de Base de Datos**
   - **Referencia:** Sección 4.2 (Módulo de Reacciones)
   - **Modelos:** `ContentReaction`, `ReactionRewardConfig`

3. **Integración con CoordinadorCentral**
   - **Operación:** `REACCIONAR_CONTENIDO`
   - **Referencia:** Sección 3.1 (código completo de la operación)

#### Integraciones Requeridas
- Con `modules/narrative` para reacciones en fragmentos
- Con `modules/admin` para reacciones en posts de canales
- Con `besitos.py` para otorgar recompensas
- Con Event Bus para emitir eventos

#### Configuración Inicial
- **Recompensas por reacción:**
  - ❤️ (love): 10 besitos
  - 🔥 (fire): 15 besitos
  - ⭐ (star): 20 besitos
  - 👍 (like): 5 besitos

#### Entregables
- [ ] `modules/gamification/reactions.py` implementado
- [ ] Modelos de BD creados y migrados
- [ ] Handlers de Telegram configurados
- [ ] Integración con CoordinadorCentral completa
- [ ] Tests de integración

#### Dependencias
- Requiere CoordinadorCentral (Sprint 1)
- Requiere extensiones de User model (Sprint 2)

---

### SPRINT 3.5: Analytics Básico (Semana 6)

#### Objetivos
- Habilitar tracking automático de eventos
- Crear queries básicas de métricas
- Dashboard simple

#### Análisis de Brecha
- **Referencia:** Sección 2.6 - BRECHA CRÍTICA 1 (Analytics Unificado)

#### Componentes a Crear
1. **Event Collector**
   - **Ubicación:** `modules/analytics/collector.py`
   - **Referencia:** Sección 2.6 (especificación de componentes)

2. **Event Subscriber**
   - **Ubicación:** `modules/analytics/event_subscriber.py`
   - **Referencia:** Sección 2.6 - BRECHA 2 (integración con Event Bus)

3. **Modelos de Base de Datos**
   - **Referencia:** Sección 4.2 (Módulo de Analytics)
   - **Modelos:** `AnalyticsEvent`, `DailyMetrics`, `UserSessionMetrics`

#### Optimización de Performance
- **Referencia:** Sección 6.1.1 - Punto 3 (Tracking de Analytics)
- **Estrategia:** Batch inserts, buffer en memoria
- **Implementación:** EventCollectorBuffer (ver código en Sección 6.1.1)

#### Eventos a Trackear (Prioritarios)
- **Lista completa:** Sección 3.2
- **Prioritarios Sprint 3.5:**
  - Todos los eventos de narrativa
  - Todos los eventos de gamificación
  - `analytics.vip_content_accessed`

#### Entregables
- [ ] `modules/analytics/collector.py` implementado
- [ ] Suscripción automática a Event Bus
- [ ] Modelos de BD con particionamiento (ver Sección 6.1.3)
- [ ] Queries básicas de métricas funcionando
- [ ] Buffer de eventos implementado

#### Dependencias
- Requiere Event Bus extendido (Sprint 1)
- Requiere eventos nuevos implementados

## Referencias del Documento de Investigación

### Sección 2.2 - Sistema 2: Gamificación Avanzada

#### Brechas Identificadas

**BRECHA CRÍTICA 1: Ausencia de Sistema de Reacciones Integrado**
```
Actual: No existe módulo de reacciones
Requerido: modules/gamification/reactions.py
```

**Especificación del Componente:**
```python
# modules/gamification/reactions.py (NUEVO)

class ReactionProcessor:
    def process_reaction(user_id, content_type, content_id, reaction_type):
        # Validar contenido existe (narrativa, canal, etc.)
        # Calcular besitos según configuración
        # Otorgar besitos via besitos.py
        # Emitir evento al CoordinadorCentral
        # Actualizar estadísticas de engagement
        pass
    
    def get_reaction_rewards_config():
        # Configuración de qué reacciones otorgan cuántos besitos
        pass
```

**Integraciones Requeridas:**
- Con `modules/narrative` para reacciones en fragmentos
- Con `modules/admin` para reacciones en posts de canales
- Con `besitos.py` para otorgar recompensas
- Con sistema de estadísticas para métricas

### Sección 2.6 - Sistema 6: Estadísticas y Analytics

#### Brechas Identificadas

**BRECHA CRÍTICA 1: Ausencia de Sistema de Analytics Unificado**
```
Actual: Estadísticas dispersas en módulos individuales
Requerido: modules/analytics/ centralizado
```

**Estructura del Módulo a Crear:**
```
modules/analytics/
├── __init__.py
├── collector.py           # Recolector de eventos
├── aggregator.py          # Agregador de métricas
├── dashboard.py           # Data para dashboard
├── reports.py             # Generador de reportes
├── insights.py            # Sistema de insights automáticos
└── export.py              # Exportación de datos
```

**Especificación de Componentes:**

**A. collector.py**
```python
class EventCollector:
    def track_event(user_id, event_type, event_data):
        # Registrar evento en base de datos
        # Tipos: narrative_progress, purchase, reaction, mission_completed, etc.
        # Almacenar con timestamp y metadata
        pass
    
    def track_user_action(user_id, action, context):
        # Tracking granular de acciones de usuario
        pass
```

**B. aggregator.py**
```python
class MetricsAggregator:
    def get_engagement_metrics(time_range):
        # MAU, DAU, retention
        # Engagement por módulo
        # Tiempo promedio de sesión
        pass
    
    def get_monetization_metrics(time_range):
        # Revenue total
        # Conversión free -> VIP
        # Valor de vida del usuario (LTV)
        # ARPU, ARPPU
        pass
    
    def get_narrative_metrics(time_range):
        # Fragmentos más visitados
        # Tasa de completitud de narrativas
        # Decisiones más populares
        pass
    
    def get_experience_metrics(time_range):
        # Experiencias iniciadas vs completadas
        # Tasa de abandono por experiencia
        # Tiempo promedio de completitud
        pass
```

**C. dashboard.py**
```python
class DashboardDataProvider:
    def get_overview_stats():
        # Stats principales para dashboard admin
        # Usuarios activos, revenue, engagement
        pass
    
    def get_funnel_data():
        # Funnel de conversión
        # Free -> Engaged -> Purchaser -> VIP
        pass
    
    def get_cohort_analysis(cohort_definition):
        # Análisis de cohortes
        # Retención por cohorte
        pass
```

**D. insights.py**
```python
class InsightEngine:
    def detect_drop_off_points():
        # Identificar dónde usuarios abandonan
        # En narrativa, experiencias, misiones
        pass
    
    def identify_high_value_users():
        # Usuarios con mayor potencial de conversión
        # Basado en engagement y comportamiento
        pass
    
    def suggest_content_optimizations():
        # Sugerencias de contenido a crear/modificar
        # Basado en gaps en engagement
        pass
```

**Modelo de Base de Datos:**
```sql
-- AnalyticsEvent (tabla de eventos)
CREATE TABLE analytics_events (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    event_type VARCHAR(100),
    event_category VARCHAR(50),  -- narrative, gamification, commerce, admin
    event_data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255)
);

-- CREATE INDEX para queries rápidas
CREATE INDEX idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_events_timestamp ON analytics_events(timestamp);
CREATE INDEX idx_analytics_events_category ON analytics_events(event_category);

-- DailyMetrics (agregación diaria)
CREATE TABLE daily_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE NOT NULL,
    metric_type VARCHAR(100),
    metric_value DECIMAL(15,2),
    metadata JSONB,
    UNIQUE(metric_date, metric_type)
);

-- UserSessionMetrics
CREATE TABLE user_session_metrics (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_start TIMESTAMP,
    session_end TIMESTAMP,
    actions_count INTEGER,
    modules_accessed JSONB,  -- Array de módulos visitados
    session_duration INTEGER  -- segundos
);
```

**BRECHA 2: Integración con Event Bus para Tracking Automático**
```
Actual: Tracking manual en módulos individuales
Requerido: Tracking automático vía Event Bus
```

**Modificaciones Necesarias:**
- Suscribir `EventCollector` a todos los eventos del Event Bus
- Mapeo automático de eventos a métricas
- Sistema de filtrado de eventos relevantes para analytics

**Componente a Crear:** `modules/analytics/event_subscriber.py`
```python
class AnalyticsEventSubscriber:
    def __init__(self, event_bus):
        # Suscribirse a todos los eventos relevantes
        event_bus.subscribe('gamification.besitos_earned', self.track_besitos)
        event_bus.subscribe('narrative.fragment_visited', self.track_narrative)
        event_bus.subscribe('commerce.purchase_completed', self.track_purchase)
        event_bus.subscribe('experience.started', self.track_experience)
        # ... más suscripciones
    
    def track_besitos(self, event_data):
        # Convertir evento a registro analytics
        pass
    
    def track_narrative(self, event_data):
        pass
    
    # ... más handlers
```

### Sección 3.1 - CoordinadorCentral - Operación REACCIONAR_CONTENIDO

```python
def REACCIONAR_CONTENIDO(self, user_id, content_type, content_id, reaction):
    """
    Procesa reacción de usuario con efectos multi-sistema
    
    Flujo:
    1. Validar que contenido existe
    2. Registrar reacción
    3. Otorgar besitos según configuración
    4. Actualizar estadísticas de engagement
    5. Verificar si desbloquea logros
    6. Actualizar progreso de misiones relacionadas
    """
    with self.transaction_manager.begin() as tx:
        # Validar contenido
        content = tx.execute(
            f'{content_type}.get_content',
            content_id=content_id
        )
        
        if not content:
            return {'success': False, 'reason': 'content_not_found'}
        
        # Registrar reacción
        tx.execute(
            'gamification.register_reaction',
            user_id=user_id,
            content_type=content_type,
            content_id=content_id,
            reaction=reaction
        )
        
        # Otorgar besitos
        besitos_config = self._get_reaction_rewards_config()
        besitos_amount = besitos_config.get(reaction, 0)
        
        if besitos_amount > 0:
            tx.execute(
                'gamification.grant_besitos',
                user_id=user_id,
                amount=besitos_amount,
                reason=f"Reacción {reaction} en {content_type}"
            )
        
        # Verificar logros
        achievements_unlocked = tx.execute(
            'gamification.check_reaction_achievements',
            user_id=user_id
        )
        
        # Actualizar misiones
        missions_progressed = tx.execute(
            'gamification.update_reaction_missions',
            user_id=user_id,
            reaction=reaction
        )
        
        # Emitir eventos
        tx.on_commit(lambda: self.event_bus.emit(
            'coordinator.content_reacted',
            {
                'user_id': user_id,
                'content_type': content_type,
                'content_id': content_id,
                'reaction': reaction,
                'besitos_earned': besitos_amount,
                'achievements': achievements_unlocked,
                'missions': missions_progressed
            }
        ))
        
        return {
            'success': True,
            'besitos_earned': besitos_amount,
            'achievements_unlocked': achievements_unlocked,
            'missions_progressed': missions_progressed
        }
```

### Sección 3.2 - Nuevos Tipos de Eventos Requeridos

**Eventos de Gamificación:**
- `gamification.mission_started`
- `gamification.mission_completed`
- `gamification.achievement_unlocked`
- `gamification.item_acquired`
- `gamification.reaction_registered`

**Eventos del Coordinador:**
- `coordinator.content_reacted`
- `coordinator.purchase_completed`
- `coordinator.access_denied`
- `coordinator.requirements_failed`

**Eventos de Analytics:**
- `analytics.vip_content_accessed`
- `analytics.conversion_opportunity`
- `analytics.user_churn_risk`

### Sección 4.2 - Nuevos Modelos Requeridos

#### Módulo de Reacciones
```python
# database/models/reactions.py (COMPLETAMENTE NUEVO)

class ContentReaction(Base):
    __tablename__ = 'content_reactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content_type = Column(String(50), nullable=False)  # narrative_fragment, channel_post, mission
    content_id = Column(Integer, nullable=False)
    reaction_type = Column(String(50), nullable=False)  # like, love, fire, star, custom
    
    # Recompensa
    besitos_earned = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    user = relationship("User")
    fragment = relationship("NarrativeFragment", foreign_keys=[content_id], 
                          primaryjoin="and_(ContentReaction.content_type=='narrative_fragment', "
                                     "ContentReaction.content_id==NarrativeFragment.id)",
                          back_populates="reactions", uselist=False, viewonly=True)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'content_type', 'content_id', 'reaction_type', 
                        name='unique_user_content_reaction'),
        Index('idx_content_reactions', 'content_type', 'content_id'),
    )


class ReactionRewardConfig(Base):
    __tablename__ = 'reaction_reward_configs'
    
    id = Column(Integer, primary_key=True)
    content_type = Column(String(50), nullable=False)
    reaction_type = Column(String(50), nullable=False)
    besitos_reward = Column(Integer, default=0)
    
    # Límites
    max_per_user_per_content = Column(Integer, default=1)
    max_per_user_per_day = Column(Integer, nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        UniqueConstraint('content_type', 'reaction_type', name='unique_content_reaction_config'),
    )
```

#### Módulo de Analytics
```python
# database/models/analytics.py (COMPLETAMENTE NUEVO)

class AnalyticsEvent(Base):
    __tablename__ = 'analytics_events'
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Nullable para eventos del sistema
    event_type = Column(String(100), nullable=False)
    event_category = Column(String(50), nullable=False)  # narrative, gamification, commerce, admin, experience
    event_data = Column(JSONB, nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    
    # Metadata
    user_agent = Column(String(500), nullable=True)
    platform = Column(String(50), nullable=True)  # ios, android, web
    
    # Relaciones
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_analytics_events_user_id', 'user_id'),
        Index('idx_analytics_events_type', 'event_type'),
        Index('idx_analytics_events_category', 'event_category'),
        Index('idx_analytics_events_timestamp', 'timestamp'),
    )


class DailyMetrics(Base):
    __tablename__ = 'daily_metrics'
    
    id = Column(Integer, primary_key=True)
    metric_date = Column(Date, nullable=False, index=True)
    metric_type = Column(String(100), nullable=False)
    metric_value = Column(Numeric(15, 2), nullable=False)
    
    # Metadata adicional
    metadata = Column(JSONB, nullable=True)
    # Ejemplo:
    # {
    #     "segment": "vip_users",
    #     "category": "revenue",
    #     "subcategory": "subscriptions"
    # }
    
    __table_args__ = (
        UniqueConstraint('metric_date', 'metric_type', 'metadata', name='unique_daily_metric'),
        Index('idx_daily_metrics_date', 'metric_date'),
        Index('idx_daily_metrics_type', 'metric_type'),
    )


class UserSessionMetrics(Base):
    __tablename__ = 'user_session_metrics'
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(String(255), nullable=False, unique=True)
    
    session_start = Column(DateTime, nullable=False)
    session_end = Column(DateTime, nullable=True)
    session_duration = Column(Integer, nullable=True)  # segundos
    
    # Actividad
    actions_count = Column(Integer, default=0)
    modules_accessed = Column(JSONB)  # Array de módulos visitados
    # Ejemplo: ["narrative", "gamification", "commerce"]
    
    content_consumed = Column(JSONB)
    # Ejemplo:
    # {
    #     "fragments_viewed": [1, 2, 3],
    #     "missions_started": [5],
    #     "shop_items_viewed": [10, 11]
    # }
    
    # Engagement
    engagement_score = Column(Numeric(5, 2), default=0.00)
    
    # Relaciones
    user = relationship("User", back_populates="session_metrics")
    
    __table_args__ = (
        Index('idx_user_sessions_user_id', 'user_id'),
        Index('idx_user_sessions_start', 'session_start'),
    )
```

### Sección 6.1.1 - Punto 3 (Tracking de Analytics)

**Problema:** Cada evento genera writes a base de datos
**Impacto:** Miles de inserts por minuto bajo carga

**Soluciones:**
- Batch inserts cada 5-10 segundos
- Buffer en memoria con flush periódico
- Tabla particionada por fecha
- Índices optimizados para queries de lectura

**Implementación:**
```python
class EventCollectorBuffer:
    def __init__(self):
        self.buffer = []
        self.buffer_size = 1000
        self.flush_interval = 10  # segundos
    
    def track_event(self, event):
        self.buffer.append(event)
        if len(self.buffer) >= self.buffer_size:
            self.flush()
    
    def flush(self):
        if self.buffer:
            # Bulk insert
            db.bulk_insert_mappings(AnalyticsEvent, self.buffer)
            db.commit()
            self.buffer = []
```

### Sección 6.1.3 - Optimización de Queries

**Índices para Analytics:**
```sql
-- Analytics queries
CREATE INDEX idx_analytics_user_time ON analytics_events(user_id, timestamp DESC);
CREATE INDEX idx_analytics_type_time ON analytics_events(event_type, timestamp DESC);

-- Partitioning para analytics_events
CREATE TABLE analytics_events_2025_10 PARTITION OF analytics_events
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
```