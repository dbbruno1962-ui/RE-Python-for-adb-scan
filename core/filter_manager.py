from pathlib import Path


DEFAULT_FILTERS = [
    "Vlion", "mentamob", "advlion", "Vungle", "Pangle",
    "firebase", "analytics", "NebulaLog", "getaddrinfo", "gai_error",
]

NOISE_CATEGORIES = {
    "ADS": [
        "advlion", "applovin", "banner", "google.android.gms.ads",
        "nonagon", "pangle", "vungle", "vlion",
    ],
    "ANDROID": [
        "chatty", "resourcetype", "zygote", "audiocapabilities",
        "videocapabilities",
    ],
    "OEM": [
        "nebulalog",
    ],
}

PROTO_PATTERNS = {
    "BLE": ["bluetooth", "blescan", "gatt", "btbind"],
    "PAIR": ["configwifi", "pair", "bind", "choicemodeactivity"],
    "TLS": ["443", "okhttp", "https", "tls"],
    "UDP": ["udp", "9377", "broadcast"],
    "TUTK": ["tutk", "iotc", "avapi"],
    "UI": ["activity", "fragment", "view", "layout"],
}


def _filter_path(path):
    return Path(path)


def ensure_filter_file(path):
    filter_path = _filter_path(path)
    if filter_path.exists():
        return

    with filter_path.open("w", encoding="utf-8") as f:
        for item in DEFAULT_FILTERS:
            f.write(item + "\n")


def load_filters(path):
    ensure_filter_file(path)
    result = []
    with _filter_path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                result.append(line)
    return result


def load_filter_candidates(path):
    """Load review candidates without changing the active filters."""
    candidate_path = _filter_path(path)
    if not candidate_path.exists():
        return []

    result = []
    section = ""
    review_sections = {
        "[AD_MEDIATION]",
        "[AD_DOMAINS]",
        "[AD_CLASSES_OR_MARKERS]",
    }
    with candidate_path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line.upper()
                continue
            if section in review_sections and line not in result:
                result.append(line)
    return result


def append_filter(path, pattern):
    existing = load_filters(path)
    if pattern in existing:
        return

    with _filter_path(path).open("a", encoding="utf-8") as f:
        f.write(pattern + "\n")


def classify_noise(line):
    lower = line.lower()
    for category, patterns in NOISE_CATEGORIES.items():
        for pattern in patterns:
            if pattern in lower:
                return category
    return ""


def map_proto(line):
    lower = line.lower()
    for proto, patterns in PROTO_PATTERNS.items():
        for pattern in patterns:
            if pattern in lower:
                return proto
    return "GEN"
