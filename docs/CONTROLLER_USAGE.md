# Controller Application - Usage Guide

## Overview

The controller application is a desktop tkinter UI for managing match state and publishing updates via MQTT. This is the Phase 1 implementation with basic features:

- Match setup (title, stipulations, crowd meter)
- Competitor selection for both players
- Manual state updates (turn rolls, hand/deck counts, turns won/passed)
- Real-time MQTT publishing

## Running the Controller

```bash
# Using Poetry (recommended)
poetry run bpp-controller

# Or directly with Python module
poetry run python -m src.controller.main
```

The application will:
1. Load configuration from `config.toml`
2. Connect to database at `./data/cards.db`
3. Connect to MQTT broker (localhost:1883 by default)
4. Load 1,094 competitors from database
5. Display the UI

## UI Layout

### Match Setup Section (Top)
- **Title**: Enter match title (required)
- **Stipulations**: Enter match stipulations (optional)
- **Crowd Meter**: Display with +/- buttons (range: 0-10)
- **Player 1/2 Competitors**: Searchable dropdowns with all competitors
- **Start Match**: Validates inputs and publishes initial state
- **Reset Match**: Clears state and publishes reset signal
- **Quit**: Closes the application

### Player State Sections (Middle, Side-by-Side)

Each player has:

**Turn Roll**
- Type dropdown: Power, Technique, Agility
- Value spinner: 1-12
- Update Roll button

**Hand Count**
- Display with +/- buttons
- Range: 0-30
- Auto-updates deck count

**Deck Count**
- Read-only calculated value
- Formula: 30 - hand_count

**Finish Roll**
- Value spinner: 1-12
- Set Finish button (publishes finish roll)
- Clear button (clears finish roll)

**Breakout Rolls**
- Value spinner: 1-12
- Add Roll button (adds to list)
- Clear All button (clears all rolls)
- Display shows current rolls (e.g., "Rolls: 4, 8, 11")

**Turns Passed**
- Display with +1 button

### Status Bar (Bottom)
- MQTT connection status: Connected (green) / Disconnected (red)

## Workflow

### 1. Start a Match

1. Enter match title (required)
2. Enter stipulations (optional)
3. Set initial crowd meter (default 0)
4. Select Player 1 competitor from dropdown (type to search)
5. Select Player 2 competitor from dropdown
6. Click "Start Match"

This publishes all initial state to MQTT:
- `supershow/match/init`
- `supershow/match/title`
- `supershow/match/stipulations`
- `supershow/match/crowd_meter`
- `supershow/player/1/competitor`
- `supershow/player/2/competitor`
- `supershow/player/{1,2}/hand_count` (initial: 0)
- `supershow/player/{1,2}/deck_count` (initial: 30)
- `supershow/player/{1,2}/turns_won` (initial: 0)
- `supershow/player/{1,2}/turns_passed` (initial: 0)

### 2. Update Match State

After starting, all changes publish immediately:

**Update Turn Roll**
1. Select roll type (Power/Technique/Agility)
2. Enter roll value (1-12)
3. Click "Update Roll"
→ Publishes `supershow/player/{1,2}/last_turn_roll`

**Change Hand Count**
- Click +/- buttons
→ Publishes both `hand_count` and `deck_count`

**Set Finish Roll**
1. Enter finish roll value (1-12)
2. Click "Set Finish"
→ Publishes `supershow/player/{1,2}/finish_roll`
3. Click "Clear" to remove finish roll

**Add Breakout Rolls**
1. Enter first breakout roll value (1-12)
2. Click "Add Roll"
3. Repeat for each additional breakout roll
→ Publishes updated list to `supershow/player/{1,2}/breakout_rolls`
4. Click "Clear All" when breakout sequence is complete

**Increment Turns**
- Click "+1 Turn Passed"
→ Publishes updated count

**Live Editing**
- Title and stipulations can be edited after match starts
- Changes publish on focus out or pressing Enter
- Crowd meter publishes when +/- buttons are clicked

### 3. Reset Match

1. Click "Reset Match"
2. Confirm dialog
3. All state clears, reset signal published
→ Publishes `supershow/match/reset`

## Testing MQTT Messages

Run the test subscriber in a separate terminal:

```bash
# Terminal 1: Run test subscriber
poetry run python test_controller.py

# Terminal 2: Run controller
poetry run bpp-controller

# Or use mosquitto_sub directly
mosquitto_sub -h localhost -t 'supershow/#' -v
```

Expected message flow:
1. Start match → ~15 messages (init + all initial state, including finish_roll and breakout_rolls)
2. Update turn roll → 1 message
3. Change hand count → 2 messages (hand + deck)
4. Set finish roll → 1 message
5. Add breakout roll → 1 message (full list)
6. Increment turns passed → 1 message

## Configuration

Settings in `config.toml`:

```toml
[mqtt]
broker_host = "localhost"
broker_port = 1883
client_id_controller = "bpp_controller"

[database]
cards_db_path = "./data/cards.db"

[controller_ui]
theme = "dark"  # or "light"
font_size = 12
```

## Troubleshooting

### Database Error on Startup
```
Failed to connect to database at ./data/cards.db
```
**Solution**: Run the sync script first:
```bash
poetry run bpp-sync
# Or: poetry run python -m src.shared.example_usage
```

### MQTT Connection Failed
```
Failed to connect to MQTT broker at localhost:1883
```
**Solution**: Start the mosquitto broker:
```bash
# Check if running
ps aux | grep mosquitto

# Start if not running
/usr/sbin/mosquitto -d
```

The controller will work in "offline mode" if MQTT is disconnected, but no state will be published.

### No Competitors in Dropdown
```
The database contains no competitor cards
```
**Solution**: Sync the database:
```bash
poetry run bpp-sync
```

## Files Created

### Core Logic
- `src/controller/controller.py` - State management
- `src/controller/publisher.py` - MQTT publishing
- `src/controller/main.py` - Entry point

### UI Components
- `src/controller/ui/__init__.py` - Package exports
- `src/controller/ui/main_window.py` - Main window
- `src/controller/ui/match_setup_frame.py` - Match setup controls
- `src/controller/ui/player_frame.py` - Player state widget
- `src/controller/ui/status_bar.py` - Status indicator

### Testing
- `test_controller.py` - MQTT message monitor

## Next Steps

Phase 1 is complete! Future phases will add:

- **Phase 2**: Card zone management (in-play, discard, autocomplete)
- **Phase 3**: Production view (overlay UI)
- **Phase 4**: Match recording (JSON export)
- **Phase 5**: Polish (animations, keyboard shortcuts, themes)

## Architecture

```
User → UI → Controller → MatchState → Publisher → MQTT Broker
                ↓                                       ↓
           Database                          Production View (future)
```

All state flows through the MatchController, which maintains the single source of truth and coordinates between the UI and MQTT publisher.
