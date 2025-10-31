# Análisis Técnico Detallado del Proyecto DianaBot

## 1. Estructura General del Proyecto

DianaBot es un sistema de Telegram con narrativa ramificada, gamificación y administración de contenido. El proyecto sigue una arquitectura modular con un enfoque en la narrativa interactiva y la economía de besitos (sistema de puntos).

## 2. Módulos del Sistema

### 2.1. Módulos Funcionales
- **bot/**: Contiene el punto de entrada y handlers del bot de Telegram
- **core/**: Componentes centrales como Event Bus y Config Manager
- **modules/narrative/**: Sistema de narrativa ramificada
- **modules/gamification/**: Sistema de gamificación con besitos, misiones, inventario, logros y subastas
- **modules/admin/**: Gestión de canales VIP y suscripciones
- **database/**: Modelos, conexiones a bases de datos y migraciones
- **api/**: API REST para panel administrativo
- **config/**: Configuración y settings
- **docker/**: Configuración de contenedores
- **tasks/**: Tareas programadas
- **utils/**: Utilidades comunes

### 2.2. Submódulos de Gamificación
- **besitos.py**: Sistema de economía de puntos "besitos"
- **missions.py**: Sistema de misiones y objetivos
- **inventory.py**: Sistema de inventario de objetos
- **achievements.py**: Sistema de logros y reconocimientos
- **auctions.py**: Sistema de subastas en tiempo real
- **trivias.py**: Sistema de preguntas y respuestas

### 2.3. Submódulos de Narrativa
- **engine.py**: Motor de narrativa ramificada
- **flags.py**: Sistema de flags narrativos
- **unlocks.py**: Sistema de desbloqueo condicional
- **secrets.py**: Sistema de descubrimiento de secretos
- **rewards.py**: Sistema de recompensas narrativas

## 3. Conexión y Configuración de Bases de Datos

### 3.1. PostgreSQL (SQLAlchemy)
- **Propósito**: Almacenamiento principal de datos estructurados
- **Modelos clave**:
  - `User`: Información de usuarios de Telegram
  - `UserBalance`: Saldo de besitos por usuario
  - `Transaction`: Historial de transacciones
  - `NarrativeLevel/Fragment`: Contenido narrativo estructurado
  - `UserNarrativeProgress`: Progreso narrativo por usuario
  - `Item/UserInventory`: Sistema de inventario
  - `Mission/UserMission`: Sistema de misiones
  - `Achievement/UserAchievement`: Sistema de logros
  - `Subscription`: Gestión de suscripciones VIP
  - `Channel/ChannelPost`: Gestión de canales
  - `Auction/Bid`: Sistema de subastas

### 3.2. MongoDB 
- **Propósito**: Almacenamiento de contenido narrativo dinámico y flexible
- **Colecciones clave**:
  - `narrative_content`: Contenido narrativo detallado con decisiones
  - `user_narrative_states`: Estados narrativos de usuarios
  - `trivia_questions`: Preguntas para sistema de trivia

### 3.3. Redis
- **Propósito**: Pub/Sub para Event Bus y caché de datos
- **Usos**:
  - Sistema de mensajes entre módulos (Event Bus)
  - Caché para verificación de membresía VIP
  - Almacenamiento temporal de datos

## 4. Sistema de Event Bus y Comunicación entre Módulos

### 4.1. Event Bus (core/event_bus.py)
- **Implementación**: Basado en Redis Pub/Sub
- **Funcionalidad**: Comunicación asíncrona entre módulos
- **Eventos comunes**:
  - `gamification.besitos_earned`: Se emite cuando un usuario gana besitos
  - `gamification.besitos_spent`: Se emite cuando un usuario gasta besitos
- **Patrón**: Patrón de observador con suscripción/desuscripción

### 4.2. Integración
- Los handlers de eventos se registran en `core/event_handlers.py`
- Se inicia en un hilo separado en `bot/main.py`
- Permite desacoplamiento entre módulos

## 5. Sistema de Gamificación

### 5.1. Sistema de Economía de Besitos
- **Modelo**: UserBalance y Transaction
- **Operaciones**: `grant_besitos()` y `spend_besitos()` con transacciones atómicas
- **Historial**: Seguimiento detallado de transacciones
- **Eventos**: Notificaciones a través del Event Bus

### 5.2. Sistema de Misiones
- **Tipos**: Diarias, semanales, narrativas, especiales
- **Requisitos y recompensas variables**
- **Progreso individual por usuario**

### 5.3. Sistema de Inventario
- **Modelo**: Items con diferentes tipos (narrative_key, collectible, power_up, etc.)
- **Rarezas**: común, raro, épico, legendario
- **Acumulación por usuario con cantidades**

### 5.4. Sistema de Logros
- **Criterios de desbloqueo variables**
- **Recompensas de puntos y besitos**
- **Progreso parcial para logros progresivos**

### 5.5. Sistema de Subastas
- **Tipos**: Estándar, holandés, silencioso
- **Puja en tiempo real**
- **Gestión automática de cierre y ganadores**

## 6. Sistema de Narrativa Ramificada

### 6.1. Motor de Narrativa
- **Arquitectura híbrida**: PostgreSQL para estructura y MongoDB para contenido
- **Capas de contenido**:
  - `NarrativeLevel`: Agrupaciones temáticas de fragmentos
  - `NarrativeFragment`: Unidades individuales de contenido narrativo
  - `FragmentContent`: Contenido detallado en MongoDB
  - `UserNarrativeProgress`: Progreso individual

### 6.2. Sistema de Decisiones
- **Contenido dinámico**: Condiciones basadas en flags narrativos
- **Variables interpoladas**: Cambian el contenido según el estado del usuario
- **Consecuencias**: Cambios en la narrativa y recompensas

### 6.3. Sistema de Desbloqueos
- **Condiciones variadas**: Requisitos de besitos, objetos, logros
- **Evaluación dinámica**: Se verifican al acceder al contenido

## 7. Sistema de Administración y Canales VIP

### 7.1. Sistema de Suscripciones
- **Tipos**: Mensual, anual, perpetua
- **Verificación**: Multi-capa (base de datos + membresía en canal)
- **Control de acceso**: Con cache de membresía

### 7.2. Gestión de Contenido
- **Publicación programada**: Posts con fechas de publicación específicas
- **Contenido VIP**: Restricciones basadas en tipo de suscripción
- **Sistema de canales**: Diferentes tipos (gratuito, VIP, anuncios)

### 7.3. Sistema de Reacciones y Recompensas
- **Reacciones con besitos**: Recompensas por interacción con contenido
- **Configuración dinámica**: Recompensas basadas en reacciones específicas

## 8. Configuración de Contenedores (Docker)

### 8.1. Servicios en docker-compose.yml
- **postgres** (puerto 5432): Base de datos principal
- **mongodb** (puerto 27017): Base de datos de contenido narrativo
- **redis** (puerto 6379): Caché y mensajería
- **app** (puerto 8000): API FastAPI
- **celery** (sin puerto): Workers para tareas asíncronas

### 8.2. Configuración del API
- **FastAPI**: Framework para la API REST
- **Endpoints**: Autenticación, configuración, usuarios, contenido, análisis, dashboard
- **Conexión a todas las bases de datos**

## 9. Sistema de Tareas Programadas

### 9.1. Tareas Programadas (tasks/scheduled.py)
- **Verificación de suscripciones**: Chequeo de expiraciones
- **Notificaciones**: Recordatorios de expiración
- **Gestión de canales**: Verificación y actualización de membresías
- **Publicación programada**: Contenido con fechas específicas
- **Cierre de subastas**: Subastas expiradas
- **Ejecución automática**: A través de workers (presumiblemente Celery)

## 10. Arquitectura General

El proyecto implementa una arquitectura de microservicios mediante contenedores Docker, con una base de datos híbrida (SQL para estructura, NoSQL para contenido), un sistema de eventos para comunicación entre componentes y una arquitectura modular que separa las responsabilidades del sistema en módulos especializados.

El bot de Telegram actúa como punto de entrada principal para los usuarios, mientras que la API REST permite la gestión administrativa y el dashboard web proporciona una interfaz para administradores. El sistema de tareas programadas se encarga de operaciones asíncronas que no requieren respuesta inmediata.