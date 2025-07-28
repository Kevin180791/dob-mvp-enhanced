import { api } from './api';

/**
 * Service für die Verwaltung von RFIs (Requests for Information)
 */
export const rfiService = {
  /**
   * RFIs abrufen
   * @param {Object} params - Optionale Parameter (project_id, status, priority, search)
   * @returns {Promise<Array>} Liste der RFIs
   */
  async getRFIs(params = {}) {
    try {
      const response = await api.get('/rfi', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching RFIs:', error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Abrufen der RFIs');
    }
  },

  /**
   * RFI nach ID abrufen
   * @param {string} id - RFI-ID
   * @returns {Promise<Object>} RFI-Objekt
   */
  async getRFIById(id) {
    try {
      const response = await api.get(`/rfi/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching RFI ${id}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Abrufen der RFI');
    }
  },

  /**
   * RFI erstellen
   * @param {FormData} formData - FormData mit RFI-Daten und Anhängen
   * @returns {Promise<Object>} Erstellte RFI
   */
  async createRFI(formData) {
    try {
      const response = await api.uploadFile('/rfi', formData);
      return response.data;
    } catch (error) {
      console.error('Error creating RFI:', error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Erstellen der RFI');
    }
  },

  /**
   * RFI aktualisieren
   * @param {string} id - RFI-ID
   * @param {Object} data - Zu aktualisierende Daten
   * @returns {Promise<Object>} Aktualisierte RFI
   */
  async updateRFI(id, data) {
    try {
      const response = await api.patch(`/rfi/${id}`, data);
      return response.data;
    } catch (error) {
      console.error(`Error updating RFI ${id}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Aktualisieren der RFI');
    }
  },

  /**
   * RFI löschen
   * @param {string} id - RFI-ID
   * @returns {Promise<Object>} Antwort
   */
  async deleteRFI(id) {
    try {
      const response = await api.delete(`/rfi/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting RFI ${id}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Löschen der RFI');
    }
  },

  /**
   * Kommentar zu RFI hinzufügen
   * @param {string} id - RFI-ID
   * @param {Object} commentData - Kommentar-Daten
   * @returns {Promise<Object>} Aktualisierte RFI
   */
  async addComment(id, commentData) {
    try {
      const response = await api.post(`/rfi/${id}/comments`, commentData);
      return response.data;
    } catch (error) {
      console.error(`Error adding comment to RFI ${id}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Hinzufügen des Kommentars');
    }
  },

  /**
   * KI-Antwort für RFI generieren
   * @param {string} id - RFI-ID
   * @returns {Promise<Object>} Generierte Antwort
   */
  async generateAIResponse(id) {
    try {
      const response = await api.post(`/rfi/${id}/ai-response`);
      return response.data;
    } catch (error) {
      console.error(`Error generating AI response for RFI ${id}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler bei der Generierung der KI-Antwort');
    }
  },

  /**
   * Anhang zu RFI hinzufügen
   * @param {string} id - RFI-ID
   * @param {FormData} formData - FormData mit Anhang
   * @returns {Promise<Object>} Aktualisierte RFI
   */
  async addAttachment(id, formData) {
    try {
      const response = await api.uploadFile(`/rfi/${id}/attachments`, formData);
      return response.data;
    } catch (error) {
      console.error(`Error adding attachment to RFI ${id}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Hinzufügen des Anhangs');
    }
  },

  /**
   * Anhang von RFI entfernen
   * @param {string} rfiId - RFI-ID
   * @param {string} attachmentId - Anhang-ID
   * @returns {Promise<Object>} Aktualisierte RFI
   */
  async removeAttachment(rfiId, attachmentId) {
    try {
      const response = await api.delete(`/rfi/${rfiId}/attachments/${attachmentId}`);
      return response.data;
    } catch (error) {
      console.error(`Error removing attachment ${attachmentId} from RFI ${rfiId}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Entfernen des Anhangs');
    }
  }
};

