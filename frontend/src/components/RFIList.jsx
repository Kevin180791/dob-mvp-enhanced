import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { rfiService } from '../services/rfiService';
import { projectService } from '../services/projectService';
import { toast } from 'react-toastify';

const RFIList = () => {
  const [rfis, setRfis] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    project_id: '',
    status: '',
    priority: '',
    search: ''
  });

  // RFIs und Projekte laden
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Projekte laden
        const projectsData = await projectService.getProjects();
        setProjects(projectsData);
        
        // RFIs laden
        await fetchRFIs();
      } catch (error) {
        toast.error('Fehler beim Laden der Daten');
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // RFIs mit Filtern laden
  const fetchRFIs = async () => {
    try {
      // Filter für API-Anfrage vorbereiten
      const queryParams = {};
      if (filters.project_id) queryParams.project_id = filters.project_id;
      if (filters.status) queryParams.status = filters.status;
      if (filters.priority) queryParams.priority = filters.priority;
      if (filters.search) queryParams.search = filters.search;
      
      const data = await rfiService.getRFIs(queryParams);
      setRfis(data);
    } catch (error) {
      toast.error('Fehler beim Laden der RFIs');
      console.error('Error fetching RFIs:', error);
    }
  };

  // Filter-Änderungen verarbeiten
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  // Filter anwenden
  const applyFilters = (e) => {
    e.preventDefault();
    fetchRFIs();
  };

  // Filter zurücksetzen
  const resetFilters = () => {
    setFilters({
      project_id: '',
      status: '',
      priority: '',
      search: ''
    });
    // Nach dem Zurücksetzen der Filter sofort neue Daten laden
    setTimeout(() => {
      fetchRFIs();
    }, 0);
  };

  // Status-Badge rendern
  const renderStatusBadge = (status) => {
    let bgColor = '';
    let textColor = '';
    let label = '';

    switch (status) {
      case 'new':
        bgColor = 'bg-blue-100';
        textColor = 'text-blue-800';
        label = 'Neu';
        break;
      case 'in_progress':
        bgColor = 'bg-yellow-100';
        textColor = 'text-yellow-800';
        label = 'In Bearbeitung';
        break;
      case 'answered':
        bgColor = 'bg-green-100';
        textColor = 'text-green-800';
        label = 'Beantwortet';
        break;
      case 'closed':
        bgColor = 'bg-gray-100';
        textColor = 'text-gray-800';
        label = 'Geschlossen';
        break;
      default:
        bgColor = 'bg-gray-100';
        textColor = 'text-gray-800';
        label = status;
    }

    return (
      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${bgColor} ${textColor}`}>
        {label}
      </span>
    );
  };

  // Prioritäts-Badge rendern
  const renderPriorityBadge = (priority) => {
    let bgColor = '';
    let textColor = '';
    let label = '';

    switch (priority) {
      case 'low':
        bgColor = 'bg-green-100';
        textColor = 'text-green-800';
        label = 'Niedrig';
        break;
      case 'medium':
        bgColor = 'bg-blue-100';
        textColor = 'text-blue-800';
        label = 'Mittel';
        break;
      case 'high':
        bgColor = 'bg-orange-100';
        textColor = 'text-orange-800';
        label = 'Hoch';
        break;
      case 'critical':
        bgColor = 'bg-red-100';
        textColor = 'text-red-800';
        label = 'Kritisch';
        break;
      default:
        bgColor = 'bg-gray-100';
        textColor = 'text-gray-800';
        label = priority;
    }

    return (
      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${bgColor} ${textColor}`}>
        {label}
      </span>
    );
  };

  // Datum formatieren
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('de-DE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }).format(date);
  };

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">RFI-Übersicht</h2>
        <Link
          to="/rfi/new"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Neue RFI erstellen
        </Link>
      </div>
      
      {/* Filter-Bereich */}
      <div className="mb-6 bg-gray-50 p-4 rounded-md">
        <form onSubmit={applyFilters}>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Projekt-Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Projekt</label>
              <select
                name="project_id"
                value={filters.project_id}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Alle Projekte</option>
                {projects.map(project => (
                  <option key={project.id} value={project.id}>{project.name}</option>
                ))}
              </select>
            </div>
            
            {/* Status-Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                name="status"
                value={filters.status}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Alle Status</option>
                <option value="new">Neu</option>
                <option value="in_progress">In Bearbeitung</option>
                <option value="answered">Beantwortet</option>
                <option value="closed">Geschlossen</option>
              </select>
            </div>
            
            {/* Prioritäts-Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Priorität</label>
              <select
                name="priority"
                value={filters.priority}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Alle Prioritäten</option>
                <option value="low">Niedrig</option>
                <option value="medium">Mittel</option>
                <option value="high">Hoch</option>
                <option value="critical">Kritisch</option>
              </select>
            </div>
            
            {/* Suchfeld */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Suche</label>
              <input
                type="text"
                name="search"
                value={filters.search}
                onChange={handleFilterChange}
                placeholder="Titel oder Beschreibung..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          {/* Filter-Aktionen */}
          <div className="mt-4 flex justify-end space-x-3">
            <button
              type="button"
              onClick={resetFilters}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Zurücksetzen
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Filter anwenden
            </button>
          </div>
        </form>
      </div>
      
      {/* RFI-Tabelle */}
      {loading ? (
        <div className="flex justify-center items-center py-8">
          <svg className="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      ) : rfis.length === 0 ? (
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Keine RFIs gefunden</h3>
          <p className="mt-1 text-sm text-gray-500">
            Erstellen Sie eine neue RFI oder passen Sie Ihre Filter an.
          </p>
          <div className="mt-6">
            <Link
              to="/rfi/new"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg className="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
              Neue RFI erstellen
            </Link>
          </div>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Titel
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Projekt
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priorität
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Erstellt am
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fällig am
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {rfis.map((rfi) => (
                <tr key={rfi.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {rfi.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link to={`/rfi/${rfi.id}`} className="text-blue-600 hover:text-blue-900">
                      {rfi.title}
                    </Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {projects.find(p => p.id === rfi.project_id)?.name || rfi.project_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {renderStatusBadge(rfi.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {renderPriorityBadge(rfi.priority)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(rfi.created_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(rfi.due_date)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default RFIList;

