# FASE 5: INTEGRACIONES PROFUNDAS (Semanas 15-16)

## Especificación de la Fase

### SPRINT 10: Operaciones Avanzadas del Coordinador (Semana 15)

#### Objetivos
- Completar todas las operaciones del CoordinadorCentral
- Sistema de rollback robusto
- Optimización de performance

#### Operaciones a Completar
**Referencia:** Sección 3.1 (CoordinadorCentral)

1. **`REACCIONAR_CONTENIDO`** (completar)
   - **Especificación completa:** Código en Sección 3.1
   - **Integraciones:** reacciones → besitos → logros → misiones → analytics

2. **`COMPRAR_ITEM`** (extender)
   - **Ya implementado en Sprint 6**
   - **Extender con:** Experiencias, actualizaciones de arquetipos completas

3. **Operaciones adicionales** (si requeridas)
   - Definir según necesidades identificadas en testing

#### Sistema de Rollback Robusto
- **Referencia:** Sección 3.1 (TransactionManager)
- **Mejorar:**
  - Logging detallado de cada paso
  - Retry automático en fallos transitorios
  - Alertas a admins en rollbacks

#### Priorización de Eventos
- Eventos críticos (compras, VIP) → alta prioridad
- Eventos de tracking → baja prioridad
- Queue management para evitar overflow

#### Optimización de Performance
- **Referencia:** Sección 6.1.1 (Puntos Críticos de Performance)
- **Implementar:**
  - Caching de validaciones (ver Sección 6.1.1 - Punto 1)
  - Procesamiento asíncrono (ver Sección 6.1.1 - Punto 2)
  - Circuit breaker pattern (ver Sección 7.1 - Riesgo 2)

#### Entregables
- [ ] 4 operaciones principales completas y optimizadas
- [ ] Sistema de rollback robusto con logging
- [ ] Circuit breakers implementados
- [ ] Performance P95 < 1 segundo
- [ ] Documentación de operaciones

#### Dependencias
- Requiere todos los módulos implementados
- Requiere experiencias integradas (Sprint 9)

---

### SPRINT 11: Flujos de Conversión y Retroalimentación (Semana 16)

#### Objetivos
- Implementar flujos de conversión free→VIP
- Sistema de ofertas contextuales completo
- Retroalimentación positiva entre sistemas

#### Análisis Conceptual
- **Referencia:** Sección del documento de arquitectura (arquitectura_sistema_dianabot.md)
  - "Sistema de Retroalimentación" - Retroalimentación Positiva
  - "Mecanismos de Conversión"

#### Componentes a Implementar/Extender
1. **Flujos de Conversión**
   - **Modelo de BD:** `ConversionFunnel` (ver Sección 4.2 - Analytics)
   - **Tracking de etapas:** entered, current, completed
   - **Triggers:** Acceso denegado a VIP, oferta contextual, etc.

2. **Sistema de Ofertas Inteligente**
   - Extender `upselling.py` (creado en Sprint 6)
   - **Contextos:**
     - Post decisión narrativa importante
     - Al completar misión
     - Después de reaccionar
     - Al ver contenido VIP bloqueado

3. **Retroalimentación Positiva**
   - Más narrativa → más puntos → más compras → más contenido
   - Más participación → más VIP → más narrativa → más engagement

#### Integración con Arquetipos
- **Referencia:** Sección 2.3 (Sistema de Arquetipos)
- Personalizar ofertas según arquetipo del usuario:
  - NARRATIVE_LOVER → Ofrecer desbloqueos narrativos
  - COLLECTOR → Ofrecer items raros
  - COMPETITIVE → Ofrecer ventajas
  - etc.

#### Modelo de Administración de Suscripciones
- **Referencia:** Sección 2.4 - BRECHA 4 (Lifecycle de Suscripción)
- **Componente:** `subscription_lifecycle.py`
- **Funciones:**
  - `handle_subscription_expiring()`
  - `handle_subscription_expired()`
  - `handle_subscription_renewed()`

#### Métricas de Conversión
- Funnel de conversión Free → Engaged → Purchaser → VIP
- Tasa de conversión por arquetipo
- Efectividad de ofertas contextuales
- ROI de cada tipo de oferta

#### Entregables
- [ ] Flujos de conversión automatizados
- [ ] Sistema de ofertas contextuales funcionando
- [ ] `modules/admin/subscription_lifecycle.py` implementado
- [ ] Tracking de conversión funnel
- [ ] Dashboard de métricas de conversión
- [ ] Tests de flujos de conversión

#### Dependencias
- Requiere arquetipos (Sprint 6)
- Requiere experiencias (Sprint 9)
- Requiere CoordinadorCentral optimizado (Sprint 10)

#### Riesgos
- **Referencia:** Sección 7.2 - Riesgo 5 (Complejidad Abruma a Usuarios)
- **Mitigación:** Onboarding gradual, UI simplificada

## Referencias del Documento de Investigación

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

### Sección 3.1 - TransactionManager

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

### Sección 6.1.1 - Puntos Críticos de Performance

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

### Sección 7.1 - Riesgo 2 (Performance de Transacciones)

**Descripción:** Las transacciones distribuidas que involucran múltiples sistemas pueden ser lentas y causar timeout en operaciones críticas.

**Mitigaciones:**
```python
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

@breaker
def call_external_service():
    # Llamada que puede fallar
    pass
```

### Sección 2.4 - Sistema 4: Administración de Canales

#### Brechas Identificadas

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

### Sección 4.2 - Módulo de Analytics

#### Módulo de Analytics
```python
# database/models/analytics.py (COMPLETAMENTE NUEVO)

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

### Sección 7.2 - Riesgo 5 (Complejidad Abruma a Usuarios)

**Descripción:** La integración profunda de sistemas puede confundir a usuarios con demasiadas opciones y requisitos.

**Mitigaciones:**
1. **Onboarding Gradual:**
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