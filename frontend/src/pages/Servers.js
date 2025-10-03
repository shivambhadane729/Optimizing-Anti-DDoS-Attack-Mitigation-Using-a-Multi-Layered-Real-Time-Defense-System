import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Servers.css';

const Servers = () => {
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    requestsPerSecond: 1248,
    avgResponseTime: 142,
    errorRate: 0.12
  });

  const fetchServerData = async () => {
    try {
      const response = await axios.get('http://localhost:3000/api/all-server-health');

      setServers(response.data || []);
      setLoading(false);
      setError(null);
    } catch (error) {
      console.error('Error fetching server data:', error);
      setError('Failed to load server data.');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServerData();
    const interval = setInterval(fetchServerData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="loading">Loading server data...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="container">
      <header>
        <h1>Load Balancer Dashboard</h1>
        <div className="status healthy">All Systems Operational</div>
      </header>
      
      <div className="dashboard">
        <div className="servers-panel">
          <h2>Server Nodes</h2>
          <div className="server-list">
            {servers.map((server, index) => (
              <div key={index} className="server-card">
                <div className="server-info">
                  <div className={`status-indicator ${server.status.toLowerCase()}`}></div>
                  <span className="server-name">{server.name}</span>
                </div>
                <div className="server-stats">
                  <span>CPU: {server.cpu}%</span>
                  <span>RAM: {server.ram}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="visualization">
          <div className="load-balancer">LB</div>
          
          {/* Server Nodes */}
          <div className="server-nodes">
  {servers.map((_, index) => (
    <div
      key={index}
      className="server-node"
      style={{
        top: `${30 + (index * 60)}px`,
        left: `${200 + (Math.sin(index) * 100)}px`,
        position: 'absolute'
      }}
    >
      {index + 1}
    </div>
  ))}
</div>

          
          {/* Connections */}
          <svg width="100%" height="100%" style={{ position: 'absolute', top: 0, left: 0, zIndex: 1 }}>
  {servers.map((_, index) => (
    <line
      key={index}
      x1="50%" y1="50%"
      x2={`${30 + (index * 60)}`} y2={`${80 + (index * 60)}`}
      stroke="var(--primary)"
      strokeWidth="2"
    />
  ))}
</svg>

        </div>
      </div>
      
      <div className="stats">
        <div className="stat-card">
          <div className="stat-label">Requests per second</div>
          <div className="stat-value">{stats.requestsPerSecond.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg response time</div>
          <div className="stat-value">{stats.avgResponseTime}ms</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Error rate</div>
          <div className="stat-value">{stats.errorRate}%</div>
        </div>
      </div>
    </div>
  );
};

export default Servers; 