export default function UserRiskPanel({ anomalies }) {
  const users = ["user1", "user2", "user3", "user4", "user5"];

  const getScore = (user) => {
    const userAnomalies = anomalies.filter(a => a.user_id === user);
    return userAnomalies.reduce((acc, a) => {
      const amount = parseFloat(a.amount);
      if (amount > 15000) return acc + 30;
      if (amount > 10000) return acc + 20;
      if (amount > 5000) return acc + 10;
      return acc;
    }, 0);
  };

  const getLevel = (score) => {
    if (score >= 50) return { label: "HIGH", color: "var(--accent)" };
    if (score >= 20) return { label: "MEDIUM", color: "var(--orange)" };
    return { label: "LOW", color: "var(--green)" };
  };

  return (
  <div className="risk-panel">
    <div className="panel-header">USER RISK SCORES</div>
    <div className="panel-body">
      {users.map(u => {
        const score = getScore(u);
        const level = getLevel(score);
        const pct = Math.min((score / 100) * 100, 100);
        return (
          <div key={u} className="risk-row">
            <span className="risk-user">{u}</span>
            <div className="risk-bar-wrap">
              <div className="risk-bar-fill" style={{ width: `${pct}%`, background: level.color }} />
            </div>
            <span className="risk-badge" style={{ color: level.color }}>{level.label}</span>
          </div>
        );
      })}
    </div>
  </div>
);
}