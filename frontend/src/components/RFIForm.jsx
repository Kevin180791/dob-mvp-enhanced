import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { rfiService } from '../services/rfiService';
import { projectService } from '../services/projectService';
import { toast } from 'react-toastify';

const RFIForm = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState([]);
  const [formData, setFormData] = useState({
    project_id: '',
    title: '',
    description: '',
    priority: 'medium',
    due_date: '',
    attachments: []
  });

  // Projekte laden
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await projectService.getProjects();
        setProjects(data);
        // Wenn Projekte vorhanden sind, das erste als Standard setzen
        if (data.length > 0) {
          setFormData(prev => ({ ...prev, project_id: data[0].id }));
        }
      } catch (error) {
        toast.error('Fehler beim Laden der Projekte');
        console.error('Error fetching projects:', error);
      }
    };

    fetchProjects();
  }, []);

  // Formular-Änderungen verarbeiten
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Datei-Upload verarbeiten
  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    setFormData(prev => ({ ...prev, attachments: [...prev.attachments, ...files] }));
  };

  // Datei entfernen
  const handleRemoveFile = (index) => {
    setFormData(prev => ({
      ...prev,
      attachments: prev.attachments.filter((_, i) => i !== index)
    }));
  };

  // Formular absenden
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // FormData für Datei-Upload erstellen
      const submitData = new FormData();
      submitData.append('project_id', formData.project_id);
      submitData.append('title', formData.title);
      submitData.append('description', formData.description);
      submitData.append('priority', formData.priority);
      submitData.append('due_date', formData.due_date);

      // Dateien hinzufügen
      formData.attachments.forEach((file, index) => {
        submitData.append(`attachments`, file);
      });

      // RFI erstellen
      const response = await rfiService.createRFI(submitData);
      toast.success('RFI erfolgreich erstellt');
      navigate(`/rfi/${response.id}`);
    } catch (error) {
      toast.error('Fehler beim Erstellen der RFI');
      console.error('Error creating RFI:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-6">Neue RFI erstellen</h2>
      
      <form onSubmit={handleSubmit}>
        {/* Projekt-Auswahl */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Projekt</label>
          <select
            name="project_id"
            value={formData.project_id}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Projekt auswählen</option>
            {projects.map(project => (
              <option key={project.id} value={project.id}>{project.name}</option>
            ))}
          </select>
        </div>
        
        {/* Titel */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Titel</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Kurzer, beschreibender Titel für die Anfrage"
            required
          />
        </div>
        
        {/* Beschreibung */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Beschreibung</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows="5"
            placeholder="Detaillierte Beschreibung der Anfrage..."
            required
          ></textarea>
        </div>
        
        {/* Priorität und Fälligkeitsdatum */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priorität</label>
            <select
              name="priority"
              value={formData.priority}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Niedrig</option>
              <option value="medium">Mittel</option>
              <option value="high">Hoch</option>
              <option value="critical">Kritisch</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Fälligkeitsdatum</label>
            <input
              type="date"
              name="due_date"
              value={formData.due_date}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        
        {/* Datei-Upload */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-1">Anhänge</label>
          <div className="flex items-center justify-center w-full">
            <label className="flex flex-col w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                </svg>
                <p className="pt-1 text-sm text-gray-500">Dateien hierher ziehen oder klicken zum Hochladen</p>
                <p className="text-xs text-gray-500">PDF, CAD, BIM, Bilder</p>
              </div>
              <input 
                type="file" 
                className="hidden" 
                multiple 
                onChange={handleFileChange}
              />
            </label>
          </div>
          
          {/* Anzeige der ausgewählten Dateien */}
          {formData.attachments.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Ausgewählte Dateien:</h4>
              <ul className="space-y-2">
                {formData.attachments.map((file, index) => (
                  <li key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                    <div className="flex items-center">
                      <svg className="w-4 h-4 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                      </svg>
                      <span className="text-sm text-gray-700">{file.name}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveFile(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        
        {/* Aktionsbuttons */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/rfi')}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Abbrechen
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-blue-300"
          >
            {loading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Wird erstellt...
              </span>
            ) : 'RFI erstellen'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default RFIForm;

