import React, { useState, useEffect } from 'react';
import './Alerts.css';

const Alerts = () => {
  const [notificationType, setNotificationType] = useState('Email');
  const [severityLevels, setSeverityLevels] = useState({
    Critical: true,
    High: false,
    Medium: false,
    Low: false,
  });
  const [frequency, setFrequency] = useState('Real-Time');
  const [userChannels, setUserChannels] = useState({
    Email: true,
    SMS: false,
    'In-App': false,
  });
  const [filterDate, setFilterDate] = useState('');
  const [filterType, setFilterType] = useState('All Types');
  const [alertHistory, setAlertHistory] = useState([]);
  const [emailSent, setEmailSent] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [userEmails, setUserEmails] = useState(() => {
    try {
      const storedEmails = localStorage.getItem('userEmails');
      return storedEmails ? JSON.parse(storedEmails) : [];
    } catch (error) {
      console.error("Failed to parse userEmails from localStorage", error);
      return [];
    }
  });
  const [newEmail, setNewEmail] = useState('');

  useEffect(() => {
    localStorage.setItem('userEmails', JSON.stringify(userEmails));
  }, [userEmails]);

  // Attack types based on severity
  const getAttackType = (severity) => {
    const attackTypes = {
      Critical: ['SQL Injection Attack', 'Zero-Day Exploit', 'Data Breach'],
      High: ['Brute Force Attack', 'DDoS Attack', 'Malware Detection'],
      Medium: ['Suspicious Login', 'Port Scanning', 'Phishing Attempt'],
      Low: ['Failed Login', 'Unusual Traffic', 'Minor Security Warning']
    };
    const types = attackTypes[severity] || ['Security Alert'];
    return types[Math.floor(Math.random() * types.length)];
  };

  // Simulate email API call
  const sendEmailAlert = async (severity, attackType, emailToSendTo) => {
    
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const emailData = {
        to: emailToSendTo,
        subject: `Security Alert: ${severity} - ${attackType}`,
        body: `
          Alert Configuration Activated
          
          Severity Level: ${severity}
          Attack Type: ${attackType}
          Notification Type: Email
          Frequency: Real-Time
          
          This is an automated security alert. Please take immediate action if this is a critical threat.
          
          Time: ${new Date().toLocaleString()}
        `
      };

      // In a real application, you would make an actual API call here
      console.log('Email sent:', emailData);
      
      // Add to alert history
      const newAlert = {
        id: Date.now(),
        date: new Date().toISOString().split('T')[0],
        type: 'Email',
        severity: severity,
        status: 'Unread',
        attackType: attackType,
        message: `${severity} alert: ${attackType} detected to ${emailToSendTo}`
      };
      
      setAlertHistory(prev => [newAlert, ...prev]);
      
    } catch (error) {
      console.error('Error sending email:', error);
    }
  };

  const handleSeverityChange = (level) => {
    setSeverityLevels((prev) => ({ ...prev, [level]: !prev[level] }));
  };

  const handleAddEmail = () => {
    if (newEmail && !userEmails.includes(newEmail)) {
      setUserEmails(prev => [...prev, newEmail]);
      setNewEmail('');
    } else if (userEmails.includes(newEmail)) {
      alert('This email is already added.');
    }
  };

  const handleDeleteEmail = (emailToDelete) => {
    setUserEmails(prev => prev.filter(email => email !== emailToDelete));
  };

  const handleSendTestAlert = async () => {
    if (userEmails.length === 0) {
      alert('Please add at least one email address.');
      return;
    }
    const activeSeverities = Object.keys(severityLevels).filter(level => severityLevels[level]);
    if (activeSeverities.length === 0) {
      alert('Please select at least one severity level');
      return;
    }

    setIsLoading(true);
    setEmailSent(false); // Reset success message before new sends

    const randomSeverity = activeSeverities[Math.floor(Math.random() * activeSeverities.length)];
    const attackType = getAttackType(randomSeverity);

    for (const email of userEmails) {
      await sendEmailAlert(randomSeverity, attackType, email);
    }
    
    setIsLoading(false);
    setEmailSent(true);
    setTimeout(() => setEmailSent(false), 5000);
  };

  const markAsRead = (id) => {
    setAlertHistory(prev => 
      prev.map(alert => 
        alert.id === id ? { ...alert, status: 'Read' } : alert
      )
    );
  };

  const deleteAlert = (id) => {
    setAlertHistory(prev => prev.filter(alert => alert.id !== id));
  };

  const getSeverityBadgeClass = (severity) => {
    const badgeClasses = {
      Critical: 'badge-critical',
      High: 'badge-high',
      Medium: 'badge-medium',
      Low: 'badge-low'
    };
    return badgeClasses[severity] || 'badge-caution';
  };

  const filteredHistory = alertHistory.filter(alert => {
    const dateMatch = !filterDate || alert.date === filterDate;
    const typeMatch = filterType === 'All Types' || alert.type === filterType;
    return dateMatch && typeMatch;
  });

  if (emailSent) {
    return (
      <div className="email-success-overlay">
        <div className="email-success-card">
          <div className="email-success-icon">
            <svg width="64" height="64" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="email-success-title">Email Sent Successfully!</h2>
          <p className="email-success-desc">
            Security alert has been sent to configured emails. The alert details have been added to your history.
          </p>
          <button 
            onClick={() => setEmailSent(false)}
            className="btn btn-primary"
          >
            Back to Alerts
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="alerts-container">
      <h2 className="alerts-title">Alerts & Notifications</h2>
      <p className="alerts-desc">Configure how you receive alerts and manage alert history.</p>
      
      <div className="alerts-row">
        {/* Alert Configuration Card */}
        <div className="alerts-card">
          <h3>Alert Configuration</h3>
          
          <div className="form-group">
            <label>Email Addresses:</label>
            <div className="email-input-group">
              <input
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="Enter email for alerts"
                className="email-input"
              />
              <button onClick={handleAddEmail} className="btn btn-secondary add-email-btn">Add</button>
            </div>
            <div className="saved-emails">
              {userEmails.length > 0 ? (
                userEmails.map((email, index) => (
                  <div key={index} className="email-tag">
                    <span>{email}</span>
                    <button onClick={() => handleDeleteEmail(email)} className="delete-email-btn">Delete</button>
                  </div>
                ))
              ) : (
                <p className="no-emails-msg">No emails added yet.</p>
              )}
            </div>
          </div>

          <div className="form-group">
            <label>Severity Level:</label>
            <div className="checkbox-group">
              {['Critical', 'High', 'Medium', 'Low'].map(level => (
                <label key={level}>
                  <input
                    type="checkbox"
                    checked={severityLevels[level]}
                    onChange={() => handleSeverityChange(level)}
                  />
                  {level}
                </label>
              ))}
            </div>
          </div>
          
          <div className="alerts-actions">
            <button 
              onClick={handleSendTestAlert}
              disabled={isLoading}
              className="btn btn-primary"
            >
              {isLoading ? 'Sending...' : 'Send Alert'}
            </button>
          </div>
        </div>
      </div>

      {/* Alert History Card */}
      <div className="alerts-history-card">
        <h3>Alert History</h3>
        
        <div className="alerts-history-filters">
          <div className="form-group">
            <label>Date:</label>
            <input 
              type="date" 
              value={filterDate} 
              onChange={(e) => setFilterDate(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Alert Type:</label>
            <select 
              value={filterType} 
              onChange={(e) => setFilterType(e.target.value)}
            >
              <option value="All Types">All Types</option>
              <option value="Email">Email</option>
              <option value="SMS">SMS</option>
              <option value="In-App">In-App</option>
            </select>
          </div>
          <button className="btn btn-secondary">Filter Alerts</button>
        </div>
        
        <table className="alerts-history-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Severity</th>
              <th>Attack Type</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredHistory.length > 0 ? (
              filteredHistory.map((alert) => (
                <tr key={alert.id}>
                  <td>{alert.date}</td>
                  <td>{alert.type}</td>
                  <td>
                    <span className={`badge ${getSeverityBadgeClass(alert.severity)}`}>
                      {alert.severity}
                    </span>
                  </td>
                  <td>{alert.attackType}</td>
                  <td>{alert.status}</td>
                  <td>
                    {alert.status === 'Unread' && (
                      <button 
                        onClick={() => markAsRead(alert.id)}
                        className="btn btn-info btn-sm"
                        style={{marginRight: '5px'}}
                      >
                        Mark Read
                      </button>
                    )}
                    <button 
                      onClick={() => deleteAlert(alert.id)}
                      className="btn btn-danger btn-sm"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" style={{textAlign: 'center', padding: '20px'}}>No alerts found</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Alerts; 