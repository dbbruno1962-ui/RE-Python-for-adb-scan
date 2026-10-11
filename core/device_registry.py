import json
from pathlib import Path


DEFAULT_DEVICE = {
    "alias": "",
    "category": "",
    "vendor": "",
    "ip": "",
    "ignored": False,
    "notes": "",
}


def _normalize_mac(mac):
    return mac.strip().upper()


def _device_path(path="devices.json"):
    registry_path = Path(path)
    if registry_path.is_absolute():
        return registry_path
    return Path(__file__).resolve().parent.parent / registry_path


def load(path="devices.json"):
    registry_path = _device_path(path)
    if not registry_path.exists():
        return {}

    with registry_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return {}

    return data


def save(registry, path="devices.json"):
    registry_path = _device_path(path)
    with registry_path.open("w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
        f.write("\n")


def add_device(mac, device=None, path="devices.json"):
    registry = load(path)
    key = _normalize_mac(mac)
    if key not in registry:
        registry[key] = dict(DEFAULT_DEVICE)

    if device:
        registry[key].update(device)

    save(registry, path)
    return registry[key]


def get_device(mac, path="devices.json"):
    registry = load(path)
    return registry.get(_normalize_mac(mac))


def update_device(mac, updates, path="devices.json"):
    registry = load(path)
    key = _normalize_mac(mac)
    current = registry.get(key, dict(DEFAULT_DEVICE))
    current.update(updates)
    registry[key] = current
    save(registry, path)
    return current


def is_ignored(mac, path="devices.json"):
    device = get_device(mac, path)
    if not device:
        return False
    return bool(device.get("ignored", False))
