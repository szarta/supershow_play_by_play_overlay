"""
Database module for BPP Supershow Overlay
Handles SQLite connection and card queries
"""
import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Tuple
from contextlib import contextmanager

from .models import Card, CardType, AttackType, PlayOrder

logger = logging.getLogger(__name__)


class DatabaseService:
    """SQLite database service for card data"""

    def __init__(self, db_path: str):
        """
        Initialize database service

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._ensure_directory()
        self._connection: Optional[sqlite3.Connection] = None

    def _ensure_directory(self) -> None:
        """Ensure database directory exists"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> None:
        """Open database connection"""
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self._connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
            self._init_tables()

    def disconnect(self) -> None:
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Disconnected from database")

    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        if not self._connection:
            self.connect()

        try:
            yield self._connection
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            logger.error(f"Transaction failed, rolling back: {e}")
            raise

    def _init_tables(self) -> None:
        """Create tables if they don't exist"""
        cursor = self._connection.cursor()

        # Cards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
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
            )
        """)

        # Card related finishes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS card_related_finishes (
                card_uuid TEXT NOT NULL,
                finish_uuid TEXT NOT NULL,
                PRIMARY KEY (card_uuid, finish_uuid)
            )
        """)

        # Card related cards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS card_related_cards (
                card_uuid TEXT NOT NULL,
                related_uuid TEXT NOT NULL,
                PRIMARY KEY (card_uuid, related_uuid)
            )
        """)

        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cards_name
            ON cards(name)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cards_type
            ON cards(card_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cards_deck_number
            ON cards(deck_card_number)
        """)

        self._connection.commit()
        logger.info("Database tables initialized")

    def get_card_count(self) -> int:
        """Get total number of cards in database"""
        if not self._connection:
            self.connect()

        cursor = self._connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM cards")
        return cursor.fetchone()[0]

    def get_card_by_uuid(self, uuid: str) -> Optional[Card]:
        """
        Get card by UUID

        Args:
            uuid: Card UUID

        Returns:
            Card object or None if not found
        """
        if not self._connection:
            self.connect()

        cursor = self._connection.cursor()
        cursor.execute("SELECT * FROM cards WHERE db_uuid = ?", (uuid,))
        row = cursor.fetchone()

        if row:
            return self._row_to_card(row)
        return None

    def get_card_by_name(self, name: str, exact: bool = True) -> Optional[Card]:
        """
        Get card by name

        Args:
            name: Card name
            exact: If True, exact match. If False, case-insensitive partial match

        Returns:
            Card object or None if not found
        """
        if not self._connection:
            self.connect()

        cursor = self._connection.cursor()

        if exact:
            cursor.execute("SELECT * FROM cards WHERE name = ?", (name,))
        else:
            cursor.execute(
                "SELECT * FROM cards WHERE name LIKE ? COLLATE NOCASE",
                (f"%{name}%",)
            )

        row = cursor.fetchone()

        if row:
            return self._row_to_card(row)
        return None

    def search_cards(
        self,
        query: Optional[str] = None,
        card_type: Optional[str] = None,
        atk_type: Optional[str] = None,
        play_order: Optional[str] = None,
        division: Optional[str] = None,
        limit: int = 100
    ) -> List[Card]:
        """
        Search cards with filters

        Args:
            query: Text search in card name
            card_type: Filter by card type
            atk_type: Filter by attack type
            play_order: Filter by play order
            division: Filter by division
            limit: Maximum results to return

        Returns:
            List of matching cards
        """
        if not self._connection:
            self.connect()

        conditions = []
        params = []

        if query:
            conditions.append("name LIKE ? COLLATE NOCASE")
            params.append(f"%{query}%")

        if card_type:
            conditions.append("card_type = ?")
            params.append(card_type)

        if atk_type:
            conditions.append("atk_type = ?")
            params.append(atk_type)

        if play_order:
            conditions.append("play_order = ?")
            params.append(play_order)

        if division:
            conditions.append("division = ?")
            params.append(division)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM cards WHERE {where_clause} ORDER BY name LIMIT ?"
        params.append(limit)

        cursor = self._connection.cursor()
        cursor.execute(sql, params)

        return [self._row_to_card(row) for row in cursor.fetchall()]

    def get_competitors(
        self,
        division: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Card]:
        """
        Get all competitor cards

        Args:
            division: Filter by division (optional)
            limit: Maximum results to return (optional)

        Returns:
            List of competitor cards
        """
        if not self._connection:
            self.connect()

        cursor = self._connection.cursor()

        if division:
            sql = (
                "SELECT * FROM cards WHERE card_type LIKE '%Competitor%' "
                "AND division = ? ORDER BY name"
            )
            if limit:
                sql += f" LIMIT {limit}"
            cursor.execute(sql, (division,))
        else:
            sql = (
                "SELECT * FROM cards WHERE card_type LIKE '%Competitor%' "
                "ORDER BY name"
            )
            if limit:
                sql += f" LIMIT {limit}"
            cursor.execute(sql)

        return [self._row_to_card(row) for row in cursor.fetchall()]

    def get_main_deck_cards(self) -> List[Card]:
        """
        Get all main deck cards

        Returns:
            List of main deck cards ordered by deck number
        """
        if not self._connection:
            self.connect()

        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT * FROM cards WHERE card_type = 'MainDeckCard' "
            "ORDER BY deck_card_number"
        )

        return [self._row_to_card(row) for row in cursor.fetchall()]

    def get_related_finishes(self, card_uuid: str) -> List[str]:
        """
        Get related finish UUIDs for a card

        Args:
            card_uuid: Card UUID

        Returns:
            List of finish card UUIDs
        """
        if not self._connection:
            self.connect()

        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT finish_uuid FROM card_related_finishes WHERE card_uuid = ?",
            (card_uuid,)
        )

        return [row[0] for row in cursor.fetchall()]

    def clear_card_data(self) -> None:
        """Clear all card data (for sync replacement)"""
        if not self._connection:
            self.connect()

        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM card_related_finishes")
            cursor.execute("DELETE FROM card_related_cards")
            cursor.execute("DELETE FROM cards")
            logger.info("Cleared all card data")

    def replace_from_temp_db(self, temp_db_path: str) -> Tuple[int, int, int]:
        """
        Replace card data from temporary database

        Args:
            temp_db_path: Path to temporary database file

        Returns:
            Tuple of (cards_count, finishes_count, related_cards_count)
        """
        if not self._connection:
            self.connect()

        cursor = self._connection.cursor()

        # First, attach temp database (outside transaction)
        logger.info(f"Attaching temporary database: {temp_db_path}")
        cursor.execute(f"ATTACH DATABASE '{temp_db_path}' AS temp_db")

        try:
            # Use with statement for transaction
            with self.transaction():
                # Clear existing data
                logger.info("Clearing existing card data...")
                cursor.execute("DELETE FROM card_related_finishes")
                cursor.execute("DELETE FROM card_related_cards")
                cursor.execute("DELETE FROM cards")

                # Copy cards
                logger.info("Copying cards...")
                cursor.execute("INSERT INTO cards SELECT * FROM temp_db.cards")

                # Copy related finishes
                logger.info("Copying related finishes...")
                cursor.execute(
                    "INSERT INTO card_related_finishes "
                    "SELECT * FROM temp_db.card_related_finishes"
                )

                # Copy related cards
                logger.info("Copying related cards...")
                cursor.execute(
                    "INSERT INTO card_related_cards "
                    "SELECT * FROM temp_db.card_related_cards"
                )

            # Transaction committed successfully, now detach
            logger.info("Detaching temporary database...")
            cursor.execute("DETACH DATABASE temp_db")

            # Get counts
            cards_count = cursor.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
            finishes_count = cursor.execute(
                "SELECT COUNT(*) FROM card_related_finishes"
            ).fetchone()[0]
            related_count = cursor.execute(
                "SELECT COUNT(*) FROM card_related_cards"
            ).fetchone()[0]

            logger.info(
                f"Database sync complete: {cards_count} cards, "
                f"{finishes_count} finishes, {related_count} related cards"
            )

            return (cards_count, finishes_count, related_count)

        except Exception as e:
            # Rollback happened in transaction context manager
            logger.error(f"Database replacement failed: {e}")
            # Try to detach if still attached
            try:
                cursor.execute("DETACH DATABASE temp_db")
            except:
                pass
            raise

    def _row_to_card(self, row: sqlite3.Row) -> Card:
        """
        Convert database row to Card object

        Args:
            row: Database row

        Returns:
            Card object
        """
        # Parse tags from comma-separated string
        tags = []
        if row['tags']:
            tags = [t.strip() for t in row['tags'].split(',')]

        # Parse enums
        card_type = None
        if row['card_type']:
            try:
                card_type = CardType(row['card_type'])
            except ValueError:
                card_type = row['card_type']  # Store as string if not in enum

        atk_type = None
        if row['atk_type']:
            try:
                atk_type = AttackType(row['atk_type'])
            except ValueError:
                pass

        play_order = None
        if row['play_order']:
            try:
                play_order = PlayOrder(row['play_order'])
            except ValueError:
                pass

        return Card(
            db_uuid=row['db_uuid'],
            name=row['name'],
            card_type=card_type,
            rules_text=row['rules_text'],
            errata_text=row['errata_text'],
            is_banned=bool(row['is_banned']),
            release_set=row['release_set'],
            srg_url=row['srg_url'],
            srgpc_url=row['srgpc_url'],
            comments=row['comments'],
            tags=tags,
            power=row['power'],
            agility=row['agility'],
            strike=row['strike'],
            submission=row['submission'],
            grapple=row['grapple'],
            technique=row['technique'],
            division=row['division'],
            gender=row['gender'],
            deck_card_number=row['deck_card_number'],
            atk_type=atk_type,
            play_order=play_order,
        )

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
