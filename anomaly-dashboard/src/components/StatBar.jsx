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

  return (
    <div className="statbar">
      {stats.map((s, i) => (
        <div key={i} className="stat-card">
          <span className="stat-value" style={{ color: s.color }}>{s.value}</span>
          <span className="stat-label">{s.label}</span>
        </div>
      ))}
    </div>
  );
}