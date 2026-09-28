# Incident Response Agent with Hindsight Memory

A reference implementation of the incident-response architecture described in the article:

**What Broke When Our Incident Agent Queried Hindsight Concurrently**

The project demonstrates:
1. Deterministic structural fingerprinting for noisy alerts.
2. Single-flight coalescing so identical concurrent memory questions share one recall.
3. Asynchronous, deduplicated retention so memory writes do not block incident triage.

## Important note

The source material provided for this repository contained the article and project structure, but not the original source-code files. Therefore, the files in this repository are a **clean reference implementation generated from the documented architecture and behavior**. They should not be presented as the original unpublished source code.

The article reports a simulated 140-alert scenario in which recall calls went from 140 to 4, P99 recall latency from 9,120 ms to 185 ms, retain records from 140 to 2, and connection errors from 38 to 0. Those published figures are described in the article; this repository's benchmark measures the implementation on the machine where it is run.

## Architecture

Alert Storm
  -> Alert Ingestion
  -> Structural Fingerprinting
  -> Single-Flight Request Coalescer
  -> Hindsight Memory
  -> Historical Resolution Matching
  -> Remediation Synthesis
  -> Incident Response
  -> Asynchronous Retention
  -> Hindsight Memory Update

## Project structure

```text
incident-agent/
├── incident_agent/
│   ├── __init__.py
│   ├── models.py
│   ├── fingerprint.py
│   ├── memory_client.py
│   ├── retain_queue.py
│   ├── orchestrator.py
│   └── simulator.py
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── tests/
│   ├── test_fingerprint.py
│   └── test_coalescing.py
├── app.py
├── benchmark.py
├── run_benchmark.py
├── run_simulation.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## Hindsight integration

The memory adapter uses the official Python Hindsight client when `HINDSIGHT_BASE_URL` is configured.

```python
from hindsight_client import Hindsight

client = Hindsight(base_url="http://localhost:8888")
client.retain(bank_id="my-bank", content="...")
client.recall(bank_id="my-bank", query="...")
```

The adapter also has a local in-memory fallback so the demo and tests can run without a Hindsight server.

Official Hindsight repository:
https://github.com/vectorize-io/hindsight

## Run the local demo

```bash
python -m pip install -r requirements.txt
python run_simulation.py database
```

## Run the benchmark

```bash
python run_benchmark.py
```

The benchmark compares one recall per alert with one recall per unique structural fingerprint.

## Run tests

```bash
python -m pytest -q
```

## Run the dashboard

```bash
python app.py
```

Then open `http://127.0.0.1:5000`.

## Connect to Hindsight

Install the client:

```bash
python -m pip install hindsight-client
```

Set:

```text
HINDSIGHT_BASE_URL=http://localhost:8888
HINDSIGHT_BANK_ID=incident-agent
```

Then run the simulation again.
