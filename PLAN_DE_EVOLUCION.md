# Documento de Diseño Técnico y Plan de Evolución: DianaBot

## 1. Objetivo del Documento

Este documento es el resultado de una investigación técnica exhaustiva y sirve como **plan maestro** para evolucionar el código base de DianaBot desde su estado actual (un esqueleto funcional) hasta la arquitectura objetivo descrita en la documentación del proyecto. Contiene las especificaciones de diseño, las definiciones de componentes y los planes de acción necesarios para que un equipo de desarrollo implemente un sistema robusto, escalable y mantenible.

---

## 2. Fase 1: Especificación de la Fundación del Sistema

### 2.1. Especificación de Modelos de Datos (`database/models.py`)

```python
# /data/data/com.termux/files/home/repos/DianaBotFinal/database/models.py
# -*- coding: utf-8 -*-

from sqlalchemy import (
    create_engine, Column, Integer, String, BigInteger, Boolean, DateTime,
    Text, ForeignKey, UniqueConstraint, Index, ARRAY, Numeric
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# --- Core User and Admin Models ---

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    language_code = Column(String(10))
    is_premium = Column(Boolean, default=False)
    is_bot = Column(Boolean, default=False)
    user_state = Column(String(50), default='free', index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    balance = relationship("UserBalance", back_populates="user", uselist=False, cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")

class AdminUser(Base):
    __tablename__ = 'admin_users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='admin', index=True)
    is_active = Column(Boolean, default=True, index=True)
    permissions = Column(JSONB)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# --- Gamification Models ---

class UserBalance(Base):
    __tablename__ = 'user_balances'
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    besitos = Column(Integer, nullable=False, default=0)
    lifetime_besitos = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="balance")

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    transaction_type = Column(String(50), nullable=False)
    source = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    item_key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    item_type = Column(String(50), nullable=False, index=True)
    rarity = Column(String(50), default='common', index=True)
    price_besitos = Column(Integer, default=0)
    metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserInventory(Base):
    __tablename__ = 'user_inventory'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey('items.id', ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, default=1)
    acquired_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint('user_id', 'item_id', name='_user_item_uc'),)

class Mission(Base):
    __tablename__ = 'missions'
    id = Column(Integer, primary_key=True)
    mission_key = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    mission_type = Column(String(50), nullable=False, index=True)
    recurrence = Column(String(50), nullable=False)
    requirements = Column(JSONB, nullable=False)
    rewards = Column(JSONB, nullable=False)
    expiry_date = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserMission(Base):
    __tablename__ = 'user_missions'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    mission_id = Column(Integer, ForeignKey('missions.id'), primary_key=True)
    status = Column(String(50), nullable=False, index=True)
    progress = Column(JSONB)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(DateTime(timezone=True))

class Achievement(Base):
    __tablename__ = 'achievements'
    id = Column(Integer, primary_key=True)
    achievement_key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    icon_emoji = Column(String(50))
    points = Column(Integer, default=0, index=True)
    reward_besitos = Column(Integer, default=0)
    reward_item_id = Column(Integer, ForeignKey('items.id'))
    unlock_conditions = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserAchievement(Base):
    __tablename__ = 'user_achievements'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), primary_key=True)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    progress = Column(JSONB)

class Auction(Base):
    __tablename__ = 'auctions'
    auction_id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False, index=True)
    auction_type = Column(String(50), nullable=False, default='standard')
    start_price = Column(Integer, nullable=False, default=0)
    current_bid = Column(Integer, nullable=False, default=0)
    current_bidder_id = Column(BigInteger, ForeignKey('users.telegram_id'))
    winner_id = Column(BigInteger, ForeignKey('users.telegram_id'))
    status = Column(String(50), nullable=False, default='active', index=True)
    start_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)
    min_bid_increment = Column(Integer, nullable=False, default=10)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Bid(Base):
    __tablename__ = 'bids'
    bid_id = Column(Integer, primary_key=True)
    auction_id = Column(Integer, ForeignKey('auctions.auction_id'), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    __table_args__ = (UniqueConstraint('auction_id', 'user_id', 'amount', name='_auction_user_amount_uc'),)

# --- Narrative and Content Models ---

class NarrativeFragment(Base):
    __tablename__ = 'narrative_fragments'
    id = Column(Integer, primary_key=True)
    # Esta tabla necesita ser completada con las columnas de las migraciones.
    # Por ahora, se incluye el campo 'is_secret' como ejemplo.
    is_secret = Column(Boolean, default=False)

class SecretCode(Base):
    __tablename__ = 'secret_codes'
    id = Column(Integer, primary_key=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    fragment_key = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserSecretDiscovery(Base):
    __tablename__ = 'user_secret_discoveries'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    secret_code_id = Column(Integer, ForeignKey('secret_codes.id'), index=True)
    fragment_key = Column(String(100), nullable=False, index=True)
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())

# --- Admin & Channel Models ---

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False, index=True)
    subscription_type = Column(String(50), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    payment_reference = Column(String(255))
    auto_renew = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="subscriptions")

class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, unique=True, nullable=False, index=True)
    channel_type = Column(String(50), nullable=False, index=True)
    channel_username = Column(String(255))
    channel_title = Column(String(255))
    settings = Column(JSONB)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChannelPost(Base):
    __tablename__ = 'channel_posts'
    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, nullable=False, index=True)
    post_id = Column(BigInteger)
    post_type = Column(String(50), nullable=False, index=True)
    content = Column(Text)
    post_metadata = Column(JSONB)
    scheduled_for = Column(DateTime(timezone=True), index=True)
    published_at = Column(DateTime(timezone=True))
    status = Column(String(50), default='draft', index=True)
    recurrence = Column(String(50))
    is_protected = Column(Boolean, default=False)
    reaction_rewards = Column(JSONB)
    linked_mission_id = Column(Integer, ForeignKey('missions.id'))
    linked_fragment_id = Column(Integer, ForeignKey('narrative_fragments.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserReaction(Base):
    __tablename__ = 'user_reactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    post_id = Column(Integer, nullable=False, index=True)
    emoji = Column(String(50), nullable=False, index=True)
    rewarded_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (Index('idx_user_reactions_user_post_emoji', 'user_id', 'post_id', 'emoji'),)

# --- System & Config Models ---

class EventLog(Base):
    __tablename__ = 'event_logs'
    id = Column(Integer, primary_key=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSONB, nullable=False)
    telegram_id = Column(BigInteger, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class ConfigTemplate(Base):
    __tablename__ = 'config_templates'
    id = Column(Integer, primary_key=True)
    template_key = Column(String(100), unique=True, nullable=False, index=True)
    template_type = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    template_schema = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ConfigInstance(Base):
    __tablename__ = 'config_instances'
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey('config_templates.id'), index=True)
    instance_data = Column(JSONB, nullable=False)
    created_by = Column(Integer)
    status = Column(String(50), default='draft', index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class FeatureFlag(Base):
    __tablename__ = 'feature_flags'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=False)
    rollout_percentage = Column(Integer, default=0)
    beta_testers = Column(ARRAY(BigInteger))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ConversionFunnel(Base):
    __tablename__ = 'conversion_funnels'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    funnel_type = Column(String(50), nullable=False, index=True)
    stage_current = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_completed = Column(Boolean, default=False, index=True)
    entered_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True), onupdate=func.now(), index=True)
    completed_at = Column(DateTime(timezone=True))
    funnel_data = Column(JSONB)

# Nota: Las tablas de 'experiences' son complejas y se omiten aquí por brevedad,
# pero su estructura en la migración 018 es la referencia a seguir.
```

### 2.2. Especificación de Infraestructura como Código (`docker-compose.yml`)

```yaml
# /data/data/com.termux/files/home/repos/DianaBotFinal/docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: dianabot_postgres
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - dianabot_net

  mongodb:
    image: mongo:6.0
    container_name: dianabot_mongo
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"
    networks:
      - dianabot_net

  redis:
    image: redis:7
    container_name: dianabot_redis
    restart: always
    ports:
      - "6379:6379"
    networks:
      - dianabot_net

  app:
    build: .
    container_name: dianabot_app
    restart: always
    depends_on:
      - db
      - mongodb
      - redis
    env_file:
      - .env
    ports:
      - "8000:8000" # Para la API de FastAPI
    networks:
      - dianabot_net
    command: >
      sh -c "uvicorn api.main:app --host 0.0.0.0 --port 8000 &
             python bot/main.py"

  celery_worker:
    build: .
    container_name: dianabot_celery
    restart: always
    command: celery -A tasks.celery_app worker --loglevel=info
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - redis
      - db
    networks:
      - dianabot_net

volumes:
  postgres_data:
  mongo_data:

networks:
  dianabot_net:
    driver: bridge
```

### 2.3. Especificación de la Lógica de Conexión (`database/connection.py`)

```python
# /data/data/com.termux/files/home/repos/DianaBotFinal/database/connection.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import redis
from dotenv import load_dotenv

load_dotenv()

# --- PostgreSQL (SQLAlchemy) ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- MongoDB ---
MONGO_URL = os.getenv("MONGO_URL")
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client[os.getenv("MONGO_DB_NAME")]

def get_mongo():
    return mongo_db

# --- Redis ---
REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def get_redis():
    return redis_client
```

---

## 3. Fase 2: Diseño del Núcleo de Integración

### 3.1. Diseño del `CoordinadorCentral` y `TransactionManager`

**`core/coordinator.py`:**
```python
# Especificación para core/coordinator.py
class CoordinadorCentral:
    def __init__(self, narrative_service, besitos_service, ...):
        self.narrative_service = narrative_service
        # ...
        self.transaction_manager = TransactionManager()

    def tomar_decision(self, user_id: int, fragment_key: str, decision_id: str) -> dict:
        with self.transaction_manager.begin() as tx:
            # ... (lógica de orquestación como se detalló previamente) ...
            pass
```

**`core/transaction_manager.py`:**
```python
# Especificación para core/transaction_manager.py
class TransactionManager:
    def begin(self):
        return DistributedTransaction()

class DistributedTransaction:
    def __init__(self):
        self._rollback_stack = []
        self._commit_callbacks = []
    # ... (implementación del context manager y rollback como se detalló previamente) ...
```

### 3.2. Diseño del `EventBus` Asíncrono

**`core/event_bus.py`:**
```python
# Especificación para core/event_bus.py
class EventBus:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.handlers = defaultdict(list)
        # ... (implementación con Redis Pub/Sub y listener en background como se detalló) ...
```

**`core/event_handlers.py`:**
```python
# Especificación para core/event_handlers.py
def register_all_handlers():
    event_bus.subscribe('gamification.besitos_earned', achievements_service.check_besitos_milestones)
    # ... (mapa completo de eventos y suscriptores) ...
```

---

## 4. Fase 3 y 4: Plan de Refactorización y Especificación de Módulos

Se seguirán los planes detallados en la investigación anterior, moviendo la lógica de los handlers al `CoordinadorCentral` y completando la implementación de los servicios en los directorios `modules/` para que utilicen los modelos de datos y componentes de integración especificados.

---

## 5. Fase 5: Plan de Pruebas de Integración

Se implementarán escenarios de prueba en `pytest` que validen los flujos de extremo a extremo, como se describió en la investigación, para asegurar que la arquitectura funciona de manera cohesiva. Se probarán específicamente las transacciones con rollback y la comunicación por eventos.
