# Quick Resume Guide

## Current State (2026-01-11)

✅ **Phase 3 Production View Complete!**
- Mosquitto broker running
- Database synced (5,562 cards, 1,094 competitors)
- Controller GUI implemented and working
- ✨ **NEW**: Production overlay view implemented
- ✨ **NEW**: Frameless, transparent overlay window
- ✨ **NEW**: Collapsed (150px) and expanded (500px) views
- ✨ **NEW**: Real-time MQTT subscription
- ✨ **NEW**: Auto-collapse timer and window dragging
- Poetry setup complete with pre-commit hooks

## Resume Steps

### 1. Install dependencies with Poetry

```bash
cd ~/data/overlay_app
poetry install
```

### 2. Run the production view overlay

```bash
poetry run bpp-production
```

What you get:
- 🎬 Frameless overlay window at bottom of screen
- 📊 Minimal collapsed view (1920x150px)
- 📈 Detailed expanded view (1920x500px)
- 🖼️ Competitor images with caching
- 📡 Real-time MQTT subscription to all `supershow/*` topics
- ⏱️ Auto-collapse after 10 seconds
- 🖱️ Click-and-drag to reposition

### 3. Run the controller (in another terminal)

```bash
poetry run bpp-controller
```

What you get:
- 🎮 Match setup UI (title, stipulations, competitors, crowd meter)
- 👥 Player state controls (turn rolls, hand/deck counts, finish/breakout rolls)
- 📡 Real-time MQTT publishing to `supershow/*` topics
- 🟢 Connection status indicator
- 🚪 Quit button

### 3. Test MQTT messages (optional)

```bash
# Terminal 1: Monitor MQTT
poetry run python test_controller.py

# Terminal 2: Run controller and make changes
poetry run bpp-controller
```

### 4. Test end-to-end

With both controller and production view running:
1. Create a match in the controller
2. Watch the production view update in real-time
3. Click player sections to expand/collapse
4. Drag the overlay to reposition

### 5. Next: Phase 2 - Card Zone Management

**Now that Phase 3 is complete, add card management to controller:**
- In-play card management
- Discard pile with card list
- Card search/autocomplete
- Update production view to display cards

## Quick Commands

```bash
# Production view overlay
poetry run bpp-production

# Controller app
poetry run bpp-controller

# Sync database and images
poetry run bpp-sync

# Test MQTT connectivity
poetry run bpp-mqtt-test

# Monitor MQTT messages
mosquitto_sub -h localhost -t 'supershow/#' -v

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
- `src/production/` - Production view implementation (10 files)
- `src/controller/` - Controller implementation (8 files)
- `src/shared/mqtt_client.py` - MQTT implementation
- `DESIGN.md` - Full technical design
