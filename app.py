from flask import Flask, jsonify, request

from incident_agent.memory_client import build_memory_client
from incident_agent.orchestrator import IncidentOrchestrator
from incident_agent.retain_queue import AsyncRetainQueue
from incident_agent.simulator import generate_alerts

app = Flask(__name__, static_folder="static", static_url_path="/static")
memory = build_memory_client()
queue = AsyncRetainQueue(memory)
started = False


def ensure_queue():
    global started
    if not started:
        import asyncio
        asyncio.run(queue.start())
        started = True


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.post("/api/simulate")
def simulate():
    import asyncio
    ensure_queue()
    payload = request.get_json(silent=True) or {}
    count = max(1, min(int(payload.get("count", 20)), 140))

    async def run():
        orchestrator = IncidentOrchestrator(memory, queue)
        responses = await orchestrator.triage(generate_alerts(count))
        await queue.drain()
        return responses

    responses = asyncio.run(run())
    return jsonify({
        "alerts": count,
        "incidents": len(responses),
        "recall_calls": memory.recall_calls,
        "retain_calls": memory.retain_calls,
        "responses": [
            {
                "fingerprint": r.fingerprint,
                "affected_alerts": r.affected_alerts,
                "diagnosis": r.diagnosis,
                "action": r.recommended_action,
            }
            for r in responses
        ],
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
