import asyncio
import os
from collections import defaultdict
from typing import Any

from .models import MemoryMatch


class LocalMemoryBackend:
    """Deterministic backend used for tests and offline demos."""

    def __init__(self) -> None:
        self._banks: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.recall_calls = 0
        self.retain_calls = 0

    async def recall(self, bank_id: str, query: str) -> list[MemoryMatch]:
        self.recall_calls += 1
        await asyncio.sleep(0.01)
        rows = self._banks.get(bank_id, [])
        matches = []
        for row in rows:
            if any(word in row["content"].lower() for word in query.lower().split()[:3]):
                matches.append(
                    MemoryMatch(bank_id, row["content"], 0.9, row["metadata"])
                )
        return matches[:5]

    async def retain(self, bank_id: str, content: str, metadata=None) -> None:
        self.retain_calls += 1
        await asyncio.sleep(0.005)
        self._banks[bank_id].append(
            {"content": content, "metadata": metadata or {}}
        )


class HindsightBackend:
    """Async wrapper around the official Hindsight Python client."""

    def __init__(self, base_url: str) -> None:
        from hindsight_client import Hindsight
        self.client = Hindsight(base_url=base_url)
        self.recall_calls = 0
        self.retain_calls = 0

    async def recall(self, bank_id: str, query: str) -> list[MemoryMatch]:
        self.recall_calls += 1
        response = await asyncio.to_thread(
            self.client.recall, bank_id=bank_id, query=query
        )
        return [
            MemoryMatch(
                bank_id=bank_id,
                text=getattr(item, "text", str(item)),
                score=float(getattr(item, "score", 0.0) or 0.0),
                metadata=getattr(item, "metadata", {}) or {},
            )
            for item in getattr(response, "results", [])[:5]
        ]

    async def retain(self, bank_id: str, content: str, metadata=None) -> None:
        self.retain_calls += 1
        await asyncio.to_thread(
            self.client.retain,
            bank_id=bank_id,
            content=content,
            metadata=metadata or {},
        )


class CoalescedMemoryClient:
    """Concurrency-controlled memory client with single-flight recall."""

    def __init__(self, backend: Any, max_concurrent: int = 15) -> None:
        self.backend = backend
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._inflight: dict[tuple[str, str], asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def recall(self, bank_id: str, query: str) -> list[MemoryMatch]:
        key = (bank_id, query)
        async with self._lock:
            task = self._inflight.get(key)
            if task is None:
                task = asyncio.create_task(self._perform_recall(bank_id, query))
                self._inflight[key] = task
                owner = True
            else:
                owner = False

        try:
            return await task
        finally:
            if owner:
                async with self._lock:
                    self._inflight.pop(key, None)

    async def _perform_recall(self, bank_id: str, query: str):
        async with self.semaphore:
            return await self.backend.recall(bank_id, query)

    async def retain(self, bank_id: str, content: str, metadata=None) -> None:
        async with self.semaphore:
            await self.backend.retain(bank_id, content, metadata)

    @property
    def recall_calls(self) -> int:
        return self.backend.recall_calls

    @property
    def retain_calls(self) -> int:
        return self.backend.retain_calls


def build_memory_client() -> CoalescedMemoryClient:
    base_url = os.getenv("HINDSIGHT_BASE_URL", "").strip()
    backend = HindsightBackend(base_url) if base_url else LocalMemoryBackend()
    return CoalescedMemoryClient(backend)
