import os
from pathlib import Path

def load_env(path: str | None = None, override: bool = False) -> bool:
    env_path = Path(path) if path else Path(".") / ".env"
    if not env_path.exists():
        return False
    
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        value = val.strip().strip('"').strip("'")
        if not override and key in os.environ:
            continue
        os.environ[key] = value
    return True