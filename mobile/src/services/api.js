import axios from 'axios';
import { Platform } from 'react-native';

// Automatically pointing to the local computer's network IP for Expo Go physical device testing
const API_BASE_URL = 'http://10.16.87.39:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
    'Bypass-Tunnel-Reminder': 'true' // For localtunnel fallback
  },
});

export const loginUser = async (mobile) => {
  const response = await api.post('/auth/login', { mobile });
  return response.data;
};

export const registerUser = async (profile) => {
  const response = await api.post('/auth/register', profile);
  return response.data;
};

export const getDailyLog = async () => {
  const response = await api.get('/diet/daily_log');
  return response.data;
};

export const updateDailyLog = async (logUpdate) => {
  const response = await api.post('/diet/daily_log', logUpdate);
  return response.data;
};

export const chatWithBot = async (history, newMessage) => {
  const response = await api.post('/ai/chat', { history, new_message: newMessage });
  return response.data;
};
