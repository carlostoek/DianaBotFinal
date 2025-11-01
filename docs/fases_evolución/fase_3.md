# FASE 3: MÓDULO DE COMERCIO (Semanas 7-10)

## Especificación de la Fase

### SPRINT 4: Tienda y Catálogo (Semanas 7-8)

#### Objetivos
- Crear sistema completo de tienda
- Habilitar navegación y búsqueda de productos
- UI de tienda en Telegram

#### Análisis de Brecha
- **Referencia:** Sección 2.3 - Estado Actual (NO EXISTE módulo)
- **Brecha:** BRECHA CRÍTICA 1 - Ausencia Total del Módulo de Comercio

#### Estructura del Módulo
- **Referencia completa:** Sección 2.3 - estructura de carpetas
```
modules/commerce/
├── shop.py
├── cart.py
├── checkout.py
├── payments.py
├── unlocks.py
├── upselling.py
└── subscriptions.py
```

#### Componentes Sprint 4
1. **shop.py**
   - **Especificación:** Sección 2.3 (ShopManager)
   - **Funciones:** `get_catalog()`, `get_item_details()`

2. **Modelos de Base de Datos**
   - **Referencia:** Sección 4.2 (Módulo de Comercio)
   - **Modelos Sprint 4:**
     - `ShopItem` (tabla completa)
     - `UserPurchase` (estructura base)

3. **UI de Telegram**
   - Menú de tienda con categorías
   - Vista de detalle de items
   - Filtros (tipo, precio, rareza)

#### Catálogo Inicial
- Crear 10-15 items de prueba
- Variar tipos: narrative_unlock, experience_unlock, power_up
- Variar raridades: common, rare, epic, legendary
- Precios: 100-5000 besitos

#### Entregables
- [ ] `modules/commerce/shop.py` implementado
- [ ] Modelos ShopItem y UserPurchase creados
- [ ] Catálogo inicial poblado
- [ ] UI de tienda funcional en Telegram
- [ ] Sistema de filtros y búsqueda

#### Dependencias
- Requiere User model extendido (Sprint 2)
- Requiere Item model extendido (Sprint 2)

---

### SPRINT 5: Sistema de Pagos (Semana 9)

#### Objetivos
- Integrar Telegram Payments
- Implementar compras con besitos
- Crear flujo de checkout completo

#### Componentes a Implementar
1. **payments.py**
   - **Especificación:** Sección 2.3 - BRECHA CRÍTICA 2
   - **Funcionalidades:**
     - Manejo de `PreCheckoutQuery`
     - Procesamiento de `SuccessfulPayment`
     - Sistema de refunds

2. **checkout.py**
   - **Especificación:** Sección 2.3 (CheckoutProcessor)
   - **Funciones:** `process_purchase()`, `process_vip_subscription()`

#### Validación de Seguridad
- **Referencia:** Sección 6.2.1 - Punto 2 (Validación de Compras)
- **Implementar:** `PurchaseSecurityValidator`
- **Validaciones:**
  - Item disponible
  - No duplicar compras únicas
  - Verificar requisitos
  - Rate limiting

#### Métodos de Pago
1. **Besitos (interno)**
   - Validar balance suficiente
   - Transacción atómica con CoordinadorCentral

2. **Telegram Payments (dinero real)**
   - Integración con provider
   - Manejo de webhooks
   - Confirmaciones

#### Entregables
- [ ] `modules/commerce/payments.py` implementado
- [ ] `modules/commerce/checkout.py` implementado
- [ ] Integración con Telegram Payments funcional
- [ ] Compras con besitos funcionando
- [ ] Sistema de validación de seguridad
- [ ] Tests de flujos de compra

#### Dependencias
- Requiere shop.py (Sprint 4)
- Requiere CoordinadorCentral (Sprint 1)
- Requiere sistema de besitos funcional

#### Riesgos
- **Referencia:** Sección 7.1 - Riesgo 2 (Performance de Transacciones)
- **Mitigación:** Procesamiento asíncrono de operaciones no críticas

---

### SPRINT 6: Desbloqueos y Arquetipos (Semana 10)

#### Objetivos
- Implementar desbloqueos automáticos post-compra
- Crear sistema de arquetipos de usuario
- Habilitar ofertas personalizadas

#### Componentes a Implementar
1. **unlocks.py**
   - **Especificación:** Sección 2.3 (PurchaseUnlockEngine)
   - **Funciones:** `apply_unlocks()`, `check_purchase_requirements()`

2. **archetypes.py**
   - **Especificación:** Sección 2.3 - BRECHA CRÍTICA 3
   - **Clase:** `ArchetypeEngine`
   - **Arquetipos:** NARRATIVE_LOVER, COLLECTOR, COMPETITIVE, SOCIAL, COMPLETIONIST

3. **upselling.py**
   - **Especificación:** Sección 2.3 (UpsellEngine)
   - **Funciones:** `get_contextual_offers()`, `trigger_conversion_flow()`

4. **Modelos de Base de Datos**
   - **Referencia:** Sección 4.2 (Módulo de Comercio)
   - **Modelos Sprint 6:**
     - `UserArchetype`
     - `PersonalizedOffer`

#### Lógica de Desbloqueos
- Desbloquear fragmentos narrativos
- Activar experiencias exclusivas
- Otorgar acceso a canales especiales
- Desbloquear misiones premium

#### Detección de Arquetipos
- **Basado en:**
  - Patrones de consumo de contenido
  - Frecuencia de interacciones
  - Tipos de compras realizadas
  - Decisiones narrativas tomadas

#### Integración con CoordinadorCentral
- **Operación:** `COMPRAR_ITEM` completa
- **Referencia:** Sección 3.1 (código completo)
- **Flujo:** Compra → Inventory → Unlocks → Archetipos → Upsell

#### Entregables
- [ ] `modules/commerce/unlocks.py` implementado
- [ ] `modules/commerce/archetypes.py` implementado
- [ ] `modules/commerce/upselling.py` implementado
- [ ] Modelos UserArchetype y PersonalizedOffer
- [ ] Integración completa con COMPRAR_ITEM
- [ ] Tests de desbloqueos automáticos

#### Dependencias
- Requiere checkout.py (Sprint 5)
- Requiere analytics básico (Sprint 3.5) para detección de arquetipos
- Requiere extensiones de NarrativeFragment (Sprint 2)

#### Riesgos
- **Referencia:** Sección 7.2 - Riesgo 6 (Balance Económico)
- **Mitigación:** Simulación económica (ver código en Sección 7.2)

## Referencias del Documento de Investigación

### Sección 2.3 - Sistema 3: Comercio Integrado

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

### Sección 3.1 - CoordinadorCentral - Operación COMPRAR_ITEM

```python
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
```

### Sección 4.2 - Nuevos Modelos Requeridos (Módulo de Comercio)

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

### Sección 6.2.1 - Punto 2 (Validación de Compras)

**Validación de Compras**
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

### Sección 7.1 - Riesgo 2 (Performance de Transacciones)

**Descripción:** Las transacciones distribuidas que involucran múltiples sistemas pueden ser lentas y causar timeout en operaciones críticas.

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

### Sección 7.2 - Riesgo 6 (Balance Económico)

**Descripción:** El sistema de economía puede quedar desbalanceado, generando inflación o deflación de besitos.

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