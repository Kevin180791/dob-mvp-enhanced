import { api } from './api';

/**
 * Service für die Interaktion mit der Workflow-API
 */
export const workflowService = {
  /**
   * Holt alle Workflows
   * @returns {Promise<Array>} Liste der Workflows
   */
  async getWorkflows() {
    const response = await api.get('/workflow');
    return response.data;
  },

  /**
   * Holt einen Workflow anhand seiner ID
   * @param {string} id - ID des Workflows
   * @returns {Promise<Object>} Workflow-Objekt
   */
  async getWorkflow(id) {
    const response = await api.get(`/workflow/${id}`);
    return response.data;
  },

  /**
   * Erstellt einen neuen Workflow
   * @param {Object} data - Workflow-Daten
   * @returns {Promise<Object>} Erstellter Workflow
   */
  async createWorkflow(data) {
    const response = await api.post('/workflow', data);
    return response.data;
  },

  /**
   * Startet einen Workflow
   * @param {string} id - ID des Workflows
   * @returns {Promise<Object>} Aktualisierter Workflow
   */
  async startWorkflow(id) {
    const response = await api.post(`/workflow/${id}/start`);
    return response.data;
  },

  /**
   * Bricht einen Workflow ab
   * @param {string} id - ID des Workflows
   * @param {Object} data - Abbruch-Daten (z.B. Grund)
   * @returns {Promise<Object>} Aktualisierter Workflow
   */
  async cancelWorkflow(id, data) {
    const response = await api.post(`/workflow/${id}/cancel`, data);
    return response.data;
  },

  /**
   * Holt alle Workflow-Vorlagen
   * @returns {Promise<Array>} Liste der Workflow-Vorlagen
   */
  async getWorkflowTemplates() {
    const response = await api.get('/workflow/templates');
    return response.data;
  },

  /**
   * Holt eine Workflow-Vorlage anhand ihrer ID
   * @param {string} id - ID der Workflow-Vorlage
   * @returns {Promise<Object>} Workflow-Vorlage
   */
  async getWorkflowTemplate(id) {
    const response = await api.get(`/workflow/templates/${id}`);
    return response.data;
  },

  /**
   * Erstellt eine neue Workflow-Vorlage
   * @param {Object} data - Vorlagen-Daten
   * @returns {Promise<Object>} Erstellte Workflow-Vorlage
   */
  async createWorkflowTemplate(data) {
    const response = await api.post('/workflow/templates', data);
    return response.data;
  },

  /**
   * Aktualisiert eine Workflow-Vorlage
   * @param {string} id - ID der Workflow-Vorlage
   * @param {Object} data - Aktualisierte Vorlagen-Daten
   * @returns {Promise<Object>} Aktualisierte Workflow-Vorlage
   */
  async updateWorkflowTemplate(id, data) {
    const response = await api.put(`/workflow/templates/${id}`, data);
    return response.data;
  },

  /**
   * Löscht eine Workflow-Vorlage
   * @param {string} id - ID der Workflow-Vorlage
   * @returns {Promise<void>}
   */
  async deleteWorkflowTemplate(id) {
    await api.delete(`/workflow/templates/${id}`);
  },

  /**
   * Holt einen Task anhand seiner ID
   * @param {string} workflowId - ID des Workflows
   * @param {string} taskId - ID des Tasks
   * @returns {Promise<Object>} Task-Objekt
   */
  async getTask(workflowId, taskId) {
    const response = await api.get(`/workflow/${workflowId}/tasks/${taskId}`);
    return response.data;
  },

  /**
   * Schließt einen Task ab
   * @param {string} workflowId - ID des Workflows
   * @param {string} taskId - ID des Tasks
   * @param {Object} data - Ergebnis-Daten
   * @returns {Promise<Object>} Aktualisierter Task
   */
  async completeTask(workflowId, taskId, data) {
    const response = await api.post(`/workflow/${workflowId}/tasks/${taskId}/complete`, data);
    return response.data;
  },

  /**
   * Genehmigt oder lehnt einen Task ab
   * @param {string} workflowId - ID des Workflows
   * @param {string} taskId - ID des Tasks
   * @param {string} approvalId - ID der Genehmigung
   * @param {Object} data - Genehmigungs-Daten
   * @returns {Promise<Object>} Aktualisierter Task
   */
  async approveTask(workflowId, taskId, approvalId, data) {
    const response = await api.post(`/workflow/${workflowId}/tasks/${taskId}/approvals/${approvalId}`, data);
    return response.data;
  },

  /**
   * Delegiert eine Genehmigung an einen anderen Benutzer
   * @param {string} workflowId - ID des Workflows
   * @param {string} taskId - ID des Tasks
   * @param {string} approvalId - ID der Genehmigung
   * @param {Object} data - Delegierungs-Daten
   * @returns {Promise<Object>} Aktualisierter Task
   */
  async delegateApproval(workflowId, taskId, approvalId, data) {
    const response = await api.post(`/workflow/${workflowId}/tasks/${taskId}/approvals/${approvalId}/delegate`, data);
    return response.data;
  },

  /**
   * Stellt Eingabedaten für einen Task bereit
   * @param {string} workflowId - ID des Workflows
   * @param {string} taskId - ID des Tasks
   * @param {Object} data - Eingabedaten
   * @returns {Promise<Object>} Aktualisierter Task
   */
  async provideInput(workflowId, taskId, data) {
    const response = await api.post(`/workflow/${workflowId}/tasks/${taskId}/input`, data);
    return response.data;
  },

  /**
   * Fügt einen Teilnehmer zu einem Workflow hinzu
   * @param {string} workflowId - ID des Workflows
   * @param {Object} data - Teilnehmer-Daten
   * @returns {Promise<Object>} Aktualisierter Workflow
   */
  async addWorkflowParticipant(workflowId, data) {
    const response = await api.post(`/workflow/${workflowId}/participants`, data);
    return response.data;
  },

  /**
   * Entfernt einen Teilnehmer aus einem Workflow
   * @param {string} workflowId - ID des Workflows
   * @param {string} participantId - ID des Teilnehmers
   * @returns {Promise<Object>} Aktualisierter Workflow
   */
  async removeWorkflowParticipant(workflowId, participantId) {
    const response = await api.delete(`/workflow/${workflowId}/participants/${participantId}`);
    return response.data;
  },

  /**
   * Aktualisiert einen Teilnehmer in einem Workflow
   * @param {string} workflowId - ID des Workflows
   * @param {string} participantId - ID des Teilnehmers
   * @param {Object} data - Aktualisierte Teilnehmer-Daten
   * @returns {Promise<Object>} Aktualisierter Workflow
   */
  async updateWorkflowParticipant(workflowId, participantId, data) {
    const response = await api.put(`/workflow/${workflowId}/participants/${participantId}`, data);
    return response.data;
  }
};

