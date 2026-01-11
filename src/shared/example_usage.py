"""
Example usage of database and sync modules
Run this to test the infrastructure
"""

import logging

from .config import Config
from .database import DatabaseService
from .sync import SyncService

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Example usage of database and sync services"""

    # Load configuration
    logger.info("Loading configuration...")
    try:
        config = Config("config.toml")
    except FileNotFoundError:
        logger.error("Configuration file not found. Copy config.toml.example to config.toml")
        return

    # Initialize database service
    logger.info("Initializing database service...")
    db_service = DatabaseService(config.database.cards_db_path)
    db_service.connect()

    # Initialize sync service
    logger.info("Initializing sync service...")
    sync_service = SyncService(
        api_base_url=config.sync.api_base_url,
        cards_manifest_url=config.sync.cards_manifest_url,
        cards_database_url=config.sync.cards_database_url,
        images_manifest_url=config.sync.images_manifest_url,
        images_base_url=config.sync.images_base_url,
        database_service=db_service,
        images_path=config.database.images_path,
        local_manifest_path=config.database.local_manifest_path,
        timeout=config.sync.sync_timeout,
    )

    # Check current database state
    card_count = db_service.get_card_count()
    logger.info(f"Current database has {card_count} cards")

    # Sync database
    logger.info("=" * 60)
    logger.info("SYNCING DATABASE")
    logger.info("=" * 60)

    def db_progress(message: str, progress: float):
        logger.info(f"[{progress * 100:.0f}%] {message}")

    try:
        current_version = 0  # Start from 0 to force initial sync
        updated, new_version = sync_service.sync_database(
            current_version=current_version, progress_callback=db_progress
        )

        if updated:
            logger.info(f"Database updated to version {new_version}")
            card_count = db_service.get_card_count()
            logger.info(f"Database now has {card_count} cards")
        else:
            logger.info("Database is already up to date")

    except Exception as e:
        logger.error(f"Database sync failed: {e}")

    # Test database queries
    logger.info("=" * 60)
    logger.info("TESTING DATABASE QUERIES")
    logger.info("=" * 60)

    # Get some competitors
    competitors = db_service.get_competitors(limit=5)
    logger.info(f"Found {len(competitors)} competitors:")
    for comp in competitors:
        logger.info(
            f"  - {comp.name} ({comp.division}): "
            f"POW={comp.power} TECH={comp.technique} AGI={comp.agility}"
        )

    # Get some main deck cards
    main_deck = db_service.get_main_deck_cards()
    logger.info(f"Found {len(main_deck)} main deck cards")
    if main_deck:
        logger.info("First 5 main deck cards:")
        for card in main_deck[:5]:
            logger.info(
                f"  - #{card.deck_card_number}: {card.name} ({card.play_order}, {card.atk_type})"
            )

    # Search for a card
    search_results = db_service.search_cards(query="punch", limit=5)
    logger.info(f"Search for 'punch' found {len(search_results)} results:")
    for card in search_results:
        logger.info(f"  - {card.name}")

    # Check image sync status
    logger.info("=" * 60)
    logger.info("CHECKING IMAGE SYNC STATUS")
    logger.info("=" * 60)

    try:
        need_sync, total = sync_service.get_sync_status()
        logger.info(f"Images: {total - need_sync}/{total} synced")
        logger.info(f"Need to sync: {need_sync} images")

        if need_sync > 0:
            logger.info("To sync images, uncomment the sync_images() call below")
            # Uncomment to actually sync images (may take a while):
            # logger.info("=" * 60)
            # logger.info("SYNCING IMAGES")
            # logger.info("=" * 60)
            #
            # def img_progress(downloaded: int, total: int):
            #     if downloaded % 10 == 0 or downloaded == total:
            #         logger.info(f"Images: {downloaded}/{total}")
            #
            # downloaded, total = sync_service.sync_images(
            #     progress_callback=img_progress
            # )
            # logger.info(f"Downloaded {downloaded} images")

    except Exception as e:
        logger.error(f"Image sync status check failed: {e}")

    # Cleanup
    db_service.disconnect()
    logger.info("Done!")


if __name__ == "__main__":
    main()
