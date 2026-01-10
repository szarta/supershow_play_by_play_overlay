# Testing Database and Sync Modules

This guide shows how to test the database and sync infrastructure.

## Setup

1. Install dependencies:
```bash
cd ~/data/supershow_play_by_play_overlay
pip install -r requirements.txt
```

2. Create configuration file:
```bash
cp config.toml.example config.toml
```

The default configuration should work for testing. You can customize the MQTT settings later.

## Testing Database and Sync

Run the example script:

```bash
python -m src.shared.example_usage
```

This will:
1. Load the configuration
2. Initialize the database service
3. Initialize the sync service
4. Check current database status
5. Sync the database from get-diced.com
6. Run test queries (competitors, main deck cards, search)
7. Check image sync status

### Expected Output

```
INFO - Loading configuration...
INFO - Initializing database service...
INFO - Connected to database: ./data/cards.db
INFO - Database tables initialized
INFO - Initializing sync service...
INFO - Current database has 0 cards
============================================================
SYNCING DATABASE
============================================================
INFO - [10%] Checking for updates...
INFO - Fetching cards manifest from: https://get-diced.com/api/cards/manifest
INFO - Database manifest: v5 (5.0 MB)
INFO - [30%] Downloading database v5...
INFO - [50%] Downloading: 2.5 / 5.0 MB
INFO - [70%] Downloading: 5.0 / 5.0 MB
INFO - [70%] Installing database...
INFO - Saved temp database to: ./data/cards_temp.db
INFO - [80%] Replacing card data...
INFO - Clearing existing card data...
INFO - Attaching temporary database: ./data/cards_temp.db
INFO - Copying cards...
INFO - Copying related finishes...
INFO - Copying related cards...
INFO - Database sync complete: 500 cards, 150 finishes, 200 related cards
INFO - Database updated: 500 cards, 150 finishes, 200 related
INFO - [100%] Database updated to v5
INFO - Database updated to version 5
INFO - Database now has 500 cards
============================================================
TESTING DATABASE QUERIES
============================================================
INFO - Found 5 competitors:
INFO -   - Alex Hammerstone (Global): POW=10 TECH=8 AGI=5
INFO -   - El Toro Guapo (Super Lucha): POW=10 TECH=5 AGI=6
INFO -   ...
INFO - Found 30 main deck cards
INFO - First 5 main deck cards:
INFO -   - #1: American Double Punch (Lead, Strike)
INFO -   - #2: Kick (Lead, Strike)
INFO -   ...
INFO - Search for 'punch' found 3 results:
INFO -   - American Double Punch
INFO -   - Punch
INFO -   ...
============================================================
CHECKING IMAGE SYNC STATUS
============================================================
INFO - Fetching images manifest from: https://get-diced.com/api/images/manifest
INFO - Images: 0/500 synced
INFO - Need to sync: 500 images
INFO - To sync images, uncomment the sync_images() call below
INFO - Done!
```

## Syncing Images

The example script checks image status but doesn't download by default (to save bandwidth).

To actually download images, edit `src/shared/example_usage.py` and uncomment the image sync section:

```python
# Uncomment these lines:
logger.info("=" * 60)
logger.info("SYNCING IMAGES")
logger.info("=" * 60)

def img_progress(downloaded: int, total: int):
    if downloaded % 10 == 0 or downloaded == total:
        logger.info(f"Images: {downloaded}/{total}")

downloaded, total = sync_service.sync_images(
    progress_callback=img_progress
)
logger.info(f"Downloaded {downloaded} images")
```

**Note**: Image sync may take a while (300+ MB of images).

## Manual Testing

You can also test the modules interactively:

```python
from src.shared.config import Config
from src.shared.database import DatabaseService
from src.shared.sync import SyncService

# Load config
config = Config("config.toml")

# Test database
db = DatabaseService(config.database.cards_db_path)
db.connect()

# Search for a card
results = db.search_cards(query="John Cena")
for card in results:
    print(f"{card.name} - {card.division}")

# Get all competitors
competitors = db.get_competitors()
print(f"Found {len(competitors)} competitors")

# Test sync
sync = SyncService(
    api_base_url=config.sync.api_base_url,
    cards_manifest_url=config.sync.cards_manifest_url,
    cards_database_url=config.sync.cards_database_url,
    images_manifest_url=config.sync.images_manifest_url,
    images_base_url=config.sync.images_base_url,
    database_service=db,
    images_path=config.database.images_path,
    local_manifest_path=config.database.local_manifest_path
)

# Check manifest
manifest = sync.get_cards_manifest()
print(f"Latest database version: {manifest.version}")

# Check image status
need_sync, total = sync.get_sync_status()
print(f"Images: {total - need_sync}/{total} synced")
```

## Verifying the Database

After syncing, you can verify the database directly:

```bash
sqlite3 data/cards.db

# Count cards
SELECT COUNT(*) FROM cards;

# List competitors
SELECT name, division FROM cards
WHERE card_type LIKE '%Competitor%'
ORDER BY name
LIMIT 10;

# List main deck cards
SELECT deck_card_number, name, play_order, atk_type
FROM cards
WHERE card_type = 'MainDeckCard'
ORDER BY deck_card_number
LIMIT 10;

# Search
SELECT name, card_type FROM cards
WHERE name LIKE '%strike%'
LIMIT 5;
```

## Troubleshooting

### "Configuration file not found"
- Make sure you copied `config.toml.example` to `config.toml`
- Check you're running from the project root directory

### Network errors
- Check internet connection
- Verify get-diced.com is accessible
- Check firewall settings

### Database errors
- Delete `data/cards.db` and try again
- Check file permissions on the `data/` directory
- Ensure SQLite3 is installed

### "Image hash mismatch"
- Network corruption - retry the sync
- Check disk space
- Clear `data/images/` and `data/local_manifest.json` and retry
