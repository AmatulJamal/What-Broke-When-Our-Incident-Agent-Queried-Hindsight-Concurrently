from collections import defaultdict

from .fingerprint import structural_fingerprint
from .models import Alert, IncidentResponse
from .retain_queue import RetainEvent


class IncidentOrchestrator:
    def __init__(self, memory_client, retain_queue, bank_id="incident-agent"):
        self.memory = memory_client
        self.retain_queue = retain_queue
        self.bank_id = bank_id

    async def triage(self, alerts: list[Alert]) -> list[IncidentResponse]:
        groups = defaultdict(list)
        for alert in alerts:
            groups[structural_fingerprint(alert)].append(alert)

        responses = []
        for fingerprint, group in groups.items():
            representative = group[0]
            query = (
                f"{representative.component} "
                f"{representative.error_type} "
                f"{representative.error_code}"
            )
            matches = await self.memory.recall(self.bank_id, query)

            diagnosis = f"{len(group)} alerts share failure fingerprint {fingerprint}."
            action = (
                matches[0].text
                if matches
                else f"Investigate {representative.component} and verify the "
                     f"{representative.error_type} condition before applying a runbook."
            )

            response = IncidentResponse(
                fingerprint=fingerprint,
                affected_alerts=len(group),
                diagnosis=diagnosis,
                recommended_action=action,
                memory_matches=tuple(matches),
            )
            responses.append(response)

            await self.retain_queue.enqueue(
                RetainEvent(
                    bank_id=self.bank_id,
                    content=f"{diagnosis} Verified action: {action}",
                    fingerprint=fingerprint,
                    metadata={"source": "incident-triage"},
                )
            )
        return responses
