import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { rfiService } from '../services/rfiService';
import { toast } from 'react-toastify';

const RFIDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [rfi, setRfi] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [comment, setComment] = useState('');
  const [showAiResponse, setShowAiResponse] = useState(false);
  const [aiResponse, setAiResponse] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);

  // RFI laden
  useEffect(() => {
    const fetchRFI = async () => {
      setLoading(true);
      try {
        const data = await rfiService.getRFIById(id);
        setRfi(data);
      } catch (error) {
        toast.error('Fehler beim Laden der RFI');
        console.error('Error fetching RFI:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRFI();
  }, [id]);

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
      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${bgColor} ${textColor}`}>
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
      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${bgColor} ${textColor}`}>
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
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  // Kommentar hinzufügen
  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!comment.trim()) return;

    setProcessing(true);
    try {
      const updatedRfi = await rfiService.addComment(id, { text: comment });
      setRfi(updatedRfi);
      setComment('');
      toast.success('Kommentar erfolgreich hinzugefügt');
    } catch (error) {
      toast.error('Fehler beim Hinzufügen des Kommentars');
      console.error('Error adding comment:', error);
    } finally {
      setProcessing(false);
    }
  };

  // Status ändern
  const handleChangeStatus = async (newStatus) => {
    setProcessing(true);
    try {
      const updatedRfi = await rfiService.updateRFI(id, { status: newStatus });
      setRfi(updatedRfi);
      toast.success(`Status erfolgreich auf "${newStatus}" geändert`);
    } catch (error) {
      toast.error('Fehler beim Ändern des Status');
      console.error('Error changing status:', error);
    } finally {
      setProcessing(false);
    }
  };

  // KI-Antwort generieren
  const handleGenerateAIResponse = async () => {
    setAiLoading(true);
    try {
      const response = await rfiService.generateAIResponse(id);
      setAiResponse(response);
      setShowAiResponse(true);
      toast.success('KI-Antwort erfolgreich generiert');
    } catch (error) {
      toast.error('Fehler bei der Generierung der KI-Antwort');
      console.error('Error generating AI response:', error);
    } finally {
      setAiLoading(false);
    }
  };

  // KI-Antwort übernehmen
  const handleAcceptAIResponse = async () => {
    setProcessing(true);
    try {
      const updatedRfi = await rfiService.addComment(id, { 
        text: aiResponse.text,
        is_ai_generated: true
      });
      setRfi(updatedRfi);
      setShowAiResponse(false);
      setAiResponse(null);
      toast.success('KI-Antwort erfolgreich übernommen');
    } catch (error) {
      toast.error('Fehler beim Übernehmen der KI-Antwort');
      console.error('Error accepting AI response:', error);
    } finally {
      setProcessing(false);
    }
  };

  // RFI löschen
  const handleDeleteRFI = async () => {
    if (!window.confirm('Sind Sie sicher, dass Sie diese RFI löschen möchten?')) {
      return;
    }

    setProcessing(true);
    try {
      await rfiService.deleteRFI(id);
      toast.success('RFI erfolgreich gelöscht');
      navigate('/rfi');
    } catch (error) {
      toast.error('Fehler beim Löschen der RFI');
      console.error('Error deleting RFI:', error);
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <svg className="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    );
  }

  if (!rfi) {
    return (
      <div className="bg-white shadow-md rounded-lg p-6">
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">RFI nicht gefunden</h3>
          <p className="mt-1 text-sm text-gray-500">
            Die angeforderte RFI existiert nicht oder wurde gelöscht.
          </p>
          <div className="mt-6">
            <button
              onClick={() => navigate('/rfi')}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Zurück zur Übersicht
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      {/* Header mit Titel und Aktionen */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold">{rfi.title}</h2>
          <div className="mt-2 flex flex-wrap gap-2">
            {renderStatusBadge(rfi.status)}
            {renderPriorityBadge(rfi.priority)}
            <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
              ID: {rfi.id}
            </span>
          </div>
        </div>
        <div className="mt-4 md:mt-0 flex flex-wrap gap-2">
          <button
            onClick={() => navigate('/rfi')}
            className="px-3 py-1 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Zurück
          </button>
          <button
            onClick={handleDeleteRFI}
            disabled={processing}
            className="px-3 py-1 border border-red-300 text-red-700 rounded-md hover:bg-red-50 disabled:opacity-50"
          >
            Löschen
          </button>
        </div>
      </div>
      
      {/* RFI-Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <h3 className="text-lg font-medium mb-2">Details</h3>
          <div className="bg-gray-50 p-4 rounded-md">
            <dl className="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Projekt</dt>
                <dd className="mt-1 text-sm text-gray-900">{rfi.project_name || rfi.project_id}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Erstellt von</dt>
                <dd className="mt-1 text-sm text-gray-900">{rfi.created_by || 'Unbekannt'}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Erstellt am</dt>
                <dd className="mt-1 text-sm text-gray-900">{formatDate(rfi.created_at)}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Fällig am</dt>
                <dd className="mt-1 text-sm text-gray-900">{formatDate(rfi.due_date) || 'Nicht festgelegt'}</dd>
              </div>
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <div className="flex items-center space-x-2">
                    {renderStatusBadge(rfi.status)}
                    <div className="ml-2">
                      <select
                        value={rfi.status}
                        onChange={(e) => handleChangeStatus(e.target.value)}
                        disabled={processing}
                        className="mt-1 block w-full pl-3 pr-10 py-1 text-sm border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
                      >
                        <option value="new">Neu</option>
                        <option value="in_progress">In Bearbeitung</option>
                        <option value="answered">Beantwortet</option>
                        <option value="closed">Geschlossen</option>
                      </select>
                    </div>
                  </div>
                </dd>
              </div>
            </dl>
          </div>
        </div>
        
        <div>
          <h3 className="text-lg font-medium mb-2">Beschreibung</h3>
          <div className="bg-gray-50 p-4 rounded-md">
            <p className="text-sm text-gray-900 whitespace-pre-wrap">{rfi.description}</p>
          </div>
        </div>
      </div>
      
      {/* Anhänge */}
      {rfi.attachments && rfi.attachments.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-2">Anhänge</h3>
          <div className="bg-gray-50 p-4 rounded-md">
            <ul className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {rfi.attachments.map((attachment, index) => (
                <li key={index} className="flex items-center p-2 border border-gray-200 rounded-md">
                  <svg className="w-5 h-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  <a
                    href={attachment.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-800 truncate"
                  >
                    {attachment.filename || `Anhang ${index + 1}`}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
      
      {/* KI-Antwort */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-medium">KI-Antwort</h3>
          <button
            onClick={handleGenerateAIResponse}
            disabled={aiLoading || processing}
            className="px-3 py-1 bg-purple-600 text-white rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:bg-purple-300"
          >
            {aiLoading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generiere...
              </span>
            ) : 'KI-Antwort generieren'}
          </button>
        </div>
        
        {showAiResponse && aiResponse && (
          <div className="bg-purple-50 p-4 rounded-md border border-purple-200 mb-4">
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                <span className="font-medium text-purple-800">KI-generierte Antwort</span>
              </div>
              <button
                onClick={() => setShowAiResponse(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            <div className="text-sm text-gray-900 whitespace-pre-wrap mb-4">
              {aiResponse.text}
            </div>
            <div className="flex justify-end">
              <button
                onClick={handleAcceptAIResponse}
                disabled={processing}
                className="px-3 py-1 bg-purple-600 text-white rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:bg-purple-300"
              >
                Antwort übernehmen
              </button>
            </div>
          </div>
        )}
      </div>
      
      {/* Kommentare */}
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">Kommentare</h3>
        
        {/* Kommentar-Liste */}
        {rfi.comments && rfi.comments.length > 0 ? (
          <div className="space-y-4 mb-4">
            {rfi.comments.map((comment, index) => (
              <div key={index} className={`p-4 rounded-md ${comment.is_ai_generated ? 'bg-purple-50 border border-purple-200' : 'bg-gray-50'}`}>
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center">
                    {comment.is_ai_generated ? (
                      <svg className="w-5 h-5 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                      </svg>
                    ) : (
                      <svg className="w-5 h-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                      </svg>
                    )}
                    <span className="font-medium">{comment.created_by || 'System'}</span>
                    <span className="ml-2 text-xs text-gray-500">{formatDate(comment.created_at)}</span>
                  </div>
                </div>
                <div className="text-sm text-gray-900 whitespace-pre-wrap">
                  {comment.text}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-gray-50 p-4 rounded-md mb-4 text-center">
            <p className="text-sm text-gray-500">Noch keine Kommentare vorhanden.</p>
          </div>
        )}
        
        {/* Kommentar-Formular */}
        <form onSubmit={handleAddComment}>
          <div className="mb-4">
            <label htmlFor="comment" className="block text-sm font-medium text-gray-700 mb-1">
              Neuer Kommentar
            </label>
            <textarea
              id="comment"
              name="comment"
              rows="3"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Geben Sie Ihren Kommentar ein..."
              required
            ></textarea>
          </div>
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={processing || !comment.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-blue-300"
            >
              {processing ? 'Wird gesendet...' : 'Kommentar hinzufügen'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RFIDetail;

