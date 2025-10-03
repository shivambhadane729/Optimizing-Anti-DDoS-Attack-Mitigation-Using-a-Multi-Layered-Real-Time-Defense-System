import React, { useEffect, useState, useCallback } from 'react';
import AttackLogs from '../components/Dashboard/AttackLogs';
import './Response.css';

const Response = () => {
  const [status, setStatus] = useState('Disconnected');

  const connectWebSocket = useCallback(() => {
    const websocket = new WebSocket('ws://localhost:5000/ws/server-health');

    websocket.onopen = () => {
      console.log('✅ WebSocket connection opened');
      setStatus('Connected');
    };

    websocket.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setStatus('Error');
    };

    websocket.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      setStatus('Disconnected');
      setTimeout(() => {
        console.log('🔁 Attempting to reconnect...');
        connectWebSocket();
      }, 5000);
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('📡 WebSocket message:', data);
    };

    return websocket;
  }, []);

  useEffect(() => {
    const ws = connectWebSocket();

    return () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  return (
    <div className="response-page">
      <div className="response-header">
        <h2>Attack Response Center</h2>
        <div className="connection-status">
          <span className={`status-indicator ${status.toLowerCase()}`}></span>
          <span>Status: {status}</span>
        </div>
      </div>

      <div className="response-content">
        <AttackLogs />
      </div>
    </div>
  );
};

export default Response;
