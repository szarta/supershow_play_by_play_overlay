"""
Configuration management for BPP Supershow Overlay
"""
import toml
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class MQTTConfig:
    """MQTT configuration"""
    broker_host: str
    broker_port: int
    username: str
    password: str
    client_id_controller: str
    client_id_production: str
    keepalive: int = 60
    reconnect_delay_min: int = 1
    reconnect_delay_max: int = 60


@dataclass
class SyncConfig:
    """Sync configuration"""
    api_base_url: str
    cards_manifest_url: str
    cards_database_url: str
    images_manifest_url: str
    images_base_url: str
    check_on_startup: bool = True
    auto_sync: bool = False
    sync_timeout: int = 300


@dataclass
class DatabaseConfig:
    """Database configuration"""
    cards_db_path: str
    images_path: str
    local_manifest_path: str


@dataclass
class RecorderConfig:
    """Recorder configuration"""
    output_directory: str
    auto_save: bool = True
    pretty_print_json: bool = True


@dataclass
class UIConfig:
    """UI configuration"""
    theme: str
    font_size: int
    window_width: int
    window_height: int
    remember_position: bool = True


@dataclass
class ProductionUIConfig:
    """Production UI configuration"""
    theme: str
    default_height: int
    expanded_height: int
    default_width: int
    window_opacity: float
    always_on_top: bool
    frameless: bool
    draggable: bool
    auto_collapse_seconds: int
    show_card_thumbnails: bool
    thumbnail_width: int
    thumbnail_height: int
    max_discard_visible: int
    background_color: str
    text_color: str
    accent_color: str
    power_color: str
    technique_color: str
    agility_color: str
    strike_color: str
    grapple_color: str
    submission_color: str


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str
    log_to_file: bool
    log_file_path: str
    log_rotation: str


class Config:
    """Main configuration class"""

    def __init__(self, config_path: str = "config.toml"):
        self.config_path = Path(config_path)
        self._data: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from file"""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Copy config.toml.example to config.toml and customize it."
            )

        with open(self.config_path, 'r') as f:
            self._data = toml.load(f)

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._data.get(section, {}).get(key, default)

    @property
    def mqtt(self) -> MQTTConfig:
        """Get MQTT configuration"""
        mqtt = self._data.get('mqtt', {})
        return MQTTConfig(
            broker_host=mqtt.get('broker_host', 'localhost'),
            broker_port=mqtt.get('broker_port', 1883),
            username=mqtt.get('username', ''),
            password=mqtt.get('password', ''),
            client_id_controller=mqtt.get('client_id_controller', 'bpp_controller'),
            client_id_production=mqtt.get('client_id_production', 'bpp_production'),
            keepalive=mqtt.get('keepalive', 60),
            reconnect_delay_min=mqtt.get('reconnect_delay_min', 1),
            reconnect_delay_max=mqtt.get('reconnect_delay_max', 60),
        )

    @property
    def sync(self) -> SyncConfig:
        """Get sync configuration"""
        sync = self._data.get('sync', {})
        return SyncConfig(
            api_base_url=sync.get('api_base_url', 'https://get-diced.com'),
            cards_manifest_url=sync.get('cards_manifest_url', '/api/cards/manifest'),
            cards_database_url=sync.get('cards_database_url', '/api/cards/database'),
            images_manifest_url=sync.get('images_manifest_url', '/api/images/manifest'),
            images_base_url=sync.get('images_base_url', '/images/mobile'),
            check_on_startup=sync.get('check_on_startup', True),
            auto_sync=sync.get('auto_sync', False),
            sync_timeout=sync.get('sync_timeout', 300),
        )

    @property
    def database(self) -> DatabaseConfig:
        """Get database configuration"""
        db = self._data.get('database', {})
        return DatabaseConfig(
            cards_db_path=db.get('cards_db_path', './data/cards.db'),
            images_path=db.get('images_path', './data/images/'),
            local_manifest_path=db.get('local_manifest_path', './data/local_manifest.json'),
        )

    @property
    def recorder(self) -> RecorderConfig:
        """Get recorder configuration"""
        rec = self._data.get('recorder', {})
        return RecorderConfig(
            output_directory=rec.get('output_directory', './recordings/'),
            auto_save=rec.get('auto_save', True),
            pretty_print_json=rec.get('pretty_print_json', True),
        )

    @property
    def controller_ui(self) -> UIConfig:
        """Get controller UI configuration"""
        ui = self._data.get('controller_ui', {})
        return UIConfig(
            theme=ui.get('theme', 'dark'),
            font_size=ui.get('font_size', 12),
            window_width=ui.get('window_width', 1000),
            window_height=ui.get('window_height', 800),
            remember_position=ui.get('remember_position', True),
        )

    @property
    def production_ui(self) -> ProductionUIConfig:
        """Get production UI configuration"""
        ui = self._data.get('production_ui', {})
        return ProductionUIConfig(
            theme=ui.get('theme', 'dark'),
            default_height=ui.get('default_height', 150),
            expanded_height=ui.get('expanded_height', 500),
            default_width=ui.get('default_width', 1920),
            window_opacity=ui.get('window_opacity', 0.95),
            always_on_top=ui.get('always_on_top', True),
            frameless=ui.get('frameless', True),
            draggable=ui.get('draggable', True),
            auto_collapse_seconds=ui.get('auto_collapse_seconds', 10),
            show_card_thumbnails=ui.get('show_card_thumbnails', True),
            thumbnail_width=ui.get('thumbnail_width', 60),
            thumbnail_height=ui.get('thumbnail_height', 84),
            max_discard_visible=ui.get('max_discard_visible', 4),
            background_color=ui.get('background_color', '#1a1a1a'),
            text_color=ui.get('text_color', '#ffffff'),
            accent_color=ui.get('accent_color', '#4a9eff'),
            power_color=ui.get('power_color', '#ff4444'),
            technique_color=ui.get('technique_color', '#ff8800'),
            agility_color=ui.get('agility_color', '#44ff44'),
            strike_color=ui.get('strike_color', '#ffff44'),
            grapple_color=ui.get('grapple_color', '#4444ff'),
            submission_color=ui.get('submission_color', '#aa44ff'),
        )

    @property
    def logging(self) -> LoggingConfig:
        """Get logging configuration"""
        log = self._data.get('logging', {})
        return LoggingConfig(
            level=log.get('level', 'INFO'),
            log_to_file=log.get('log_to_file', True),
            log_file_path=log.get('log_file_path', './logs/app.log'),
            log_rotation=log.get('log_rotation', 'daily'),
        )
