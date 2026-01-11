# Current Status - Supershow Overlay Project

**Last Updated**: 2026-01-10

## ✅ Completed Modules

### Phase 1: Core Infrastructure - COMPLETE

1. **Configuration System** (`src/shared/config.py` - 232 lines)
   - TOML configuration parsing
   - Typed dataclasses for all settings
   - MQTT, Sync, Database, UI configuration

2. **Data Models** (`src/shared/models.py` - 169 lines)
   - Card, PlayerState, MatchState models
   - Enums: RollType, AttackType, PlayOrder, CardType
   - Manifest models for sync

3. **Database Module** (`src/shared/database.py` - 490 lines)
   - SQLite connection management
   - Card CRUD operations (by UUID, name, search)
   - Competitor and main deck queries
   - Database replacement with ATTACH/DETACH outside transaction
   - Context manager support
   - **Status**: Tested and working with 5,562 cards synced

4. **Sync Module** (`src/shared/sync.py` - 501 lines)
   - API client for get-diced.com
   - Database manifest checking and download
   - Image manifest with SHA256 hash verification
   - Progress callbacks for UI integration
   - Incremental image sync
   - **Status**: Tested and working, 4,375 images pre-loaded

5. **MQTT Client Module** (`src/shared/mqtt_client.py` - 482 lines)
   - MQTTClient class with paho-mqtt
   - Auto-reconnection with exponential backoff (1-60s)
   - Publish/subscribe with QoS support
   - Topic constants for all 20+ supershow/* topics
   - Callback system (connection, disconnect, message)
   - Topic-specific handlers
   - Context manager support
   - **Status**: Implemented, committed, NOT YET TESTED

## 📝 Testing Scripts

1. **Database & Sync Example** (`src/shared/example_usage.py` - 150 lines)
   - Tests database connection
   - Syncs from get-diced.com API
   - Runs sample queries
   - **Status**: Fully tested and working

2. **MQTT Example** (`src/shared/example_mqtt.py` - 326 lines)
   - Basic pub/sub test
   - Match state publishing simulation
   - Topic helper demonstrations
   - Context manager test
   - **Status**: Ready to test, needs venv with paho-mqtt

## 📚 Documentation

- `README.md` - Project overview and quick start
- `DESIGN.md` - Full technical design with MQTT topics
- `docs/PROJECT_OVERVIEW.md` - Module responsibilities and status
- `docs/TESTING_SYNC.md` - Database and sync testing guide
- `docs/TESTING_MQTT.md` - MQTT testing guide (NEW)
- `docs/CURRENT_STATUS.md` - This file

## 🔧 Environment Setup

### Mosquitto Broker
- Installed via `sudo apt-get install mosquitto`
- Location: `/usr/sbin/mosquitto`
- Started with: `/usr/sbin/mosquitto -d`
- **Status**: Currently running (PID 23583)
- Tested with mosquitto_pub/mosquitto_sub - working

### Python Dependencies (requirements.txt)
```
paho-mqtt>=1.6.1
requests>=2.31.0
Pillow>=10.0.0
toml>=0.10.2
```

### What's Needed
- Create venv and install requirements.txt
- **NOT INSTALLED YET**: paho-mqtt (needed for MQTT tests)

## ⏭️ Next Steps

### Immediate: Test MQTT Module

1. Set up venv:
   ```bash
   cd ~/data/overlay_app
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Test MQTT:
   ```bash
   # Mosquitto is already running at /usr/sbin/mosquitto
   python -m src.shared.example_mqtt
   ```

3. Expected outcome:
   - Topic helpers test (no broker needed)
   - Basic pub/sub test (2 messages received)
   - Match state publishing test (controller → production simulation)
   - Context manager test

### After MQTT Testing: Build Controller App

Next phase is `src/controller/main.py`:
- tkinter UI for match management
- Competitor selection from database
- Match state management
- MQTT publishing on state changes
- Sync database/images on startup

## 🗂️ Git Status

- **Repository**: github.com:szarta/supershow_play_by_play_overlay.git
- **Branch**: main
- **Last Commit**: c49865b "Add MQTT client module with connection management and pub/sub"
- **Commits**: 2 total
  - 523f36f: Initial project structure, database, sync modules
  - c49865b: MQTT client module
- **Status**: All changes committed and pushed

## 📊 Statistics

- **Total Lines of Code**: ~2,400 lines
- **Modules Complete**: 5/5 (Phase 1 complete)
- **Cards in Database**: 5,562
- **Images Downloaded**: 4,375
- **MQTT Topics Defined**: 25+

## 🐛 Known Issues

None currently. All tested modules working as expected.

## 💡 Notes

1. System uses WSL or non-systemd init - must start mosquitto manually
2. Database/image sync working perfectly with get-diced.com API
3. Database locking issue resolved by moving ATTACH/DETACH outside transaction
4. API field naming fixed (camelCase → snake_case)
5. Git repo using SSH authentication successfully
6. Images and database properly excluded from git via .gitignore

## 🎯 Project Goals Reminder

Building a live stream overlay for Supershow card game with:
- **Controller**: Desktop app for match management
- **Production View**: Minimal bottom overlay (overlays.uno style)
- **Communication**: MQTT pub/sub
- **Data**: SQLite database + WebP images from get-diced.com
- **Recording**: JSON event logs for replay (future phase)
- **Platform**: Streamyard compatible
