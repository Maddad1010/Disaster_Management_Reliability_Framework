const lineOpts = {
  plugins: { legend: { labels: { color: "#e8eef7" } } },
  scales: {
    x: { ticks: { color: "#93a9c4" }, grid: { color: "#1e426e" } },
    y: { ticks: { color: "#93a9c4" }, grid: { color: "#1e426e" } },
  },
};

function makeLine(id, label, color) {
  return new Chart(document.getElementById(id), {
    type: "line",
    data: { labels: [], datasets: [{ label, data: [], borderColor: color, tension: 0.25, fill: false, pointRadius: 0 }] },
    options: lineOpts,
  });
}

const chartRt = makeLine("chartRt", "Response Time (ms)", "#f39c12");
const chartRps = makeLine("chartRps", "Requests / Second", "#2ecc71");
const chartCpu = makeLine("chartCpu", "CPU %", "#5dade2");
const chartMem = makeLine("chartMem", "Memory %", "#af7ac5");
const chartUsers = makeLine("chartUsers", "Active Users", "#e85d04");
const chartPie = new Chart(document.getElementById("chartPie"), {
  type: "doughnut",
  data: {
    labels: ["Success", "Failure"],
    datasets: [{ data: [1, 0], backgroundColor: ["#2a9d8f", "#d90429"] }],
  },
  options: { plugins: { legend: { labels: { color: "#e8eef7" } } } },
});

function updateLine(chart, labels, values) {
  chart.data.labels = labels;
  chart.data.datasets[0].data = values;
  chart.update("none");
}

async function tick() {
  const res = await fetch("/testing/api/live-metrics");
  const m = await res.json();
  const banner = document.getElementById("modeBanner");
  banner.textContent = m.data_mode || "DEMO DATA";
  banner.className = "mode-banner " + (m.data_mode === "LIVE TEST DATA" ? "mode-live" : "mode-demo");
  document.getElementById("testMeta").textContent = `${m.test_type || ""} ${m.test_id || ""} · ${m.state} · ${m.elapsed_seconds}s`;
  document.getElementById("mUsers").textContent = m.active_users;
  document.getElementById("mReq").textContent = Number(m.total_requests || 0).toLocaleString();
  document.getElementById("mOk").textContent = `${m.success_rate}%`;
  document.getElementById("mRt").textContent = `${m.avg_response_ms} ms`;
  document.getElementById("mErr").textContent = `${m.error_rate}%`;
  document.getElementById("mCpu").textContent = `${m.cpu_percent}%`;
  document.getElementById("mPerf").textContent = m.performance_score ? `${m.performance_score}/100` : "—";
  document.getElementById("mPerfLabel").textContent = m.performance_label || m.message || "";
  document.getElementById("mRel").textContent = m.reliability_score ? `${m.reliability_score}%` : "—";
  document.getElementById("relBar").style.width = `${Math.min(100, m.reliability_score || 0)}%`;
  document.getElementById("mStatus").textContent = m.overall_status || m.state;
  document.getElementById("mBreak").textContent = m.breaking_point_users
    ? `Approx. breaking point: ${m.breaking_point_users} users`
    : "";
  document.getElementById("mHealth").textContent = m.system_status;
  document.getElementById("mSys").textContent =
    `CPU ${m.cpu_percent}% · Memory ${m.memory_percent}% (${m.memory_mb} MB) · Disk ${m.disk_percent}% · Net ${m.net_mb_s} MB/s`;

  const s = m.series || {};
  updateLine(chartRt, s.time || [], s.response || []);
  updateLine(chartRps, s.time || [], s.rps || []);
  updateLine(chartCpu, s.time || [], s.cpu || []);
  updateLine(chartMem, s.time || [], s.memory || []);
  updateLine(chartUsers, s.time || [], s.users || []);
  chartPie.data.datasets[0].data = [m.successful_requests || 0, m.failed_requests || 0];
  chartPie.update("none");

  if (m.smoke_results && m.smoke_results.length) {
    document.getElementById("smokeBox").style.display = "block";
    document.getElementById("smokePre").textContent = m.smoke_results
      .map((r) => `${r.endpoint.padEnd(24, ".")} ${r.pass ? "PASS" : "FAIL"}  ${r.latency_ms} ms`)
      .join("\n");
  }
  if (m.html_report) {
    document.getElementById("reportBox").style.display = "block";
    document.getElementById("reportLinks").innerHTML = ["html", "json", "csv", "pdf"]
      .map((k) => {
        const file = m[k + "_report"];
        return file
          ? `<a class="btn btn-sm btn-outline-info me-2" href="/testing/reports/${file}">Download ${k.toUpperCase()}</a>`
          : "";
      })
      .join("");
  }
}

tick();
setInterval(tick, 1000);
