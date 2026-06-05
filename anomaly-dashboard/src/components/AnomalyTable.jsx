export default function AnomalyTable({ anomalies }) {
  const levelColor = {
    HIGH: "var(--accent)",
    MEDIUM: "var(--orange)",
    LOW: "var(--green)"
  };

  return (
    <div className="table-wrap">
      <p className="panel-title">Live Anomaly Feed</p>
      <table className="anomaly-table">
        <thead>
          <tr>
            {["User", "Amount", "Merchant", "Type", "Risk", "Explanation"].map(h => (
              <th key={h}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {anomalies.map((a, i) => (
            <tr key={i} className="anomaly-row">
              <td className="mono">{a.user_id}</td>
              <td className="amount">₹{parseFloat(a.amount).toLocaleString("en-IN")}</td>
              <td>{a.merchant}</td>
              <td className="muted">{a.transaction_type}</td>
              <td>
                <span className="badge" style={{ color: levelColor[a.risk_level] || "var(--text-muted)", borderColor: levelColor[a.risk_level] || "var(--border)" }}>
                  {a.risk_level || "N/A"}
                </span>
              </td>
              <td className="explanation">{a.explanation}</td>
            </tr>
          ))}
          {anomalies.length === 0 && (
            <tr>
              <td colSpan="6" className="empty">Monitoring... no anomalies yet</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}