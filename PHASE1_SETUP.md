# DianaBot - Fase 1 Setup

## Estado Actual
La implementación de la Fase 1 está completa. El bot básico está listo para funcionar con:

- ✅ Bot de Telegram con python-telegram-bot
- ✅ Modelo de usuario en PostgreSQL
- ✅ Registro automático de usuarios
- ✅ Comandos `/start`, `/help`, `/stats`
- ✅ Gestión básica de estado de usuario

## Próximos Pasos para Ejecutar

### 1. Configurar Variables de Entorno
```bash
cp .env.example .env
# Edita .env y configura:
# - TELEGRAM_BOT_TOKEN (obtén de @BotFather)
# - Credenciales de base de datos
```

### 2. Configurar Base de Datos
```bash
# Asegúrate de que PostgreSQL esté ejecutándose
sudo systemctl start postgresql

# Crea la base de datos y usuario
sudo -u postgres psql
CREATE DATABASE dianabot;
CREATE USER dianabot_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE dianabot TO dianabot_user;
\q

# Ejecuta migraciones
python run_migrations.py
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar el Bot
```bash
python bot/main.py
```

## Comandos Disponibles

- `/start` - Registra al usuario y da la bienvenida
- `/help` - Muestra comandos disponibles
- `/stats` - Muestra estadísticas del usuario

## Estructura de la Fase 1

```
DianaBot/
├── bot/
│   ├── main.py              # Entry point del bot
│   └── handlers/
│       ├── start.py         # Handler /start
│       ├── help.py          # Handler /help
│       └── stats.py         # Handler /stats
├── database/
│   ├── models.py            # Modelo User
│   ├── connection.py        # Conexiones DB
│   └── migrations/
│       └── 002_create_users.sql
├── core/
│   └── user_state.py        # Gestión de estado
└── config/
    └── settings.py          # Configuración
```

## Pruebas

Ejecuta las pruebas básicas:
```bash
python test_bot.py
```

## Siguientes Fases

Una vez que la Fase 1 esté funcionando, continúa con:
- Fase 2: Sistema de mensajes básico
- Fase 3: Narrativas interactivas
- Fase 4: Sistema de gamificación

Consulta `docs/HOJA_DE_RUTA.md` para el plan completo.