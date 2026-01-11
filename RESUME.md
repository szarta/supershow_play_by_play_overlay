# Quick Resume Guide

## Current State (2026-01-11)

✅ **Phase 1 Controller Complete with Updates!**
- Mosquitto broker running
- Database synced (5,562 cards, 1,094 competitors)
- Controller GUI implemented and working
- MQTT publishing functional
- Poetry setup complete with pre-commit hooks
- ✨ **NEW**: Finish roll tracking
- ✨ **NEW**: Breakout rolls tracking
- ✨ **NEW**: Quit button
- 🗑️ **REMOVED**: Turns won tracking (inferred from recording)

## Resume Steps

### 1. Install dependencies with Poetry

```bash
cd ~/data/overlay_app
poetry install
```

### 2. Run the controller

```bash
poetry run bpp-controller
```

What you get:
- 🎮 Match setup UI (title, stipulations, competitors, crowd meter)
- 👥 Player state controls (turn rolls, hand/deck counts, turns)
- 📡 Real-time MQTT publishing to `supershow/*` topics
- 🟢 Connection status indicator

### 3. Test MQTT messages (optional)

```bash
# Terminal 1: Monitor MQTT
poetry run python test_controller.py

# Terminal 2: Run controller and make changes
poetry run bpp-controller
```

### 4. Next: Phase 2 - Card Zone Management

Next steps:
- In-play card management
- Discard pile with card list
- Card search/autocomplete
- Deck count auto-calculation

## Quick Commands

```bash
# Controller app
poetry run bpp-controller

# Sync database and images
poetry run bpp-sync

# Test MQTT connectivity
poetry run bpp-mqtt-test

# Monitor MQTT messages
poetry run python test_controller.py
# Or: mosquitto_sub -h localhost -t 'supershow/#' -v

# Check broker status
ps aux | grep mosquitto

# Restart broker if needed
pkill mosquitto
/usr/sbin/mosquitto -d

# Code quality checks
poetry run pre-commit run --all-files

# Run tests
poetry run pytest
```

## Files to Review

- `docs/CURRENT_STATUS.md` - Full progress report
- `docs/TESTING_MQTT.md` - MQTT testing guide
- `src/shared/mqtt_client.py` - MQTT implementation
- `src/shared/example_mqtt.py` - MQTT test suite
