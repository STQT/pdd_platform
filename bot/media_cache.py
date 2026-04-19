import json
import asyncio
from pathlib import Path

CACHE_FILE = Path("/app/data/media_cache.json")


class MediaCache:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._data: dict[str, str] = {}
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        if CACHE_FILE.exists():
            try:
                self._data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            except Exception:
                self._data = {}

    def get(self, path: str) -> str | None:
        return self._data.get(path)

    async def save(self, path: str, file_id: str):
        async with self._lock:
            self._data[path] = file_id
            CACHE_FILE.write_text(
                json.dumps(self._data, ensure_ascii=False), encoding="utf-8"
            )

    def __len__(self):
        return len(self._data)


media_cache = MediaCache()
