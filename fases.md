# DianaBot - Plan de Implementación por Fases

## Introducción

Este documento detalla el plan de implementación progresiva de DianaBot, un sistema integral que combina narrativa inmersiva, gamificación y administración de canales para Telegram. El plan se divide en 6 fases principales, cada una construida sobre la anterior, comenzando con la funcionalidad más básica y avanzando hacia un sistema completo con panel de administración.

## Fase 1: Bot Básico con Comando Start y Registro de Usuarios (Semanas 1-2)

### Objetivos Centrales
- Crear un bot funcional de Telegram que responda al comando `/start`
- Implementar el registro de usuarios en la base de datos
- Configurar la estructura básica del proyecto
- Establecer la infraestructura técnica

### Pasos de Implementación Técnica

#### 1. Estructura Básica del Bot
- Crear la aplicación principal del bot con python-telegram-bot
- Implementar el handler del comando `/start`
- Configurar la conexión con la base de datos PostgreSQL
- Crear el modelo de usuario básico y la conexión ORM

#### 2. Modelos de Base de Datos
```python
# Modelo de usuario con información básica
class User(Base):
    user_id = Column(BigInteger, primary_key=True, index=True)
    telegram_username = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True))
    user_state = Column(String(50), default='free')
```

#### 3. Handlers de Comandos Básicos
- `/start` - Registrar usuario y mostrar mensaje de bienvenida
- `/help` - Mostrar comandos disponibles
- Implementar manejo básico de errores

#### 4. Configuración de Infraestructura
- Completar la configuración de Docker para todos los servicios (PostgreSQL, MongoDB, Redis)
- Configurar variables de entorno
- Implementar sistema básico de logging
- Crear sistema de migración de base de datos (Alembic)

#### 5. Flujo de Registro de Usuarios
1. El usuario envía el comando `/start` al bot
2. El bot verifica si el usuario existe en la base de datos
3. Si es un nuevo usuario, se crea un registro en la tabla `users`
4. Envía un mensaje de bienvenida con información básica sobre DianaBot

### Características Clave a Implementar
- Bot responde al comando `/start`
- Registro de usuarios en PostgreSQL
- Sistema básico de conexión y ORM
- Respuestas simples de mensajes
- Manejo de errores y logging

### Criterios de Éxito
- El bot inicia y responde al comando `/start`
- Los nuevos usuarios se registran en la base de datos
- El logging básico está funcionando
- La conexión con la base de datos se establece correctamente
- El entorno de desarrollo está completamente configurado

### Resultados Entregables
- Bot funcional con comando `/start`
- Sistema de registro de usuarios
- Esquema básico de base de datos
- Configuración de Docker
- Configuración del entorno de desarrollo

---

## Fase 2: Sistema Narrativo Central con Fragmentos Simples (Semanas 3-4)

### Objetivos Centrales
- Implementar el motor narrativo básico
- Crear un sistema simple de historia ramificada
- Permitir a los usuarios progresar a través de fragmentos narrativos
- Implementar mecánicas básicas de toma de decisiones

### Pasos de Implementación Técnica

#### 1. Modelos de Base de Datos Narrativa
- Crear modelos `NarrativeLevel` y `NarrativeFragment` en PostgreSQL
- Implementar relaciones entre niveles y fragmentos
- Crear modelo `UserNarrativeProgress` para rastrear el progreso del usuario

#### 2. Desarrollo del Motor Narrativo
- Crear el motor narrativo central para manejar el flujo de la historia
- Implementar sistema de carga de fragmentos
- Crear manejo de decisiones para historias ramificadas
- Implementar gestión de estado narrativo

#### 3. Contenido Narrativo en MongoDB
- Configurar colección MongoDB para contenido narrativo
- Crear estructura de documentos para fragmentos narrativos
- Implementar sistema de recuperación de contenido
- Almacenar texto narrativo, decisiones y consecuencias

#### 4. Integración con Telegram
- Crear comando `/story` o `/narrative` para acceder a la historia
- Implementar teclados inline para elecciones de decisiones
- Mostrar fragmentos narrativos con formato apropiado
- Manejar consultas de callback para selección de decisiones

#### 5. Seguimiento de Progreso
- Rastrear la posición narrativa actual del usuario
- Registrar decisiones tomadas por los usuarios
- Implementar funcionalidad de guardar/cargar
- Almacenar banderas y variables narrativas

### Características Clave a Implementar
- Comando `/story` para acceder a la narrativa
- Historia ramificada simple (3-5 fragmentos)
- Toma de decisiones con teclados inline
- Seguimiento y persistencia de progreso
- Contenido almacenado en MongoDB con referencias PostgreSQL

### Componentes Técnicos
1. **Modelo de Fragmento Narrativo**: Almacenar metadatos de fragmentos en PostgreSQL (fragment_key, level_id, title, unlock_conditions)
2. **Contenido MongoDB**: Almacenar contenido narrativo real (texto, decisiones, consecuencias, medios)
3. **Rastreador de Progreso**: Almacenar posición actual del usuario y elecciones realizadas
4. **Manejador de Decisiones**: Procesar elecciones del usuario y determinar el siguiente fragmento
5. **Motor Narrativo**: Lógica central para flujo y estado de la historia

### Criterios de Éxito
- Los usuarios pueden iniciar y progresar a través de una narrativa simple
- Las elecciones conducen a diferentes rutas de la historia
- El progreso del usuario se guarda y se puede reanudar
- El contenido narrativo se carga correctamente desde MongoDB
- El flujo de la historia funciona sin errores

### Resultados Entregables
- Motor narrativo funcional
- 3-5 fragmentos narrativos interconectados
- Sistema de toma de decisiones
- Seguimiento y persistencia de progreso
- Integración con comandos del bot de Telegram

---

## Fase 3: Sistema de Gamificación Básico con Besitos (Semanas 5-6)

### Objetivos Centrales
- Implementar el sistema económico de "besitos"
- Crear sistema básico de inventario para ítems
- Implementar seguimiento de transacciones
- Integrar gamificación con el sistema narrativo

### Pasos de Implementación Técnica

#### 1. Modelos del Sistema de Besitos
- Crear modelo `UserBalance` para rastrear besitos
- Crear modelo `Transaction` para rastrear todos los movimientos de besitos
- Implementar tipos de transacciones (ganar/gastar/regalar)

#### 2. Sistema Básico de Ítems
- Crear modelo `Item` para ítems coleccionables
- Crear modelo `UserInventory` para rastrear los ítems del usuario
- Implementar categorías básicas de ítems

#### 3. Mecánicas Económicas
- Recompensas diarias de besitos para usuarios activos
- Recompensas de besitos por completar fragmentos narrativos
- Sistema simple de gasto (comprar ítems básicos)
- Seguimiento de historial de transacciones

#### 4. Integración con Narrativa
- Los fragmentos narrativos otorgan besitos como recompensa
- Las elecciones narrativas pueden desbloquear ítems especiales
- La posesión de ítems puede afectar las opciones narrativas

#### 5. Comandos para Usuarios
- `/balance` - Mostrar saldo actual de besitos
- `/inventory` - Mostrar los ítems del usuario
- `/shop` - Acceder a la tienda de ítems básicos
- `/daily` - Reclamar recompensa diaria de besitos

### Características Clave a Implementar
- Seguimiento de saldo de besitos por usuario
- Sistema de transacciones con registro de auditoría
- Sistema de inventario de ítems básicos
- Sistema de recompensas diarias (10 besitos por día)
- Integración narrativa-gamificación
- Tienda simple para comprar ítems

### Componentes Técnicos
1. **Saldo de Besitos**: Rastrear besitos por usuario con validación (sin saldos negativos)
2. **Registro de Transacciones**: Registro completo de todo movimiento de besitos
3. **Sistema de Ítems**: Marco básico de ítems con categorías
4. **Interfaz de Tienda**: Interfaz de Telegram para comprar ítems
5. **Sistema de Recompensas**: Recompensas automáticas por finalización de narrativa y login diario

### Criterios de Éxito
- Los usuarios tienen saldos de besitos que se rastrean
- Las recompensas diarias se reclaman automáticamente
- La finalización de narrativa otorga besitos
- Se mantiene un historial de transacciones
- Los usuarios pueden comprar ítems de la tienda
- La integración con la narrativa funciona correctamente

### Resultados Entregables
- Sistema económico de besitos funcionando
- Seguimiento y auditoría de transacciones
- Sistema de inventario de ítems
- Mecanismo de recompensa diaria
- Integración de tienda básica
- Integración narrativa-gamificación

---

## Fase 4: Sistema de Gestión de Canales y VIP (Semanas 7-8)

### Objetivos Centrales
- Implementar sistema de suscripción VIP
- Crear control de acceso a canales
- Implementar validación de suscripción
- Integrar funciones VIP con narrativa y gamificación

### Pasos de Implementación Técnica

#### 1. Modelos de Suscripción
- Crear modelo `Subscription` para rastrear estado VIP
- Implementar tipos de suscripción (mensual, anual)
- Agregar seguimiento de estado de suscripción (activa, expirada, cancelada)

#### 2. Modelos de Gestión de Canales
- Crear modelo `Channel` para rastrear canales gestionados
- Implementar clasificación de tipo de canal (gratuito, VIP)
- Configurar permisos de acceso a canales

#### 3. Integración con Telegram
- Implementar verificación de suscripción con `getChatMember`
- Crear invitación automatizada al canal VIP para nuevos suscriptores
- Implementar eliminación automática del canal VIP cuando expira la suscripción

#### 4. Acceso a Contenido VIP
- Restringir ciertos fragmentos narrativos a usuarios VIP
- Implementar recompensas de besitos más altas para usuarios VIP
- Crear ítems y beneficios exclusivos para VIP

#### 5. Gestión de Suscripciones
- Comando `/subscribe` para iniciar proceso de suscripción
- Comando `/subscription` para consultar estado de suscripción
- Manejo automatizado de expiración
- Gestión de renovación

### Características Clave a Implementar
- Sistema de seguimiento de suscripción VIP
- Control de acceso a canales
- Invitación/remoción automatizada del canal VIP
- Contenido narrativo exclusivo para VIP
- Recompensas mejoradas para usuarios VIP
- Monitoreo de estado de suscripción

### Componentes Técnicos
1. **Motor de Suscripción**: Rastrear y monitorear suscripciones de usuarios
2. **Validador de Canales**: Verificar membresía de usuarios en canales requeridos
3. **Control de Acceso**: Restringir contenido basado en estado de suscripción
4. **Contenido VIP**: Fragmentos narrativos y beneficios especiales
5. **Comandos de Gestión**: Gestión de suscripción para usuarios
6. **Sistema de Notificaciones**: Recordatorios y actualizaciones automatizados de estado

### Criterios de Éxito
- Los usuarios pueden suscribirse y recibir estado VIP
- El acceso al canal VIP se gestiona correctamente
- El contenido VIP solo es accesible para usuarios VIP
- La expiración de suscripción se maneja automáticamente
- Los usuarios VIP reciben beneficios mejorados
- Los usuarios no VIP están restringidos del contenido premium

### Resultados Entregables
- Sistema de gestión de suscripción funcionando
- Control de acceso a canales
- Sistema de restricción de contenido VIP
- Validación y monitoreo de suscripción
- Integración con sistemas de narrativa y gamificación

---

## Fase 5: Funciones Avanzadas - Trivias, Subastas y Logros (Semanas 9-10)

### Objetivos Centrales
- Implementar sistema de logros con insignias
- Crear sistema de trivias con preguntas sobre la narrativa
- Implementar sistema de subastas para ítems raros
- Mejorar gamificación con mecánicas avanzadas

### Pasos de Implementación Técnica

#### 1. Sistema de Logros
- Crear modelo `Achievement` con condiciones de desbloqueo
- Crear modelo `UserAchievement` para rastrear logros desbloqueados
- Implementar verificación y mecánicas de recompensa
- Crear sistema de visualización de logros

#### 2. Sistema de Trivias
- Crear modelo `TriviaQuestion` en MongoDB para almacenamiento de preguntas
- Implementar respuestas de trivias con tiempo límite
- Crear categorías de trivias relacionadas con la narrativa
- Implementar recompensas de trivias (besitos, ítems, pistas)

#### 3. Sistema de Subastas
- Crear modelo `Auction` para rastrear subastas activas
- Implementar mecánicas de puja
- Crear gestión de ítems de subasta
- Implementar temporización y selección de ganadores

#### 4. Gamificación Avanzada
- Misiones diarias y semanales con requisitos específicos
- Eventos especiales y desafíos limitados en el tiempo
- Sistemas de logros progresivos
- Elementos sociales (tablas de clasificación, sistema de amigos)

#### 5. Comandos para Usuarios
- `/achievements` - Ver logros desbloqueados
- `/trivia` - Participar en trivia diaria
- `/auctions` - Ver subastas activas
- `/missions` - Ver misiones disponibles
- `/leaderboard` - Ver usuarios principales

### Características Clave a Implementar
- Sistema de logros con condiciones y recompensas
- Sistema de trivias con límites de tiempo y recompensas
- Sistema de subastas para ítems raros
- Misiones diarias/semanales con dificultad variable
- Tablas de clasificación y clasificaciones
- Gestión avanzada de inventario

### Componentes Técnicos
1. **Motor de Logros**: Rastrear y validar progreso de logros
2. **Sistema de Trivias**: Gestión de preguntas y validación de respuestas
3. **Sistema de Subastas**: Puja, temporización y selección de ganadores
4. **Sistema de Misiones**: Gestión de tareas diarias/semanales
5. **Sistema de Tabla de Clasificación**: Clasificación y funciones de competencia
6. **Gestión de Eventos**: Eventos especiales limitados en el tiempo

### Criterios de Éxito
- Los usuarios pueden desbloquear logros con recompensas significativas
- El sistema de trivias funciona con límites de tiempo y recompensas
- El sistema de subastas maneja pujas y selección de ganadores
- El sistema de misiones proporciona engagement diario
- Las tablas de clasificación muestran correctamente a los usuarios principales
- Los sistemas se integran bien con las mecánicas existentes

### Resultados Entregables
- Sistema de logros completo con recompensas
- Sistema de trivias funcional
- Sistema de subastas operativo
- Sistema de misiones diarias/semanales
- Tablas de clasificación de usuarios
- Mecánicas de gamificación mejoradas

---

## Fase 6: Panel de Administración y Configuración Unificada (Semanas 11-12)

### Objetivos Centrales
- Crear panel administrativo integral
- Implementar sistema de configuración unificada
- Proporcionar herramientas para creadores de contenido
- Habilitar monitoreo y gestión en tiempo real

### Pasos de Implementación Técnica

#### 1. Backend del Panel de Administración (FastAPI)
- Crear aplicación FastAPI para interfaz administrativa
- Implementar autenticación basada en JWT para administradores
- Crear endpoints API para todas las funciones de gestión
- Implementar control de acceso basado en roles (admin, creador de contenido, moderador)

#### 2. Gestor de Configuración
- Crear modelo `ConfigTemplate` para plantillas de contenido
- Crear modelo `ConfigInstance` para configuraciones específicas
- Implementar sistema de configuración unificado que afecta a todos los módulos
- Crear sistema de validación para integridad de configuración

#### 3. Frontend del Panel
- Crear plantillas HTML con Jinja2
- Implementar UI responsive con Tailwind CSS
- Crear editores visuales para flujos narrativos
- Implementar interfaces de gestión de contenido

#### 4. Monitoreo y Analíticas
- Crear panel de métricas en tiempo real
- Implementar seguimiento de actividad de usuarios
- Crear analíticas de rendimiento de contenido
- Implementar monitoreo de salud del sistema

#### 5. Herramientas de Creación de Contenido
- Editor de narrativas con interfaz visual de flujos
- Herramientas de configuración de gamificación
- Sistema de programación de publicaciones en canales
- Creador de logros y misiones

#### 6. Funciones Administrativas
- Interfaz de gestión de usuarios
- Gestión de suscripciones
- Flujos de trabajo de aprobación de contenido
- Controles de configuración del sistema

### Características Clave a Implementar
- Sistema de autenticación admin completa
- Sistema de configuración unificada que abarca todos los módulos
- Editor visual de narrativas
- Panel de analíticas en tiempo real
- Sistema de gestión de contenido
- Gestión de usuarios y suscripciones
- Monitoreo de rendimiento
- Sistema de validación de configuración

### Componentes Técnicos
1. **Sistema de Autenticación**: Login seguro para administradores con tokens JWT
2. **Motor de Configuración**: Sistema unificado que gestiona todos los elementos del juego
3. **Editor de Contenido**: Herramientas visuales para crear narrativas y gamificación
4. **Motor de Analíticas**: Seguimiento en tiempo real del engagement del usuario
5. **Gestión de Usuarios**: Herramientas para gestionar usuarios y suscripciones
6. **Flujo de Contenido**: Sistemas de aprobación y publicación de contenido

### Criterios de Éxito
- Los administradores pueden iniciar sesión de forma segura en el panel
- El sistema de configuración gestiona todos los aspectos del juego
- Los creadores de contenido pueden crear y modificar contenido fácilmente
- Las analíticas en tiempo real proporcionan información útil
- Todos los módulos se pueden configurar desde la interfaz unificada
- Las tareas administrativas se pueden realizar con eficiencia

### Resultados Entregables
- Panel administrativo completo con autenticación
- Sistema de gestión de configuración unificada
- Herramientas de creación de contenido visual
- Panel de analíticas en tiempo real
- Herramientas de gestión de usuarios y suscripciones
- Flujos de trabajo de aprobación y publicación de contenido

---

## Resumen de la Línea de Tiempo de Implementación

| Fase | Duración | Enfoque | Entregable Clave |
|------|----------|---------|------------------|
| Fase 1 | Semanas 1-2 | Funcionalidad Básica del Bot | Comando `/start` funcional y registro de usuarios |
| Fase 2 | Semanas 3-4 | Sistema Narrativo | Historia ramificada simple con 3-5 fragmentos |
| Fase 3 | Semanas 5-6 | Gamificación | Economía de besitos y sistema de inventario básico |
| Fase 4 | Semanas 7-8 | Gestión de Canales | Sistema de suscripción VIP y control de acceso |
| Fase 5 | Semanas 9-10 | Funciones Avanzadas | Trivias, subastas, logros, misiones |
| Fase 6 | Semanas 11-12 | Sistema de Administración | Panel completo y configuración unificada |

## Directrices de Desarrollo

### Estrategia de Pruebas
- Fase 1-2: Pruebas unitarias para funcionalidad básica
- Fase 3-4: Pruebas de integración para características entre módulos
- Fase 5-6: Pruebas E2E y pruebas de rendimiento

### Consideraciones de Seguridad
- Validación de entradas en todos los niveles
- Limitación de tasa para todos los endpoints
- Manejo seguro de datos de callback
- Autenticación y autorización adecuadas

### Planificación de Escalabilidad
- Indexación de base de datos para rendimiento
- Caché Redis para datos accedidos frecuentemente
- Procesamiento asincrónico con Celery para operaciones pesadas

### Calidad del Código
- Anotaciones de tipo en todo el códigobase
- Manejo de errores integral
- Logging y monitoreo adecuados
- Formato de código consistente con linters