from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class SourceType(str, Enum):
    ADB = "ADB"
    ETH = "ETH"
    WLAN = "WLAN"
    BLE = "BLE"


class WifiMode(str, Enum):
    UNKNOWN = "UNKNOWN"
    STATION = "STATION"
    ACCESS_POINT = "ACCESS_POINT"
    MONITOR = "MONITOR"


@dataclass(frozen=True)
class RuntimeContext:
    base_dir: Path
    filter_file: Path
    log_dir: Path
    adb_fallback_path: Path
    source_type: SourceType = SourceType.ADB
    wifi_mode: WifiMode = WifiMode.UNKNOWN

    @classmethod
    def from_file(cls, file_path):
        base_dir = Path(file_path).resolve().parent
        return cls(
            base_dir=base_dir,
            filter_file=base_dir / "filters.txt",
            log_dir=base_dir / "logs",
            adb_fallback_path=Path(r"E:\platform-tools\adb.exe"),
        )
