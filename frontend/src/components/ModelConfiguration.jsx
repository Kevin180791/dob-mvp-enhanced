import React, { useState, useEffect } from 'react';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import 'react-tabs/style/react-tabs.css';
import { modelService } from '../services/modelService';
import { toast } from 'react-toastify';

const ModelConfiguration = () => {
  // State für Provider
  const [providers, setProviders] = useState([]);
  const [newProvider, setNewProvider] = useState({
    name: '',
    provider_type: 'openai',
    config: {}
  });

  // State für Modelle
  const [models, setModels] = useState([]);
  const [newModel, setNewModel] = useState({
    name: '',
    provider_id: '',
    model_id: '',
    model_type: 'text',
    parameters: {},
    is_active: true,
    is_default: false
  });

  // State für Zuweisungen
  const [assignments, setAssignments] = useState([]);
  const [newAssignment, setNewAssignment] = useState({
    agent_id: '',
    model_id: '',
    fallback_model_id: ''
  });

  // State für Modelltest
  const [testModel, setTestModel] = useState({
    model_id: '',
    prompt: '',
    parameters: {}
  });
  const [testResult, setTestResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Agents Liste (in einer realen Anwendung würde dies von einer API kommen)
  const agents = [
    { id: 'rfi_analyst', name: 'RFI-Analyst' },
    { id: 'plan_reviewer', name: 'Plan-Prüfer' },
    { id: 'communication_agent', name: 'Kommunikations-Agent' }
  ];

  // Laden der Daten beim Komponenten-Mount
  useEffect(() => {
    loadProviders();
    loadModels();
    loadAssignments();
  }, []);

  // Provider laden
  const loadProviders = async () => {
    try {
      const data = await modelService.getProviders();
      setProviders(data);
    } catch (error) {
      toast.error('Fehler beim Laden der Provider: ' + error.message);
    }
  };

  // Modelle laden
  const loadModels = async () => {
    try {
      const data = await modelService.getModels();
      setModels(data);
    } catch (error) {
      toast.error('Fehler beim Laden der Modelle: ' + error.message);
    }
  };

  // Zuweisungen laden
  const loadAssignments = async () => {
    try {
      const data = await modelService.getAssignments();
      setAssignments(data);
    } catch (error) {
      toast.error('Fehler beim Laden der Zuweisungen: ' + error.message);
    }
  };

  // Provider erstellen
  const handleCreateProvider = async (e) => {
    e.preventDefault();
    try {
      const data = await modelService.createProvider(newProvider);
      setProviders([...providers, data]);
      setNewProvider({
        name: '',
        provider_type: 'openai',
        config: {}
      });
      toast.success('Provider erfolgreich erstellt');
    } catch (error) {
      toast.error('Fehler beim Erstellen des Providers: ' + error.message);
    }
  };

  // Modell erstellen
  const handleCreateModel = async (e) => {
    e.preventDefault();
    try {
      const data = await modelService.createModel(newModel);
      setModels([...models, data]);
      setNewModel({
        name: '',
        provider_id: '',
        model_id: '',
        model_type: 'text',
        parameters: {},
        is_active: true,
        is_default: false
      });
      toast.success('Modell erfolgreich erstellt');
    } catch (error) {
      toast.error('Fehler beim Erstellen des Modells: ' + error.message);
    }
  };

  // Zuweisung erstellen
  const handleCreateAssignment = async (e) => {
    e.preventDefault();
    try {
      const data = await modelService.createAssignment(newAssignment);
      setAssignments([...assignments, data]);
      setNewAssignment({
        agent_id: '',
        model_id: '',
        fallback_model_id: ''
      });
      toast.success('Zuweisung erfolgreich erstellt');
    } catch (error) {
      toast.error('Fehler beim Erstellen der Zuweisung: ' + error.message);
    }
  };

  // Modell testen
  const handleTestModel = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const data = await modelService.testModel(testModel.model_id, testModel);
      setTestResult(data);
      toast.success('Modelltest erfolgreich durchgeführt');
    } catch (error) {
      toast.error('Fehler beim Testen des Modells: ' + error.message);
      setTestResult({
        success: false,
        error: error.message
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Provider löschen
  const handleDeleteProvider = async (providerId) => {
    if (window.confirm('Sind Sie sicher, dass Sie diesen Provider löschen möchten?')) {
      try {
        await modelService.deleteProvider(providerId);
        setProviders(providers.filter(p => p.id !== providerId));
        toast.success('Provider erfolgreich gelöscht');
      } catch (error) {
        toast.error('Fehler beim Löschen des Providers: ' + error.message);
      }
    }
  };

  // Modell löschen
  const handleDeleteModel = async (modelId) => {
    if (window.confirm('Sind Sie sicher, dass Sie dieses Modell löschen möchten?')) {
      try {
        await modelService.deleteModel(modelId);
        setModels(models.filter(m => m.id !== modelId));
        toast.success('Modell erfolgreich gelöscht');
      } catch (error) {
        toast.error('Fehler beim Löschen des Modells: ' + error.message);
      }
    }
  };

  // Zuweisung löschen
  const handleDeleteAssignment = async (assignmentId) => {
    if (window.confirm('Sind Sie sicher, dass Sie diese Zuweisung löschen möchten?')) {
      try {
        await modelService.deleteAssignment(assignmentId);
        setAssignments(assignments.filter(a => a.id !== assignmentId));
        toast.success('Zuweisung erfolgreich gelöscht');
      } catch (error) {
        toast.error('Fehler beim Löschen der Zuweisung: ' + error.message);
      }
    }
  };

  // Provider-Konfiguration aktualisieren
  const handleProviderConfigChange = (key, value) => {
    setNewProvider({
      ...newProvider,
      config: {
        ...newProvider.config,
        [key]: value
      }
    });
  };

  // Modell-Parameter aktualisieren
  const handleModelParameterChange = (key, value) => {
    setNewModel({
      ...newModel,
      parameters: {
        ...newModel.parameters,
        [key]: value
      }
    });
  };

  // Test-Parameter aktualisieren
  const handleTestParameterChange = (key, value) => {
    setTestModel({
      ...testModel,
      parameters: {
        ...testModel.parameters,
        [key]: value
      }
    });
  };

  // Render-Funktion für Provider-Konfiguration basierend auf Provider-Typ
  const renderProviderConfig = (providerType) => {
    switch (providerType) {
      case 'openai':
        return (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700">API-Schlüssel</label>
              <input
                type="password"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={newProvider.config.api_key || ''}
                onChange={(e) => handleProviderConfigChange('api_key', e.target.value)}
              />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700">Basis-URL (optional)</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={newProvider.config.base_url || ''}
                onChange={(e) => handleProviderConfigChange('base_url', e.target.value)}
                placeholder="https://api.openai.com/v1"
              />
            </div>
          </>
        );
      case 'gemini':
        return (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">API-Schlüssel</label>
            <input
              type="password"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              value={newProvider.config.api_key || ''}
              onChange={(e) => handleProviderConfigChange('api_key', e.target.value)}
            />
          </div>
        );
      case 'ollama':
        return (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700">Host</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={newProvider.config.host || ''}
                onChange={(e) => handleProviderConfigChange('host', e.target.value)}
                placeholder="localhost"
              />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700">Port</label>
              <input
                type="number"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={newProvider.config.port || ''}
                onChange={(e) => handleProviderConfigChange('port', e.target.value)}
                placeholder="11434"
              />
            </div>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Modellkonfiguration</h1>
      
      <Tabs>
        <TabList>
          <Tab>Provider</Tab>
          <Tab>Modelle</Tab>
          <Tab>Zuweisungen</Tab>
          <Tab>Modelltest</Tab>
        </TabList>

        {/* Provider Tab */}
        <TabPanel>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-xl font-semibold mb-4">Provider hinzufügen</h2>
              <form onSubmit={handleCreateProvider}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <input
                    type="text"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    value={newProvider.name}
                    onChange={(e) => setNewProvider({...newProvider, name: e.target.value})}
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Provider-Typ</label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    value={newProvider.provider_type}
                    onChange={(e) => setNewProvider({...newProvider, provider_type: e.target.value})}
                    required
                  >
                    <option value="openai">OpenAI</option>
                    <option value="gemini">Google Gemini</option>
                    <option value="ollama">Ollama</option>
                  </select>
                </div>
                
                {renderProviderConfig(newProvider.provider_type)}
                
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Provider hinzufügen
                </button>
              </form>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-4">Vorhandene Provider</h2>
              {providers.length === 0 ? (
                <p className="text-gray-500">Keine Provider vorhanden</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Typ</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Aktionen</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {providers.map((provider) => (
                        <tr key={provider.id}>
                          <td className="px-6 py-4 whitespace-nowrap">{provider.name}</td>
                          <td className="px-6 py-4 whitespace-nowrap">{provider.provider_type}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              provider.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              {provider.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <button
                              onClick={() => handleDeleteProvider(provider.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              Löschen
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </TabPanel>

        {/* Modelle Tab */}
        <TabPanel>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-xl font-semibold mb-4">Modell hinzufügen</h2>
              <form onSubmit={handleCreateModel}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <input
                    type="text"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    value={newModel.name}
                    onChange={(e) => setNewModel({...newModel, name: e.target.value})}
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Provider</label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    value={newModel.provider_id}
                    onChange={(e) => setNewModel({...newModel, provider_id: e.target.value})}
                    required
                  >
                    <option value="">Provider auswählen</option>
                    {providers.map((provider) => (
                      <option key={provider.id} value={provider.id}>{provider.name}</option>
                    ))}
                  </select>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Modell-ID</label>
                  <input
                    type="text"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    value={newModel.model_id}
                    onChange={(e) => setNewModel({...newModel, model_id: e.target.value})}
                    placeholder="z.B. gpt-3.5-turbo, gemini-pro, llama2"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Modelltyp</label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    value={newModel.model_type}
                    onChange={(e) => setNewModel({...newModel, model_type: e.target.value})}
                    required
                  >
                    <option value="text">Text</option>
                    <option value="embedding">Embedding</option>
                    <option value="image">Bild</option>
                    <option value="multimodal">Multimodal</option>
                  </select>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Parameter</label>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-700">Temperatur</label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="2"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                        value={newModel.parameters.temperature || ''}
                        onChange={(e) => handleModelParameterChange('temperature', parseFloat(e.target.value))}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700">Max Tokens</label>
                      <input
                        type="number"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                        value={newModel.parameters.max_tokens || ''}
                        onChange={(e) => handleModelParameterChange('max_tokens', parseInt(e.target.value))}
                      />
                    </div>
                  </div>
                </div>
                <div className="mb-4 flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    checked={newModel.is_active}
                    onChange={(e) => setNewModel({...newModel, is_active: e.target.checked})}
                  />
                  <label className="ml-2 block text-sm text-gray-900">Aktiv</label>
                </div>
                <div className="mb-4 flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    checked={newModel.is_default}
                    onChange={(e) => setNewModel({...newModel, is_default: e.target.checked})}
                  />
                  <label className="ml-2 block text-sm text-gray-900">Standard für diesen Typ</label>
                </div>
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Modell hinzufügen
                </button>
              </form>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-4">Vorhandene Modelle</h2>
              {models.length === 0 ? (
                <p className="text-gray-500">Keine Modelle vorhanden</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Provider</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Modell-ID</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Typ</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Aktionen</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {models.map((model) => (
                        <tr key={model.id}>
                          <td className="px-6 py-4 whitespace-nowrap">{model.name}</td>
                          <td className="px-6 py-4 whitespace-nowrap">{model.provider_id}</td>
                          <td className="px-6 py-4 whitespace-nowrap">{model.model_id}</td>
                          <td className="px-6 py-4 whitespace-nowrap">{model.model_type}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                model.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                              }`}>
                                {model.is_active ? 'Aktiv' : 'Inaktiv'}
                              </span>
                              {model.is_default && (
                                <span className="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                                  Standard
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <button
                              onClick={() => handleDeleteModel(model.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              Löschen
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </TabPanel>

        {/* Zuweisungen Tab */}
        <TabPanel>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-xl font-semibold mb-4">Zuweisung hinzufügen</h2>
              <form onSubmit={handleCreateAssignment}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Agent</label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    value={newAssignment.agent_id}
                    onChange={(e) => setNewAssignment({...newAssignment, agent_id: e.target.value})}
                    required
                  >
                    <option value="">Agent auswählen</option>
                    {agents.map((agent) => (
                      <option key={agent.id} value={agent.id}>{agent.name}</option>
                    ))}
                  </select>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Primäres Modell</label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    value={newAssignment.model_id}
                    onChange={(e) => setNewAssignment({...newAssignment, model_id: e.target.value})}
                    required
                  >
                    <option value="">Modell auswählen</option>
                    {models.filter(m => m.is_active).map((model) => (
                      <option key={model.id} value={model.id}>{model.name} ({model.model_id})</option>
                    ))}
                  </select>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Fallback-Modell (optional)</label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    value={newAssignment.fallback_model_id || ''}
                    onChange={(e) => setNewAssignment({...newAssignment, fallback_model_id: e.target.value || null})}
                  >
                    <option value="">Kein Fallback</option>
                    {models.filter(m => m.is_active && m.id !== newAssignment.model_id).map((model) => (
                      <option key={model.id} value={model.id}>{model.name} ({model.model_id})</option>
                    ))}
                  </select>
                </div>
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Zuweisung hinzufügen
                </button>
              </form>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-4">Vorhandene Zuweisungen</h2>
              {assignments.length === 0 ? (
                <p className="text-gray-500">Keine Zuweisungen vorhanden</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Agent</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Primäres Modell</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fallback-Modell</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Aktionen</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {assignments.map((assignment) => (
                        <tr key={assignment.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {agents.find(a => a.id === assignment.agent_id)?.name || assignment.agent_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {models.find(m => m.id === assignment.model_id)?.name || assignment.model_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {assignment.fallback_model_id
                              ? models.find(m => m.id === assignment.fallback_model_id)?.name || assignment.fallback_model_id
                              : <span className="text-gray-400">Keins</span>
                            }
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <button
                              onClick={() => handleDeleteAssignment(assignment.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              Löschen
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </TabPanel>

        {/* Modelltest Tab */}
        <TabPanel>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-xl font-semibold mb-4">Modell testen</h2>
              <form onSubmit={handleTestModel}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Modell</label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    value={testModel.model_id}
                    onChange={(e) => setTestModel({...testModel, model_id: e.target.value})}
                    required
                  >
                    <option value="">Modell auswählen</option>
                    {models.filter(m => m.is_active && m.model_type === 'text').map((model) => (
                      <option key={model.id} value={model.id}>{model.name} ({model.model_id})</option>
                    ))}
                  </select>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Prompt</label>
                  <textarea
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    rows="4"
                    value={testModel.prompt}
                    onChange={(e) => setTestModel({...testModel, prompt: e.target.value})}
                    placeholder="Geben Sie einen Prompt ein, um das Modell zu testen..."
                    required
                  ></textarea>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Parameter</label>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-700">Temperatur</label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="2"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                        value={testModel.parameters.temperature || ''}
                        onChange={(e) => handleTestParameterChange('temperature', parseFloat(e.target.value))}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700">Max Tokens</label>
                      <input
                        type="number"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                        value={testModel.parameters.max_tokens || ''}
                        onChange={(e) => handleTestParameterChange('max_tokens', parseInt(e.target.value))}
                      />
                    </div>
                  </div>
                </div>
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
                  disabled={isLoading}
                >
                  {isLoading ? 'Wird ausgeführt...' : 'Modell testen'}
                </button>
              </form>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-4">Testergebnis</h2>
              {testResult ? (
                <div className={`p-4 rounded-md ${testResult.success ? 'bg-green-50' : 'bg-red-50'}`}>
                  <div className="mb-2 flex items-center">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      testResult.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {testResult.success ? 'Erfolgreich' : 'Fehler'}
                    </span>
                    <span className="ml-2 text-sm text-gray-500">
                      Ausführungszeit: {testResult.execution_time?.toFixed(2)}s
                    </span>
                  </div>
                  
                  {testResult.success ? (
                    <div>
                      <h3 className="text-md font-medium mb-2">Antwort:</h3>
                      <div className="bg-white p-3 rounded border border-gray-200 whitespace-pre-wrap">
                        {testResult.result?.text || JSON.stringify(testResult.result, null, 2)}
                      </div>
                      
                      {testResult.result?.usage && (
                        <div className="mt-4">
                          <h3 className="text-md font-medium mb-2">Nutzung:</h3>
                          <div className="grid grid-cols-3 gap-2 text-sm">
                            <div className="bg-gray-50 p-2 rounded">
                              <span className="font-medium">Prompt Tokens:</span> {testResult.result.usage.prompt_tokens}
                            </div>
                            <div className="bg-gray-50 p-2 rounded">
                              <span className="font-medium">Completion Tokens:</span> {testResult.result.usage.completion_tokens}
                            </div>
                            <div className="bg-gray-50 p-2 rounded">
                              <span className="font-medium">Gesamt Tokens:</span> {testResult.result.usage.total_tokens}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-red-700">
                      <h3 className="text-md font-medium mb-2">Fehler:</h3>
                      <div className="bg-white p-3 rounded border border-red-200">
                        {testResult.error}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-500">Noch kein Test durchgeführt</p>
              )}
            </div>
          </div>
        </TabPanel>
      </Tabs>
    </div>
  );
};

export default ModelConfiguration;

