# Investigación de Brechas Arquitectónicas: DianaBot
## Estado Actual vs. Arquitectura Conceptual Deseada

---

## 1. RESUMEN EJECUTIVO

### Síntesis de Brechas Principales

**Brecha Crítica Identificada:** El proyecto actual implementa módulos funcionales independientes (~70% completado), pero carece del **sistema de integración profunda** que los convierta en un ecosistema cohesivo. El concepto arquitectónico requiere una transformación de "módulos aislados" a "sistema nervioso interconectado".

### Esfuerzo Estimado por Categoría

| Categoría | Complejidad | Esfuerzo |
|-----------|-------------|----------|
| Sistema de Coordinación Central | ALTA | 40% del proyecto |
| Sistema de Requisitos Compuestos | ALTA | 25% del proyecto |
| Sistema de Experiencias Unificadas | MEDIA-ALTA | 20% del proyecto |
| Refactorización de Integraciones | MEDIA | 10% del proyecto |
| Analytics Unificado | MEDIA | 5% del proyecto |

### Hallazgos Clave

1. **Módulo Inexistente Crítico:** El "Sistema de Experiencias Unificadas" no existe actualmente
2. **Event Bus vs CoordinadorCentral:** Brecha fundamental en capacidades de orquestación
3. **Arquitectura de Requisitos:** Sistema actual no soporta validación compuesta multi-módulo
4. **Data Model:** Requiere extensión significativa para soportar relaciones cruzadas
5. **Monetización Integrada:** Flujos de conversión conceptuales no implementados

---

## 2. ANÁLISIS MODULAR DETALLADO

### 2.1. Sistema 1: Narrativa Inmersiva

#### Estado Actual
**Componentes Existentes:**
- ✅ `modules/narrative/engine.py` - Motor básico de narrativa
- ✅ `modules/narrative/flags.py` - Sistema de flags
- ✅ `modules/narrative/unlocks.py` - Desbloqueos básicos
- ✅ `modules/narrative/secrets.py` - Sistema de secretos
- ✅ `modules/narrative/rewards.py` - Recompensas narrativas
- ✅ Modelos: `NarrativeLevel`, `NarrativeFragment`, `UserNarrativeProgress`
- ✅ MongoDB: `narrative_content`, `user_narrative_states`

#### Brechas Identificadas

**BRECHA CRÍTICA 1: Sistema de Requisitos Compuestos**
```
Actual: unlocks.py valida requisitos simples (flags, nivel)
Requerido: Validación multi-dimensional que integre:
  - Flags narrativos
  - Membresía VIP (admin/channels)
  - Items de inventario (gamification/inventory)
  - Logros completados (gamification/achievements)
  - Experiencias previas (módulo nuevo)
  - Nivel de besitos (gamification/besitos)
```

**Componente a Crear:** `modules/narrative/composite_requirements.py`
- Función: `validate_composite_requirements(user_id, fragment_id) -> ValidationResult`
- Debe consultar: narrative, gamification, admin, experiences
- Debe retornar: requisitos cumplidos/faltantes con detalles específicos

**BRECHA CRÍTICA 2: Integración con Sistema de Recompensas Cruzadas**
```
Actual: rewards.py otorga recompensas narrativas aisladas
Requerido: Trigger automático de recompensas en múltiples sistemas
```

**Modificaciones Necesarias:**
- `rewards.py` debe emitir eventos al CoordinadorCentral
- Nuevos tipos de recompensa: `UNLOCK_SHOP_ITEM`, `GRANT_VIP_PREVIEW`, `TRIGGER_EXPERIENCE`
- Sistema de recompensas diferidas basado en progreso futuro

**BRECHA 3: Fragmentos como Parte de Experiencias**
```
Actual: NarrativeFragment es entidad independiente
Requerido: Fragmentos pueden ser componentes de Experiences
```

**Cambios en Data Model:**
- Agregar campo `experience_id` (nullable) a `NarrativeFragment`
- Crear tabla intermedia `ExperienceFragment` para secuenciación
- Agregar metadatos de contexto cuando fragmento es parte de experiencia

#### Componentes Reutilizables
- ✅ Motor de navegación de fragmentos (engine.py)
- ✅ Sistema de flags (puede extenderse)
- ✅ Almacenamiento híbrido PostgreSQL/MongoDB
- ⚠️ Sistema de unlocks (requiere refactorización profunda)

---

### 2.2. Sistema 2: Gamificación Avanzada

#### Estado Actual
**Componentes Existentes:**
- ✅ `modules/gamification/besitos.py` - Economía de puntos
- ✅ `modules/gamification/missions.py` - Sistema de misiones
- ✅ `modules/gamification/inventory.py` - Inventario de items
- ✅ `modules/gamification/achievements.py` - Logros
- ✅ `modules/gamification/auctions.py` - Subastas
- ✅ Modelos: `UserBalance`, `Transaction`, `Mission`, `Item`, `Achievement`

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

**BRECHA CRÍTICA 2: Misiones como Parte de Experiencias**
```
Actual: Mission es entidad independiente
Requerido: Misiones pueden ser etapas de Experiences
```

**Modificaciones Necesarias:**
- Agregar campo `experience_id` a tabla `Mission`
- Crear relación `Experience.missions` (one-to-many)
- Sistema de misiones secuenciales dentro de experiencias
- Desbloqueo automático de siguiente misión al completar actual

**BRECHA 3: Sistema de Conversión de Besitos a Monetización**
```
Actual: besitos.py gestiona economía interna
Requerido: Flujo de conversión besitos -> compras -> desbloqueos
```

**Componente a Crear:** `modules/gamification/conversion_engine.py`
- Tracking de patrones de gasto de besitos
- Identificación de usuarios con alto potencial de conversión
- Triggers para ofertas personalizadas
- Integración con sistema de arquetipos (no existe aún)

#### Componentes Reutilizables
- ✅ Sistema de besitos completo (bien implementado)
- ✅ Sistema de misiones base
- ✅ Sistema de inventario (puede extenderse)
- ✅ Sistema de logros (puede extenderse para experiencias)

---

### 2.3. Sistema 3: Comercio Integrado

#### Estado Actual
**Componentes Existentes:**
- ❌ **NO EXISTE módulo de comercio/tienda**
- ⚠️ Modelos relacionados: `Item` (en gamification, pero sin comercio)
- ⚠️ Sistema de besitos puede usarse como moneda

#### Brechas Identificadas

**BRECHA CRÍTICA 1: Ausencia Total del Módulo de Comercio**
```
Requerido: modules/commerce/ (COMPLETAMENTE NUEVO)
```

**Estructura del Módulo a Crear:**
```
modules/commerce/
├── __init__.py
├── shop.py              # Catálogo de productos
├── cart.py              # Carrito de compras
├── checkout.py          # Proceso de compra
├── payments.py          # Integración con Telegram Payments
├── unlocks.py           # Desbloqueos post-compra
├── upselling.py         # Sistema de ofertas contextuales
└── subscriptions.py     # Gestión de suscripciones VIP
```

**Especificaciones Funcionales:**

**A. shop.py**
```python
class ShopManager:
    def get_catalog(user_id, filters):
        # Catálogo personalizado según arquetipos
        # Filtros: tipo de item, rango de precio, rareza
        # Items disponibles según nivel y progreso narrativo
        pass
    
    def get_item_details(item_id, user_id):
        # Detalles del item
        # Preview de qué desbloquea (narrativa, experiencias)
        # Verificar si usuario ya lo posee
        pass
```

**B. checkout.py**
```python
class CheckoutProcessor:
    def process_purchase(user_id, item_id, payment_method):
        # Validar fondos (besitos o dinero real)
        # Procesar pago
        # Otorgar item al inventario
        # Trigger desbloqueos automáticos
        # Emitir eventos al CoordinadorCentral
        pass
    
    def process_vip_subscription(user_id, subscription_type):
        # Procesar compra de membresía VIP
        # Integración con modules/admin para acceso a canales
        # Activar beneficios VIP
        pass
```

**C. unlocks.py**
```python
class PurchaseUnlockEngine:
    def apply_unlocks(user_id, item_id):
        # Desbloquear fragmentos narrativos
        # Activar experiencias exclusivas
        # Otorgar acceso a canales especiales
        # Desbloquear misiones premium
        pass
    
    def check_purchase_requirements(user_id, item_id):
        # Verificar si puede comprar (nivel, progreso, etc.)
        pass
```

**D. upselling.py**
```python
class UpsellEngine:
    def get_contextual_offers(user_id, context):
        # context: "post_narrative_decision", "mission_completed", etc.
        # Retornar ofertas personalizadas
        # Basado en arquetipos y comportamiento
        pass
    
    def trigger_conversion_flow(user_id, trigger_event):
        # Iniciar flujo de conversión inteligente
        # Mostrar valor de compra según contexto
        pass
```

**BRECHA CRÍTICA 2: Integración con Telegram Payments**
```
Requerido: Integración completa con Telegram Payments API
```

**Componente a Crear:** `modules/commerce/payments.py`
- Manejo de `PreCheckoutQuery`
- Procesamiento de `SuccessfulPayment`
- Sistema de refunds
- Gestión de múltiples proveedores de pago
- Validación de transacciones

**BRECHA CRÍTICA 3: Sistema de Arquetipos para Personalización**
```
Actual: No existe sistema de arquetipos de usuario
Requerido: modules/commerce/archetypes.py
```

**Especificación:**
```python
class ArchetypeEngine:
    ARCHETYPES = [
        "NARRATIVE_LOVER",      # Compra por historia
        "COLLECTOR",            # Compra por completitud
        "COMPETITIVE",          # Compra por ventaja
        "SOCIAL",              # Compra por estatus
        "COMPLETIONIST"        # Compra por 100%
    ]
    
    def detect_archetype(user_id):
        # Análisis de comportamiento histórico
        # Patrones de consumo de contenido
        # Interacciones y decisiones
        pass
    
    def personalize_offers(user_id, base_catalog):
        # Personalizar catálogo según arquetipo
        pass
```

#### Modelos de Base de Datos Requeridos

**Nuevas Tablas:**
```sql
-- ShopItem (diferente de Item de gamification)
CREATE TABLE shop_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50),  -- narrative_unlock, experience_unlock, vip_preview, etc.
    price_besitos INTEGER,
    price_real DECIMAL(10,2),  -- Precio en dinero real (opcional)
    rarity VARCHAR(50),
    unlocks_content_type VARCHAR(50),  -- narrative, experience, mission
    unlocks_content_id INTEGER,
    is_available BOOLEAN DEFAULT TRUE,
    stock INTEGER,  -- NULL = ilimitado
    discount_percentage INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- UserPurchase (historial de compras)
CREATE TABLE user_purchases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    shop_item_id INTEGER REFERENCES shop_items(id),
    purchase_type VARCHAR(50),  -- besitos, real_money
    amount_paid DECIMAL(10,2),
    besitos_spent INTEGER,
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unlocks_applied BOOLEAN DEFAULT FALSE
);

-- UserArchetype
CREATE TABLE user_archetypes (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    primary_archetype VARCHAR(50),
    secondary_archetype VARCHAR(50),
    confidence_score DECIMAL(3,2),  -- 0.00 - 1.00
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- VIPSubscription (extender existente si hay)
CREATE TABLE vip_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    subscription_type VARCHAR(50),  -- monthly, annual, lifetime
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    auto_renew BOOLEAN DEFAULT FALSE,
    payment_method VARCHAR(50)
);
```

---

### 2.4. Sistema 4: Administración de Canales

#### Estado Actual
**Componentes Existentes:**
- ✅ `modules/admin/` - Gestión de canales VIP y suscripciones
- ✅ Modelos: `Subscription`, `Channel`, `ChannelPost`
- ✅ Sistema de verificación de membresía con cache (Redis)

#### Brechas Identificadas

**BRECHA 1: Integración con Sistema de Reacciones**
```
Actual: ChannelPost existe, pero no integrado con reacciones
Requerido: Sistema de tracking de reacciones en posts
```

**Modificaciones Necesarias:**
- Extender modelo `ChannelPost` con campos de engagement:
  ```python
  reaction_count = Column(Integer, default=0)
  unique_reactors = Column(Integer, default=0)
  besitos_distributed = Column(Integer, default=0)
  ```
- Crear handler de reacciones en posts de canal
- Integración con `gamification/reactions.py` (a crear)

**BRECHA 2: Sistema de Contenido VIP Integrado con Narrativa**
```
Actual: ChannelPost es independiente de narrativa
Requerido: Posts pueden desbloquear fragmentos narrativos
```

**Componente a Crear:** `modules/admin/content_integration.py`
```python
class ContentIntegrationManager:
    def link_post_to_narrative(post_id, fragment_id):
        # Vincular post con fragmento narrativo
        # Desbloquear fragmento al interactuar con post
        pass
    
    def create_narrative_preview_post(fragment_id):
        # Crear post de preview de fragmento VIP
        # Incluir CTA para upgrade a VIP
        pass
```

**BRECHA 3: Sistema de Roles Dinámico**
```
Actual: Roles simples (admin, VIP, free)
Requerido: Sistema de roles con permisos granulares
```

**Modificaciones Necesarias:**
- Crear tabla `user_roles` con permisos detallados
- Permisos: acceso a narrativa VIP, experiencias premium, shop items exclusivos
- Sistema de roles temporales (VIP trial, acceso especial por evento)

**BRECHA 4: Automatización de Gestión de Suscripciones**
```
Actual: Verificación básica de suscripciones (tasks/scheduled.py)
Requerido: Sistema completo de lifecycle de suscripción
```

**Componente a Crear:** `modules/admin/subscription_lifecycle.py`
```python
class SubscriptionLifecycleManager:
    def handle_subscription_expiring(user_id, days_before=7):
        # Notificar usuario
        # Ofrecer renovación con descuento
        # Preparar downgrade a contenido free
        pass
    
    def handle_subscription_expired(user_id):
        # Remover de canal VIP
        # Bloquear acceso a contenido premium
        # Mantener progreso para posible re-suscripción
        pass
    
    def handle_subscription_renewed(user_id):
        # Re-activar acceso completo
        # Notificar contenido nuevo disponible
        # Otorgar bonus de bienvenida
        pass
```

#### Componentes Reutilizables
- ✅ Sistema de verificación de membresía (bien implementado)
- ✅ Modelos base de Channel y Subscription
- ⚠️ Sistema de roles (requiere extensión)
- ⚠️ Gestión de posts (requiere integración profunda)

---

### 2.5. Sistema 5: Experiencias Unificadas (MÓDULO COMPLETAMENTE NUEVO)

#### Estado Actual
**Componentes Existentes:**
- ❌ **NO EXISTE este módulo**

#### Especificación Completa del Módulo

**BRECHA CRÍTICA: Módulo Inexistente que es Central a la Arquitectura**

**Estructura del Módulo a Crear:**
```
modules/experiences/
├── __init__.py
├── engine.py              # Motor de experiencias
├── builder.py             # Constructor de experiencias
├── propagation.py         # Sistema de propagación automática
├── validator.py           # Validador de requisitos compuestos
├── coordinator.py         # Coordinador de dependencias
└── templates.py           # Templates de experiencias predefinidas
```

**Concepto de Experiencia:**
Una Experiencia es un flujo unificado que integra múltiples elementos de diferentes sistemas en una secuencia cohesiva con requisitos compuestos y recompensas combinadas.

**Modelo de Base de Datos:**
```sql
-- Experience (entidad principal)
CREATE TABLE experiences (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50),  -- narrative_journey, mission_chain, hybrid
    difficulty VARCHAR(50),  -- easy, medium, hard, expert
    estimated_duration INTEGER,  -- minutos
    is_vip_exclusive BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ExperienceComponent (componentes de la experiencia)
CREATE TABLE experience_components (
    id SERIAL PRIMARY KEY,
    experience_id INTEGER REFERENCES experiences(id),
    component_type VARCHAR(50),  -- narrative, mission, purchase, achievement
    component_id INTEGER,  -- ID del componente específico
    sequence_order INTEGER,
    is_required BOOLEAN DEFAULT TRUE,
    unlock_conditions JSONB,  -- Condiciones para desbloquear este componente
    completion_rewards JSONB  -- Recompensas al completar
);

-- UserExperienceProgress
CREATE TABLE user_experience_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    experience_id INTEGER REFERENCES experiences(id),
    status VARCHAR(50),  -- not_started, in_progress, completed, abandoned
    current_component_id INTEGER REFERENCES experience_components(id),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    completion_percentage DECIMAL(5,2),
    UNIQUE(user_id, experience_id)
);

-- ExperienceRequirement (requisitos para iniciar experiencia)
CREATE TABLE experience_requirements (
    id SERIAL PRIMARY KEY,
    experience_id INTEGER REFERENCES experiences(id),
    requirement_type VARCHAR(50),  -- level, vip_membership, item, achievement, experience_completed
    requirement_value JSONB
);

-- ExperienceReward (recompensas al completar experiencia)
CREATE TABLE experience_rewards (
    id SERIAL PRIMARY KEY,
    experience_id INTEGER REFERENCES experiences(id),
    reward_type VARCHAR(50),  -- besitos, item, narrative_unlock, achievement
    reward_value JSONB
);
```

**Especificación de Componentes:**

**A. engine.py**
```python
class ExperienceEngine:
    def start_experience(user_id, experience_id):
        # Validar requisitos compuestos
        # Inicializar progreso
        # Desbloquear primer componente
        # Emitir evento al CoordinadorCentral
        pass
    
    def progress_experience(user_id, experience_id, component_completed):
        # Marcar componente como completado
        # Validar siguiente componente
        # Otorgar recompensas intermedias
        # Verificar si experiencia completada
        pass
    
    def complete_experience(user_id, experience_id):
        # Otorgar recompensas finales
        # Actualizar estadísticas
        # Desbloquear contenido relacionado
        # Emitir eventos de completitud
        pass
    
    def get_experience_status(user_id, experience_id):
        # Estado actual de la experiencia
        # Componentes completados vs pendientes
        # Progreso en porcentaje
        pass
```

**B. builder.py**
```python
class ExperienceBuilder:
    def create_experience(experience_data):
        # Crear experiencia con componentes
        # Validar integridad de secuencia
        # Configurar requisitos y recompensas
        pass
    
    def add_component(experience_id, component_data):
        # Agregar componente a experiencia existente
        # Reordenar secuencia si necesario
        pass
    
    def from_template(template_name, customizations):
        # Crear experiencia desde template predefinido
        # Aplicar customizaciones
        pass
```

**C. propagation.py**
```python
class PropagationEngine:
    def auto_propagate_experience(experience_id, propagation_config):
        # Crear automáticamente componentes en otros sistemas
        # Ejemplo: crear misiones, fragmentos narrativos, items de tienda
        # Vincular todo a la experiencia central
        pass
    
    def generate_narrative_fragments(experience_id, narrative_arc):
        # Generar fragmentos narrativos para la experiencia
        # Integrarlos en el motor de narrativa
        pass
    
    def generate_missions(experience_id, mission_spec):
        # Crear misiones asociadas a la experiencia
        # Configurar recompensas integradas
        pass
```

**D. validator.py**
```python
class CompositeValidator:
    def validate_composite_requirements(user_id, requirements):
        # Validar requisitos de múltiples sistemas
        # Retornar estado detallado de cada requisito
        # Calcular progreso hacia cumplimiento
        pass
    
    def can_start_experience(user_id, experience_id):
        # Verificar todos los requisitos
        # Incluir: nivel, VIP, items, logros, experiencias previas
        pass
    
    def get_missing_requirements(user_id, experience_id):
        # Listar requisitos faltantes
        # Con detalles de cómo obtenerlos
        pass
```

**E. coordinator.py**
```python
class DependencyCoordinator:
    def resolve_dependencies(experience_id):
        # Mapear todas las dependencias entre componentes
        # Crear grafo de dependencias
        # Validar que no hay ciclos
        pass
    
    def get_next_available_components(user_id, experience_id):
        # Determinar qué componentes puede hacer ahora
        # Basado en completitud de dependencias
        pass
    
    def handle_component_completion(user_id, component_id):
        # Procesar completitud de componente
        # Desbloquear componentes dependientes
        # Actualizar progreso de experiencia
        pass
```

**F. templates.py**
```python
class ExperienceTemplates:
    TEMPLATE_NARRATIVE_JOURNEY = {
        "type": "narrative_journey",
        "components": [
            {"type": "narrative", "count": 5},
            {"type": "decision", "count": 3},
            {"type": "achievement", "count": 1}
        ]
    }
    
    TEMPLATE_MISSION_CHAIN = {
        "type": "mission_chain",
        "components": [
            {"type": "mission", "count": 3},
            {"type": "purchase", "count": 1},
            {"type": "narrative", "count": 2}
        ]
    }
    
    def get_template(template_name):
        pass
    
    def customize_template(template, customizations):
        pass
```

**Integraciones Requeridas:**

1. **Con Narrativa:**
   - Fragmentos pueden ser parte de experiencias
   - Progreso narrativo actualiza progreso de experiencia
   - Desbloqueos narrativos pueden ser recompensas de experiencia

2. **Con Gamificación:**
   - Misiones como componentes de experiencia
   - Logros otorgados al completar experiencias
   - Besitos como recompensas de experiencia

3. **Con Comercio:**
   - Items de shop pueden ser requisitos o recompensas
   - Experiencias exclusivas para compradores de ciertos items
   - Descuentos especiales al completar experiencias

4. **Con Administración:**
   - Experiencias VIP exclusivas
   - Contenido de experiencias publicado en canales
   - Acceso a canales especiales como recompensa

---

### 2.6. Sistema 6: Estadísticas y Analytics

#### Estado Actual
**Componentes Existentes:**
- ⚠️ Sistema básico existe probablemente en `api/` o módulos individuales
- ⚠️ No hay sistema centralizado de analytics

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

**BRECHA 3: Sistema de Alertas Proactivas**
```
Actual: No existe sistema de alertas
Requerido: Alertas automáticas para anomalías
```

**Componente a Crear:** `modules/analytics/alerts.py`
```python
class AlertSystem:
    def check_anomalies():
        # Detectar caídas en engagement
        # Detectar picos de abandono
        # Detectar problemas técnicos
        pass
    
    def notify_admin(alert_type, alert_data):
        # Enviar notificación a admins via Telegram
        pass
    
    def get_alert_config():
        # Configuración de umbrales de alerta
        pass
```

---

## 3. ARQUITECTURA DE INTEGRACIÓN

### 3.1. Event Bus vs CoordinadorCentral

#### Estado Actual del Event Bus
**Ubicación:** `core/event_bus.py`

**Capacidades Actuales:**
- ✅ Pub/Sub básico con Redis
- ✅ Suscripción/desuscripción a eventos
- ✅ Emisión asíncrona de eventos
- ✅ Registro de handlers en `core/event_handlers.py`

**Limitaciones Identificadas:**
- ❌ No hay orquestación de flujos complejos
- ❌ No hay sistema de transacciones distribuidas
- ❌ No hay validación de requisitos compuestos
- ❌ No hay coordinación de acciones multi-módulo
- ❌ No hay sistema de rollback en caso de fallo
- ❌ No hay priorización de eventos

#### Transformación a CoordinadorCentral

**BRECHA CRÍTICA: Event Bus requiere evolución significativa**

**Componente a Crear:** `core/coordinator.py`

```python
class CoordinadorCentral:
    """
    Sistema de coordinación que extiende Event Bus con capacidades de orquestación
    """
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.validators = {}  # Validadores por tipo de acción
        self.orchestrators = {}  # Orquestadores de flujos
        self.transaction_manager = TransactionManager()
    
    # === ACCIONES COORDINADAS ===
    
    def TOMAR_DECISION(self, user_id, fragment_id, decision_id):
        """
        Coordina toma de decisión narrativa con validación compuesta
        
        Flujo:
        1. Validar requisitos compuestos (narrativa + gamificación + admin + commerce)
        2. Si válido: aplicar decisión
        3. Otorgar recompensas en múltiples sistemas
        4. Actualizar progreso de experiencias relacionadas
        5. Emitir eventos a todos los sistemas afectados
        6. Si falla: rollback completo
        """
        with self.transaction_manager.begin() as tx:
            # Paso 1: Validar requisitos compuestos
            validation = self._validate_composite_requirements(
                user_id, 
                fragment_id,
                requirement_types=['narrative', 'vip', 'items', 'level']
            )
            
            if not validation.is_valid:
                return {
                    'success': False,
                    'missing_requirements': validation.missing,
                    'suggestions': self._get_requirement_suggestions(validation.missing)
                }
            
            # Paso 2: Aplicar decisión en narrativa
            narrative_result = tx.execute(
                'narrative.apply_decision',
                user_id=user_id,
                fragment_id=fragment_id,
                decision_id=decision_id
            )
            
            # Paso 3: Otorgar recompensas
            rewards = narrative_result.get('rewards', {})
            
            if rewards.get('besitos'):
                tx.execute(
                    'gamification.grant_besitos',
                    user_id=user_id,
                    amount=rewards['besitos'],
                    reason=f"Decisión narrativa {decision_id}"
                )
            
            if rewards.get('items'):
                for item_id in rewards['items']:
                    tx.execute(
                        'gamification.add_to_inventory',
                        user_id=user_id,
                        item_id=item_id
                    )
            
            if rewards.get('unlock_content'):
                tx.execute(
                    'narrative.unlock_fragments',
                    user_id=user_id,
                    fragment_ids=rewards['unlock_content']
                )
            
            # Paso 4: Actualizar experiencias relacionadas
            related_experiences = self._get_related_experiences(fragment_id)
            for exp_id in related_experiences:
                tx.execute(
                    'experience.progress_component',
                    user_id=user_id,
                    experience_id=exp_id,
                    component_type='narrative',
                    component_id=fragment_id
                )
            
            # Paso 5: Emitir eventos
            tx.on_commit(lambda: self.event_bus.emit(
                'coordinator.decision_taken',
                {
                    'user_id': user_id,
                    'fragment_id': fragment_id,
                    'decision_id': decision_id,
                    'rewards': rewards,
                    'experiences_affected': related_experiences
                }
            ))
            
            # Paso 6: Commit o rollback automático
            return {
                'success': True,
                'narrative_result': narrative_result,
                'rewards_granted': rewards,
                'experiences_updated': related_experiences
            }
    
    def ACCEDER_NARRATIVA_VIP(self, user_id, fragment_id):
        """
        Coordina acceso a contenido VIP con validación multi-nivel
        
        Flujo:
        1. Verificar membresía VIP activa
        2. Verificar acceso al canal VIP
        3. Validar requisitos adicionales del fragmento
        4. Si no tiene acceso: ofrecer upgrade
        5. Registrar intento de acceso para analytics
        6. Si tiene acceso: permitir y trackear
        """
        # Paso 1: Verificar membresía
        is_vip = self._check_vip_membership(user_id)
        
        if not is_vip:
            # Registrar intento fallido
            self._track_conversion_opportunity(
                user_id, 
                'vip_content_access_denied',
                {'fragment_id': fragment_id}
            )
            
            # Generar oferta personalizada
            offer = self._generate_personalized_vip_offer(user_id)
            
            return {
                'success': False,
                'reason': 'vip_required',
                'offer': offer,
                'preview': self._get_content_preview(fragment_id)
            }
        
        # Paso 2: Verificar acceso a canal
        has_channel_access = self._verify_channel_membership(
            user_id, 
            channel_type='VIP'
        )
        
        if not has_channel_access:
            # Caso raro: es VIP pero no está en canal
            self._fix_channel_membership(user_id)
        
        # Paso 3: Validar requisitos adicionales
        additional_reqs = self._validate_fragment_requirements(
            user_id,
            fragment_id
        )
        
        if not additional_reqs.is_valid:
            return {
                'success': False,
                'reason': 'additional_requirements',
                'missing': additional_reqs.missing
            }
        
        # Paso 4: Permitir acceso
        fragment_content = self._get_fragment_content(user_id, fragment_id)
        
        # Paso 5: Trackear acceso
        self.event_bus.emit('analytics.vip_content_accessed', {
            'user_id': user_id,
            'fragment_id': fragment_id,
            'timestamp': datetime.now()
        })
        
        return {
            'success': True,
            'content': fragment_content,
            'vip_status': 'active'
        }
    
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
    
    def COMPRAR_ITEM(self, user_id, item_id, payment_method):
        """
        Coordina compra con desbloqueos automáticos
        
        Flujo:
        1. Validar que usuario puede comprar
        2. Procesar pago (besitos o real)
        3. Agregar item al inventario
        4. Aplicar desbloqueos automáticos (narrativa, experiencias)
        5. Otorgar beneficios adicionales
        6. Verificar upselling contextual
        7. Actualizar arquetipos de usuario
        """
        with self.transaction_manager.begin() as tx:
            # Validar compra
            can_purchase = tx.execute(
                'commerce.validate_purchase',
                user_id=user_id,
                item_id=item_id,
                payment_method=payment_method
            )
            
            if not can_purchase.is_valid:
                return {
                    'success': False,
                    'reason': can_purchase.reason,
                    'missing': can_purchase.missing_requirements
                }
            
            # Procesar pago
            payment_result = tx.execute(
                'commerce.process_payment',
                user_id=user_id,
                item_id=item_id,
                payment_method=payment_method
            )
            
            if not payment_result.success:
                return {
                    'success': False,
                    'reason': 'payment_failed',
                    'details': payment_result.error
                }
            
            # Agregar a inventario
            tx.execute(
                'gamification.add_to_inventory',
                user_id=user_id,
                item_id=item_id,
                quantity=1
            )
            
            # Aplicar desbloqueos
            unlocks = tx.execute(
                'commerce.apply_purchase_unlocks',
                user_id=user_id,
                item_id=item_id
            )
            
            # Desbloqueos narrativos
            if unlocks.get('narrative_fragments'):
                tx.execute(
                    'narrative.unlock_fragments',
                    user_id=user_id,
                    fragment_ids=unlocks['narrative_fragments']
                )
            
            # Desbloqueos de experiencias
            if unlocks.get('experiences'):
                for exp_id in unlocks['experiences']:
                    tx.execute(
                        'experience.unlock',
                        user_id=user_id,
                        experience_id=exp_id
                    )
            
            # Verificar upselling
            upsell_offers = tx.execute(
                'commerce.get_post_purchase_offers',
                user_id=user_id,
                purchased_item_id=item_id
            )
            
            # Actualizar arquetipo
            tx.execute(
                'commerce.update_user_archetype',
                user_id=user_id,
                purchase_data={'item_id': item_id, 'method': payment_method}
            )
            
            # Emitir eventos
            tx.on_commit(lambda: self.event_bus.emit(
                'coordinator.purchase_completed',
                {
                    'user_id': user_id,
                    'item_id': item_id,
                    'payment_method': payment_method,
                    'unlocks': unlocks,
                    'upsell_offers': upsell_offers
                }
            ))
            
            return {
                'success': True,
                'payment_result': payment_result,
                'unlocks_applied': unlocks,
                'upsell_offers': upsell_offers
            }
    
    # === VALIDADORES COMPUESTOS ===
    
    def _validate_composite_requirements(self, user_id, target_id, requirement_types):
        """
        Valida requisitos de múltiples sistemas simultáneamente
        """
        validation_result = CompositeValidationResult()
        
        for req_type in requirement_types:
            validator = self.validators.get(req_type)
            if validator:
                result = validator.validate(user_id, target_id)
                validation_result.add_result(req_type, result)
        
        return validation_result
    
    def _get_related_experiences(self, fragment_id):
        """
        Obtiene experiencias relacionadas a un fragmento
        """
        # Consultar tabla experience_components
        pass
    
    # === OTROS MÉTODOS DE SOPORTE ===
    # ... (métodos auxiliares)
```

**Componente Adicional:** `core/transaction_manager.py`
```python
class TransactionManager:
    """
    Gestor de transacciones distribuidas para coordinación multi-módulo
    """
    
    def begin(self):
        return DistributedTransaction(self)
    
    class DistributedTransaction:
        def __init__(self, manager):
            self.manager = manager
            self.operations = []
            self.rollback_stack = []
            self.commit_callbacks = []
        
        def execute(self, operation_name, **kwargs):
            # Ejecutar operación y guardar rollback
            result = self._execute_operation(operation_name, **kwargs)
            rollback = self._create_rollback(operation_name, result, **kwargs)
            self.rollback_stack.append(rollback)
            return result
        
        def on_commit(self, callback):
            self.commit_callbacks.append(callback)
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                # Hubo error: hacer rollback
                self._rollback()
                return False
            else:
                # Todo bien: ejecutar callbacks
                self._commit()
                return True
        
        def _rollback(self):
            for rollback_func in reversed(self.rollback_stack):
                try:
                    rollback_func()
                except Exception as e:
                    logger.error(f"Error en rollback: {e}")
        
        def _commit(self):
            for callback in self.commit_callbacks:
                try:
                    callback()
                except Exception as e:
                    logger.error(f"Error en commit callback: {e}")
```

### 3.2. Nuevos Tipos de Eventos Requeridos

**Eventos Actuales (probables):**
- `gamification.besitos_earned`
- `gamification.besitos_spent`

**Eventos Adicionales Necesarios:**

```python
# === EVENTOS DE NARRATIVA ===
'narrative.fragment_visited'
'narrative.decision_taken'
'narrative.content_unlocked'
'narrative.level_completed'

# === EVENTOS DE GAMIFICACIÓN ===
'gamification.mission_started'
'gamification.mission_completed'
'gamification.achievement_unlocked'
'gamification.item_acquired'
'gamification.reaction_registered'

# === EVENTOS DE COMERCIO ===
'commerce.item_viewed'
'commerce.cart_updated'
'commerce.purchase_initiated'
'commerce.purchase_completed'
'commerce.purchase_failed'
'commerce.vip_subscribed'
'commerce.vip_renewed'
'commerce.vip_cancelled'

# === EVENTOS DE EXPERIENCIAS ===
'experience.unlocked'
'experience.started'
'experience.component_completed'
'experience.completed'
'experience.abandoned'

# === EVENTOS DE ADMINISTRACIÓN ===
'admin.user_joined_channel'
'admin.user_left_channel'
'admin.vip_status_changed'
'admin.content_published'

# === EVENTOS DEL COORDINADOR ===
'coordinator.decision_taken'
'coordinator.content_reacted'
'coordinator.purchase_completed'
'coordinator.access_denied'
'coordinator.requirements_failed'

# === EVENTOS DE ANALYTICS ===
'analytics.vip_content_accessed'
'analytics.conversion_opportunity'
'analytics.user_churn_risk'
```

### 3.3. APIs de Integración entre Módulos

**APIs Internas Requeridas (no REST, sino interfaces Python):**

```python
# === API de Narrativa ===
class NarrativeAPI:
    def get_fragment(fragment_id, user_id=None) -> Fragment:
        """Obtiene fragmento con contenido personalizado para usuario"""
        pass
    
    def check_fragment_requirements(user_id, fragment_id) -> RequirementCheck:
        """Verifica si usuario cumple requisitos para fragmento"""
        pass
    
    def apply_decision(user_id, fragment_id, decision_id) -> DecisionResult:
        """Aplica decisión de usuario"""
        pass
    
    def unlock_fragments(user_id, fragment_ids: List[int]) -> UnlockResult:
        """Desbloquea múltiples fragmentos"""
        pass
    
    def get_user_progress(user_id) -> NarrativeProgress:
        """Obtiene progreso narrativo completo"""
        pass

# === API de Gamificación ===
class GamificationAPI:
    def grant_besitos(user_id, amount, reason) -> TransactionResult:
        """Otorga besitos a usuario"""
        pass
    
    def spend_besitos(user_id, amount, reason) -> TransactionResult:
        """Gasta besitos de usuario"""
        pass
    
    def add_to_inventory(user_id, item_id, quantity=1) -> InventoryResult:
        """Agrega item al inventario"""
        pass
    
    def check_achievements(user_id, trigger_type) -> List[Achievement]:
        """Verifica logros desbloqueados por acción"""
        pass
    
    def progress_mission(user_id, mission_id, progress_data) -> MissionProgress:
        """Actualiza progreso de misión"""
        pass
    
    def register_reaction(user_id, content_type, content_id, reaction) -> ReactionResult:
        """Registra reacción de usuario"""
        pass

# === API de Comercio ===
class CommerceAPI:
    def get_item(item_id) -> ShopItem:
        """Obtiene item de tienda"""
        pass
    
    def validate_purchase(user_id, item_id, payment_method) -> ValidationResult:
        """Valida si usuario puede comprar"""
        pass
    
    def process_payment(user_id, item_id, payment_method) -> PaymentResult:
        """Procesa pago"""
        pass
    
    def apply_purchase_unlocks(user_id, item_id) -> UnlockResult:
        """Aplica desbloqueos de compra"""
        pass
    
    def get_personalized_offers(user_id, context) -> List[Offer]:
        """Obtiene ofertas personalizadas"""
        pass

# === API de Administración ===
class AdminAPI:
    def check_vip_membership(user_id) -> VIPStatus:
        """Verifica si usuario es VIP"""
        pass
    
    def verify_channel_membership(user_id, channel_type) -> bool:
        """Verifica membresía en canal"""
        pass
    
    def grant_vip_access(user_id, subscription_type, duration) -> VIPGrant:
        """Otorga acceso VIP"""
        pass
    
    def revoke_vip_access(user_id) -> VIPRevoke:
        """Revoca acceso VIP"""
        pass

# === API de Experiencias ===
class ExperienceAPI:
    def get_experience(experience_id) -> Experience:
        """Obtiene experiencia completa"""
        pass
    
    def check_requirements(user_id, experience_id) -> RequirementCheck:
        """Verifica requisitos para iniciar experiencia"""
        pass
    
    def start_experience(user_id, experience_id) -> ExperienceStart:
        """Inicia experiencia para usuario"""
        pass
    
    def progress_component(user_id, experience_id, component_data) -> ProgressResult:
        """Actualiza progreso de componente"""
        pass
    
    def get_user_progress(user_id, experience_id) -> ExperienceProgress:
        """Obtiene progreso de usuario en experiencia"""
        pass

# === API de Analytics ===
class AnalyticsAPI:
    def track_event(user_id, event_type, event_data) -> None:
        """Registra evento"""
        pass
    
    def get_user_metrics(user_id) -> UserMetrics:
        """Obtiene métricas de usuario"""
        pass
    
    def get_conversion_probability(user_id) -> float:
        """Calcula probabilidad de conversión"""
        pass
    
    def identify_user_archetype(user_id) -> Archetype:
        """Identifica arquetipo de usuario"""
        pass
```

**Registro de APIs en CoordinadorCentral:**
```python
class CoordinadorCentral:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        
        # Registrar APIs
        self.apis = {
            'narrative': NarrativeAPI(),
            'gamification': GamificationAPI(),
            'commerce': CommerceAPI(),
            'admin': AdminAPI(),
            'experience': ExperienceAPI(),
            'analytics': AnalyticsAPI()
        }
    
    def get_api(self, api_name):
        return self.apis.get(api_name)
```

---

## 4. EVOLUCIÓN DE DATA MODEL

### 4.1. Extensiones a Modelos Existentes

#### User Model (Extensiones)
```python
# database/models/user.py (MODIFICACIONES)

class User(Base):
    __tablename__ = 'users'
    
    # Campos existentes...
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    # ... otros campos existentes
    
    # === NUEVOS CAMPOS ===
    archetype_primary = Column(String(50), nullable=True)
    archetype_secondary = Column(String(50), nullable=True)
    archetype_confidence = Column(Numeric(3, 2), nullable=True)
    archetype_updated_at = Column(DateTime, nullable=True)
    
    conversion_score = Column(Numeric(5, 2), nullable=True)  # 0.00 - 100.00
    churn_risk_score = Column(Numeric(5, 2), nullable=True)  # 0.00 - 100.00
    lifetime_value = Column(Numeric(10, 2), default=0.00)
    
    vip_trial_used = Column(Boolean, default=False)
    vip_trial_end_date = Column(DateTime, nullable=True)
    
    last_engagement_date = Column(DateTime, nullable=True)
    engagement_streak = Column(Integer, default=0)
    
    # === NUEVAS RELACIONES ===
    experience_progress = relationship("UserExperienceProgress", back_populates="user")
    purchases = relationship("UserPurchase", back_populates="user")
    archetype_data = relationship("UserArchetype", back_populates="user", uselist=False)
    session_metrics = relationship("UserSessionMetrics", back_populates="user")
```

#### NarrativeFragment Model (Extensiones)
```python
# database/models/narrative.py (MODIFICACIONES)

class NarrativeFragment(Base):
    __tablename__ = 'narrative_fragments'
    
    # Campos existentes...
    id = Column(Integer, primary_key=True)
    # ... otros campos existentes
    
    # === NUEVOS CAMPOS ===
    experience_id = Column(Integer, ForeignKey('experiences.id'), nullable=True)
    is_experience_component = Column(Boolean, default=False)
    component_sequence = Column(Integer, nullable=True)
    
    # Requisitos compuestos (JSONB)
    composite_requirements = Column(JSONB, nullable=True)
    # Ejemplo de estructura:
    # {
    #     "vip_required": true,
    #     "min_level": 5,
    #     "required_items": [1, 3, 7],
    #     "required_achievements": [2],
    #     "required_experiences": [1, 2]
    # }
    
    # Recompensas extendidas (JSONB)
    extended_rewards = Column(JSONB, nullable=True)
    # Ejemplo:
    # {
    #     "besitos": 50,
    #     "items": [4, 5],
    #     "unlock_fragments": [10, 11],
    #     "unlock_experiences": [3],
    #     "achievements": [5]
    # }
    
    # Métricas de engagement
    view_count = Column(Integer, default=0)
    completion_rate = Column(Numeric(5, 2), default=0.00)
    average_time_spent = Column(Integer, default=0)  # segundos
    
    # === NUEVAS RELACIONES ===
    experience = relationship("Experience", back_populates="narrative_components")
    reactions = relationship("ContentReaction", back_populates="fragment")
```

#### Mission Model (Extensiones)
```python
# database/models/gamification.py (MODIFICACIONES)

class Mission(Base):
    __tablename__ = 'missions'
    
    # Campos existentes...
    id = Column(Integer, primary_key=True)
    # ... otros campos existentes
    
    # === NUEVOS CAMPOS ===
    experience_id = Column(Integer, ForeignKey('experiences.id'), nullable=True)
    is_experience_component = Column(Boolean, default=False)
    component_sequence = Column(Integer, nullable=True)
    
    # Requisitos compuestos
    composite_requirements = Column(JSONB, nullable=True)
    
    # Recompensas extendidas
    extended_rewards = Column(JSONB, nullable=True)
    
    # === NUEVAS RELACIONES ===
    experience = relationship("Experience", back_populates="mission_components")
```

#### Item Model (Extensiones)
```python
# database/models/gamification.py (MODIFICACIONES)

class Item(Base):
    __tablename__ = 'items'
    
    # Campos existentes...
    id = Column(Integer, primary_key=True)
    # ... otros campos existentes
    
    # === NUEVOS CAMPOS ===
    is_purchasable = Column(Boolean, default=False)
    shop_item_id = Column(Integer, ForeignKey('shop_items.id'), nullable=True)
    
    # Desbloqueos que otorga
    unlocks_content = Column(JSONB, nullable=True)
    # Ejemplo:
    # {
    #     "narrative_fragments": [5, 6, 7],
    #     "experiences": [2],
    #     "missions": [10]
    # }
    
    # === NUEVAS RELACIONES ===
    shop_item = relationship("ShopItem", back_populates="game_item")
```

### 4.2. Nuevos Modelos Requeridos

#### Módulo de Experiencias
```python
# database/models/experience.py (COMPLETAMENTE NUEVO)

class Experience(Base):
    __tablename__ = 'experiences'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # narrative_journey, mission_chain, hybrid
    difficulty = Column(String(50))  # easy, medium, hard, expert
    estimated_duration = Column(Integer)  # minutos
    is_vip_exclusive = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    tags = Column(ARRAY(String), nullable=True)
    preview_image_url = Column(String(500), nullable=True)
    
    # Métricas
    start_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    average_completion_time = Column(Integer, default=0)  # minutos
    
    # Relaciones
    components = relationship("ExperienceComponent", back_populates="experience", cascade="all, delete-orphan")
    requirements = relationship("ExperienceRequirement", back_populates="experience", cascade="all, delete-orphan")
    rewards = relationship("ExperienceReward", back_populates="experience", cascade="all, delete-orphan")
    user_progress = relationship("UserExperienceProgress", back_populates="experience")
    
    # Relaciones inversas con componentes
    narrative_components = relationship("NarrativeFragment", back_populates="experience")
    mission_components = relationship("Mission", back_populates="experience")


class ExperienceComponent(Base):
    __tablename__ = 'experience_components'
    
    id = Column(Integer, primary_key=True)
    experience_id = Column(Integer, ForeignKey('experiences.id'), nullable=False)
    component_type = Column(String(50), nullable=False)  # narrative, mission, purchase, achievement, reaction
    component_id = Column(Integer, nullable=False)
    sequence_order = Column(Integer, nullable=False)
    is_required = Column(Boolean, default=True)
    
    # Condiciones para desbloquear
    unlock_conditions = Column(JSONB, nullable=True)
    # Ejemplo:
    # {
    #     "requires_previous": true,
    #     "requires_all_before": false,
    #     "custom_conditions": {
    #         "min_besitos": 100,
    #         "has_items": [1, 2]
    #     }
    # }
    
    # Recompensas al completar
    completion_rewards = Column(JSONB, nullable=True)
    # Ejemplo:
    # {
    #     "besitos": 25,
    #     "items": [3],
    #     "unlock_next": true
    # }
    
    # Metadata
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # minutos
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    experience = relationship("Experience", back_populates="components")
    user_completions = relationship("UserComponentCompletion", back_populates="component")


class UserExperienceProgress(Base):
    __tablename__ = 'user_experience_progress'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    experience_id = Column(Integer, ForeignKey('experiences.id'), nullable=False)
    status = Column(String(50), default='not_started')  # not_started, in_progress, completed, abandoned
    current_component_id = Column(Integer, ForeignKey('experience_components.id'), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, nullable=True)
    completion_percentage = Column(Numeric(5, 2), default=0.00)
    
    # Tracking
    total_time_spent = Column(Integer, default=0)  # minutos
    components_completed = Column(Integer, default=0)
    components_total = Column(Integer, default=0)
    
    # Relaciones
    user = relationship("User", back_populates="experience_progress")
    experience = relationship("Experience", back_populates="user_progress")
    current_component = relationship("ExperienceComponent", foreign_keys=[current_component_id])
    component_completions = relationship("UserComponentCompletion", back_populates="user_progress")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'experience_id', name='unique_user_experience'),
    )


class UserComponentCompletion(Base):
    __tablename__ = 'user_component_completions'
    
    id = Column(Integer, primary_key=True)
    user_progress_id = Column(Integer, ForeignKey('user_experience_progress.id'), nullable=False)
    component_id = Column(Integer, ForeignKey('experience_components.id'), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    time_spent = Column(Integer, default=0)  # minutos
    
    # Metadata de completitud
    completion_data = Column(JSONB, nullable=True)
    # Ejemplo:
    # {
    #     "score": 85,
    #     "attempts": 2,
    #     "bonus_earned": true
    # }
    
    # Relaciones
    user_progress = relationship("UserExperienceProgress", back_populates="component_completions")
    component = relationship("ExperienceComponent", back_populates="user_completions")
    
    __table_args__ = (
        UniqueConstraint('user_progress_id', 'component_id', name='unique_user_component'),
    )


class ExperienceRequirement(Base):
    __tablename__ = 'experience_requirements'
    
    id = Column(Integer, primary_key=True)
    experience_id = Column(Integer, ForeignKey('experiences.id'), nullable=False)
    requirement_type = Column(String(50), nullable=False)  # level, vip_membership, item, achievement, experience_completed
    requirement_value = Column(JSONB, nullable=False)
    # Ejemplo según tipo:
    # level: {"min_level": 5}
    # vip_membership: {"required": true}
    # item: {"item_ids": [1, 2, 3], "all_required": true}
    # achievement: {"achievement_ids": [5]}
    # experience_completed: {"experience_ids": [1, 2]}
    
    is_mandatory = Column(Boolean, default=True)
    
    # Relaciones
    experience = relationship("Experience", back_populates="requirements")


class ExperienceReward(Base):
    __tablename__ = 'experience_rewards'
    
    id = Column(Integer, primary_key=True)
    experience_id = Column(Integer, ForeignKey('experiences.id'), nullable=False)
    reward_type = Column(String(50), nullable=False)  # besitos, item, narrative_unlock, achievement, vip_trial
    reward_value = Column(JSONB, nullable=False)
    # Ejemplo según tipo:
    # besitos: {"amount": 500}
    # item: {"item_ids": [10, 11]}
    # narrative_unlock: {"fragment_ids": [20, 21]}
    # achievement: {"achievement_id": 15}
    # vip_trial: {"duration_days": 7}
    
    is_bonus = Column(Boolean, default=False)  # Recompensa bonus vs regular
    
    # Relaciones
    experience = relationship("Experience", back_populates="rewards")
```

#### Módulo de Comercio
```python
# database/models/commerce.py (COMPLETAMENTE NUEVO)

class ShopItem(Base):
    __tablename__ = 'shop_items'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # narrative_unlock, experience_unlock, vip_preview, power_up, cosmetic
    category = Column(String(50))  # content, subscription, boost, collectible
    
    # Pricing
    price_besitos = Column(Integer, nullable=True)
    price_real = Column(Numeric(10, 2), nullable=True)  # Precio en moneda real
    currency = Column(String(3), default='USD')
    
    # Disponibilidad
    is_available = Column(Boolean, default=True)
    stock = Column(Integer, nullable=True)  # NULL = stock ilimitado
    is_limited_time = Column(Boolean, default=False)
    available_from = Column(DateTime, nullable=True)
    available_until = Column(DateTime, nullable=True)
    
    # Descuentos
    discount_percentage = Column(Integer, default=0)
    discount_expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    rarity = Column(String(50))  # common, rare, epic, legendary
    image_url = Column(String(500), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    
    # Desbloqueos
    unlocks_content_type = Column(String(50), nullable=True)  # narrative, experience, mission, channel
    unlocks_content_id = Column(Integer, nullable=True)
    unlocks_data = Column(JSONB, nullable=True)
    # Ejemplo:
    # {
    #     "narrative_fragments": [10, 11, 12],
    #     "experiences": [3],
    #     "vip_days": 30
    # }
    
    # Requisitos para comprar
    purchase_requirements = Column(JSONB, nullable=True)
    # Ejemplo:
    # {
    #     "min_level": 10,
    #     "vip_required": false,
    #     "required_items": [1, 2]
    # }
    
    # Métricas
    view_count = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    conversion_rate = Column(Numeric(5, 2), default=0.00)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    purchases = relationship("UserPurchase", back_populates="shop_item")
    game_item = relationship("Item", back_populates="shop_item", uselist=False)


class UserPurchase(Base):
    __tablename__ = 'user_purchases'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shop_item_id = Column(Integer, ForeignKey('shop_items.id'), nullable=False)
    
    # Detalles de compra
    purchase_type = Column(String(50))  # besitos, real_money, reward, gift
    amount_paid = Column(Numeric(10, 2))
    currency = Column(String(3), default='USD')
    besitos_spent = Column(Integer, nullable=True)
    
    # Estado
    status = Column(String(50), default='pending')  # pending, completed, failed, refunded
    
    # Telegram Payment info
    telegram_payment_charge_id = Column(String(255), nullable=True)
    provider_payment_charge_id = Column(String(255), nullable=True)
    
    # Metadata
    unlocks_applied = Column(Boolean, default=False)
    unlocks_applied_at = Column(DateTime, nullable=True)
    
    purchase_date = Column(DateTime, default=datetime.utcnow)
    
    # Tracking
    purchase_context = Column(JSONB, nullable=True)
    # Ejemplo:
    # {
    #     "source": "narrative_unlock_prompt",
    #     "fragment_id": 15,
    #     "offer_type": "contextual"
    # }
    
    # Relaciones
    user = relationship("User", back_populates="purchases")
    shop_item = relationship("ShopItem", back_populates="purchases")


class UserArchetype(Base):
    __tablename__ = 'user_archetypes'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    primary_archetype = Column(String(50), nullable=False)
    secondary_archetype = Column(String(50), nullable=True)
    confidence_score = Column(Numeric(3, 2), default=0.00)  # 0.00 - 1.00
    
    # Scores por arquetipo
    archetype_scores = Column(JSONB)
    # Ejemplo:
    # {
    #     "NARRATIVE_LOVER": 0.85,
    #     "COLLECTOR": 0.62,
    #     "COMPETITIVE": 0.45,
    #     "SOCIAL": 0.38,
    #     "COMPLETIONIST": 0.71
    # }
    
    # Comportamiento detectado
    behavior_patterns = Column(JSONB)
    # Ejemplo:
    # {
    #     "content_preference": "narrative",
    #     "spending_tendency": "high",
    #     "engagement_frequency": "daily",
    #     "social_activity": "moderate"
    # }
    
    last_updated = Column(DateTime, default=datetime.utcnow)
    last_analyzed = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="archetype_data")


class VIPSubscription(Base):
    __tablename__ = 'vip_subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subscription_type = Column(String(50), nullable=False)  # monthly, annual, lifetime, trial
    
    # Fechas
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # NULL para lifetime
    
    # Estado
    is_active = Column(Boolean, default=True)
    auto_renew = Column(Boolean, default=False)
    
    # Pago
    payment_method = Column(String(50))
    amount_paid = Column(Numeric(10, 2))
    currency = Column(String(3), default='USD')
    
    # Telegram Payment info
    telegram_payment_charge_id = Column(String(255), nullable=True)
    
    # Tracking
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", backref="vip_subscriptions")


class PersonalizedOffer(Base):
    __tablename__ = 'personalized_offers'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shop_item_id = Column(Integer, ForeignKey('shop_items.id'), nullable=False)
    
    # Personalización
    offer_type = Column(String(50))  # contextual, archetype_based, upsell, retention
    discount_percentage = Column(Integer, default=0)
    custom_message = Column(Text, nullable=True)
    
    # Contexto
    trigger_event = Column(String(100), nullable=True)
    trigger_context = Column(JSONB, nullable=True)
    
    # Validez
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Estado
    is_active = Column(Boolean, default=True)
    viewed = Column(Boolean, default=False)
    viewed_at = Column(DateTime, nullable=True)
    accepted = Column(Boolean, default=False)
    accepted_at = Column(DateTime, nullable=True)
    
    # Relaciones
    user = relationship("User")
    shop_item = relationship("ShopItem")
```

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


class ConversionFunnel(Base):
    __tablename__ = 'conversion_funnels'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    funnel_type = Column(String(50), nullable=False)  # free_to_vip, engagement_to_purchase
    
    # Etapas
    stage_entered = Column(String(50), nullable=False)
    stage_current = Column(String(50), nullable=False)
    stage_completed = Column(String(50), nullable=True)
    
    # Fechas
    entered_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Metadata
    funnel_data = Column(JSONB)
    # Ejemplo:
    # {
    #     "touchpoints": 5,
    #     "offers_shown": 3,
    #     "offers_clicked": 1,
    #     "barriers_encountered": ["price", "uncertainty"]
    # }
    
    # Relaciones
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_conversion_funnels_user', 'user_id'),
        Index('idx_conversion_funnels_type', 'funnel_type'),
    )
```

### 4.3. Migraciones de Datos Requeridas

**Estrategia de Migración:**

1. **Fase 1: Extensiones a Tablas Existentes**
   - Agregar nuevas columnas a `users`, `narrative_fragments`, `missions`, `items`
   - Usar valores por defecto que no rompan funcionalidad existente
   - Agregar índices para nuevas consultas

2. **Fase 2: Nuevas Tablas sin Dependencias**
   - Crear tablas: `analytics_events`, `daily_metrics`, `user_session_metrics`
   - Crear tablas: `reaction_reward_configs`
   - Pueden existir sin afectar sistema actual

3. **Fase 3: Módulo de Experiencias**
   - Crear todas las tablas de `experiences`
   - No tienen dependencias críticas con sistema actual

4. **Fase 4: Módulo de Comercio**
   - Crear tablas de `commerce`
   - Establecer relaciones con tablas existentes

5. **Fase 5: Integraciones**
   - Establecer foreign keys entre módulos
   - Poblar datos iniciales (configs, archetipos base, etc.)

**Script de Migración Ejemplo:**
```python
# migrations/versions/001_add_composite_features.py

def upgrade():
    # Fase 1: Extensiones a Users
    op.add_column('users', sa.Column('archetype_primary', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('archetype_secondary', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('conversion_score', sa.Numeric(5, 2), nullable=True))
    op.add_column('users', sa.Column('lifetime_value', sa.Numeric(10, 2), server_default='0.00'))
    
    # Extensiones a NarrativeFragment
    op.add_column('narrative_fragments', sa.Column('experience_id', sa.Integer(), nullable=True))
    op.add_column('narrative_fragments', sa.Column('composite_requirements', postgresql.JSONB(), nullable=True))
    op.add_column('narrative_fragments', sa.Column('extended_rewards', postgresql.JSONB(), nullable=True))
    op.create_foreign_key('fk_fragment_experience', 'narrative_fragments', 'experiences', ['experience_id'], ['id'])
    
    # Crear índices
    op.create_index('idx_users_archetype', 'users', ['archetype_primary'])
    op.create_index('idx_fragments_experience', 'narrative_fragments', ['experience_id'])

def downgrade():
    # Rollback
    op.drop_column('users', 'archetype_primary')
    op.drop_column('users', 'archetype_secondary')
    # ... etc
```

---

## 5. PLAN DE IMPLEMENTACIÓN

### 5.1. Roadmap de Desarrollo

**Duración Estimada Total: 16-20 semanas**

#### FASE 1: Fundamentos (Semanas 1-4)

**Objetivo:** Establecer infraestructura base para integración

**Sprint 1 (Semana 1-2): CoordinadorCentral Base**
- Crear `core/coordinator.py` con estructura básica
- Implementar `TransactionManager` para operaciones distribuidas
- Extender Event Bus con capacidades de orquestación
- Crear sistema de validación compuesta básico

**Entregables:**
- CoordinadorCentral funcional con 2 operaciones: `TOMAR_DECISION` y `ACCEDER_NARRATIVA_VIP`
- Sistema de transacciones distribuidas operativo
- Tests unitarios para coordinación

**Sprint 2 (Semana 3-4): Migraciones de Data Model - Fase 1**
- Extender modelos existentes (`User`, `NarrativeFragment`, `Mission`, `Item`)
- Crear migraciones para nuevas columnas
- Poblar datos de configuración inicial
- Actualizar queries existentes para nuevos campos

**Entregables:**
- Modelos extendidos desplegados
- Datos legacy migrados sin pérdida
- Documentación de cambios en schema

**Dependencias Críticas:** Ninguna (puede iniciarse en paralelo)

---

#### FASE 2: Módulo de Reacciones y Analytics Básico (Semanas 5-6)

**Objetivo:** Implementar sistema de reacciones y tracking básico

**Sprint 3 (Semana 5-6): Sistema de Reacciones**
- Crear `modules/gamification/reactions.py`
- Implementar modelos `ContentReaction` y `ReactionRewardConfig`
- Integrar con besitos para otorgar recompensas
- Crear handlers de reacciones en Telegram

**Entregables:**
- Sistema de reacciones funcional
- Configuración de recompensas por reacción
- Integración con Event Bus

**Sprint 3.5 (Semana 6): Analytics Básico**
- Crear `modules/analytics/collector.py`
- Implementar modelos `AnalyticsEvent`
- Suscribir collector a Event Bus
- Crear queries básicas de métricas

**Entregables:**
- Tracking automático de eventos principales
- Dashboard básico de métricas

**Dependencias:** Requiere CoordinadorCentral (Fase 1)

---

#### FASE 3: Módulo de Comercio (Semanas 7-10)

**Objetivo:** Implementar sistema completo de comercio y monetización

**Sprint 4 (Semana 7-8): Tienda y Catálogo**
- Crear estructura `modules/commerce/`
- Implementar `shop.py` con catálogo
- Crear modelos `ShopItem`, `UserPurchase`
- Construir UI de tienda en Telegram

**Entregables:**
- Catálogo de productos funcional
- Sistema de navegación de tienda
- Filtros y búsqueda de items

**Sprint 5 (Semana 9): Sistema de Pagos**
- Implementar `payments.py` con Telegram Payments
- Integrar procesamiento de pagos con besitos
- Crear flujo de checkout completo
- Implementar sistema de refunds

**Entregables:**
- Compras con besitos funcionales
- Integración con Telegram Payments (real money)
- Sistema de confirmación y recibos

**Sprint 6 (Semana 10): Desbloqueos y Arquetipos**
- Implementar `unlocks.py` para desbloqueos post-compra
- Crear `archetypes.py` para detección de comportamiento
- Implementar `upselling.py` para ofertas contextuales
- Integrar desbloqueos con narrativa y experiencias

**Entregables:**
- Desbloqueos automáticos funcionando
- Sistema básico de arquetipos
- Ofertas personalizadas contextuales

**Dependencias:** Requiere CoordinadorCentral y Analytics (Fases 1-2)

---

#### FASE 4: Módulo de Experiencias Unificadas (Semanas 11-14)

**Objetivo:** Crear sistema completo de experiencias que integre todos los módulos

**Sprint 7 (Semana 11-12): Core de Experiencias**
- Crear estructura `modules/experiences/`
- Implementar todos los modelos de experiencias
- Crear `engine.py` con lógica de progreso
- Implementar `validator.py` para requisitos compuestos

**Entregables:**
- Modelos de experiencias desplegados
- Motor de experiencias funcional
- Validación de requisitos compuestos operativa

**Sprint 8 (Semana 13): Builder y Propagación**
- Implementar `builder.py` para creación de experiencias
- Crear `propagation.py` para generación automática de componentes
- Implementar `templates.py` con templates predefinidos
- Construir UI de administración de experiencias

**Entregables:**
- Herramientas de creación de experiencias
- Propagación automática funcional
- Templates listos para usar

**Sprint 9 (Semana 14): Integración Profunda**
- Integrar experiencias con narrativa
- Integrar experiencias con gamificación
- Integrar experiencias con comercio
- Crear flujos de usuario completos

**Entregables:**
- Experiencias totalmente integradas
- Flujos de usuario end-to-end funcionando
- Tests de integración completos

**Dependencias:** Requiere Comercio completamente (Fase 3) y CoordinadorCentral avanzado

---

#### FASE 5: Integraciones Profundas y CoordinadorCentral Completo (Semanas 15-16)

**Objetivo:** Completar todas las operaciones del CoordinadorCentral y establecer flujos complejos

**Sprint 10 (Semana 15): Operaciones Avanzadas del Coordinador**
- Implementar `REACCIONAR_CONTENIDO` completo
- Implementar `COMPRAR_ITEM` con todas las integraciones
- Crear sistema de rollback robusto
- Implementar priorización de eventos

**Entregables:**
- 4 operaciones principales del CoordinadorCentral completas
- Sistema de transacciones distribuidas robusto
- Manejo de errores y rollback automático

**Sprint 11 (Semana 16): Flujos de Conversión y Retroalimentación**
- Implementar flujos de conversión free->VIP
- Crear sistema de ofertas contextuales completo
- Implementar retroalimentación positiva entre sistemas
- Optimizar performance de operaciones coordinadas

**Entregables:**
- Flujos de conversión automatizados
- Sistema de upselling inteligente
- Métricas de conversión tracking

**Dependencias:** Requiere todas las fases anteriores

---

#### FASE 6: Analytics Avanzado y Dashboard (Semanas 17-18)

**Objetivo:** Sistema completo de analytics y visualización

**Sprint 12 (Semana 17): Analytics Completo**
- Completar `modules/analytics/` con todos los componentes
- Implementar `aggregator.py` con métricas avanzadas
- Crear `insights.py` con detección de patrones
- Implementar sistema de alertas

**Entregables:**
- Métricas avanzadas de engagement, monetización y narrativa
- Sistema de insights automáticos
- Alertas proactivas para admins

**Sprint 13 (Semana 18): Dashboard Administrativo**
- Crear `dashboard.py` con data providers
- Construir UI de dashboard web
- Implementar visualizaciones de métricas
- Crear sistema de reportes exportables

**Entregables:**
- Dashboard web completo
- Visualizaciones interactivas
- Sistema de reportes

**Dependencias:** Puede iniciarse en paralelo con Fase 5

---

#### FASE 7: Optimización y Pulido (Semanas 19-20)

**Objetivo:** Optimizar performance, corregir bugs y mejorar UX

**Sprint 14 (Semana 19): Optimización de Performance**
- Optimizar queries de base de datos
- Implementar caching estratégico
- Optimizar operaciones del CoordinadorCentral
- Realizar load testing

**Entregables:**
- Sistema optimizado para 10k+ usuarios concurrentes
- Tiempos de respuesta < 500ms para operaciones críticas
- Uso eficiente de recursos

**Sprint 15 (Semana 20): Testing y Documentación**
- Tests de integración end-to-end completos
- Documentación técnica de todos los módulos
- Guías de uso para administradores
- Manual de troubleshooting

**Entregables:**
- Cobertura de tests > 80%
- Documentación completa
- Sistema production-ready

**Dependencias:** Requiere todas las fases anteriores

---

### 5.2. Matriz de Dependencias

```
┌─────────────────────────────────────────────────────────────┐
│                   DEPENDENCIAS CRÍTICAS                      │
└─────────────────────────────────────────────────────────────┘

FASE 1: CoordinadorCentral + Data Model Extensions
  │
  ├──> FASE 2: Reacciones + Analytics Básico
  │      │
  │      └──> FASE 3: Módulo de Comercio
  │             │
  │             └──> FASE 4: Módulo de Experiencias
  │                    │
  │                    └──> FASE 5: Integraciones Profundas
  │                           │
  │                           ├──> FASE 6: Analytics Avanzado
  │                           │
  │                           └──> FASE 7: Optimización
  │
  └──> FASE 6: Analytics (puede iniciar en paralelo)

TRABAJO EN PARALELO POSIBLE:
- Fases 1 y 2 pueden trabajarse simultáneamente por equipos diferentes
- Fase 6 (Analytics) puede avanzar en paralelo con Fase 5
- Sprint de optimización puede comenzar antes si hay capacidad
```

### 5.3. Componentes Independientes vs Coordinados

#### Implementación Independiente Posible:
1. **Módulo de Analytics Básico** - Puede funcionar desde el inicio
2. **Sistema de Reacciones** - Puede implementarse sin comercio
3. **Extensiones de Data Model** - No afectan funcionalidad existente
4. **Dashboard Web** - Puede construirse con datos existentes

#### Requieren Implementación Coordinada:
1. **CoordinadorCentral + Experiencias** - Altamente acoplados
2. **Comercio + Desbloqueos** - Deben implementarse juntos
3. **Arquetipos + Ofertas Personalizadas** - Requieren datos de comportamiento
4. **Validación Compuesta** - Necesita todos los módulos operativos

### 5.4. Estrategia de Migración para Usuarios Existentes

**Principio:** Nunca romper funcionalidad existente

#### Paso 1: Modo Compatibilidad (Semanas 1-10)
- Nuevas funcionalidades se agregan sin afectar flujos actuales
- Sistema antiguo y nuevo coexisten
- Usuarios existentes no notan cambios

#### Paso 2: Migración Gradual (Semanas 11-16)
- Usuarios nuevos usan sistema nuevo por defecto
- Usuarios existentes pueden optar por nuevas features
- Datos legacy se migran bajo demanda

#### Paso 3: Unificación (Semanas 17-20)
- Todos los usuarios en sistema nuevo
- Sistema antiguo se depreca pero mantiene compatibilidad
- Rollback plan disponible

**Estrategias de Mitigación de Riesgo:**
1. Feature flags para activar/desactivar nuevas funcionalidades
2. A/B testing para validar nuevos flujos
3. Rollback automático en caso de errores críticos
4. Monitoreo continuo de métricas de salud del sistema

---

## 6. CONSIDERACIONES TÉCNICAS

### 6.1. Performance y Escalabilidad

#### 6.1.1. Puntos Críticos de Performance

**1. Validación de Requisitos Compuestos**
```
PROBLEMA: Validar requisitos puede requerir queries a múltiples tablas
IMPACTO: Latencia de 200-500ms por validación

SOLUCIONES:
- Caching de requisitos frecuentes en Redis
- Índices compuestos en tablas críticas
- Pre-cálculo de requisitos cumplidos
- Lazy loading de requisitos no críticos

IMPLEMENTACIÓN:
class RequirementCache:
    def get_cached_validation(user_id, target_id):
        cache_key = f"req_validation:{user_id}:{target_id}"
        cached = redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        result = compute_validation(user_id, target_id)
        redis.setex(cache_key, 300, json.dumps(result))  # 5 min TTL
        return result
```

**2. Operaciones del CoordinadorCentral**
```
PROBLEMA: Transacciones distribuidas pueden ser lentas
IMPACTO: Operaciones complejas toman 1-2 segundos

SOLUCIONES:
- Procesamiento asíncrono de operaciones no críticas
- Queue de operaciones con workers dedicados
- Optimización de queries con EXPLAIN ANALYZE
- Connection pooling optimizado

IMPLEMENTACIÓN:
# Operaciones críticas: síncronas
# Operaciones no críticas: asíncronas via Celery

@celery.task
def apply_purchase_unlocks_async(user_id, item_id):
    # Ejecutar en background
    pass

def COMPRAR_ITEM(user_id, item_id, payment_method):
    # Compra síncrona
    result = process_payment_sync(user_id, item_id)
    
    # Desbloqueos asíncronos
    apply_purchase_unlocks_async.delay(user_id, item_id)
    
    return result
```

**3. Tracking de Analytics**
```
PROBLEMA: Cada evento genera writes a base de datos
IMPACTO: Miles de inserts por minuto bajo carga

SOLUCIONES:
- Batch inserts cada 5-10 segundos
- Buffer en memoria con flush periódico
- Tabla particionada por fecha
- Índices optimizados para queries de lectura

IMPLEMENTACIÓN:
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

#### 6.1.2. Estrategias de Caching

**Redis Cache Strategy:**
```
┌──────────────────────────────────────────────────────────┐
│                   CACHING LAYERS                          │
└──────────────────────────────────────────────────────────┘

L1: User Session Cache (TTL: 30 min)
  - Estado VIP del usuario
  - Balance de besitos
  - Progreso narrativo actual
  - Experiencias activas

L2: Content Cache (TTL: 1 hora)
  - Fragmentos narrativos frecuentes
  - Catálogo de tienda
  - Configuración de recompensas
  - Templates de experiencias

L3: Computed Cache (TTL: 5 min)
  - Validaciones de requisitos
  - Arquetipos de usuario
  - Métricas agregadas
  - Ofertas personalizadas

INVALIDACIÓN:
- Manual: Al modificar contenido
- Automática: Por TTL
- Selective: Solo claves afectadas por cambio
```

**Implementación de Cache Manager:**
```python
class CacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def get_user_vip_status(self, user_id):
        cache_key = f"user:{user_id}:vip_status"
        cached = self.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        # Consultar DB
        status = db_query_vip_status(user_id)
        
        # Cachear por 30 minutos
        self.redis.setex(cache_key, 1800, json.dumps(status))
        return status
    
    def invalidate_user_cache(self, user_id):
        # Invalidar todas las claves del usuario
        pattern = f"user:{user_id}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
```

#### 6.1.3. Optimización de Queries

**Índices Críticos Requeridos:**
```sql
-- User queries
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_vip_status ON users(archetype_primary, conversion_score);

-- Narrative queries
CREATE INDEX idx_fragments_experience ON narrative_fragments(experience_id) 
    WHERE experience_id IS NOT NULL;
CREATE INDEX idx_fragments_vip ON narrative_fragments(is_vip_exclusive) 
    WHERE is_vip_exclusive = true;
CREATE INDEX idx_user_progress_composite ON user_narrative_progress(user_id, status, last_activity_at);

-- Experience queries
CREATE INDEX idx_experience_components_composite ON experience_components(experience_id, sequence_order);
CREATE INDEX idx_user_experience_status ON user_experience_progress(user_id, status, last_activity_at);

-- Commerce queries
CREATE INDEX idx_shop_items_available ON shop_items(is_available, type) 
    WHERE is_available = true;
CREATE INDEX idx_purchases_user_date ON user_purchases(user_id, purchase_date DESC);

-- Analytics queries
CREATE INDEX idx_analytics_user_time ON analytics_events(user_id, timestamp DESC);
CREATE INDEX idx_analytics_type_time ON analytics_events(event_type, timestamp DESC);

-- Partitioning para analytics_events
CREATE TABLE analytics_events_2025_10 PARTITION OF analytics_events
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
```

**Query Optimization Patterns:**
```python
# MALO: N+1 queries
def get_user_experiences(user_id):
    progress = UserExperienceProgress.query.filter_by(user_id=user_id).all()
    for p in progress:
        p.experience = Experience.query.get(p.experience_id)  # N queries
        p.components = ExperienceComponent.query.filter_by(
            experience_id=p.experience_id
        ).all()  # N queries más
    return progress

# BUENO: Single query with joins
def get_user_experiences(user_id):
    return db.session.query(UserExperienceProgress)\
        .options(
            joinedload(UserExperienceProgress.experience)
                .joinedload(Experience.components),
            joinedload(UserExperienceProgress.component_completions)
        )\
        .filter(UserExperienceProgress.user_id == user_id)\
        .all()
```

#### 6.1.4. Escalabilidad Horizontal

**Componentes que Escalan Horizontalmente:**
1. **API Workers (FastAPI)** - Stateless, fácil replicación
2. **Celery Workers** - Agregar workers según carga
3. **Redis** - Redis Cluster para alta disponibilidad
4. **Event Bus** - Redis Pub/Sub puede escalar

**Componentes que Requieren Atención:**
1. **PostgreSQL** - Read replicas para queries pesadas
2. **MongoDB** - Sharding por colecciones grandes
3. **Telegram Bot** - Múltiples instancias con load balancing

**Arquitectura Escalada:**
```
┌─────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA ESCALADA                     │
└─────────────────────────────────────────────────────────────┘

                     Load Balancer
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    Bot Instance 1   Bot Instance 2   Bot Instance 3
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                   Redis Cluster
                   (Event Bus)
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
  API Workers      Celery Workers    Coordinator
  (3+ instances)   (5+ instances)     (Primary)
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   PostgreSQL       MongoDB Cluster    Redis Cache
   (Primary +       (Sharded)          (Cluster)
    2 Replicas)
```

### 6.2. Seguridad y Validación

#### 6.2.1. Validación de Transacciones

**Puntos Críticos de Seguridad:**

1. **Validación de Besitos**
```python
class BesitosSecurityValidator:
    def validate_grant(self, user_id, amount, reason):
        # Validar que reason es válido
        if reason not in VALID_BESITOS_REASONS:
            raise SecurityError("Invalid besitos grant reason")
        
        # Validar límites diarios
        today_total = self.get_today_grants(user_id)
        if today_total + amount > MAX_DAILY_GRANTS:
            raise SecurityError("Daily grant limit exceeded")
        
        # Validar que no es manipulación
        if self.detect_manipulation(user_id, amount, reason):
            self.flag_for_review(user_id)
            raise SecurityError("Suspicious activity detected")
        
        return True
    
    def validate_spend(self, user_id, amount, reason):
        # Validar balance suficiente
        balance = self.get_balance(user_id)
        if balance < amount:
            raise InsufficientFundsError()
        
        # Validar que gasto es legítimo
        if reason not in VALID_SPEND_REASONS:
            raise SecurityError("Invalid spend reason")
        
        return True
```

2. **Validación de Compras**
```python
class PurchaseSecurityValidator:
    def validate_purchase(self, user_id, item_id, payment_method):
        # Validar que item existe y está disponible
        item = ShopItem.query.get(item_id)
        if not item or not item.is_available:
            raise ItemNotAvailableError()
        
        # Validar que usuario no ha comprado ya (si es único)
        if item.type == 'unique' and self.user_owns_item(user_id, item_id):
            raise AlreadyOwnedError()
        
        # Validar requisitos de compra
        if not self.meets_purchase_requirements(user_id, item):
            raise RequirementsNotMetError()
        
        # Validar método de pago
        if payment_method == 'besitos':
            balance = self.get_besitos_balance(user_id)
            if balance < item.price_besitos:
                raise InsufficientFundsError()
        
        # Rate limiting: prevenir spam de compras
        if self.is_rate_limited(user_id):
            raise RateLimitError("Too many purchase attempts")
        
        return True
```

3. **Validación de Acceso VIP**
```python
class VIPAccessValidator:
    def validate_vip_access(self, user_id, content_id, content_type):
        # Verificar membresía VIP
        vip_status = self.check_vip_membership(user_id)
        if not vip_status.is_active:
            return ValidationResult(
                valid=False,
                reason='vip_required',
                data={'vip_status': vip_status}
            )
        
        # Verificar que está en canal VIP
        in_channel = self.verify_channel_membership(user_id, 'VIP')
        if not in_channel:
            # Intentar re-agregar automáticamente
            self.attempt_channel_readd(user_id)
            if not self.verify_channel_membership(user_id, 'VIP'):
                return ValidationResult(
                    valid=False,
                    reason='channel_access_required'
                )
        
        # Verificar que contenido es realmente VIP
        content = self.get_content(content_type, content_id)
        if not content.is_vip_exclusive:
            # Permitir acceso sin VIP
            return ValidationResult(valid=True)
        
        return ValidationResult(valid=True)
```

#### 6.2.2. Prevención de Fraude

**Detección de Patrones Sospechosos:**
```python
class FraudDetectionEngine:
    def detect_suspicious_activity(self, user_id, action_type, action_data):
        signals = []
        
        # Señal 1: Actividad inusualmente alta
        activity_rate = self.get_recent_activity_rate(user_id)
        if activity_rate > NORMAL_ACTIVITY_THRESHOLD * 3:
            signals.append('high_activity_rate')
        
        # Señal 2: Patrones de bot
        if self.matches_bot_pattern(user_id):
            signals.append('bot_like_behavior')
        
        # Señal 3: Múltiples cuentas desde mismo dispositivo
        if self.detect_multi_accounting(user_id):
            signals.append('multi_accounting')
        
        # Señal 4: Explotación de mecánicas
        if self.detect_exploit_attempt(action_type, action_data):
            signals.append('exploit_attempt')
        
        if len(signals) >= 2:
            self.flag_user(user_id, signals)
            return FraudAlert(
                user_id=user_id,
                signals=signals,
                severity='high' if len(signals) >= 3 else 'medium'
            )
        
        return None
```

#### 6.2.3. Rate Limiting

**Implementación de Rate Limits:**
```python
class RateLimiter:
    def check_rate_limit(self, user_id, action_type):
        limits = {
            'purchase': (5, 3600),  # 5 compras por hora
            'reaction': (50, 300),   # 50 reacciones por 5 min
            'decision': (20, 60),    # 20 decisiones por minuto
            'api_call': (100, 60)    # 100 llamadas API por minuto
        }
        
        max_count, window = limits.get(action_type, (100, 60))
        
        key = f"rate_limit:{user_id}:{action_type}"
        current = redis.get(key)
        
        if current and int(current) >= max_count:
            raise RateLimitExceededError(f"Rate limit exceeded for {action_type}")
        
        # Incrementar contador
        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        pipe.execute()
        
        return True
```

### 6.3. Mantenibilidad y Testing

#### 6.3.1. Estrategia de Testing

**Pirámide de Tests:**
```
                    ╱╲
                   ╱E2E╲        10% - Tests End-to-End
                  ╱────╲
                 ╱ INT  ╲       30% - Tests de Integración
                ╱────────╲
               ╱   UNIT   ╲     60% - Tests Unitarios
              ╱────────────╲
```

**Tests Unitarios Críticos:**
```python
# tests/test_coordinator.py

class TestCoordinadorCentral:
    def test_tomar_decision_valid_requirements(self):
        # Setup
        user = create_test_user(vip=True, besitos=100)
        fragment = create_test_fragment(requirements={'vip': True})
        decision = create_test_decision(fragment_id=fragment.id)
        
        # Execute
        result = coordinator.TOMAR_DECISION(
            user.id, fragment.id, decision.id
        )
        
        # Assert
        assert result['success'] == True
        assert result['rewards_granted'] is not None
        assert user.refresh_balance() >= 100  # Besitos otorgados
    
    def test_tomar_decision_missing_requirements(self):
        user = create_test_user(vip=False)
        fragment = create_test_fragment(requirements={'vip': True})
        
        result = coordinator.TOMAR_DECISION(user.id, fragment.id, 1)
        
        assert result['success'] == False
        assert 'vip' in result['missing_requirements']
    
    def test_transaction_rollback_on_error(self):
        user = create_test_user(besitos=100)
        
        # Simular error en medio de transacción
        with patch('modules.gamification.besitos.grant_besitos', 
                   side_effect=Exception("DB Error")):
            with pytest.raises(Exception):
                coordinator.COMPRAR_ITEM(user.id, item_id=1, payment_method='besitos')
        
        # Verificar que balance no cambió
        assert user.refresh_balance() == 100
```

**Tests de Integración:**
```python
# tests/integration/test_experience_flow.py

class TestExperienceFlow:
    def test_complete_experience_flow(self):
        # Setup: Crear experiencia completa
        user = create_test_user()
        experience = create_test_experience_with_components([
            {'type': 'narrative', 'id': 1},
            {'type': 'mission', 'id': 2},
            {'type': 'purchase', 'id': 3}
        ])
        
        # Step 1: Iniciar experiencia
        result = experience_api.start_experience(user.id, experience.id)
        assert result.success == True
        
        # Step 2: Completar fragmento narrativo
        narrative_result = coordinator.TOMAR_DECISION(
            user.id, fragment_id=1, decision_id=1
        )
        assert narrative_result['success'] == True
        
        # Step 3: Verificar progreso
        progress = experience_api.get_user_progress(user.id, experience.id)
        assert progress.completion_percentage > 0
        
        # Step 4: Completar misión
        mission_result = gamification_api.complete_mission(user.id, mission_id=2)
        assert mission_result.success == True
        
        # Step 5: Realizar compra
        purchase_result = coordinator.COMPRAR_ITEM(
            user.id, item_id=3, payment_method='besitos'
        )
        assert purchase_result['success'] == True
        
        # Verificar experiencia completada
        progress = experience_api.get_user_progress(user.id, experience.id)
        assert progress.status == 'completed'
        assert progress.completion_percentage == 100.00
```

**Tests End-to-End:**
```python
# tests/e2e/test_user_journey.py

class TestUserJourney:
    def test_new_user_to_vip_conversion(self, telegram_bot_client):
        # Simular journey completo de usuario
        
        # 1. Usuario nuevo inicia bot
        response = telegram_bot_client.send_message('/start')
        assert 'Bienvenido' in response.text
        
        # 2. Usuario consume contenido narrativo
        response = telegram_bot_client.send_message('Ver historia')
        assert response.has_narrative_content
        
        # 3. Usuario gana besitos por reacciones
        telegram_bot_client.react_to_message(message_id=123, reaction='❤️')
        balance = get_user_balance(telegram_bot_client.user_id)
        assert balance > 0
        
        # 4. Usuario intenta acceder contenido VIP
        response = telegram_bot_client.send_message('Ver contenido exclusivo')
        assert 'VIP requerido' in response.text
        assert response.has_upgrade_offer
        
        # 5. Usuario se suscribe a VIP
        telegram_bot_client.click_button('Suscribirse a VIP')
        # Simular pago exitoso
        telegram_bot_client.complete_payment(amount=9.99)
        
        # 6. Verificar acceso VIP
        response = telegram_bot_client.send_message('Ver contenido exclusivo')
        assert response.has_vip_content
        assert 'VIP requerido' not in response.text
```

#### 6.3.2. Logging y Monitoreo

**Estrategia de Logging:**
```python
import logging
import structlog

# Configuración de structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

class CoordinadorCentral:
    def TOMAR_DECISION(self, user_id, fragment_id, decision_id):
        logger.info(
            "decision_started",
            user_id=user_id,
            fragment_id=fragment_id,
            decision_id=decision_id
        )
        
        try:
            result = self._execute_decision(user_id, fragment_id, decision_id)
            
            logger.info(
                "decision_completed",
                user_id=user_id,
                fragment_id=fragment_id,
                success=True,
                rewards=result['rewards_granted']
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "decision_failed",
                user_id=user_id,
                fragment_id=fragment_id,
                error=str(e),
                exc_info=True
            )
            raise
```

**Métricas de Monitoreo:**
```python
from prometheus_client import Counter, Histogram, Gauge

# Contadores
decisions_total = Counter('decisions_total', 'Total decisions taken', ['status'])
purchases_total = Counter('purchases_total', 'Total purchases', ['method', 'status'])
experiences_started = Counter('experiences_started_total', 'Experiences started')

# Histogramas (latencia)
decision_duration = Histogram('decision_duration_seconds', 'Decision processing time')
purchase_duration = Histogram('purchase_duration_seconds', 'Purchase processing time')

# Gauges (estado actual)
active_users = Gauge('active_users', 'Currently active users')
vip_users = Gauge('vip_users_total', 'Total VIP users')

# Uso en código
@decision_duration.time()
def TOMAR_DECISION(self, user_id, fragment_id, decision_id):
    try:
        result = self._execute_decision(user_id, fragment_id, decision_id)
        decisions_total.labels(status='success').inc()
        return result
    except Exception as e:
        decisions_total.labels(status='error').inc()
        raise
```

---

## 7. RIESGOS Y MITIGACIONES

### 7.1. Riesgos Técnicos

#### RIESGO 1: Complejidad del CoordinadorCentral
**Severidad:** ALTA  
**Probabilidad:** MEDIA

**Descripción:** El CoordinadorCentral puede volverse extremadamente complejo y difícil de mantener con múltiples integraciones.

**Impacto:**
- Bugs difíciles de reproducir
- Dificultad para agregar nuevas features
- Performance degradado
- Alto costo de mantenimiento

**Mitigaciones:**
1. **Arquitectura Modular:** Separar responsabilidades en componentes especializados
2. **Tests Exhaustivos:** >80% cobertura con tests de integración robustos
3. **Documentación Detallada:** Documentar cada flujo de coordinación
4. **Code Reviews Rigurosos:** Revisiones obligatorias para cambios en coordinator
5. **Monitoring Proactivo:** Alertas automáticas para anomalías

**Plan B:** Si se vuelve inmanejable, dividir en múltiples coordinadores especializados

---

#### RIESGO 2: Performance de Transacciones Distribuidas
**Severidad:** MEDIA-ALTA  
**Probabilidad:**
ALTA

**Descripción:** Las transacciones distribuidas que involucran múltiples sistemas pueden ser lentas y causar timeout en operaciones críticas.

**Impacto:**
- Usuarios experimentan delays al tomar decisiones
- Compras fallan por timeout
- Experiencia de usuario degradada
- Posibles inconsistencias de datos

**Mitigaciones:**
1. **Procesamiento Asíncrono:** Mover operaciones no críticas a background jobs
   ```python
   def COMPRAR_ITEM(user_id, item_id, payment_method):
       # Crítico: Procesamiento síncrono
       payment_result = process_payment_sync(user_id, item_id)
       add_to_inventory_sync(user_id, item_id)
       
       # No crítico: Procesamiento asíncrono
       apply_unlocks_async.delay(user_id, item_id)
       update_analytics_async.delay(user_id, 'purchase', item_id)
       generate_recommendations_async.delay(user_id)
       
       return {'success': True, 'payment': payment_result}
   ```

2. **Caching Agresivo:** Cache de validaciones y requisitos comunes
3. **Database Optimization:** Índices optimizados + connection pooling
4. **Timeout Configuration:** Timeouts razonables con fallback gracioso
5. **Circuit Breaker Pattern:** Prevenir cascading failures
   ```python
   from pybreaker import CircuitBreaker
   
   breaker = CircuitBreaker(fail_max=5, timeout_duration=60)
   
   @breaker
   def call_external_service():
       # Llamada que puede fallar
       pass
   ```

**Métricas a Monitorear:**
- P50, P95, P99 de latencia de operaciones
- Tasa de timeout
- Tasa de rollback de transacciones

**Umbral de Alerta:** Si P95 > 2 segundos, investigar inmediatamente

---

#### RIESGO 3: Consistencia de Datos entre Sistemas
**Severidad:** ALTA  
**Probabilidad:** MEDIA

**Descripción:** Con múltiples bases de datos (PostgreSQL + MongoDB + Redis), mantener consistencia es complejo.

**Impacto:**
- Usuarios ven datos inconsistentes
- Desbloqueos no se aplican correctamente
- Balance de besitos desincronizado
- Pérdida de confianza del usuario

**Mitigaciones:**
1. **PostgreSQL como Source of Truth:** Datos críticos siempre en PostgreSQL
   - Balance de besitos
   - Estado VIP
   - Compras
   - Progreso de experiencias

2. **MongoDB como Cache Enriquecido:** Contenido narrativo puede reconstruirse
   - Si hay inconsistencia, regenerar desde PostgreSQL

3. **Redis como Cache Temporal:** Puede purgarse sin pérdida de datos
   - Si Redis falla, consultar PostgreSQL directamente

4. **Patrón Saga para Transacciones Distribuidas:**
   ```python
   class PurchaseSaga:
       def execute(self, user_id, item_id):
           steps = []
           
           try:
               # Step 1: Deduct besitos
               step1 = self.deduct_besitos(user_id, amount)
               steps.append(('deduct_besitos', step1))
               
               # Step 2: Add to inventory
               step2 = self.add_to_inventory(user_id, item_id)
               steps.append(('add_inventory', step2))
               
               # Step 3: Apply unlocks
               step3 = self.apply_unlocks(user_id, item_id)
               steps.append(('apply_unlocks', step3))
               
               return {'success': True}
               
           except Exception as e:
               # Rollback all steps in reverse order
               self.rollback(steps)
               raise
       
       def rollback(self, steps):
           for step_name, step_data in reversed(steps):
               rollback_func = getattr(self, f'rollback_{step_name}')
               rollback_func(step_data)
   ```

5. **Reconciliation Jobs:** Jobs nocturnos que detectan y corrigen inconsistencias
   ```python
   @celery.task
   def reconcile_user_inventory():
       # Comparar inventario en game vs shop
       # Corregir discrepancias
       pass
   ```

**Plan de Contingencia:**
- Sistema de auditoría para detectar inconsistencias
- Herramientas de admin para corrección manual
- Backups frecuentes de datos críticos

---

#### RIESGO 4: Escalabilidad del Sistema de Experiencias
**Severidad:** MEDIA  
**Probabilidad:** MEDIA

**Descripción:** Con cientos de experiencias y miles de usuarios, el tracking de progreso puede volverse un cuello de botella.

**Impacto:**
- Queries lentos para obtener progreso
- Alto uso de CPU en cálculos de progreso
- Problemas al escalar a 10k+ usuarios

**Mitigaciones:**
1. **Desnormalización Estratégica:** Pre-calcular valores frecuentes
   ```sql
   -- En lugar de calcular cada vez
   SELECT COUNT(*) FROM user_component_completions 
   WHERE user_progress_id = ?
   
   -- Almacenar en user_experience_progress
   UPDATE user_experience_progress 
   SET components_completed = components_completed + 1
   WHERE id = ?
   ```

2. **Particionamiento de Tablas:** Particionar por fecha o rango de users
   ```sql
   CREATE TABLE user_experience_progress_2025 PARTITION OF user_experience_progress
       FOR VALUES FROM (1) TO (1000000);
   ```

3. **Lazy Loading:** Cargar solo datos necesarios
   ```python
   # MALO: Carga todo
   experiences = user.experience_progress.all()
   
   # BUENO: Carga bajo demanda
   experiences = user.experience_progress.filter(status='in_progress').limit(10)
   ```

4. **Agregaciones Pre-calculadas:** Actualizar métricas en tiempo real
5. **Archivado de Experiencias Antiguas:** Mover experiencias completadas a tabla de archivo

---

### 7.2. Riesgos de Producto

#### RIESGO 5: Complejidad Abruma a Usuarios
**Severidad:** ALTA  
**Probabilidad:** MEDIA-ALTA

**Descripción:** La integración profunda de sistemas puede confundir a usuarios con demasiadas opciones y requisitos.

**Impacto:**
- Usuarios abandonan por confusión
- Bajo engagement con nuevas features
- Feedback negativo
- ROI bajo del desarrollo

**Mitigaciones:**
1. **Onboarding Gradual:** Introducir features progresivamente
   ```
   Día 1: Solo narrativa básica
   Día 3: Desbloquear sistema de besitos
   Día 7: Introducir misiones
   Día 14: Mostrar tienda
   Día 30: Revelar experiencias complejas
   ```

2. **UI Simplificada:** Esconder complejidad detrás de interfaz simple
   - Usar menús contextuales inteligentes
   - Mostrar solo opciones relevantes según progreso
   - Guías visuales y tooltips

3. **Sistema de Tutoriales:** Tutoriales interactivos para cada feature
4. **A/B Testing:** Probar diferentes niveles de complejidad
5. **Analytics de Confusión:** Detectar puntos donde usuarios se pierden
   ```python
   def detect_confusion_points():
       # Detectar patrones como:
       # - Usuario visita misma pantalla múltiples veces
       # - Tiempo anormalmente largo en decisión
       # - Abandono después de ver requisitos
       pass
   ```

**Métricas Clave:**
- Tasa de abandono por feature
- Tiempo hasta primera interacción exitosa
- Solicitudes de ayuda por feature

---

#### RIESGO 6: Balance Económico del Sistema de Besitos
**Severidad:** ALTA  
**Probabilidad:** MEDIA

**Descripción:** El sistema de economía puede quedar desbalanceado, generando inflación o deflación de besitos.

**Impacto:**
- **Inflación:** Usuarios tienen demasiados besitos, no necesitan comprar
- **Deflación:** Usuarios no pueden comprar nada, frustración
- Economía rota afecta monetización

**Mitigaciones:**
1. **Simulación Económica Pre-Launch:**
   ```python
   class EconomySimulator:
       def simulate_user_journey(days=30):
           user = SimulatedUser()
           
           for day in range(days):
               # Simular actividad diaria
               besitos_earned = user.daily_activity()
               besitos_spent = user.daily_spending()
               
               user.balance += besitos_earned - besitos_spent
           
           return {
               'final_balance': user.balance,
               'total_earned': user.total_earned,
               'total_spent': user.total_spent,
               'purchase_power': user.can_afford_items()
           }
   ```

2. **Sinks y Faucets Balanceados:**
   ```
   FAUCETS (fuentes de besitos):
   - Reacciones: 5-10 besitos
   - Fragmentos narrativos: 20-50 besitos
   - Misiones diarias: 100-200 besitos
   - Logros: 50-500 besitos
   
   SINKS (gastos de besitos):
   - Items comunes: 100-500 besitos
   - Items raros: 1000-2000 besitos
   - Desbloqueos narrativos: 500-1500 besitos
   ```

3. **Monitoring en Tiempo Real:**
   ```python
   class EconomyMonitor:
       def check_health(self):
           metrics = {
               'avg_balance': self.get_average_balance(),
               'median_balance': self.get_median_balance(),
               'inflation_rate': self.calculate_inflation(),
               'purchase_rate': self.get_purchase_rate(),
               'conversion_rate': self.get_besitos_to_real_money_ratio()
           }
           
           if metrics['inflation_rate'] > 0.2:  # 20% inflación
               self.alert_admin("High inflation detected")
           
           return metrics
   ```

4. **Ajustes Dinámicos:**
   - Eventos temporales que actúan como sinks (subastas, ofertas limitadas)
   - Ajuste de recompensas según métricas
   - Sistema de "impuestos" suaves (decay de besitos no usados)

5. **Segmentación de Economía:**
   - Usuarios nuevos: Faucets generosos
   - Usuarios medios: Economía balanceada
   - Usuarios veteranos: Sinks atractivos

**Plan de Contingencia:**
- Reset de economía solo como último recurso
- Compensación a usuarios afectados
- Comunicación transparente

---

#### RIESGO 7: Baja Adopción de Experiencias Unificadas
**Severidad:** MEDIA  
**Probabilidad:** MEDIA

**Descripción:** Los usuarios pueden no entender o no valorar las experiencias unificadas complejas.

**Impacto:**
- Bajo ROI del módulo más complejo
- Recursos desperdiciados en desarrollo
- Feature que no agrega valor

**Mitigaciones:**
1. **MVP de Experiencias:** Lanzar con 3-5 experiencias simples y bien diseñadas
2. **Narrativa Atractiva:** Crear experiencias con historias emocionalmente resonantes
3. **Recompensas Significativas:** Ofrecer recompensas únicas que solo se obtienen por experiencias
4. **Promoción In-App:** Destacar experiencias en momentos clave
5. **Social Proof:** Mostrar cuántos usuarios han completado cada experiencia

**Métricas de Éxito:**
- % de usuarios que inician al menos una experiencia: >40%
- % de usuarios que completan experiencias iniciadas: >60%
- NPS de usuarios que completaron experiencias vs. usuarios regulares

**Criterio de Cancelación:**
Si después de 2 meses < 20% de usuarios activos han iniciado experiencias, re-evaluar el concepto.

---

### 7.3. Riesgos de Implementación

#### RIESGO 8: Dependencias entre Sprints Causan Delays
**Severidad:** MEDIA  
**Probabilidad:** ALTA

**Descripción:** Como muchos componentes dependen de otros, delays en un sprint bloquean sprints posteriores.

**Impacto:**
- Timeline se extiende significativamente
- Equipo bloqueado esperando dependencias
- Presupuesto excedido

**Mitigaciones:**
1. **Buffer Time:** Agregar 20% de buffer a cada sprint crítico
2. **Trabajo en Paralelo:** Identificar trabajo que puede hacerse en paralelo
   ```
   PARALELO POSIBLE:
   - Analytics + Commerce (diferentes equipos)
   - Frontend + Backend (con contratos de API claros)
   - Tests + Documentación (durante desarrollo)
   ```

3. **Prototyping de Interfaces:** Crear interfaces/contratos antes de implementación
   ```python
   # Definir interfaz antes de implementar
   class IExperienceEngine(ABC):
       @abstractmethod
       def start_experience(self, user_id, exp_id): pass
       
       @abstractmethod
       def progress_component(self, user_id, comp_id): pass
   
   # Implementar mock para testing
   class MockExperienceEngine(IExperienceEngine):
       def start_experience(self, user_id, exp_id):
           return MockResult(success=True)
   ```

4. **Feature Flags:** Desplegar código sin activar features
5. **Sprints de Integración:** Dedicar sprints específicos solo a integración

**Plan de Contingencia:**
- Priorizar features críticas
- Reducir scope de features secundarias si necesario
- Agregar recursos si delays críticos

---

#### RIESGO 9: Bugs en Producción Afectan Usuarios Existentes
**Severidad:** ALTA  
**Probabilidad:** MEDIA

**Descripción:** Bugs en nuevas features pueden afectar funcionalidad existente que usuarios ya usan.

**Impacto:**
- Pérdida de datos de usuarios
- Frustración masiva
- Churn de usuarios
- Daño reputacional

**Mitigaciones:**
1. **Feature Flags con Rollout Gradual:**
   ```python
   class FeatureFlags:
       def is_enabled(self, feature_name, user_id):
           if feature_name == 'experiences':
               # Rollout gradual: 10% día 1, 50% día 3, 100% día 7
               rollout_percentage = self.get_rollout_percentage('experiences')
               user_hash = hash(user_id) % 100
               return user_hash < rollout_percentage
           
           return True
   ```

2. **Canary Deployments:** Desplegar primero a usuarios de prueba
3. **Rollback Rápido:** Capacidad de revertir en < 5 minutos
4. **Monitoring Intensivo:** Alertas automáticas para anomalías
   ```python
   def post_deployment_monitoring():
       metrics = {
           'error_rate': get_error_rate(last_minutes=15),
           'response_time': get_avg_response_time(last_minutes=15),
           'user_complaints': get_support_tickets(last_minutes=15)
       }
       
       if metrics['error_rate'] > baseline * 2:
           trigger_rollback()
           alert_team("High error rate detected, automatic rollback initiated")
   ```

5. **Backward Compatibility:** Mantener compatibilidad con datos/APIs antiguas
6. **Sandbox Testing:** Testing exhaustivo en ambiente de staging con datos reales anonimizados

---

#### RIESGO 10: Falta de Documentación Causa Problemas de Mantenimiento
**Severidad:** MEDIA-ALTA  
**Probabilidad:** ALTA

**Descripción:** Sistema complejo sin documentación adecuada se vuelve imposible de mantener.

**Impacto:**
- Onboarding lento de nuevos developers
- Bugs difíciles de resolver
- Miedo a tocar código crítico
- Deuda técnica acumulada

**Mitigaciones:**
1. **Documentación como Requerimiento:** No se acepta PR sin documentación
2. **Docs as Code:** Documentación vive con el código
   ```python
   class CoordinadorCentral:
       """
       Sistema de coordinación central para operaciones multi-módulo.
       
       El CoordinadorCentral orquesta operaciones que involucran múltiples
       sistemas (narrativa, gamificación, comercio) garantizando consistencia
       mediante transacciones distribuidas.
       
       Operaciones Principales:
       - TOMAR_DECISION: Coordina decisiones narrativas con validación compuesta
       - COMPRAR_ITEM: Procesa compras con desbloqueos automáticos
       - ACCEDER_NARRATIVA_VIP: Valida y otorga acceso a contenido VIP
       - REACCIONAR_CONTENIDO: Procesa reacciones con recompensas multi-sistema
       
       Example:
           >>> coordinator = CoordinadorCentral(event_bus)
           >>> result = coordinator.TOMAR_DECISION(
           ...     user_id=123,
           ...     fragment_id=45,
           ...     decision_id=2
           ... )
           >>> print(result['success'])
           True
       
       Ver: docs/architecture/coordinator.md para detalles de diseño
       """
   ```

3. **ADRs (Architecture Decision Records):** Documentar decisiones importantes
   ```markdown
   # ADR 001: Usar PostgreSQL como Source of Truth
   
   ## Estado
   Aceptado
   
   ## Contexto
   Necesitamos mantener consistencia entre múltiples bases de datos...
   
   ## Decisión
   PostgreSQL será la fuente de verdad para todos los datos críticos...
   
   ## Consecuencias
   - Positivas: Consistencia garantizada, ACID transactions
   - Negativas: Performance potencialmente más lenta
   ```

4. **Diagramas Actualizados:** Mantener diagramas de arquitectura al día
5. **Runbooks:** Guías para operaciones comunes y troubleshooting
6. **Video Walkthroughs:** Crear videos explicando componentes complejos

---

## 8. CONCLUSIONES Y RECOMENDACIONES

### 8.1. Resumen de Brechas Críticas

**Top 5 Brechas que Requieren Atención Inmediata:**

1. **CoordinadorCentral** - Sistema de orquestación completo (40% del esfuerzo)
2. **Módulo de Experiencias** - Completamente nuevo y central (20% del esfuerzo)
3. **Módulo de Comercio** - Inexistente pero necesario para monetización (20% del esfuerzo)
4. **Sistema de Validación Compuesta** - Base para integraciones (10% del esfuerzo)
5. **Analytics Unificado** - Necesario para tomar decisiones (10% del esfuerzo)

### 8.2. Viabilidad del Proyecto

**Evaluación:** ✅ **VIABLE** con las siguientes condiciones:

**Factores Positivos:**
- ✅ Base sólida existente (~70% de módulos individuales)
- ✅ Arquitectura conceptual bien pensada
- ✅ Stack tecnológico apropiado
- ✅ Oportunidad clara de diferenciación

**Factores de Riesgo:**
- ⚠️ Complejidad alta del sistema de integración
- ⚠️ Timeline agresivo (16-20 semanas)
- ⚠️ Requiere equipo experimentado
- ⚠️ Alto riesgo de scope creep

### 8.3. Recomendaciones Estratégicas

#### Recomendación 1: Enfoque Incremental Obligatorio
**NO intentar implementar todo a la vez.**

Enfoque recomendado:
```
Fase 1 (MVP): CoordinadorCentral + Comercio Básico (8 semanas)
  → Lanzar y validar monetización

Fase 2 (Enhanced): Experiencias + Analytics (6 semanas)
  → Agregar engagement profundo

Fase 3 (Optimized): Optimización + Features avanzadas (6 semanas)
  → Escalar y pulir
```

#### Recomendación 2: Priorizar Monetización
**Implementar primero lo que genera revenue:**
1. Sistema de comercio con besitos
2. Suscripciones VIP
3. Desbloqueos de contenido
4. Después: Features de engagement avanzadas

#### Recomendación 3: Validación Temprana
**No construir sin validar supuestos:**
- Testear arquetipos con usuarios reales
- Validar que usuarios entienden experiencias
- Confirmar que balance económico funciona
- A/B test de flujos de conversión

#### Recomendación 4: Equipo Especializado
**Requerimientos de equipo:**
- 1 Arquitecto Senior (full-time)
- 2-3 Backend Developers (Python/PostgreSQL/MongoDB)
- 1 Frontend Developer (Telegram Bot UI)
- 1 QA Engineer (automatización)
- 1 Product Manager (priorización)
- 0.5 DevOps (infraestructura)

**Total:** 5.5-6.5 FTEs por 20 semanas

#### Recomendación 5: Métricas de Éxito Claras
**Definir antes de comenzar:**
```
Métrica                          Target      Crítico
────────────────────────────────────────────────────
Conversión Free→VIP              > 5%        Sí
Retención día 30                 > 40%       Sí
ARPU (Average Revenue Per User)  > $2/mes    Sí
Engagement con Experiencias      > 30%       No
Tasa de completitud narrativa    > 50%       No
NPS                              > 40        Sí
```

### 8.4. Alternativas a Considerar

#### Opción A: Implementación Completa (Recomendado en este documento)
- **Pros:** Sistema más poderoso y diferenciado
- **Contras:** Alto riesgo, largo timeline, alto costo
- **Cuándo:** Si hay recursos y tiempo suficiente

#### Opción B: MVP Simplificado
- **Scope:** Solo CoordinadorCentral básico + Comercio
- **Pros:** Más rápido (8 semanas), menor riesgo
- **Contras:** Menos diferenciación
- **Cuándo:** Si hay presión de timeline o recursos limitados

#### Opción C: Implementación Híbrida (RECOMENDADO)
- **Fase 1:** MVP con monetización (8 semanas)
- **Validación:** Si métricas > targets, continuar
- **Fase 2:** Features avanzadas si validación exitosa
- **Pros:** Balance riesgo/recompensa, validación temprana
- **Contras:** Requiere disciplina para no hacer scope creep

### 8.5. Próximos Pasos Inmediatos

**Si se decide proceder:**

**Semana 0 (Pre-inicio):**
1. ✅ Aprobar roadmap y budget
2. ✅ Ensamblar equipo
3. ✅ Configurar ambiente de desarrollo
4. ✅ Crear repositorio de documentación técnica
5. ✅ Definir contratos de APIs entre módulos

**Semana 1 (Inicio):**
1. Sprint Planning detallado de Fase 1
2. Crear ramas de desarrollo
3. Configurar CI/CD pipeline
4. Iniciar desarrollo de CoordinadorCentral base
5. Iniciar diseño de schema de base de datos

**Hitos Críticos de Validación:**
- **Semana 4:** CoordinadorCentral funcional con 2 operaciones
- **Semana 8:** MVP con comercio funcional
- **Semana 10:** Validación de métricas de monetización
- **Decisión GO/NO-GO:** Continuar con Fase 2 o pivotar

---

## APÉNDICE: Checklist de Implementación

### Pre-Implementación
- [ ] Aprobar documento de arquitectura
- [ ] Confirmar budget y timeline
- [ ] Asegurar equipo con skills requeridos
- [ ] Configurar ambientes (dev, staging, prod)
- [ ] Crear backlog detallado de tareas

### Fase 1: Fundamentos
- [ ] Implementar CoordinadorCentral base
- [ ] Crear TransactionManager
- [ ] Extender modelos de base de datos
- [ ] Crear migraciones
- [ ] Tests unitarios >70% cobertura
- [ ] Documentación de APIs internas

### Fase 2: Reacciones y Analytics
- [ ] Implementar módulo de reacciones
- [ ] Integrar recompensas de besitos
- [ ] Crear sistema de tracking de eventos
- [ ] Dashboard básico de métricas
- [ ] Tests de integración

### Fase 3: Comercio
- [ ] Crear catálogo de productos
- [ ] Integrar Telegram Payments
- [ ] Implementar sistema de desbloqueos
- [ ] Crear sistema de arquetipos
- [ ] Implementar ofertas personalizadas
- [ ] Tests end-to-end de compras

### Fase 4: Experiencias
- [ ] Crear modelos de experiencias
- [ ] Implementar motor de experiencias
- [ ] Sistema de validación compuesta
- [ ] Builder de experiencias
- [ ] Propagación automática
- [ ] UI para administración

### Fase 5: Integraciones Profundas
- [ ] Completar todas las operaciones del Coordinador
- [ ] Flujos de conversión
- [ ] Sistema de upselling
- [ ] Retroalimentación entre sistemas
- [ ] Tests de integración completos

### Fase 6: Analytics Avanzado
- [ ] Sistema de insights automáticos
- [ ] Dashboard completo
- [ ] Sistema de alertas
- [ ] Reportes exportables
- [ ] Visualizaciones interactivas

### Fase 7: Optimización
- [ ] Optimizar queries
- [ ] Implementar caching estratégico
- [ ] Load testing
- [ ] Security audit
- [ ] Performance tuning

### Pre-Lanzamiento
- [ ] Tests de regresión completos
- [ ] Documentación final
- [ ] Runbooks operacionales
- [ ] Plan de rollback
- [ ] Monitoring configurado
- [ ] Alertas configuradas

### Post-Lanzamiento
- [ ] Monitorear métricas críticas
- [ ] Recolectar feedback de usuarios
- [ ] Iterar basado en datos
- [ ] Optimizaciones continuas

---

**FIN DEL DOCUMENTO DE INVESTIGACIÓN**

Este documento proporciona una visión completa de las brechas arquitectónicas, el esfuerzo requerido y un plan detallado para evolucionar DianaBot del estado actual al ecosistema integrado conceptual. La implementación es viable pero requiere disciplina, recursos adecuados y un enfoque incremental con validación continua.
