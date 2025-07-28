import axios from 'axios';

// API-Basis-URL aus Umgebungsvariablen oder Standard
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

// Axios-Instanz mit Basis-URL und Standardkonfiguration
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request-Interceptor für Authentifizierung
api.interceptors.request.use(
  (config) => {
    // Token aus localStorage holen (falls vorhanden)
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response-Interceptor für Fehlerbehandlung
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Globale Fehlerbehandlung
    if (error.response) {
      // Der Server hat mit einem Statuscode außerhalb des Bereichs 2xx geantwortet
      console.error('API Error:', error.response.status, error.response.data);
      
      // Bei 401 Unauthorized: Token abgelaufen oder ungültig
      if (error.response.status === 401) {
        localStorage.removeItem('auth_token');
        // Optional: Weiterleitung zur Login-Seite
        // window.location.href = '/login';
      }
    } else if (error.request) {
      // Die Anfrage wurde gestellt, aber keine Antwort erhalten
      console.error('API Request Error:', error.request);
    } else {
      // Beim Einrichten der Anfrage ist ein Fehler aufgetreten
      console.error('API Setup Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

/**
 * API-Service für alle HTTP-Anfragen
 */
export const apiService = {
  /**
   * GET-Anfrage
   * @param {string} url - Endpunkt-URL
   * @param {Object} params - Query-Parameter
   * @returns {Promise} - Antwort-Promise
   */
  async get(url, params = {}) {
    return api.get(url, { params });
  },
  
  /**
   * POST-Anfrage
   * @param {string} url - Endpunkt-URL
   * @param {Object} data - Anfragedaten
   * @returns {Promise} - Antwort-Promise
   */
  async post(url, data = {}) {
    return api.post(url, data);
  },
  
  /**
   * PUT-Anfrage
   * @param {string} url - Endpunkt-URL
   * @param {Object} data - Anfragedaten
   * @returns {Promise} - Antwort-Promise
   */
  async put(url, data = {}) {
    return api.put(url, data);
  },
  
  /**
   * PATCH-Anfrage
   * @param {string} url - Endpunkt-URL
   * @param {Object} data - Anfragedaten
   * @returns {Promise} - Antwort-Promise
   */
  async patch(url, data = {}) {
    return api.patch(url, data);
  },
  
  /**
   * DELETE-Anfrage
   * @param {string} url - Endpunkt-URL
   * @returns {Promise} - Antwort-Promise
   */
  async delete(url) {
    return api.delete(url);
  },
  
  /**
   * Datei-Upload
   * @param {string} url - Endpunkt-URL
   * @param {FormData} formData - FormData mit Dateien
   * @param {Function} onProgress - Callback für Upload-Fortschritt
   * @returns {Promise} - Antwort-Promise
   */
  async uploadFile(url, formData, onProgress = null) {
    return api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress ? (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percentCompleted);
      } : undefined,
    });
  },
  
  /**
   * Datei-Download
   * @param {string} url - Endpunkt-URL
   * @param {string} filename - Dateiname für den Download
   * @returns {Promise} - Antwort-Promise
   */
  async downloadFile(url, filename) {
    const response = await api.get(url, {
      responseType: 'blob',
    });
    
    // Blob-URL erstellen und Download auslösen
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
    
    return response;
  },
};

