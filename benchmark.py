import asyncio
import time

from incident_agent.fingerprint import structural_fingerprint
from incident_agent.memory_client import CoalescedMemoryClient, LocalMemoryBackend
from incident_agent.simulator import generate_alerts


async def run_benchmark(alert_count=140):
    alerts = generate_alerts(alert_count)

    naive_backend = LocalMemoryBackend()

    async def naive_recall(alert):
        query = f"{alert.component} {alert.error_type} {alert.error_code}"
        await naive_backend.recall("incident-agent", query)

    start = time.perf_counter()
    await asyncio.gather(*(naive_recall(a) for a in alerts))
    naive_ms = (time.perf_counter() - start) * 1000

    backend = LocalMemoryBackend()
    client = CoalescedMemoryClient(backend)

    async def coalesced_recall(alert):
        query = f"{alert.component} {alert.error_type} {alert.error_code}"
        await client.recall("incident-agent", query)

    fingerprints = {structural_fingerprint(a) for a in alerts}
    start = time.perf_counter()
    await asyncio.gather(*(coalesced_recall(a) for a in alerts))
    coalesced_ms = (time.perf_counter() - start) * 1000

    return {
        "alerts": alert_count,
        "unique_fingerprints": len(fingerprints),
        "naive_recall_calls": naive_backend.recall_calls,
        "coalesced_recall_calls": backend.recall_calls,
        "naive_elapsed_ms": round(naive_ms, 2),
        "coalesced_elapsed_ms": round(coalesced_ms, 2),
    }
