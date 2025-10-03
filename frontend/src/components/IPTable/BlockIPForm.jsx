import React, { useState, useEffect } from 'react';
import './BlockIPForm.css';

const BlockIPForm = () => {
  const [blockedIps, setBlockedIps] = useState([
    { ip: '192.168.45.23', blockedAt: '2023-06-15 14:23:45', reason: 'SQL Injection' },
    { ip: '101.202.33.44', blockedAt: '2023-06-15 11:45:23', reason: 'Port Scanning' },
    { ip: '67.89.123.45', blockedAt: '2023-06-15 10:12:34', reason: 'SSH Brute Force' },
    { ip: '45.67.89.123', blockedAt: '2023-06-14 18:30:15', reason: 'DDoS Attack' },
    { ip: '78.90.123.45', blockedAt: '2023-06-14 16:45:22', reason: 'XSS Attempt' }
  ]);

  // Function to generate random IP address
  const generateRandomIP = () => {
    return Array(4).fill(0).map(() => Math.floor(Math.random() * 256)).join('.');
  };

  // Function to generate random attack reason
  const generateRandomAttack = () => {
    const attacks = [
      'DDoS Attack',
      'SQL Injection',
      'XSS Attempt',
      'Port Scanning',
      'SSH Brute Force',
      'Malware Activity',
      'Suspicious Traffic',
      'Unauthorized Access',
      'Data Exfiltration',
      'Command Injection'
    ];
    return attacks[Math.floor(Math.random() * attacks.length)];
  };

  // Function to add a random attack
  const addRandomAttack = () => {
    const now = new Date();
    const blockedAt = now.toISOString().replace('T', ' ').substring(0, 19);
    const newBlockedIp = {
      ip: generateRandomIP(),
      blockedAt,
      reason: generateRandomAttack()
    };
    setBlockedIps(prevIps => [newBlockedIp, ...prevIps]);
  };

  // Simulate random attacks every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      addRandomAttack();
    }, 5000); // 5 seconds

    return () => clearInterval(interval);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const ipInput = e.target.elements.ipToBlock;
    const ip = ipInput.value.trim();
    
    if (ip) {
      const now = new Date();
      const blockedAt = now.toISOString().replace('T', ' ').substring(0, 19);
      const newBlockedIp = {
        ip,
        blockedAt,
        reason: 'Manual Block'
      };
      
      setBlockedIps([newBlockedIp, ...blockedIps]);
      ipInput.value = '';
      alert(`IP ${ip} has been blocked successfully via firewall.`);
    }
  };

  const handleUnblock = (ip) => {
    if (window.confirm(`Are you sure you want to unblock ${ip}?`)) {
      setBlockedIps(blockedIps.filter(blockedIp => blockedIp.ip !== ip));
      alert(`IP ${ip} has been unblocked successfully.`);
    }
  };

  return (
    <div className="dashboard-section">
      <div className="section-header">
        <h2 className="section-title">Block IP Address (Firewall)</h2>
      </div>
      <form className="firewall-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="form-control"
          placeholder="Enter IP address to block"
          name="ipToBlock"
          required
        />
        <button type="submit" className="btn btn-danger">Block IP</button>
      </form>
      <div className="attack-stats">
        <div className="stat-item">
          <span className="stat-label">Total Blocked IPs:</span>
          <span className="stat-value">{blockedIps.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Latest Attack:</span>
          <span className="stat-value">{blockedIps[0]?.blockedAt || 'None'}</span>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>IP Address</th>
            <th>Blocked At</th>
            <th>Reason</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {blockedIps.map((blockedIp, index) => (
            <tr key={index}>
              <td>{blockedIp.ip}</td>
              <td>{blockedIp.blockedAt}</td>
              <td>{blockedIp.reason}</td>
              <td>
                <button
                  className="btn btn-success btn-sm"
                  onClick={() => handleUnblock(blockedIp.ip)}
                >
                  Unblock
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BlockIPForm; 