// Simple in-page log simulation and UI binding
const logsEl = document.getElementById("logs");
const filterEl = document.getElementById("filter");
const pauseBtn = document.getElementById("pause");
const clearBtn = document.getElementById("clear");
const counts = { normal: 0, warning: 0, danger: 0 };
let running = true;
let logBuffer = [];

function renderCounts() {
	document.getElementById("count-normal").textContent = counts.normal;
	document.getElementById("count-warning").textContent = counts.warning;
	document.getElementById("count-danger").textContent = counts.danger;
}

function addLog(severity, message, source) {
	const ts = new Date();
	const entry = {
		ts: ts.toISOString(),
		time: ts.toLocaleTimeString(),
		severity,
		message,
		source,
	};
	logBuffer.unshift(entry);
	counts[severity]++;
	renderCounts();
	if (running) renderList();
}

function renderList() {
	const filter = filterEl.value;
	logsEl.innerHTML = "";
	const list = logBuffer
		.filter((e) => (filter === "all" ? true : e.severity === filter))
		.slice(0, 200);
	for (const e of list) {
		const tr = document.createElement("tr");
		tr.className = "row-" + e.severity;
		tr.innerHTML = `<td class="small">${e.time}</td>
												<td>${escapeHtml(e.message)}</td>
												<td class="small">${escapeHtml(e.source)}</td>
												<td><span class="badge ${e.severity}">${e.severity.toUpperCase()}</span></td>`;
		logsEl.appendChild(tr);
	}
}

function escapeHtml(s) {
	return String(s).replace(
		/[&<>"']/g,
		(c) =>
			({
				"&": "&amp;",
				"<": "&lt;",
				">": "&gt;",
				'"': "&quot;",
				"'": "&#39;",
			})[c] || c,
	);
}

// Simple random generator for demo
const sampleSources = ["fw-01", "router-a", "switch-2", "sensor-7", "proxy-03"];
const normalMsgs = [
	"Heartbeat",
	"Connection established",
	"Packet transmitted",
	"OK response 200",
];
const warningMsgs = ["Latency spike", "Retransmission", "High jitter observed"];
const dangerMsgs = [
	"Packet loss threshold exceeded",
	"Connection refused repeatedly",
	"Possible intrusion detected",
];

function randomChoice(arr) {
	return arr[Math.floor(Math.random() * arr.length)];
}

function produceRandom() {
	const r = Math.random();
	if (r < 0.72)
		addLog("normal", randomChoice(normalMsgs), randomChoice(sampleSources));
	else if (r < 0.92)
		addLog("warning", randomChoice(warningMsgs), randomChoice(sampleSources));
	else addLog("danger", randomChoice(dangerMsgs), randomChoice(sampleSources));
	// keep buffer trimmed
	if (logBuffer.length > 2000) logBuffer.length = 2000;
}

// Start auto-producer
const interval = setInterval(() => {
	if (running) produceRandom();
}, 1200);

pauseBtn.addEventListener("click", () => {
	running = !running;
	pauseBtn.textContent = running ? "Pause" : "Resume";
	if (running) renderList();
});

clearBtn.addEventListener("click", () => {
	logBuffer = [];
	counts.normal = counts.warning = counts.danger = 0;
	renderCounts();
	renderList();
});

filterEl.addEventListener("change", renderList);

// seed a few entries
for (let i = 0; i < 12; i++) produceRandom();
renderList();

// Expose addLog to global for integration with real network sources
window.networkLog = { addLog };
