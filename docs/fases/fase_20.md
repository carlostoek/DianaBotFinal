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

# Fase 20: Integración de Pagos

### Objetivo
Monetización real con procesadores de pago

### Componentes a Implementar

#### 20.1 Configuración de Telegram Stars
- **Crear**: Integración con Telegram Payments
- **Referencia**: Sección 9.2 - Procesamiento de Pagos (Telegram Stars)
- **Archivos**:
  - `modules/admin/payments.py`
  - `bot/handlers/payments.py`
- **Funcionalidad**:
  - Configurar provider token
  - Crear invoices

#### 20.2 Flujo de Suscripción VIP
- **Crear**: Proceso de compra
- **Referencia**: Sección 9.2 - Procesamiento de Pagos
- **Archivos**:
  - `bot/commands/subscribe.py`
- **Funcionalidad**:
  - Comando `/subscribe` muestra opciones (monthly, yearly)
  - Genera invoice
  - Maneja pre-checkout query

#### 20.3 Handler de Pagos Exitosos
- **Crear**: Procesamiento post-pago
- **Referencia**: Sección 9.2 - Handler de Pagos
- **Modificar**: `bot/handlers/payments.py`
- **Funcionalidad**:
  - Recibir `successful_payment`
  - Activar suscripción VIP
  - Invitar a canal VIP
  - Enviar confirmación
  - Registrar transacción

#### 20.4 Configuración de Stripe (Alternativa)
- **Crear**: Integración con Stripe
- **Referencia**: Sección 9.2 - Procesamiento de Pagos (Stripe)
- **Archivos**:
  - `modules/admin/stripe_integration.py`
  - `api/routers/webhooks.py`
- **Funcionalidad**:
  - Crear checkout sessions
  - Webhook para confirmar pagos
  - Sincronizar con suscripciones

#### 20.5 Compra de Besitos
- **Crear**: Microtransacciones de besitos
- **Referencia**: Sección 9.1 - Tienda Virtual
- **Archivos**:
  - `bot/commands/buy_besitos.py`
- **Packs**:
  - 500 besitos - $2.99
  - 1500 besitos - $7.99
  - 4000 besitos - $17.99

#### 20.6 Sistema de Refunds
- **Crear**: Gestión de reembolsos
- **Referencia**: Sección 9.2 - Refunds y Cancelaciones
- **Archivos**:
  - `modules/admin/refunds.py`
- **Funcionalidad**:
  - Procesar solicitudes de refund
  - Política de 48 horas
  - Revertir suscripción si refund
  - Notificar usuario

#### 20.7 Registro de Transacciones
- **Crear**: Tabla de pagos
- **Archivos**:
  - `database/models.py` (modelo Payment)
  - `database/migrations/016_create_payments.sql`
- **Campos**: payment_id, user_id, amount, currency, payment_method, status, reference

#### 20.8 Dashboard de Ingresos
- **Crear**: Vista de monetización en dashboard
- **Referencia**: Sección 12.1 - Métricas de Producto
- **Archivos**:
  - `dashboard/templates/revenue.html`
- **Contenido**:
  - MRR (Monthly Recurring Revenue)
  - Total transacciones
  - Conversión rate
  - ARPU / ARPPU
  - Gráficas temporales

### Resultado de Fase 20
✓ Pagos reales implementados
✓ Suscripciones VIP comprables
✓ Microtransacciones de besitos
✓ Sistema de refunds
✓ Tracking completo de ingresos
✓ Dashboard de monetización

## Referencias
### 9.2 Procesamiento de Pagos

Integración con múltiples procesadores para maximizar conversión:

**Telegram Stars (Recomendado)**

Telegram tiene su sistema nativo de pagos que es ideal para bots:

```python
from telegram import LabeledPrice

async def send_invoice(update, context):
    """Envía invoice para suscripción VIP"""
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="DianaBot VIP - Mensual",
        description="Acceso completo a todos los niveles narrativos y beneficios exclusivos",
        payload=f"vip_subscription:monthly:{user_id}",
        provider_token=PROVIDER_TOKEN,
        currency="USD",
        prices=[
            LabeledPrice("Suscripción Mensual", 999)  # en centavos
        ],
        start_parameter="vip-monthly"
    )

async def handle_successful_payment(update, context):
    """Maneja pago exitoso"""
    payment = update.message.successful_payment
    
    # Activar suscripción
    activate_vip_subscription(
        user_id=update.effective_user.id,
        subscription_type='monthly',
        payment_reference=payment.telegram_payment_charge_id
    )
    
    # Enviar confirmación
    await update.message.reply_text(
        "¡Bienvenido a VIP! Tu suscripción está activa. "
        "Accede ahora a los niveles 4-6 y disfruta todos los beneficios."
    )
```

**Stripe (Alternativa)**

Para usuarios que prefieren pagar fuera de Telegram:

```python
import stripe

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def create_checkout_session(user_id, subscription_type):
    """Crea sesión de pago en Stripe"""
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_monthly_vip',  # ID del precio en Stripe
            'quantity': 1,
        }],
        mode='subscription',
        success_url=f'https://dianabot.com/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url='https://dianabot.com/payment/cancel',
        client_reference_id=str(user_id),
        metadata={
            'user_id': user_id,
            'subscription_type': subscription_type
        }
    )
    
    return session.url

# Webhook para confirmar pago
@app.post('/stripe/webhook')
async def stripe_webhook(request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    event = stripe.Webhook.construct_event(
        payload, sig_header, STRIPE_WEBHOOK_SECRET
    )
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = int(session['client_reference_id'])
        
        # Activar suscripción
        activate_vip_subscription(user_id, 'monthly', session['id'])
    
    return {'status': 'success'}
```

**Refunds y Cancelaciones**

Política clara de reembolsos:

```python
def handle_refund_request(user_id, reason):
    """Procesa solicitud de reembolso"""
    subscription = get_active_subscription(user_id)
    
    if not subscription:
        return {'success': False, 'message': 'No active subscription'}
    
    # Política: reembolso completo si cancela en primeros 48 horas
    hours_since_start = (datetime.now() - subscription.start_date).total_hours()
    
    if hours_since_start <= 48:
        # Reembolso completo
        process_refund(subscription.payment_reference, full=True)
        deactivate_subscription(subscription.subscription_id)
        
        return {
            'success': True,
            'message': 'Full refund processed',
            'amount': subscription.amount
        }
    else:
        # Cancelar pero no reembolsar
        cancel_subscription_at_period_end(subscription.subscription_id)
        
        return {
            'success': True,
            'message': 'Subscription will cancel at period end',
            'access_until': subscription.end_date
        }
```

### 9.1 Estrategia de Monetización

DianaBot tiene múltiples flujos de ingresos diseñados para ser sostenibles sin ser intrusivos.

**Suscripciones VIP**

El modelo de suscripción es el pilar principal:

Tiers de Suscripción:
- VIP Mensual: $9.99/mes
- VIP Trimestral: $24.99 (17% descuento)
- VIP Anual: $89.99 (25% descuento)

Beneficios VIP claramente diferenciados:
- Acceso a niveles narrativos 4-6 (contenido exclusivo)
- Misiones VIP con recompensas premium
- Items exclusivos en tienda
- Doble besitos en misiones diarias
- Acceso prioritario a subastas
- Badge especial en perfil
- Canal VIP con contenido adicional

Funnel de Conversión:
1. Usuario free experimenta niveles 1-3 (contenido de alta calidad)
2. Al completar nivel 3, mensaje: "La historia continúa en nivel 4. ¡Hazte VIP!"
3. Trial period: 7 días gratis de VIP para usuarios enganchados
4. Recordatorios suaves durante trial
5. Al expirar trial, mensaje con descuento de "bienvenida de regreso" si se suscriben inmediatamente

**Tienda Virtual**

Venta de items digitales con dinero real o besitos:

Items con Dinero Real (micro-transacciones):
- Pack pequeño de besitos: 500 besitos por $2.99
- Pack mediano: 1,500 besitos por $7.99 (mejor valor)
- Pack grande: 4,000 besitos por $17.99 (mejor valor aún)
- Items cosméticos exclusivos: $0.99 - $4.99
- Bundles narrativos: "Pack Completo Temporada 1" por $14.99

Items con Besitos (economía interna):
- Items narrativos: 50-200 besitos
- Coleccionables: 30-100 besitos
- Power-ups: 40-150 besitos
- Items raros de subastas: 300-1000 besitos

**Modelo Freemium Balanceado**

El contenido gratuito debe ser suficientemente satisfactorio para retener usuarios, pero el contenido premium debe ser irresistible:

Ratio de Contenido:
- 40% completamente gratis (niveles 1-3, misiones básicas)
- 30% alcanzable con esfuerzo free (comprando con besitos ganados)
- 30% exclusivamente VIP (niveles 4-6, items ultra-raros)

Limitaciones Free sin Frustrar:
- Límite de inventario (20 slots vs 50 VIP)
- Límite de besitos ganables por día (200 vs 500 VIP)
- Acceso a trivias (5 por día vs ilimitado VIP)
- Sin acceso a fragmentos secretos premium

### 12.1 Métricas de Producto

**Monetización:**
- Free to VIP Conversion: % de usuarios free que se convierten a VIP
- ARPU (Average Revenue Per User): Ingreso promedio por usuario
- ARPPU (Average Revenue Per Paying User): Ingreso promedio por usuario pagador
- LTV (Lifetime Value): Valor total de un usuario durante su vida
- CAC (Customer Acquisition Cost): Costo de adquirir un usuario
- LTV/CAC Ratio: Idealmente > 3:1