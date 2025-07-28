import { api } from './api';

/**
 * Service für die Verwaltung von Projekten
 */
export const projectService = {
  /**
   * Projekte abrufen
   * @param {Object} params - Optionale Parameter (status, search)
   * @returns {Promise<Array>} Liste der Projekte
   */
  async getProjects(params = {}) {
    try {
      const response = await api.get('/projects', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching projects:', error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Abrufen der Projekte');
    }
  },

  /**
   * Projekt nach ID abrufen
   * @param {string} id - Projekt-ID
   * @returns {Promise<Object>} Projekt-Objekt
   */
  async getProjectById(id) {
    try {
      const response = await api.get(`/projects/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching project ${id}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Abrufen des Projekts');
    }
  },

  /**
   * Projekt erstellen
   * @param {Object} projectData - Projekt-Daten
   * @returns {Promise<Object>} Erstelltes Projekt
   */
  async createProject(projectData) {
    try {
      const response = await api.post('/projects', projectData);
      return response.data;
    } catch (error) {
      console.error('Error creating project:', error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Erstellen des Projekts');
    }
  },

  /**
   * Projekt aktualisieren
   * @param {string} id - Projekt-ID
   * @param {Object} projectData - Zu aktualisierende Daten
   * @returns {Promise<Object>} Aktualisiertes Projekt
   */
  async updateProject(id, projectData) {
    try {
      const response = await api.patch(`/projects/${id}`, projectData);
      return response.data;
    } catch (error) {
      console.error(`Error updating project ${id}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Aktualisieren des Projekts');
    }
  },

  /**
   * Projekt löschen
   * @param {string} id - Projekt-ID
   * @returns {Promise<Object>} Antwort
   */
  async deleteProject(id) {
    try {
      const response = await api.delete(`/projects/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting project ${id}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Löschen des Projekts');
    }
  },

  /**
   * Projektmitglieder abrufen
   * @param {string} id - Projekt-ID
   * @returns {Promise<Array>} Liste der Projektmitglieder
   */
  async getProjectMembers(id) {
    try {
      const response = await api.get(`/projects/${id}/members`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching members for project ${id}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Abrufen der Projektmitglieder');
    }
  },

  /**
   * Projektmitglied hinzufügen
   * @param {string} id - Projekt-ID
   * @param {Object} memberData - Mitgliedsdaten
   * @returns {Promise<Object>} Aktualisiertes Projekt
   */
  async addProjectMember(id, memberData) {
    try {
      const response = await api.post(`/projects/${id}/members`, memberData);
      return response.data;
    } catch (error) {
      console.error(`Error adding member to project ${id}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Hinzufügen des Projektmitglieds');
    }
  },

  /**
   * Projektmitglied entfernen
   * @param {string} projectId - Projekt-ID
   * @param {string} memberId - Mitglieds-ID
   * @returns {Promise<Object>} Aktualisiertes Projekt
   */
  async removeProjectMember(projectId, memberId) {
    try {
      const response = await api.delete(`/projects/${projectId}/members/${memberId}`);
      return response.data;
    } catch (error) {
      console.error(`Error removing member ${memberId} from project ${projectId}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Entfernen des Projektmitglieds');
    }
  },

  /**
   * Projektdokumente abrufen
   * @param {string} id - Projekt-ID
   * @returns {Promise<Array>} Liste der Projektdokumente
   */
  async getProjectDocuments(id) {
    try {
      const response = await api.get(`/projects/${id}/documents`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching documents for project ${id}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Abrufen der Projektdokumente');
    }
  },

  /**
   * Projektdokument hinzufügen
   * @param {string} id - Projekt-ID
   * @param {FormData} formData - FormData mit Dokument
   * @returns {Promise<Object>} Hinzugefügtes Dokument
   */
  async addProjectDocument(id, formData) {
    try {
      const response = await api.uploadFile(`/projects/${id}/documents`, formData);
      return response.data;
    } catch (error) {
      console.error(`Error adding document to project ${id}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Hinzufügen des Projektdokuments');
    }
  },

  /**
   * Projektdokument entfernen
   * @param {string} projectId - Projekt-ID
   * @param {string} documentId - Dokument-ID
   * @returns {Promise<Object>} Antwort
   */
  async removeProjectDocument(projectId, documentId) {
    try {
      const response = await api.delete(`/projects/${projectId}/documents/${documentId}`);
      return response.data;
    } catch (error) {
      console.error(`Error removing document ${documentId} from project ${projectId}:`, error);
      throw new Error(error.response?.data?.detail || 'Fehler beim Entfernen des Projektdokuments');
    }
  }
};

