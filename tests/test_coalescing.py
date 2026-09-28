import asyncio

from incident_agent.memory_client import CoalescedMemoryClient, LocalMemoryBackend


def test_single_flight_coalesces_identical_queries():
    async def run():
        backend = LocalMemoryBackend()
        client = CoalescedMemoryClient(backend)

        results = await asyncio.gather(
            *(client.recall("incident-agent", "database connection failure")
              for _ in range(20))
        )

        assert len(results) == 20
        assert backend.recall_calls == 1

    asyncio.run(run())
