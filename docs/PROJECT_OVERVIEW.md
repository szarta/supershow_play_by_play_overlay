# Project Overview

## Directory Structure

```
supershow_play_by_play_overlay/
├── src/
│   ├── __init__.py
│   ├── controller/           # Controller desktop app
│   │   └── __init__.py
│   ├── production_view/      # Production overlay app
│   │   └── __init__.py
│   └── shared/              # Shared modules
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       └── models.py         # Data models
├── data/
│   ├── .gitkeep
│   └── images/              # Card images (not in git)
├── recordings/              # Match recordings (not in git)
│   └── .gitkeep
├── logs/                    # Application logs (not in git)
│   └── .gitkeep
├── docs/                    # Additional documentation
│   └── PROJECT_OVERVIEW.md
├── config.toml.example      # Configuration template
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
├── DESIGN.md               # Full design document
├── grid.txt                # Original design notes
├── README.md               # Project readme
└── LICENSE                 # MIT license
```

## Next Steps

### Phase 1: Core Infrastructure

1. **Sync Module** (`src/shared/sync.py`)
   - Database sync from get-diced.com API
   - Image sync with hash-based manifest
   - Progress tracking and error handling

2. **MQTT Module** (`src/shared/mqtt_client.py`)
   - MQTT connection management
   - Topic publishing/subscribing
   - Reconnection logic

3. **Database Module** (`src/shared/database.py`)
   - SQLite connection management
   - Card queries
   - Database update transactions

4. **Controller App** (`src/controller/main.py`)
   - Basic tkinter UI
   - Match setup interface
   - MQTT publishing

5. **Production View** (`src/production_view/main.py`)
   - Basic tkinter overlay
   - MQTT subscription
   - Minimal collapsed state

## Module Responsibilities

### shared/config.py
- Load and parse config.toml
- Provide typed configuration objects
- Validate configuration values

### shared/models.py
- Data classes for all domain models
- Type definitions and enums
- Serialization/deserialization helpers

### shared/sync.py
- API client for get-diced.com
- Database manifest checking and download
- Image manifest checking and download
- Hash verification for images

### shared/mqtt_client.py
- MQTT connection wrapper
- Publish/subscribe helpers
- Topic constants
- Reconnection logic

### shared/database.py
- SQLite connection management
- Card CRUD operations
- Transaction management
- Query builders

### controller/main.py (to be created)
- Main controller application entry point
- tkinter UI layout
- Match state management
- MQTT publishing on state changes

### production_view/main.py (to be created)
- Main production view entry point
- Minimal overlay UI (collapsed state)
- Expandable sections
- Card preview popups
- MQTT subscription and UI updates

## Development Workflow

1. Set up virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

2. Copy and configure:
```bash
cp config.toml.example config.toml
# Edit config.toml with your settings
```

3. Develop modules in phases:
   - Phase 1: Sync and MQTT infrastructure
   - Phase 2: Controller UI and card management
   - Phase 3: Production view interactivity
   - Phase 4: Match recording
   - Phase 5+: Polish and features

4. Run tests:
```bash
pytest tests/
```

5. Format code:
```bash
black src/
flake8 src/
```

## Current Status

✅ Project structure created
✅ Configuration system (config.py)
✅ Data models (models.py)
✅ README and documentation
✅ Database module (database.py) - Complete
✅ Sync module (sync.py) - Complete
✅ MQTT client (mqtt_client.py) - Complete
✅ Example usage scripts
⏳ Controller app (next)
⏳ Production view app
⏳ Match recorder

### Completed Modules

**database.py** (474 lines)
- SQLite connection management
- Table creation and initialization
- Card CRUD operations (get by UUID, name, search)
- Competitor and main deck card queries
- Transaction support for database replacement
- Context manager support

**sync.py** (506 lines)
- API client for get-diced.com
- Database manifest checking and download
- Image manifest checking and download
- SHA256 hash verification for images
- Progress callbacks for UI integration
- Local manifest management for incremental sync

**config.py** (232 lines)
- TOML configuration file parsing
- Typed configuration classes for all settings
- Easy access to MQTT, sync, database, UI settings

**models.py** (169 lines)
- Data classes for all domain models
- Enums for roll types, attack types, play order
- Card, PlayerState, MatchState models
- Manifest models for sync

**mqtt_client.py** (485 lines)
- MQTT client wrapper with paho-mqtt
- Connection management with auto-reconnection
- Publish/subscribe methods with QoS support
- Topic constants for all supershow/* topics
- Callback system for connection, disconnection, and messages
- Exponential backoff for reconnection
- Context manager support
- Helper functions for controller and production clients

### Testing

Run the example script to test database and sync:
```bash
python -m src.shared.example_usage
```

See `docs/TESTING_SYNC.md` for detailed testing instructions.

Run the MQTT example to test MQTT connectivity (requires running broker):
```bash
# Start a local MQTT broker
docker run -it -p 1883:1883 eclipse-mosquitto:2

# In another terminal
python -m src.shared.example_mqtt
```
