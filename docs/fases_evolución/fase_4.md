# FASE 4: MÓDULO DE EXPERIENCIAS UNIFICADAS (Semanas 11-14)

## Especificación de la Fase

### SPRINT 7: Core de Experiencias (Semanas 11-12)

#### Objetivos
- Crear sistema completo de experiencias
- Implementar motor de progreso
- Habilitar validación de requisitos compuestos

#### Análisis de Brecha
- **Referencia:** Sección 2.5 - Estado Actual (NO EXISTE)
- **Importancia:** BRECHA CRÍTICA - Módulo central a la arquitectura

#### Concepto de Experiencia
- **Referencia:** Sección 2.5 - Concepto de Experiencia
- Un flujo unificado que integra múltiples elementos de diferentes sistemas

#### Estructura del Módulo
- **Referencia completa:** Sección 2.5
```
modules/experiences/
├── engine.py
├── builder.py
├── propagation.py
├── validator.py
├── coordinator.py
└── templates.py
```

#### Modelos de Base de Datos
- **Referencia completa:** Sección 4.2 (Módulo de Experiencias)
- **Modelos Sprint 7:**
  - `Experience`
  - `ExperienceComponent`
  - `UserExperienceProgress`
  - `UserComponentCompletion`
  - `ExperienceRequirement`
  - `ExperienceReward`

#### Componentes Sprint 7
1. **engine.py**
   - **Especificación:** Sección 2.5 (ExperienceEngine)
   - **Funciones clave:**
     - `start_experience()`
     - `progress_experience()`
     - `complete_experience()`
     - `get_experience_status()`

2. **validator.py**
   - **Especificación:** Sección 2.5 (CompositeValidator)
   - **Funcionalidad:** Validar requisitos de múltiples sistemas
   - **Tipos de requisitos:** level, vip_membership, item, achievement, experience_completed

#### Sistema de Requisitos Compuestos
- **Referencia teórica:** Sección 2.1 - BRECHA CRÍTICA 1 (Sistema de Requisitos Compuestos)
- **Implementación:** `validator.py` valida contra todos los módulos
- **Integración:** Usa APIs internas (ver Sección 3.3)

#### Entregables
- [ ] Todos los modelos de experiencias creados y migrados
- [ ] `modules/experiences/engine.py` implementado
- [ ] `modules/experiences/validator.py` implementado
- [ ] Sistema de requisitos compuestos funcional
- [ ] Tests unitarios de motor de experiencias

#### Dependencias
- Requiere TODOS los módulos previos operativos
- Requiere APIs internas definidas (Sección 3.3)
- Requiere CoordinadorCentral completo

---

### SPRINT 8: Builder y Propagación (Semana 13)

#### Objetivos
- Crear herramientas para construir experiencias
- Implementar propagación automática de componentes
- Templates predefinidos para experiencias comunes

#### Componentes a Implementar
1. **builder.py**
   - **Especificación:** Sección 2.5 (ExperienceBuilder)
   - **Funciones:**
     - `create_experience()`
     - `add_component()`
     - `from_template()`

2. **propagation.py**
   - **Especificación:** Sección 2.5 (PropagationEngine)
   - **Funcionalidad:** Crear automáticamente componentes en otros sistemas
   - **Ejemplo:** Crear fragmentos narrativos + misiones + items vinculados

3. **templates.py**
   - **Especificación:** Sección 2.5 (ExperienceTemplates)
   - **Templates:** NARRATIVE_JOURNEY, MISSION_CHAIN, HYBRID

#### Sistema de Propagación Automática
**Flujo:**
1. Admin crea experiencia con template
2. System genera componentes automáticamente:
   - Fragmentos narrativos → tabla `narrative_fragments`
   - Misiones → tabla `missions`
   - Items de recompensa → tabla `items`
3. Vincula todo a la experiencia central

#### UI de Administración
- Panel para crear experiencias
- Editor visual de componentes
- Preview de flujo de experiencia
- Configuración de requisitos y recompensas

#### Experiencias Iniciales
Crear 3-5 experiencias de ejemplo:
1. **"El Primer Beso"** (NARRATIVE_JOURNEY)
   - 5 fragmentos narrativos
   - 3 decisiones clave
   - 1 logro al completar

2. **"Cazador de Secretos"** (MISSION_CHAIN)
   - 3 misiones secuenciales
   - Requiere comprar 1 item
   - Desbloquea contenido especial

3. **"Camino VIP"** (HYBRID)
   - Mezcla narrativa + misiones
   - Requiere membresía VIP
   - Recompensas exclusivas

#### Entregables
- [ ] `modules/experiences/builder.py` implementado
- [ ] `modules/experiences/propagation.py` implementado
- [ ] `modules/experiences/templates.py` implementado
- [ ] UI de administración funcional
- [ ] 3-5 experiencias de ejemplo creadas
- [ ] Documentación de creación de experiencias

#### Dependencias
- Requiere engine.py (Sprint 7)
- Requiere todos los módulos de contenido (narrativa, gamificación, comercio)

---

### SPRINT 9: Integración Profunda (Semana 14)

#### Objetivos
- Integrar experiencias con todos los módulos
- Crear flujos de usuario end-to-end
- Validar funcionamiento completo del sistema

#### Integraciones Requeridas
**Referencia completa:** Sección 2.5 - Integraciones Requeridas

1. **Con Narrativa**
   - Fragmentos como componentes de experiencias
   - Progreso narrativo actualiza experiencia
   - Desbloqueos narrativos como recompensas

2. **Con Gamificación**
   - Misiones como componentes
   - Logros otorgados al completar
   - Besitos como recompensas

3. **Con Comercio**
   - Items como requisitos
   - Experiencias exclusivas para compradores
   - Descuentos al completar

4. **Con Administración**
   - Experiencias VIP exclusivas
   - Contenido publicado en canales
   - Acceso a canales como recompensa

#### Actualización del CoordinadorCentral
- Extender operaciones existentes para considerar experiencias
- Agregar lógica de progreso de experiencias en:
  - `TOMAR_DECISION`
  - `COMPRAR_ITEM`
  - `REACCIONAR_CONTENIDO`

#### Flujos End-to-End a Validar
1. Usuario inicia experiencia → completa todos los componentes → recibe recompensas
2. Usuario intenta iniciar experiencia sin requisitos → ve qué le falta → completa requisitos → inicia
3. Usuario abandona experiencia a mitad → puede retomar después
4. Usuario completa experiencia → desbloquea siguiente experiencia

#### Tests de Integración
- **Referencia:** Sección 6.3.1 (Tests de Integración)
- **Ejemplo:** `test_complete_experience_flow` (ver código en Sección 6.3.1)

#### Entregables
- [ ] Todas las integraciones implementadas
- [ ] CoordinadorCentral actualizado
- [ ] Flujos end-to-end funcionando
- [ ] Tests de integración completos (>30 test cases)
- [ ] Documentación de flujos de usuario

#### Dependencias
- Requiere builder y propagation (Sprint 8)
- Requiere TODOS los módulos previos estables

#### Riesgos
- **Referencia:** Sección 7.2 - Riesgo 7 (Baja Adopción de Experiencias)
- **Mitigación:** MVP con experiencias bien diseñadas y promoción in-app

## Referencias del Documento de Investigación

### Sección 2.1 - Sistema 1: Narrativa Inmersiva

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

### Sección 2.5 - Sistema 5: Experiencias Unificadas (MÓDULO COMPLETAMENTE NUEVO)

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

### Sección 4.2 - Nuevos Modelos Requeridos (Módulo de Experiencias)

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

### Sección 6.3.1 - Estrategia de Testing

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

### Sección 7.2 - Riesgo 7 (Baja Adopción de Experiencias)

**Descripción:** Los usuarios pueden no entender o no valorar las experiencias unificadas complejas.

**Mitigaciones:**
1. **MVP de Experiencias:** Lanzar con 3-5 experiencias simples y bien diseñadas
2. **Narrativa Atractiva:** Crear experiencias con historias emocionalmente resonantes
3. **Recompensas Significativas:** Ofrecer recompensas únicas que solo se obtienen por experiencias
4. **Promoción In-App:** Destacar experiencias en momentos clave
5. **Social Proof:** Mostrar cuántos usuarios han completado cada experiencia