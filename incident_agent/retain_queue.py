import asyncio
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RetainEvent:
    bank_id: str
    content: str
    fingerprint: str
    metadata: dict[str, Any]


class AsyncRetainQueue:
    """Asynchronously writes one consolidated event per fingerprint."""

    def __init__(self, memory_client) -> None:
        self.memory_client = memory_client
        self._queue: asyncio.Queue[RetainEvent] = asyncio.Queue()
        self._seen: set[str] = set()
        self._worker = None

    async def start(self) -> None:
        if self._worker is None:
            self._worker = asyncio.create_task(self._run())

    async def enqueue(self, event: RetainEvent) -> None:
        key = f"{event.bank_id}:{event.fingerprint}"
        if key not in self._seen:
            self._seen.add(key)
            await self._queue.put(event)

    async def _run(self) -> None:
        while True:
            event = await self._queue.get()
            try:
                await self.memory_client.retain(
                    event.bank_id, event.content, event.metadata
                )
            finally:
                self._queue.task_done()

    async def drain(self) -> None:
        await self._queue.join()
