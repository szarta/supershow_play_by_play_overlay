# Big Picture Premium (BPP) Supershow Overlay

Live stream overlay application for the Supershow card game. Provides real-time match state visualization with separate control and production interfaces communicating via MQTT.

![Version](https://img.shields.io/badge/version-0.1.0--alpha-orange)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

This application consists of two desktop applications:
- **Controller**: Manage match state, card zones, and player stats
- **Production View**: Minimal bottom overlay for streaming (Streamyard/OBS)

Both apps communicate via MQTT and sync card data from get-diced.com.

## Features

- Real-time match state updates via MQTT
- Minimal bottom overlay design (overlays.uno style)
- Card database syncing from get-diced.com API
- Hash-based image syncing (300MB+ card images)
- Match recording with full event history
- Expandable card previews and discard pile viewer
- Offline-first with bundled assets

## Architecture

```
Controller (tkinter) → MQTT Broker → Production View (tkinter)
                          ↓
                    Match Recorder
                    (JSON event log)

Both apps sync from get-diced.com:
  - GET /api/cards/manifest
  - GET /api/cards/database
  - GET /api/images/manifest
  - GET /images/mobile/{path}
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/docs/#installation) 1.3+ for dependency management
- MQTT broker (e.g., Mosquitto) running locally or remotely

### Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd overlay_app
```

2. Install dependencies with Poetry:
```bash
poetry install
```

3. Install pre-commit hooks (optional but recommended):
```bash
poetry run pre-commit install
```

4. Copy config template and configure:
```bash
cp config.toml.example config.toml
# Edit config.toml with your MQTT broker settings
```

5. Sync card database and images:
```bash
poetry run bpp-sync
```

### Running the Apps

**Controller:**
```bash
poetry run bpp-controller
# Or: poetry run python -m src.controller.main
```

**Production View (not yet implemented):**
```bash
poetry run python -m src.production_view.main
```

## Project Structure

```
overlay_app/
├── src/
│   ├── controller/         # Controller desktop app (Phase 1 ✅)
│   ├── production_view/    # Production overlay app (TODO)
│   └── shared/            # Shared modules (sync, mqtt, models)
├── data/
│   ├── cards.db           # SQLite card database
│   ├── images/            # Card images (webp)
│   └── local_manifest.json
├── recordings/            # Match recordings (JSON)
├── docs/                  # Additional documentation
├── config.toml           # Configuration file
├── pyproject.toml        # Poetry dependencies & settings
├── poetry.lock           # Locked dependency versions
├── .pre-commit-config.yaml  # Pre-commit hooks
├── DESIGN.md            # Full design document
└── README.md            # This file
```

## Configuration

Edit `config.toml` to configure:
- MQTT broker connection
- Sync API endpoints
- UI preferences (theme, window size, opacity)
- Recording settings

See `config.toml.example` for all available options.

## Usage

### Controller Interface

1. Start the controller app
2. Click "Check for Updates" to sync latest card data
3. Set up match: title, competitors, stipulations
4. Click "Start Match"
5. Update player state during the match
6. Add/remove cards from zones (hand, in play, discard)
7. Match is automatically recorded to JSON

### Production View

1. Start the production view app
2. Position the overlay at the bottom of your screen
3. Capture the window in Streamyard/OBS
4. Overlay automatically updates from MQTT messages
5. Click player sections to expand details
6. Click cards for full-size previews

## MQTT Topics

State topics published by Controller:
- `supershow/match/init` - Match setup
- `supershow/player/{1,2}/competitor` - Competitor cards
- `supershow/player/{1,2}/hand_count` - Cards in hand
- `supershow/player/{1,2}/in_play` - Cards in play
- `supershow/player/{1,2}/discard` - Discard pile
- `supershow/player/{1,2}/turn_roll` - Last turn roll
- `supershow/match/crowd_meter` - Crowd meter value

See DESIGN.md for full topic list.

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Quality
This project uses pre-commit hooks with:
- **Ruff**: Fast Python linter and formatter
- **Xenon**: Code complexity checker
- **Poetry check**: Validates pyproject.toml

Run manually:
```bash
poetry run pre-commit run --all-files
```

Or let it run automatically on every commit (after `poetry run pre-commit install`).

## Roadmap

- [x] **Phase 1**: Core infrastructure & controller UI (✅ Complete)
  - Database sync, MQTT client, match setup
  - Player state management (turn rolls, hand/deck, turns)
  - Real-time MQTT publishing
- [ ] **Phase 2**: Card management in controller
  - In-play cards, discard pile
  - Card search/autocomplete
- [ ] **Phase 3**: Production view overlay
  - Minimal bottom overlay
  - Expandable player sections
  - Card previews
- [ ] **Phase 4**: Match recording
- [ ] **Phase 5**: Polish & features
- [ ] **Phase 6**: Sync & update management
- [ ] **Phase 7**: Replay viewer (future)

## Contributing

Contributions welcome! Please read DESIGN.md for architecture details.

## License

MIT License - see LICENSE file for details

## Credits

- Card data and images from [get-diced.com](https://get-diced.com)
- Built for the Supershow card game community
