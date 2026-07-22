import axios from "axios";

export const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8080/api";
export const WS_BASE = import.meta.env.VITE_WS_URL || "ws://localhost:8080/ws";

const client = axios.create({ baseURL: API_BASE });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("servicehub_access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default client;
