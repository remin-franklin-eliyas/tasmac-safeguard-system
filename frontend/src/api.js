import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://tasmac-safeguard-system-production.up.railway.app';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
