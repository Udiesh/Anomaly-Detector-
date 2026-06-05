export default function StatBar({ anomalies }) {
  const high = anomalies.filter(a => a.risk_level === "HIGH").length;
  const medium = anomalies.filter(a => a.risk_level === "MEDIUM").length;
  const users = [...new Set(anomalies.map(a => a.user_id))].length;

  const stats = [
    { label: "Total Alerts", value: anomalies.length, color: "var(--text-primary)" },
    { label: "High Risk", value: high, color: "var(--accent)" },
    { label: "Medium Risk", value: medium, color: "var(--orange)" },
    { label: "Users Flagged", value: users, color: "var(--green)" },
  ];

  const colorMap = {
  "Total Alerts": "var(--text-primary)",
  "High Risk": "var(--red)",
  "Medium Risk": "var(--yellow)",
  "Users Flagged": "var(--green)"
};

return (
  <div className="statbar">
    {stats.map((s, i) => (
      <div key={i} className="stat-card">
        <div className="stat-card-header">{s.label}</div>
        <span className="stat-value" style={{ color: colorMap[s.label] }}>{s.value}</span>
      </div>
    ))}
  </div>
);
}