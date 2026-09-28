import asyncio
import sys

from incident_agent.memory_client import build_memory_client
from incident_agent.orchestrator import IncidentOrchestrator
from incident_agent.retain_queue import AsyncRetainQueue
from incident_agent.simulator import generate_alerts


async def main():
    scenario = sys.argv[1] if len(sys.argv) > 1 else "database"
    alerts = generate_alerts(20 if scenario == "quick" else 140)

    memory = build_memory_client()
    queue = AsyncRetainQueue(memory)
    await queue.start()

    orchestrator = IncidentOrchestrator(memory, queue)
    responses = await orchestrator.triage(alerts)
    await queue.drain()

    print(f"Processed alerts: {len(alerts)}")
    print(f"Grouped incidents: {len(responses)}")
    print(f"Recall calls: {memory.recall_calls}")
    print(f"Retain calls: {memory.retain_calls}")

    for response in responses:
        print("\n--- Incident ---")
        print(response.diagnosis)
        print(f"Action: {response.recommended_action}")


if __name__ == "__main__":
    asyncio.run(main())
