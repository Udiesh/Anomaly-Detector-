import { useState, useEffect } from "react";

function App() {
  const [anomalies, setAnomalies] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/anomalies")
      .then(res => res.json())
      .then(data => setAnomalies(data));

    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onmessage = (event) => {
      const newAnomaly = JSON.parse(event.data);
      setAnomalies(prev => [newAnomaly, ...prev]);
    };

    return () => ws.close();
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "monospace" }}>
      <h1>🚨 Anomaly Detection Dashboard</h1>
      <table border="1" cellPadding="10" width="100%">
        <thead>
          <tr>
            <th>User</th>
            <th>Amount</th>
            <th>Merchant</th>
            <th>Risk Level</th>
            <th>Explanation</th>
          </tr>
        </thead>
        <tbody>
          {anomalies.map((a, i) => (
            <tr key={i} style={{ background: a.risk_level === "HIGH" ? "#ffcccc" : a.risk_level === "MEDIUM" ? "#fff3cc" : "white" }}>
              <td>{a.user_id}</td>
              <td>₹{a.amount}</td>
              <td>{a.merchant}</td>
              <td>{a.risk_level || "N/A"}</td>
              <td>{a.explanation}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;