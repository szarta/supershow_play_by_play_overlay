# Current Status - Supershow Overlay Project

**Last Updated**: 2026-01-11

## ✅ Completed Modules

### Phase 1: Core Infrastructure - COMPLETE ✅

### Phase 1 Extended: Controller Application - COMPLETE ✅

**Controller Desktop App** (`src/controller/` - 8 files, ~1,200 lines)
1. **Main Entry Point** (`main.py`)
   - Application initialization sequence
   - Config/database/MQTT setup
   - Error handling with dialogs
   - Graceful shutdown

2. **Match Controller** (`controller.py`)
   - MatchState management
   - Competitor loading from database
   - State validation and updates
   - Finish roll and breakout roll tracking

3. **MQTT Publisher** (`publisher.py`)
   - High-level publishing abstraction
   - QoS 1 with retain for state topics
   - All supershow/* topic publishing

4. **UI Components** (`ui/`)
   - MainWindow - Application frame
   - MatchSetupFrame - Match config with crowd meter +/- buttons
   - PlayerFrame - Player state controls (rolls, counts, finish/breakout)
   - StatusBar - MQTT connection indicator

**Status**: Fully implemented and tested with Poetry

### Phase 3: Production View Overlay - COMPLETE ✅

**Production View Desktop App** (`src/production/` - 10 files, ~1,400 lines)
1. **Main Entry Point** (`main.py`)
   - Application initialization
   - MQTT subscription setup
   - Overlay window creation

2. **MQTT Subscriber** (`subscriber.py`)
   - Subscribes to `supershow/#` wildcard
   - Routes messages to state manager
   - Handles all state topic types

3. **State Manager** (`state_manager.py`)
   - Maintains local MatchState
   - Loads card data from database
   - Notifies UI of state changes

4. **Overlay Window** (`ui/overlay_window.py`)
   - Frameless, transparent, always-on-top
   - Expand/collapse view switching
   - Auto-collapse timer (10s)
   - Window dragging support

5. **Collapsed View** (`ui/collapsed_view.py`)
   - Minimal 1920x150px bottom bar
   - Match info + player summaries
   - Competitor mini-images (60x84px)
   - Colored roll types, finish/breakout rolls

6. **Expanded View** (`ui/expanded_view.py`)
   - Detailed 1920x500px view
   - Full competitor images (200x280px)
   - Complete player stats
   - Click background to collapse

7. **UI Utilities** (`ui/utils.py`)
   - Color helpers (roll/attack colors)
   - Image loading with caching
   - Crowd meter rendering (●●●○○○○○○○)
   - Roll formatting

**Status**: Fully implemented and ready for testing

### Phase 1 Continued: Core Infrastructure - COMPLETE

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

### Phase 2: Card Zone Management

**Enhance Controller with Card Management:**
1. In-play card section with add/remove
2. Discard pile with card list viewer
3. Card search/autocomplete from database
4. Publish card zone updates to MQTT

**Update Production View:**
1. Display in-play cards as thumbnails
2. Show discard pile with "Show" button
3. Card preview popup on click
4. Scrollable discard viewer

### Testing & Polish

**End-to-End Integration:**
1. Test controller → production view flow
2. Verify streaming software compatibility (Streamyard, OBS)
3. Adjust opacity, colors, sizes
4. Test window positioning and dragging

**Future Enhancements:**
1. Match recording to JSON
2. Replay viewer
3. Fade animations for view transitions
4. Window resize/scale controls

## 🗂️ Git Status

- **Repository**: github.com:szarta/supershow_play_by_play_overlay.git
- **Branch**: main
- **Last Commit**: Ready to commit Phase 3 production view
- **Commits**: 5 total
  - 1cba378: Initial commit
  - 523f36f: Database and sync infrastructure
  - c49865b: MQTT client module
  - 58d832d: Current status docs and venv setup guide
  - 5d24427: Phase 1 controller with Poetry setup
- **Status**: Phase 3 production view ready to commit

## 📊 Statistics

- **Total Lines of Code**: ~5,600 lines
- **Modules Complete**: Phase 1 ✅, Controller ✅, Phase 3 Production View ✅
- **Files Created**: 28 total
  - Shared: 7 files
  - Controller: 8 files
  - Production: 10 files
  - Docs: 3 files
- **Cards in Database**: 5,562
- **Competitors**: 1,094
- **Images Downloaded**: 4,375
- **MQTT Topics**: 25+ defined and implemented
- **Poetry Scripts**: 4 (controller, production, sync, mqtt-test)

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
