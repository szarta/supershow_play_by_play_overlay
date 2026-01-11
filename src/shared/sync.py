"""
Sync module for BPP Supershow Overlay
Handles database and image syncing from get-diced.com API
"""

import hashlib
import json
import logging
from collections.abc import Callable
from pathlib import Path

import requests

from .database import DatabaseService
from .models import CardsManifest, ImageInfo, ImageManifest

logger = logging.getLogger(__name__)


class SyncError(Exception):
    """Base exception for sync errors"""

    pass


class SyncService:
    """Service for syncing card database and images"""

    def __init__(
        self,
        api_base_url: str,
        cards_manifest_url: str,
        cards_database_url: str,
        images_manifest_url: str,
        images_base_url: str,
        database_service: DatabaseService,
        images_path: str,
        local_manifest_path: str,
        timeout: int = 300,
    ):
        """
        Initialize sync service

        Args:
            api_base_url: Base URL for API (e.g., https://get-diced.com)
            cards_manifest_url: Path to cards manifest endpoint
            cards_database_url: Path to database download endpoint
            images_manifest_url: Path to images manifest endpoint
            images_base_url: Base path for image downloads
            database_service: Database service instance
            images_path: Local path for storing images
            local_manifest_path: Path to local manifest file
            timeout: Request timeout in seconds
        """
        self.api_base_url = api_base_url.rstrip("/")
        self.cards_manifest_url = cards_manifest_url
        self.cards_database_url = cards_database_url
        self.images_manifest_url = images_manifest_url
        self.images_base_url = images_base_url
        self.database_service = database_service
        self.images_path = Path(images_path)
        self.local_manifest_path = Path(local_manifest_path)
        self.timeout = timeout

        self.images_path.mkdir(parents=True, exist_ok=True)
        self.local_manifest_path.parent.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "BPP-Supershow-Overlay/0.1.0"})

    # ==================== Database Sync ====================

    def get_cards_manifest(self) -> CardsManifest:
        """
        Get cards database manifest from API

        Returns:
            CardsManifest object

        Raises:
            SyncError: If request fails
        """
        url = f"{self.api_base_url}{self.cards_manifest_url}"
        logger.info(f"Fetching cards manifest from: {url}")

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            return CardsManifest(
                version=data["version"],
                filename=data["filename"],
                size_bytes=data["size_bytes"],
                generated=data["generated"],
            )
        except requests.RequestException as e:
            raise SyncError(f"Failed to fetch cards manifest: {e}") from e

    def download_cards_database(
        self, progress_callback: Callable[[int, int], None] | None = None
    ) -> bytes:
        """
        Download cards database from API

        Args:
            progress_callback: Optional callback(downloaded_bytes, total_bytes)

        Returns:
            Database file content as bytes

        Raises:
            SyncError: If download fails
        """
        url = f"{self.api_base_url}{self.cards_database_url}"
        logger.info(f"Downloading database from: {url}")

        try:
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            chunks = []

            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    chunks.append(chunk)
                    downloaded += len(chunk)

                    if progress_callback and total_size:
                        progress_callback(downloaded, total_size)

            return b"".join(chunks)

        except requests.RequestException as e:
            raise SyncError(f"Failed to download database: {e}") from e

    def sync_database(
        self, current_version: int, progress_callback: Callable[[str, float], None] | None = None
    ) -> tuple[bool, int]:
        """
        Sync card database from server

        Args:
            current_version: Current local database version
            progress_callback: Optional callback(message, progress_0_to_1)

        Returns:
            Tuple of (updated, new_version)

        Raises:
            SyncError: If sync fails
        """
        # Step 1: Check manifest
        if progress_callback:
            progress_callback("Checking for updates...", 0.1)

        manifest = self.get_cards_manifest()
        logger.info(
            f"Database manifest: v{manifest.version} ({manifest.size_bytes / 1024 / 1024:.1f} MB)"
        )

        # Check if update needed
        if manifest.version <= current_version:
            logger.info(f"Database is up to date (v{current_version})")
            if progress_callback:
                progress_callback("Database is up to date", 1.0)
            return (False, current_version)

        # Step 2: Download database
        if progress_callback:
            progress_callback(f"Downloading database v{manifest.version}...", 0.3)

        def download_progress(downloaded: int, total: int):
            if progress_callback:
                progress = 0.3 + (downloaded / total * 0.4)  # 0.3 to 0.7
                progress_callback(
                    f"Downloading: {downloaded / 1024 / 1024:.1f} / {total / 1024 / 1024:.1f} MB",
                    progress,
                )

        db_data = self.download_cards_database(download_progress)

        # Step 3: Save to temp file
        if progress_callback:
            progress_callback("Installing database...", 0.7)

        temp_path = self.database_service.db_path.parent / "cards_temp.db"
        temp_path.write_bytes(db_data)
        logger.info(f"Saved temp database to: {temp_path}")

        # Step 4: Replace database
        if progress_callback:
            progress_callback("Replacing card data...", 0.8)

        try:
            counts = self.database_service.replace_from_temp_db(str(temp_path))
            logger.info(
                f"Database updated: {counts[0]} cards, {counts[1]} finishes, {counts[2]} related"
            )
        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()

        # Step 5: Done
        if progress_callback:
            progress_callback(f"Database updated to v{manifest.version}", 1.0)

        return (True, manifest.version)

    # ==================== Image Sync ====================

    def get_images_manifest(self) -> ImageManifest:
        """
        Get images manifest from API

        Returns:
            ImageManifest object

        Raises:
            SyncError: If request fails
        """
        url = f"{self.api_base_url}{self.images_manifest_url}"
        logger.info(f"Fetching images manifest from: {url}")

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            images = {}
            for uuid, info in data.get("images", {}).items():
                images[uuid] = ImageInfo(hash=info["hash"], path=info["path"])

            return ImageManifest(
                version=data["version"],
                generated=data["generated"],
                image_count=data["image_count"],
                images=images,
            )
        except requests.RequestException as e:
            raise SyncError(f"Failed to fetch images manifest: {e}") from e

    def load_local_manifest(self) -> ImageManifest | None:
        """
        Load local images manifest

        Returns:
            ImageManifest or None if not found
        """
        if not self.local_manifest_path.exists():
            logger.info("No local manifest found")
            return None

        try:
            with open(self.local_manifest_path) as f:
                data = json.load(f)

            images = {}
            for uuid, info in data.get("images", {}).items():
                images[uuid] = ImageInfo(hash=info["hash"], path=info["path"])

            manifest = ImageManifest(
                version=data["version"],
                generated=data["generated"],
                image_count=data["image_count"],
                images=images,
            )

            logger.info(f"Loaded local manifest: {manifest.image_count} images")
            return manifest

        except Exception as e:
            logger.error(f"Failed to load local manifest: {e}")
            return None

    def save_local_manifest(self, manifest: ImageManifest) -> None:
        """
        Save local images manifest

        Args:
            manifest: ImageManifest to save
        """
        data = {
            "version": manifest.version,
            "generated": manifest.generated,
            "image_count": manifest.image_count,
            "images": {
                uuid: {"hash": info.hash, "path": info.path}
                for uuid, info in manifest.images.items()
            },
        }

        with open(self.local_manifest_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved local manifest: {manifest.image_count} images")

    def get_local_image_hashes(self) -> dict[str, str]:
        """
        Get local image hashes from manifest

        Returns:
            Dict of {uuid: hash}
        """
        manifest = self.load_local_manifest()
        if not manifest:
            return {}

        return {uuid: info.hash for uuid, info in manifest.images.items()}

    def download_image(self, uuid: str, path: str, verify_hash: str | None = None) -> Path:
        """
        Download a single image

        Args:
            uuid: Image UUID
            path: Relative path from manifest
            verify_hash: Optional SHA256 hash to verify

        Returns:
            Local path to downloaded image

        Raises:
            SyncError: If download or verification fails
        """
        url = f"{self.api_base_url}{self.images_base_url}/{path}"
        logger.debug(f"Downloading image: {uuid} from {url}")

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            image_data = response.content

            # Verify hash if provided
            if verify_hash:
                actual_hash = hashlib.sha256(image_data).hexdigest()
                if actual_hash != verify_hash:
                    raise SyncError(
                        f"Image hash mismatch for {uuid}: expected {verify_hash}, got {actual_hash}"
                    )

            # Save to local path: images/{first_2_chars}/{uuid}.webp
            first_2 = uuid[:2]
            img_dir = self.images_path / first_2
            img_dir.mkdir(parents=True, exist_ok=True)

            img_path = img_dir / f"{uuid}.webp"
            img_path.write_bytes(image_data)

            logger.debug(f"Saved image to: {img_path}")
            return img_path

        except requests.RequestException as e:
            raise SyncError(f"Failed to download image {uuid}: {e}") from e

    def sync_images(
        self, progress_callback: Callable[[int, int], None] | None = None
    ) -> tuple[int, int]:
        """
        Sync images from server

        Args:
            progress_callback: Optional callback(downloaded, total)

        Returns:
            Tuple of (downloaded_count, total_to_sync)

        Raises:
            SyncError: If sync fails
        """
        logger.info("Starting image sync...")

        # Get server manifest
        server_manifest = self.get_images_manifest()
        logger.info(f"Server manifest: {server_manifest.image_count} images")

        # Get local hashes
        local_hashes = self.get_local_image_hashes()
        logger.info(f"Local hashes: {len(local_hashes)} images")

        # Find images to sync
        to_sync = []
        for uuid, server_info in server_manifest.images.items():
            local_hash = local_hashes.get(uuid)
            if local_hash is None or local_hash != server_info.hash:
                to_sync.append((uuid, server_info))

        total = len(to_sync)
        logger.info(f"Images to sync: {total}")

        if total == 0:
            return (0, 0)

        # Download images
        downloaded = 0
        synced_images = {}

        for uuid, server_info in to_sync:
            try:
                self.download_image(uuid, server_info.path, verify_hash=server_info.hash)
                synced_images[uuid] = server_info
                downloaded += 1

                if progress_callback:
                    progress_callback(downloaded, total)

            except SyncError as e:
                logger.error(f"Failed to sync image {uuid}: {e}")

        # Update local manifest
        if synced_images:
            local_manifest = self.load_local_manifest()
            if local_manifest:
                # Merge with existing
                local_manifest.images.update(synced_images)
                local_manifest.version = server_manifest.version
                local_manifest.generated = server_manifest.generated
                local_manifest.image_count = len(local_manifest.images)
            else:
                # Create new with only synced images
                local_manifest = ImageManifest(
                    version=server_manifest.version,
                    generated=server_manifest.generated,
                    image_count=len(synced_images),
                    images=synced_images,
                )

            self.save_local_manifest(local_manifest)

        logger.info(f"Image sync complete: {downloaded}/{total} downloaded")
        return (downloaded, total)

    def get_image_path(self, uuid: str) -> Path | None:
        """
        Get local path to image file

        Args:
            uuid: Image UUID

        Returns:
            Path to image file or None if not found
        """
        first_2 = uuid[:2]
        img_path = self.images_path / first_2 / f"{uuid}.webp"

        if img_path.exists():
            return img_path
        return None

    def get_sync_status(self) -> tuple[int, int]:
        """
        Get image sync status without downloading

        Returns:
            Tuple of (need_sync, total)

        Raises:
            SyncError: If status check fails
        """
        server_manifest = self.get_images_manifest()
        local_hashes = self.get_local_image_hashes()

        need_sync = 0
        for uuid, server_info in server_manifest.images.items():
            local_hash = local_hashes.get(uuid)
            if local_hash is None or local_hash != server_info.hash:
                need_sync += 1

        return (need_sync, server_manifest.image_count)
