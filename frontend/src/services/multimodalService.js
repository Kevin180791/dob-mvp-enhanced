import { api } from './api';

/**
 * Service für die Interaktion mit der Multimodal-API
 */
export const multimodalService = {
  /**
   * Analysiert ein Dokument
   * @param {Object} data - Analysedaten
   * @param {string} data.file_id - ID der zu analysierenden Datei
   * @param {string} data.analysis_type - Typ der Analyse
   * @param {string} data.query - Optionale Frage oder Anweisung
   * @param {string} data.model - Zu verwendendes Modell
   * @returns {Promise<Object>} Analyseergebnisse
   */
  async analyzeDocument(data) {
    const response = await api.post('/multimodal/analyze', data);
    return response.data;
  },

  /**
   * Lädt ein Dokument hoch
   * @param {FormData} formData - FormData mit der Datei
   * @returns {Promise<Object>} Hochgeladene Datei
   */
  async uploadDocument(formData) {
    const response = await api.post('/multimodal/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  /**
   * Holt ein Dokument anhand seiner ID
   * @param {string} id - ID des Dokuments
   * @returns {Promise<Object>} Dokument
   */
  async getDocument(id) {
    const response = await api.get(`/multimodal/documents/${id}`);
    return response.data;
  },

  /**
   * Sucht nach Dokumenten
   * @param {Object} params - Suchparameter
   * @param {string} params.query - Suchbegriff
   * @param {string} params.collection - Dokumentensammlung
   * @param {number} params.limit - Maximale Anzahl der Ergebnisse
   * @returns {Promise<Object>} Suchergebnisse
   */
  async searchDocuments(params) {
    const response = await api.get('/multimodal/search', { params });
    return response.data;
  },

  /**
   * Extrahiert Daten aus einem Dokument
   * @param {Object} data - Extraktionsdaten
   * @param {string} data.file_id - ID der zu extrahierenden Datei
   * @param {string} data.extraction_type - Typ der Extraktion
   * @param {Object} data.options - Extraktionsoptionen
   * @returns {Promise<Object>} Extrahierte Daten
   */
  async extractData(data) {
    const response = await api.post('/multimodal/extract', data);
    return response.data;
  },

  /**
   * Vergleicht zwei Dokumente
   * @param {Object} data - Vergleichsdaten
   * @param {string} data.file_id_1 - ID der ersten Datei
   * @param {string} data.file_id_2 - ID der zweiten Datei
   * @param {string} data.comparison_type - Typ des Vergleichs
   * @returns {Promise<Object>} Vergleichsergebnisse
   */
  async compareDocuments(data) {
    const response = await api.post('/multimodal/compare', data);
    return response.data;
  },

  /**
   * Generiert eine Zusammenfassung eines Dokuments
   * @param {Object} data - Zusammenfassungsdaten
   * @param {string} data.file_id - ID der zu zusammenfassenden Datei
   * @param {string} data.summary_type - Typ der Zusammenfassung
   * @param {number} data.max_length - Maximale Länge der Zusammenfassung
   * @returns {Promise<Object>} Zusammenfassung
   */
  async summarizeDocument(data) {
    const response = await api.post('/multimodal/summarize', data);
    return response.data;
  },

  /**
   * Holt alle verfügbaren Modelle
   * @returns {Promise<Array>} Liste der verfügbaren Modelle
   */
  async getAvailableModels() {
    const response = await api.get('/multimodal/models');
    return response.data;
  },

  /**
   * Holt alle verfügbaren Dokumentensammlungen
   * @returns {Promise<Array>} Liste der verfügbaren Dokumentensammlungen
   */
  async getDocumentCollections() {
    const response = await api.get('/multimodal/collections');
    return response.data;
  },

  /**
   * Erstellt eine neue Dokumentensammlung
   * @param {Object} data - Sammlungsdaten
   * @param {string} data.name - Name der Sammlung
   * @param {string} data.description - Beschreibung der Sammlung
   * @returns {Promise<Object>} Erstellte Sammlung
   */
  async createDocumentCollection(data) {
    const response = await api.post('/multimodal/collections', data);
    return response.data;
  },

  /**
   * Fügt ein Dokument zu einer Sammlung hinzu
   * @param {string} collectionId - ID der Sammlung
   * @param {string} documentId - ID des Dokuments
   * @returns {Promise<Object>} Aktualisierte Sammlung
   */
  async addDocumentToCollection(collectionId, documentId) {
    const response = await api.post(`/multimodal/collections/${collectionId}/documents/${documentId}`);
    return response.data;
  },

  /**
   * Entfernt ein Dokument aus einer Sammlung
   * @param {string} collectionId - ID der Sammlung
   * @param {string} documentId - ID des Dokuments
   * @returns {Promise<Object>} Aktualisierte Sammlung
   */
  async removeDocumentFromCollection(collectionId, documentId) {
    const response = await api.delete(`/multimodal/collections/${collectionId}/documents/${documentId}`);
    return response.data;
  }
};

