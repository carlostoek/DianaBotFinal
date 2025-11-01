# FASE 1: FUNDAMENTOS (Semanas 1-4)

## Especificación de la Fase

### SPRINT 1: CoordinadorCentral Base (Semanas 1-2)

#### Objetivos
- Crear sistema de coordinación central operativo
- Implementar transacciones distribuidas
- Habilitar 2 operaciones básicas

#### Componentes a Implementar
1. **CoordinadorCentral**
   - **Referencia:** Sección 3.1 (Event Bus vs CoordinadorCentral)
   - **Especificación completa:** Código ejemplo en Sección 3.1
   - **Operaciones requeridas:** `TOMAR_DECISION`, `ACCEDER_NARRATIVA_VIP`

2. **TransactionManager**
   - **Referencia:** Sección 3.1 (componente adicional)
   - **Funcionalidad:** Gestión de transacciones distribuidas con rollback

3. **Extensión del Event Bus**
   - **Estado actual:** Sección 3.1 (Event Bus actual)
   - **Capacidades nuevas:** Orquestación, priorización de eventos

#### Nuevos Eventos Requeridos
- **Referencia completa:** Sección 3.2 (Nuevos Tipos de Eventos)
- **Eventos prioritarios Sprint 1:**
  - `coordinator.decision_taken`
  - `coordinator.access_denied`
  - `narrative.fragment_visited`
  - `narrative.decision_taken`

#### Entregables
- [ ] `core/coordinator.py` funcional
- [ ] `core/transaction_manager.py` implementado
- [ ] Tests unitarios >70% cobertura
- [ ] Documentación de APIs internas (ver **Sección 3.3**)

#### Dependencias
- Ninguna (puede iniciarse inmediatamente)

---

### SPRINT 2: Extensiones Data Model Fase 1 (Semanas 3-4)

#### Objetivos
- Extender modelos existentes sin romper funcionalidad
- Preparar base de datos para integraciones
- Migrar datos existentes

#### Modelos a Extender
1. **User Model**
   - **Referencia:** Sección 4.1 (Extensiones a Modelos Existentes)
   - **Campos nuevos:** archetipos, conversion_score, lifetime_value, etc.

2. **NarrativeFragment Model**
   - **Referencia:** Sección 4.1
   - **Campos nuevos:** experience_id, composite_requirements, extended_rewards, métricas

3. **Mission Model**
   - **Referencia:** Sección 4.1
   - **Campos nuevos:** experience_id, composite_requirements

4. **Item Model**
   - **Referencia:** Sección 4.1
   - **Campos nuevos:** is_purchasable, shop_item_id, unlocks_content

#### Estrategia de Migración
- **Referencia completa:** Sección 4.3 (Migraciones de Datos Requeridas)
- **Estrategia:** Fase 1 - Extensiones sin romper funcionalidad existente
- **Script ejemplo:** Ver Sección 4.3

#### Índices Críticos
- **Referencia:** Sección 6.1.3 (Optimización de Queries)
- **Índices a crear:** Todos los índices listados para User, NarrativeFragment, Mission

#### Entregables
- [ ] Migraciones creadas y probadas
- [ ] Datos legacy migrados sin pérdida
- [ ] Índices optimizados creados
- [ ] Tests de integridad de datos
- [ ] Documentación de cambios en schema

#### Dependencias
- Puede ejecutarse en paralelo con Sprint 1

#### Riesgos
- **Referencia:** Sección 7.1 - Riesgo 3 (Consistencia de Datos)
- **Mitigación:** PostgreSQL como Source of Truth

## Referencias del Documento de Investigación

### Sección 3.1 - Event Bus vs CoordinadorCentral

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

### Sección 3.2 - Nuevos Tipos de Eventos Requeridos

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

### Sección 3.3 - APIs de Integración entre Módulos

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
```

### Sección 4.1 - Extensiones a Modelos Existentes

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

### Sección 4.3 - Migraciones de Datos Requeridas

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

### Sección 6.1.3 - Optimización de Queries

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

### Sección 7.1 - Riesgo 3 (Consistencia de Datos)

**Descripción:** Con múltiples bases de datos (PostgreSQL + MongoDB + Redis), mantener consistencia es complejo.

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