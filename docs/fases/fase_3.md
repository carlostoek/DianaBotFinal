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

# Fase 3: Sistema de Besitos (Economía Base)

### Objetivo
Implementar economía virtual básica sin mecánicas complejas

### Componentes a Implementar

#### 3.1 Modelo de Balance de Besitos
- **Crear**: Tablas para balance y transacciones
- **Referencia**: Sección 2.3 - PostgreSQL (tablas `user_balances`, `transactions`)
- **Archivos**:
  - `database/models.py` (modelos UserBalance, Transaction)
  - `database/migrations/003_create_balances_transactions.sql`
- **Campos**: user_id, besitos, lifetime_besitos, transaction logs

#### 3.2 Servicio de Besitos
- **Crear**: Lógica de negocio para manejar besitos
- **Referencia**: Sección 4.1 - Economía de Besitos
- **Archivos**:
  - `modules/gamification/besitos.py`
- **Funciones**:
  - `grant_besitos(user_id, amount, source)`
  - `spend_besitos(user_id, amount, purpose)`
  - `get_balance(user_id)`
  - `get_transaction_history(user_id)`
- **Validaciones**: Balance no negativo, transacciones atómicas

#### 3.3 Eventos de Besitos
- **Crear**: Publicar eventos al otorgar/gastar besitos
- **Referencia**: Sección 7.1 - Eventos de Gamificación
- **Modificar**: `modules/gamification/besitos.py`
- **Eventos**:
  - `gamification.besitos_earned`
  - `gamification.besitos_spent`

#### 3.4 Comandos de Besitos
- **Crear**: Comandos para consultar y testear besitos
- **Referencia**: Sección 4.1 - Economía de Besitos
- **Archivos**:
  - `bot/commands/balance.py`
  - `bot/commands/history.py` (historial de transacciones)
- **Comandos**:
  - `/balance`: Mostrar besitos actuales
  - `/history`: Mostrar últimas transacciones

#### 3.5 Regalo Diario (Daily Reward)
- **Crear**: Sistema que otorga besitos diarios
- **Referencia**: Sección 4.1 - Economía de Besitos (fuentes de entrada)
- **Archivos**:
  - `modules/gamification/daily_rewards.py`
  - `bot/commands/daily.py`
- **Funcionalidad**:
  - Comando `/daily` otorga 10 besitos
  - Solo una vez por día por usuario
  - Usar Redis para tracking diario

### Resultado de Fase 3
✓ Sistema de besitos funcional
✓ Transacciones atómicas y auditadas
✓ Usuarios pueden ganar y consultar besitos
✓ Daily reward implementado

## Referencias
### 4.1 Economía de Besitos

La economía de besitos es el sistema circulatorio de DianaBot. Su diseño determina la salud del ecosistema completo.

**Principios de Diseño Económico**

Una economía virtual saludable balancea tres flujos: entrada (earning), circulación (spending) y sumideros (sinks). DianaBot necesita mantener a los usuarios con suficientes besitos para sentir progreso, pero no tantos que pierdan valor.

Las fuentes de entrada de besitos incluyen:

Recompensas diarias automáticas: 10 besitos por día simplemente por iniciar sesión. Esto asegura que usuarios inactivos puedan regresar y tener algo para gastar.

Misiones completadas: 20-50 besitos según complejidad. Las misiones diarias otorgan menos, las semanales más, las narrativas especiales aún más.

Trivias correctas: 5-15 besitos dependiendo de dificultad y tiempo de respuesta.

Reacciones en canales: 2 besitos por reaccionar a publicaciones específicas (limitado a 3 por día para prevenir farming).

Achievements desbloqueados: 50-200 besitos según rareza del logro.

Los sumideros de besitos incluyen:

Tienda virtual: Items cosméticos, pistas narrativas, power-ups temporales.

Desbloqueo de fragmentos premium: Ciertos fragmentos pueden desbloquearse con besitos como alternativa a requisitos complejos.

Subastas: Usuarios compiten por items exclusivos.

Regalos a otros usuarios: Mecánica social que consume besitos del donante.

**Prevención de Inflación**

Para prevenir que besitos pierdan valor con el tiempo, implementamos:

Límites de farming: Cada fuente de besitos tiene caps diarios o semanales. No puedes ganar infinitos besitos repitiendo trivias.

Besitos que expiran: Los besitos "bonus" obtenidos de eventos especiales expiran en 30 días si no se usan. Esto incentiva gasto activo.

Items de alto valor: La tienda siempre ofrece items premium caros (500-1000 besitos) para que usuarios avanzados tengan objetivos de ahorro.

Impuestos en subastas: Las subastas cobran una pequeña comisión del 10% que se elimina del sistema, actuando como sumidero.

**Transacciones y Auditoría**

Cada transacción de besitos genera un registro inmutable en la tabla `transactions`. Esto permite:

Auditoría completa del flujo de besitos de cada usuario.
Detección de patrones anómalos (usuarios ganando besitos demasiado rápido).
Análisis de qué fuentes son más populares y efectivas.
Rollback en caso de bugs que otorguen besitos incorrectamente.

Las transacciones usan locks de base de datos para prevenir condiciones de carrera. Cuando un usuario intenta gastar 50 besitos, usamos:

```python
with transaction.atomic():
    balance = UserBalance.objects.select_for_update().get(user_id=user_id)
    if balance.besitos >= 50:
        balance.besitos -= 50
        balance.save()
        # proceder con la compra
    else:
        # fondos insuficientes
```

El `select_for_update()` asegura que nadie más puede modificar ese balance hasta que la transacción complete.