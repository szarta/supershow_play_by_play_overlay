# Big Picture Premium (BPP) Supershow Overlay - Design Document

## Overview
Live stream overlay application for the Supershow card game. Provides real-time match state visualization with separate control and production interfaces communicating via MQTT.

## Architecture

### Components
1. **Controller** - Python desktop app (tkinter) for managing match state
2. **Production View** - Python desktop app (tkinter) with minimal bottom overlay for streaming
3. **MQTT Broker** - Message broker for component communication (e.g., Mosquitto)
4. **Card Database** - SQLite database synced from get-diced.com API
5. **Card Images** - WebP image files (300MB+) synced from get-diced.com API
6. **Match Recorder** - Event serialization system for replay functionality

### Communication Flow
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

## MQTT Topic Structure

### State Topics (Published by Controller)
- `supershow/match/init` - Match initialization (title, competitors, stipulations)
- `supershow/match/reset` - Reset match state
- `supershow/player/1/competitor` - Player 1 competitor card
- `supershow/player/2/competitor` - Player 2 competitor card
- `supershow/player/1/hand_count` - Player 1 cards in hand (count only)
- `supershow/player/2/hand_count` - Player 2 cards in hand (count only)
- `supershow/player/1/deck_count` - Player 1 cards remaining in deck
- `supershow/player/2/deck_count` - Player 2 cards remaining in deck
- `supershow/player/1/discard` - Player 1 discard pile (array of card UUIDs)
- `supershow/player/2/discard` - Player 2 discard pile (array of card UUIDs)
- `supershow/player/1/in_play` - Player 1 cards in play (array of card UUIDs)
- `supershow/player/2/in_play` - Player 2 cards in play (array of card UUIDs)
- `supershow/player/1/turn_roll` - Player 1 last turn roll (type + number)
- `supershow/player/2/turn_roll` - Player 2 last turn roll (type + number)
- `supershow/player/1/turns_won` - Player 1 turns won count
- `supershow/player/2/turns_won` - Player 2 turns won count
- `supershow/player/1/turns_passed` - Player 1 turns passed count
- `supershow/player/2/turns_passed` - Player 2 turns passed count
- `supershow/match/crowd_meter` - Current crowd meter value
- `supershow/match/title` - Match title
- `supershow/match/stipulations` - Match stipulations (free-form text)

### Event Topics (For Match Recording)
- `supershow/events/match_start` - Match started
- `supershow/events/turn_roll` - Turn roll occurred
- `supershow/events/card_played` - Card moved to in-play
- `supershow/events/card_stopped` - Card was stopped by opponent
- `supershow/events/card_discarded` - Card moved to discard
- `supershow/events/card_to_hand` - Card moved to hand
- `supershow/events/card_buried` - Card buried (to bottom of deck)
- `supershow/events/card_topped` - Card placed on top of deck
- `supershow/events/turn_won` - Turn won
- `supershow/events/turn_passed` - Turn passed
- `supershow/events/crowd_increment` - Crowd meter changed
- `supershow/events/match_end` - Match ended

### Control Topics (Production → Controller)
- `supershow/control/heartbeat` - Production view health check
- `supershow/control/ready` - Production view ready signal

## Data Models

### Match State
```json
{
  "match_id": "uuid",
  "title": "Championship Match",
  "stipulations": "New York Rules",
  "crowd_meter": 1,
  "started_at": 1234567890,
  "player1": { /* PlayerState */ },
  "player2": { /* PlayerState */ }
}
```

### Player State
```json
{
  "player_id": 1,
  "competitor_uuid": "competitor-card-uuid",
  "hand_count": 3,
  "deck_count": 23,
  "discard_pile": ["card-uuid-1", "card-uuid-2", "card-uuid-3"],
  "in_play": ["card-uuid-4", "card-uuid-5"],
  "last_turn_roll": {
    "type": "Power",
    "value": 8
  },
  "turns_won": 6,
  "turns_passed": 2
}
```

### Card Reference (from Database)
```json
{
  "db_uuid": "d9f6e890e1c846e79d4c11b649aa3683",
  "name": "American Double Punch",
  "card_type": "MainDeckCard",
  "atk_type": "Strike",
  "play_order": "Lead",
  "deck_card_number": 1,
  "rules_text": "...",
  "tags": []
}
```

### Competitor Card (from Database)
```json
{
  "db_uuid": "271b524616d04a08b7c95d67515e2599",
  "name": "El Toro Guapo",
  "card_type": "SingleCompetitorCard",
  "division": "Super Lucha",
  "gender": "Male",
  "power": 10,
  "technique": 5,
  "agility": 6,
  "strike": 9,
  "submission": 7,
  "grapple": 8,
  "rules_text": "...",
  "tags": ["Super Lucha"],
  "related_finishes": ["uuid1", "uuid2", "uuid3"]
}
```

### Match Event (for recording)
```json
{
  "event_id": "uuid",
  "match_id": "match-uuid",
  "timestamp": 1234567890,
  "event_type": "card_played",
  "player_id": 1,
  "data": {
    "card_uuid": "card-uuid",
    "from_zone": "hand",
    "to_zone": "in_play"
  }
}
```

## Card State Transitions

### Card Zones
- **Deck** - Face down, count only visible
- **Hand** - Face down to viewers, count only visible
- **In Play** - Face up, fully visible with card details
- **Discard** - Face up, list visible (scrollable if > 4 cards)
- **Buried** - Bottom of deck (zone: deck)
- **Topped** - Top of deck (zone: deck)

### Valid Transitions
```
Deck → Hand (draw)
Hand → In Play (play card)
Hand → Discard (discard from hand)
In Play → Discard (card resolves/is stopped)
Discard → Hand (recursion effect)
Discard → Deck (buried)
Discard → Deck (topped)
Deck → In Play (special effects)
```

## Turn Roll Types

### Icons & Types
- **Power (POW)** - Red icon
- **Technique (TECH)** - Orange icon
- **Agility (AGI)** - Green icon

Roll value: 1-12 (2d6)

## Attack Types & Icons
- **Strike (STR)** - Yellow icon
- **Grapple (GRA)** - Blue icon
- **Submission (SUB)** - Purple icon

## Play Order & Icons
- **Lead (L)** - Lead icon
- **Follow Up (FOL/F)** - Follow Up icon
- **Finish (FIN)** - Finish icon

## Production View Specifications

### Desktop App Architecture
- **Framework**: Python 3.10+ with tkinter
- **Purpose**: Self-contained overlay window for Streamyard window capture
- **Design Pattern**: Minimal bottom overlay inspired by overlays.uno
- **Local Assets**: Card images embedded locally (300MB+ directory)

### Layout - Minimal Bottom Overlay (1920x150px default)

**Collapsed State (Default):**
```
┌─────────────────────────────────────────────────────────────┐
│ Championship Match | Stipulations: New York Rules | Crowd: ●●●○○ │
├──────────────┬──────────────────────────────────┬──────────────┤
│ Player 1     │                                  │ Player 2     │
│ [Mini Comp]  │                                  │ [Mini Comp]  │
│ POW:8 H:3    │                                  │ TECH:10 H:8  │
│ W:6 P:2      │                                  │ W:10 P:1     │
│ Play:2 Disc:4│                                  │ Play:3 Disc:4│
└──────────────┴──────────────────────────────────┴──────────────┘
```

**Expanded State (On Click/Hover):**
```
┌─────────────────────────────────────────────────────────────┐
│ Championship Match | Stipulations: New York Rules | Crowd: ●●●○○ │
├──────────────────────┬─────────────┬──────────────────────────┤
│ PLAYER 1             │             │ PLAYER 2                 │
│ [Competitor Image]   │             │ [Competitor Image]       │
│                      │             │                          │
│ Last Roll: POW 8     │             │ Last Roll: TECH 10       │
│ Hand: 3  Deck: 23    │             │ Hand: 8  Deck: 12        │
│ Turns Won: 6         │             │ Turns Won: 10            │
│ Turns Passed: 2      │             │ Turns Passed: 1          │
│                      │             │                          │
│ IN PLAY (2):         │             │ IN PLAY (3):             │
│ • [Card Thumb] Name  │             │ • [Card Thumb] Name      │
│ • [Card Thumb] Name  │             │ • [Card Thumb] Name      │
│                      │             │ • [Card Thumb] Name      │
│ DISCARD (4): [Show]  │             │ DISCARD (4): [Show]      │
└──────────────────────┴─────────────┴──────────────────────────┘
```

**Card Preview Popup (On Card Click):**
```
┌─────────────────────────────────────┐
│  [Full-Size Card Image 600x800px]  │
│                                     │
│  American Double Punch              │
│  Deck #1 | Lead | Strike            │
│                                     │
│  Rules: Each player adds the        │
│  bottom card of their deck to       │
│  their hand or stop any lead        │
│  Grapple.                           │
│                                     │
│  [Close]                            │
└─────────────────────────────────────┘
```

### Interaction Patterns
1. **Minimal State**: Small bottom bar, always visible, minimal screen real estate
2. **Expand on Demand**: Click player name/section to expand that side
3. **Card Preview**: Click any card thumbnail/name for full-size preview popup
4. **Discard Viewer**: Click "Show" to expand scrollable discard list
5. **Auto-Collapse**: Return to minimal state after 10 seconds of inactivity (configurable)

### Window Properties
- **Transparent Background**: Use tkinter transparency for non-rectangular overlay
- **Always on Top**: Window stays above other windows (for Streamyard capture)
- **Frameless**: No title bar or borders
- **Draggable**: Click and drag to reposition overlay
- **Resizable**: Scale between 100%-200% for different stream layouts

### Styling
- **Font**: Clean sans-serif (default system font or bundled)
- **High Contrast**: Dark semi-transparent background with white/colored text
- **Color-Coded Icons**:
  - Power (POW) = Red
  - Technique (TECH) = Orange
  - Agility (AGI) = Green
  - Strike (STR) = Yellow
  - Grapple (GRA) = Blue
  - Submission (SUB) = Purple
- **Smooth Animations**: 200ms fade for state changes, 300ms for expansions
- **Theme Support**: Light/dark themes, configurable colors via config file

## Controller Interface Specifications

### Technology Stack
- **Framework**: Python 3.10+ with tkinter
- **MQTT Client**: paho-mqtt
- **Database**: SQLite (cards database)
- **HTTP Client**: requests or httpx for API calls
- **Config**: TOML for settings (broker, sync, UI preferences)

### UI Layout
```
┌──────────────────────────────────────────────────────────┐
│  File  Match  Config                         Status: ●   │
├──────────────────────────────────────────────────────────┤
│  MATCH SETUP                                             │
│  Title: [___________________________]                    │
│  Stipulations: [____________________]                    │
│  Crowd Meter: [1] [+] [-]                               │
│                                                          │
│  Player 1 Competitor: [Select...▾]                       │
│  Player 2 Competitor: [Select...▾]                       │
│                                                          │
│  [Start Match] [Reset Match] [Export Recording]          │
├──────────────────────┬───────────────────────────────────┤
│  PLAYER 1            │  PLAYER 2                         │
│                      │                                   │
│  Turn Roll:          │  Turn Roll:                       │
│  Type: [POW▾] Val:8  │  Type: [TECH▾] Val:10            │
│  [Update]            │  [Update]                         │
│                      │                                   │
│  Hand: [3] [+] [-]   │  Hand: [8] [+] [-]               │
│  Deck: 23 (calc)     │  Deck: 12 (calc)                 │
│                      │                                   │
│  [+ Turn Won]        │  [+ Turn Won]                     │
│  [+ Turn Passed]     │  [+ Turn Passed]                  │
│                      │                                   │
│  IN PLAY:            │  IN PLAY:                         │
│  [Add Card▾]         │  [Add Card▾]                      │
│  • Card 1 [x]        │  • Card 1 [x]                     │
│  • Card 2 [x]        │  • Card 2 [x]                     │
│  [Clear All to Disc] │  [Clear All to Disc]              │
│                      │                                   │
│  DISCARD:            │  DISCARD:                         │
│  [Add Card▾]         │  [Add Card▾]                      │
│  • Card 1 [→Hand][B] │  • Card 1 [→Hand][B]             │
│  • Card 2 [→Hand][B] │  • Card 2 [→Hand][B]             │
│  [Clear Discard]     │  [Clear Discard]                  │
└──────────────────────┴───────────────────────────────────┘

Legend:
[→Hand] = Move to hand
[B] = Bury (to bottom of deck)
[T] = Top (to top of deck)
[x] = Remove from zone
```

### Key Features
- **Card Autocomplete**: Type-ahead search when adding cards
- **Quick Actions**: Keyboard shortcuts for common operations
- **Deck Count Auto-Calculate**: 30 - (hand + in_play + discard)
- **Match Recording**: Auto-save all events to JSON file
- **Configuration**: MQTT broker settings, card image directory

### Control Flow
1. Load card database on startup
2. Connect to MQTT broker
3. User sets up match (title, competitors, stipulations)
4. User clicks "Start Match" → publishes `match/init` event
5. During match, user updates state → publishes state changes to MQTT
6. All events logged to match recording file
7. User clicks "Export Recording" → saves complete match JSON

## Database Schema

### Cards Table (from existing mobile app schema)
```sql
CREATE TABLE cards (
    db_uuid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    card_type TEXT NOT NULL,
    rules_text TEXT,
    errata_text TEXT,
    is_banned INTEGER NOT NULL DEFAULT 0,
    release_set TEXT,
    srg_url TEXT,
    srgpc_url TEXT,
    comments TEXT,
    tags TEXT,
    power INTEGER,
    agility INTEGER,
    strike INTEGER,
    submission INTEGER,
    grapple INTEGER,
    technique INTEGER,
    division TEXT,
    gender TEXT,
    deck_card_number INTEGER,
    atk_type TEXT,
    play_order TEXT,
    synced_at INTEGER NOT NULL
);
```

### Card Images
- **Format**: WebP (optimized for size)
- **Storage**: `data/images/{first_2_chars_of_uuid}/{uuid}.webp`
- **Size**: 300MB+ total (all card images)
- **Syncing**: Hash-based manifest from get-diced.com API
  - Bundled manifest shipped with app
  - Local manifest tracks synced images
  - Only download images that are missing or updated (hash comparison)
- **Fallback**: Placeholder image if specific card image not found

## Match Recording Format

### File Structure
```json
{
  "match_id": "uuid",
  "version": "1.0",
  "started_at": 1234567890,
  "ended_at": 1234567999,
  "metadata": {
    "title": "Championship Match",
    "stipulations": "New York Rules",
    "player1_competitor": "competitor-uuid-1",
    "player2_competitor": "competitor-uuid-2"
  },
  "events": [
    {
      "event_id": "uuid",
      "timestamp": 1234567891,
      "event_type": "turn_roll",
      "player_id": 1,
      "data": {
        "roll_type": "Power",
        "roll_value": 8
      }
    },
    {
      "event_id": "uuid",
      "timestamp": 1234567892,
      "event_type": "card_played",
      "player_id": 1,
      "data": {
        "card_uuid": "card-uuid",
        "from_zone": "hand",
        "to_zone": "in_play"
      }
    }
  ],
  "final_state": {
    "crowd_meter": 5,
    "player1": { /* PlayerState */ },
    "player2": { /* PlayerState */ }
  }
}
```

## Implementation Phases

### Phase 1: Core Infrastructure
- Database sync from get-diced.com API (manifest-based)
- Image sync from get-diced.com API (hash-based manifest)
- MQTT broker configuration and connection handling
- Basic controller UI (match setup + manual state updates)
- Basic production view (minimal bottom overlay with MQTT updates)

### Phase 2: Card Management
- Card zone management in controller
- Card search/autocomplete (from local database)
- Discard pile display with scrolling
- In-play card management
- Deck count auto-calculation

### Phase 3: Production View Interactivity
- Minimal collapsed state (always visible)
- Expand on click/hover (player sections)
- Card thumbnail display with click-to-preview
- Full-size card popup viewer
- Auto-collapse after inactivity
- Transparent frameless window with "always on top"

### Phase 4: Match Recording
- Event capture system
- JSON serialization
- Match export functionality
- Auto-save during match

### Phase 5: Polish & Features
- Production view animations/transitions (smooth fades)
- Theme configuration (light/dark, custom colors)
- Keyboard shortcuts in controller
- Window dragging/resizing for production view
- Settings UI for MQTT broker and sync preferences

### Phase 6: Sync & Update Management
- Check for updates button in controller
- Background sync with progress indicators
- Incremental image downloads
- Database version tracking

### Phase 7: Replay Viewer (Future)
- Standalone replay viewer app
- Load match recording JSON
- Step through events
- Timeline scrubbing

## Configuration Files

### config.toml
```toml
[mqtt]
broker_host = "localhost"
broker_port = 1883
username = ""
password = ""
client_id_controller = "bpp_controller"
client_id_production = "bpp_production"

[sync]
api_base_url = "https://get-diced.com"
cards_manifest_url = "/api/cards/manifest"
cards_database_url = "/api/cards/database"
images_manifest_url = "/api/images/manifest"
images_base_url = "/images/mobile"
check_on_startup = true
auto_sync = false

[database]
cards_db_path = "./data/cards.db"
images_path = "./data/images/"
local_manifest_path = "./data/local_manifest.json"

[recorder]
output_directory = "./recordings/"
auto_save = true

[controller_ui]
theme = "dark"
font_size = 12

[production_ui]
theme = "dark"
default_height = 150  # pixels for collapsed state
expanded_height = 500  # pixels for expanded state
default_width = 1920
window_opacity = 0.95
always_on_top = true
auto_collapse_seconds = 10
show_card_thumbnails = true
```

## Technical Considerations

### MQTT QoS Levels
- State topics: QoS 1 (at least once delivery)
- Event topics: QoS 2 (exactly once delivery for recording)

### Image Handling
- Card images stored locally in organized directory structure
- Production view loads images directly from local filesystem
- Synced from get-diced.com using hash-based manifest
- Bundled manifest ships with app (no internet required for core functionality)
- Optional incremental sync downloads missing/updated images
- WebP format for optimal size/quality balance
- Fallback to placeholder for missing images

### Error Handling
- MQTT reconnection logic with exponential backoff
- Production view shows "disconnected" state when broker unavailable
- Controller validates card UUIDs against database before publishing

### Performance
- Production view: Debounce rapid state updates (100ms)
- Batch discard pile updates when clearing multiple cards
- Lazy load card images in production view

### Cross-Platform Support
- Python 3.10+ (Windows, Linux, macOS)
- tkinter (included with Python standard library)
- MQTT broker can run anywhere (same machine or remote server)
- Image sync works on all platforms (SHA256 hash verification)

## Database & Image Sync Implementation

### Database Sync Flow
Based on the mobile app pattern:

1. **Check for Updates**
   - GET `/api/cards/manifest` → Returns `{version: int, filename: str, sizeBytes: int}`
   - Compare `version` with local `currentDatabaseVersion` (stored in config/prefs)
   - If remote version > local version, update is available

2. **Download Database**
   - GET `/api/cards/database` → Returns SQLite .db file as binary data
   - Save to temporary file

3. **Replace Cards Table**
   - Open temp database (read-only)
   - Open user database (read-write)
   - Begin transaction:
     - DELETE existing rows from `card_related_finishes`
     - DELETE existing rows from `card_related_cards`
     - DELETE existing rows from `cards`
     - ATTACH temp database
     - INSERT all rows from temp database into user database
     - DETACH temp database
   - Commit transaction
   - This preserves user data (collections, decks) while replacing card data

4. **Update Version**
   - Save new `currentDatabaseVersion` to config
   - Update `lastSyncDate` timestamp

### Image Sync Flow
Based on hash-based manifest pattern:

1. **Load Manifests**
   - Load bundled manifest (shipped with app): `images_manifest.json`
   - Load local manifest (tracks synced images): `local_manifest.json`
   - Combine to get current local hashes: `{uuid: hash}`

2. **Fetch Server Manifest**
   - GET `/api/images/manifest` → Returns:
     ```json
     {
       "version": 1,
       "generated": "2025-01-10T12:00:00Z",
       "imageCount": 500,
       "images": {
         "uuid1": {"hash": "sha256...", "path": "ab/cd/uuid1.webp"},
         "uuid2": {"hash": "sha256...", "path": "ef/gh/uuid2.webp"}
       }
     }
     ```

3. **Find Images to Sync**
   - For each image in server manifest:
     - If UUID not in local hashes → needs sync
     - If hash differs from local hash → needs sync
   - Result: List of images to download

4. **Download Images**
   - For each image to sync:
     - GET `/images/mobile/{path}` → Returns WebP binary data
     - Save to `data/images/{first_2_chars}/{uuid}.webp`
     - Verify SHA256 hash matches manifest
   - Update progress after each download

5. **Update Local Manifest**
   - Merge synced images into local manifest
   - Save to `local_manifest.json`
   - This tracks which images have been synced

### Sync API Endpoints

```
GET /api/cards/manifest
Response: {
  "version": 5,
  "filename": "cards_v5.db",
  "sizeBytes": 5242880,
  "generated": "2025-01-10T12:00:00Z"
}

GET /api/cards/database
Response: Binary SQLite database file

GET /api/images/manifest
Response: {
  "version": 1,
  "generated": "2025-01-10T12:00:00Z",
  "imageCount": 500,
  "images": {
    "uuid": {
      "hash": "sha256_hex_string",
      "path": "relative/path/to/image.webp"
    }
  }
}

GET /images/mobile/{path}
Response: Binary WebP image file
```

### Initial Bundled Assets
When distributing the app, include:
- `data/cards.db` - Initial card database
- `data/images_manifest.json` - Bundled image manifest
- `data/images/` - Directory with 300MB+ of card images
- User can run app offline with bundled assets
- Sync feature updates to latest cards and images when connected

### Sync UI in Controller

```
┌────────────────────────────────────────────┐
│  Database & Images Sync                    │
├────────────────────────────────────────────┤
│  Database: v5 (Latest: v5) ✓ Up to date   │
│  [Check for Updates] [Sync Now]            │
│                                            │
│  Images: 485/500 synced (15 missing)       │
│  [Sync Images]                             │
│                                            │
│  Last Sync: 2025-01-10 10:30 AM            │
│                                            │
│  During Sync:                              │
│  Downloading images: 12/15                 │
│  [████████████░░░░] 80%                    │
└────────────────────────────────────────────┘
```

## Future Enhancements
- Tag team support (2v2 matches)
- Multiple match formats (tournament brackets)
- Live statistics overlay (avg turn roll, card type distribution)
- Integration with Twitch chat for crowd meter voting
- Mobile controller app (iOS/Android)
- Cloud match recording storage
- Replay viewer with timeline
