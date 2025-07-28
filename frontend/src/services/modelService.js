import { api } from './api';

/**
 * Service für die Verwaltung von KI-Modellen und Providern
 */
export const modelService = {
  /**
   * Provider abrufen
   * @returns {Promise<Array>} Liste der Provider
   */
  async getProviders() {
    try {
      const response = await api.get('/models/providers');
      return response.data;
    } catch (error) {
      console.error('Error fetching providers:', error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Abrufen der Provider');
    }
  },

  /**
   * Provider erstellen
   * @param {Object} provider Provider-Daten
   * @returns {Promise<Object>} Erstellter Provider
   */
  async createProvider(provider) {
    try {
      const response = await api.post('/models/providers', provider);
      return response.data;
    } catch (error) {
      console.error('Error creating provider:', error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Erstellen des Providers');
    }
  },

  /**
   * Provider löschen
   * @param {string} providerId Provider-ID
   * @returns {Promise<Object>} Antwort
   */
  async deleteProvider(providerId) {
    try {
      const response = await api.delete(`/models/providers/${providerId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting provider:', error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Löschen des Providers');
    }
  },

  /**
   * Modelle abrufen
   * @param {Object} params Optionale Parameter (provider_id, model_type, active_only)
   * @returns {Promise<Array>} Liste der Modelle
   */
  async getModels(params = {}) {
    try {
      const response = await api.get('/models/models', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching models:', error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Abrufen der Modelle');
    }
  },

  /**
   * Modell erstellen
   * @param {Object} model Modell-Daten
   * @returns {Promise<Object>} Erstelltes Modell
   */
  async createModel(model) {
    try {
      const response = await api.post('/models/models', model);
      return response.data;
    } catch (error) {
      console.error('Error creating model:', error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Erstellen des Modells');
    }
  },

  /**
   * Modell löschen
   * @param {string} modelId Modell-ID
   * @returns {Promise<Object>} Antwort
   */
  async deleteModel(modelId) {
    try {
      const response = await api.delete(`/models/models/${modelId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting model:', error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Löschen des Modells');
    }
  },

  /**
   * Modell testen
   * @param {string} modelId Modell-ID
   * @param {Object} testData Test-Daten (prompt, parameters)
   * @returns {Promise<Object>} Testergebnis
   */
  async testModel(modelId, testData) {
    try {
      const response = await api.post(`/models/models/${modelId}/test`, testData);
      return response.data;
    } catch (error) {
      console.error('Error testing model:', error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Testen des Modells');
    }
  },

  /**
   * Zuweisungen abrufen
   * @param {Object} params Optionale Parameter (agent_id, model_id)
   * @returns {Promise<Array>} Liste der Zuweisungen
   */
  async getAssignments(params = {}) {
    try {
      const response = await api.get('/models/assignments', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching assignments:', error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Abrufen der Zuweisungen');
    }
  },

  /**
   * Zuweisung erstellen
   * @param {Object} assignment Zuweisungs-Daten
   * @returns {Promise<Object>} Erstellte Zuweisung
   */
  async createAssignment(assignment) {
    try {
      const response = await api.post('/models/assignments', assignment);
      return response.data;
    } catch (error) {
      console.error('Error creating assignment:', error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Erstellen der Zuweisung');
    }
  },

  /**
   * Zuweisung löschen
   * @param {string} assignmentId Zuweisungs-ID
   * @returns {Promise<Object>} Antwort
   */
  async deleteAssignment(assignmentId) {
    try {
      const response = await api.delete(`/models/assignments/${assignmentId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting assignment:', error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Löschen der Zuweisung');
    }
  }
};

