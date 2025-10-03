import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Chip,
  Box,
  Alert,
  Button,
} from '@mui/material';
import MemoryIcon from '@mui/icons-material/Memory';
import SpeedIcon from '@mui/icons-material/Speed';
import CloudDoneIcon from '@mui/icons-material/CloudDone';
import CloudOffIcon from '@mui/icons-material/CloudOff';

const ServerHealth = () => {
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchServerHealth = async () => {
    try {
      setError(null);
      const response = await axios.get('http://localhost:5000/api/server-health/live/all');
      setServers(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching server health:', err);
      setError(err?.response?.data?.detail || err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServerHealth();
    const interval = setInterval(fetchServerHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box sx={{ textAlign: 'center', mt: 5 }}>
        <CircularProgress />
        <Typography variant="body1" mt={2}>Loading server health...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button variant="contained" sx={{ mt: 2 }} onClick={fetchServerHealth}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ px: 4, py: 2 }}>
      <Typography variant="h4" gutterBottom>
        Server Health Overview
      </Typography>
      <Grid container spacing={3}>
        {servers.map((server, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card
              sx={{
                borderLeft: `6px solid ${server.status === 'healthy' ? '#4caf50' : '#f44336'}`,
                boxShadow: 3,
              }}
            >
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {server.name}
                </Typography>

                <Chip
                  icon={server.status === 'healthy' ? <CloudDoneIcon /> : <CloudOffIcon />}
                  label={server.status.toUpperCase()}
                  color={server.status === 'healthy' ? 'success' : 'error'}
                  sx={{ mb: 1 }}
                />

                <Typography variant="body2" gutterBottom>
                  <SpeedIcon fontSize="small" /> CPU: {server.cpu}% 
                </Typography>
                <Typography variant="body2">
                  <MemoryIcon fontSize="small" /> RAM: {server.ram}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default ServerHealth;
