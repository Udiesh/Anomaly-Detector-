import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import StatBar from "./components/StatBar";
import UserRiskPanel from "./components/UserRiskPanel";
import AnomalyTable from "./components/AnomalyTable";
import "./index.css";

export default function App() {
  const [anomalies, setAnomalies] = useState([]);
  const [live, setLive] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/anomalies")
      .then(res => res.json())
      .then(data => setAnomalies(data));

    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onmessage = (event) => {
      const a = JSON.parse(event.data);
      setAnomalies(prev => [a, ...prev]);
      setLive(true);
    };

    return () => ws.close();
  }, []);

  const chartData = ["user1","user2","user3","user4","user5"].map(u => ({
    user: u,
    count: anomalies.filter(a => a.user_id === u).length
  }));

  return (
    <div style={{ maxWidth: "1600px", margin: "0 auto", padding: "32px 32px" }}>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "16px", borderBottom: "1px solid var(--border)", paddingBottom: "10px" }}>
  <div style={{
    width: "8px", height: "8px",
    background: live ? "var(--green)" : "var(--text-muted)",
    boxShadow: live ? "0 0 8px var(--green)" : "none"
  }} />
  <h1 style={{ fontFamily: "var(--mono)", fontSize: "14px", letterSpacing: "4px", color: "var(--accent)" }}>
    FTRACE
  </h1>
  <span style={{ fontFamily: "var(--mono)", fontSize: "10px", color: "var(--text-muted)", letterSpacing: "2px" }}>
    FINANCIAL TRANSACTION ANALYZER
  </span>
  <span style={{ marginLeft: "auto", fontFamily: "var(--mono)", fontSize: "10px", color: live ? "var(--green)" : "var(--text-muted)" }}>
    {live ? "[ LIVE ]" : "[ STANDBY ]"}
  </span>
</div>
      {/* Stats */}
      <StatBar anomalies={anomalies} />

    {/* Chart + Risk Panel */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: "8px", marginBottom: "16px", alignItems: "start" }}>
        <div style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
          <div className="panel-header">ANOMALIES PER USER</div>
          <div style={{ padding: "12px" }}>
            <ResponsiveContainer width="100%" height={140}>
              <BarChart data={chartData}>
                <XAxis dataKey="user" stroke="var(--border)" tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "Share Tech Mono" }} />
                <YAxis stroke="var(--border)" tick={{ fill: "var(--text-muted)", fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "var(--surface2)", border: "1px solid var(--border)", fontFamily: "Share Tech Mono", fontSize: "12px" }} />
                <Bar dataKey="count" fill="var(--accent)" opacity={0.7} radius={[0,0,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <UserRiskPanel anomalies={anomalies} />
      </div>

      {/* Table */}
      <AnomalyTable anomalies={anomalies} />
    </div>
  );
}