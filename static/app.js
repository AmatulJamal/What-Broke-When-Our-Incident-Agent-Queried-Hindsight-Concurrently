const run = document.getElementById("run");

run.addEventListener("click", async () => {
  run.disabled = true;
  run.textContent = "Running...";

  const count = Number(document.getElementById("count").value);
  const response = await fetch("/api/simulate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({count})
  });

  const data = await response.json();

  document.getElementById("alerts").textContent = data.alerts;
  document.getElementById("incidents").textContent = data.incidents;
  document.getElementById("recalls").textContent = data.recall_calls;
  document.getElementById("retains").textContent = data.retain_calls;

  const tbody = document.getElementById("results");
  tbody.innerHTML = "";

  for (const item of data.responses) {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${item.fingerprint}</td>
      <td>${item.affected_alerts}</td>
      <td>${item.diagnosis}</td>
      <td>${item.action}</td>`;
    tbody.appendChild(row);
  }

  run.disabled = false;
  run.textContent = "Run alert storm";
});
