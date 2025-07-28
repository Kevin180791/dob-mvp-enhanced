# DOB-MVP Modell-Integration Architektur

## Übersicht

Diese Dokumentation beschreibt die Architektur für die Integration von Google Gemini API und lokalen Ollama-Modellen in das DOB-MVP. Die Architektur ermöglicht eine flexible Konfiguration und Auswahl verschiedener KI-Modelle über das Frontend.

## Architekturprinzipien

Die Modell-Integration folgt diesen Prinzipien:

1. **Abstraktion**: Einheitliche Schnittstelle für verschiedene KI-Modelle
2. **Erweiterbarkeit**: Einfache Integration neuer Modelle und Provider
3. **Konfigurierbarkeit**: Vollständige Konfiguration über das Frontend
4. **Ausfallsicherheit**: Fallback-Mechanismen bei Nichtverfügbarkeit von Modellen
5. **Leistungsoptimierung**: Intelligente Modellauswahl basierend auf Anforderungen

## Systemarchitektur

Die Modell-Integration erweitert die bestehende DOB-MVP-Architektur um folgende Komponenten:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend                                 │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Modell-Auswahl  │  │ Modell-Konfig.  │  │ Modell-Status   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API-Schicht                              │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Modell-API      │  │ Konfig-API      │  │ Status-API      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Modell-Manager-Schicht                       │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Modell-Registry │  │ Modell-Router   │  │ Modell-Cache    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Modell-Provider-Schicht                      │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ OpenAI-Provider │  │ Gemini-Provider │  │ Ollama-Provider │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Komponenten

### 1. Modell-Provider-Schicht

Diese Schicht stellt die Verbindung zu den verschiedenen KI-Modell-Providern her.

#### 1.1 OpenAI-Provider

- **Funktionen**: Verbindung zur OpenAI API
- **Unterstützte Modelle**: GPT-3.5, GPT-4, etc.
- **Konfigurationsoptionen**: API-Schlüssel, Modellversion, Parameter (Temperatur, etc.)

#### 1.2 Gemini-Provider

- **Funktionen**: Verbindung zur Google Gemini API
- **Unterstützte Modelle**: Gemini Pro, Gemini Ultra, etc.
- **Konfigurationsoptionen**: API-Schlüssel, Modellversion, Parameter

#### 1.3 Ollama-Provider

- **Funktionen**: Verbindung zu lokalen oder netzwerkbasierten Ollama-Instanzen
- **Unterstützte Modelle**: Llama, Mistral, Vicuna, etc.
- **Konfigurationsoptionen**: Host, Port, Modellname, Parameter

### 2. Modell-Manager-Schicht

Diese Schicht verwaltet die verfügbaren Modelle und leitet Anfragen an die entsprechenden Provider weiter.

#### 2.1 Modell-Registry

- **Funktionen**: Registrierung und Verwaltung verfügbarer Modelle
- **Datenstruktur**: Modell-ID, Provider, Konfiguration, Status
- **Operationen**: Registrieren, Aktualisieren, Entfernen, Auflisten von Modellen

#### 2.2 Modell-Router

- **Funktionen**: Intelligentes Routing von Anfragen an das passende Modell
- **Routing-Strategien**: Priorität, Verfügbarkeit, Kosten, Leistung
- **Fallback-Mechanismen**: Automatischer Wechsel bei Nichtverfügbarkeit

#### 2.3 Modell-Cache

- **Funktionen**: Caching von Modellantworten für häufige Anfragen
- **Cache-Strategien**: LRU, TTL, Kontextbasiert
- **Optimierungen**: Vorausschauendes Caching, Batch-Verarbeitung

### 3. API-Schicht

Diese Schicht stellt RESTful-Endpunkte für die Interaktion mit dem Frontend bereit.

#### 3.1 Modell-API

- **Endpunkte**: `/api/v1/models`, `/api/v1/models/{id}`
- **Operationen**: GET, POST, PUT, DELETE
- **Funktionen**: Abfragen, Hinzufügen, Aktualisieren, Entfernen von Modellen

#### 3.2 Konfig-API

- **Endpunkte**: `/api/v1/models/{id}/config`
- **Operationen**: GET, PUT
- **Funktionen**: Abfragen und Aktualisieren der Modellkonfiguration

#### 3.3 Status-API

- **Endpunkte**: `/api/v1/models/status`, `/api/v1/models/{id}/status`
- **Operationen**: GET
- **Funktionen**: Abfragen des Modellstatus und der Verfügbarkeit

### 4. Frontend-Komponenten

Diese Komponenten ermöglichen die Benutzerinteraktion mit den KI-Modellen.

#### 4.1 Modell-Auswahl

- **Funktionen**: Auswahl des zu verwendenden Modells für verschiedene Agenten
- **UI-Elemente**: Dropdown-Menüs, Radio-Buttons, Suchfeld
- **Interaktionen**: Modellauswahl, Filterung, Sortierung

#### 4.2 Modell-Konfiguration

- **Funktionen**: Konfiguration der Modellparameter
- **UI-Elemente**: Formulare, Schieberegler, Eingabefelder
- **Interaktionen**: Parameter anpassen, Speichern, Zurücksetzen

#### 4.3 Modell-Status

- **Funktionen**: Anzeige des Modellstatus und der Verfügbarkeit
- **UI-Elemente**: Status-Badges, Verfügbarkeitsanzeigen
- **Interaktionen**: Status aktualisieren, Verfügbarkeit testen

## Datenmodell

### 1. Model

```json
{
  "id": "string",
  "name": "string",
  "provider": "openai|gemini|ollama",
  "type": "text|embedding|image|multimodal",
  "capabilities": ["chat", "completion", "embedding", "image", "audio"],
  "default": "boolean",
  "active": "boolean",
  "config": {
    "provider_specific_config": "object"
  },
  "parameters": {
    "temperature": "number",
    "max_tokens": "number",
    "top_p": "number",
    "frequency_penalty": "number",
    "presence_penalty": "number"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 2. ModelProvider

```json
{
  "id": "string",
  "name": "string",
  "type": "openai|gemini|ollama",
  "config": {
    "api_key": "string",
    "base_url": "string",
    "timeout": "number"
  },
  "status": "active|inactive",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 3. ModelAssignment

```json
{
  "id": "string",
  "agent_id": "string",
  "model_id": "string",
  "priority": "number",
  "fallback_model_id": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Implementierungsdetails

### 1. Backend-Implementierung

#### 1.1 Modell-Provider-Implementierung

Jeder Modell-Provider wird als separate Klasse implementiert, die eine gemeinsame Schnittstelle implementiert:

```python
class ModelProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, parameters: dict) -> str:
        pass
    
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        pass
    
    @abstractmethod
    async def check_status(self) -> bool:
        pass
```

#### 1.2 Gemini-Provider-Implementierung

```python
class GeminiProvider(ModelProvider):
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model = model
        self.client = genai.GenerativeModel(model_name=model, api_key=api_key)
    
    async def generate(self, prompt: str, parameters: dict) -> str:
        response = self.client.generate_content(prompt, **parameters)
        return response.text
    
    async def embed(self, text: str) -> List[float]:
        embedding_model = "embedding-001"
        response = genai.embed_content(
            model=embedding_model,
            content=text,
            task_type="retrieval_document",
            api_key=self.api_key
        )
        return response["embedding"]
    
    async def check_status(self) -> bool:
        try:
            self.client.generate_content("test")
            return True
        except Exception:
            return False
```

#### 1.3 Ollama-Provider-Implementierung

```python
class OllamaProvider(ModelProvider):
    def __init__(self, host: str = "localhost", port: int = 11434, model: str = "llama2"):
        self.host = host
        self.port = port
        self.model = model
        self.base_url = f"http://{host}:{port}"
    
    async def generate(self, prompt: str, parameters: dict) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, **parameters}
            ) as response:
                result = await response.json()
                return result["response"]
    
    async def embed(self, text: str) -> List[float]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text}
            ) as response:
                result = await response.json()
                return result["embedding"]
    
    async def check_status(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    return response.status == 200
        except Exception:
            return False
```

#### 1.4 Modell-Router-Implementierung

```python
class ModelRouter:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
    
    async def route(self, agent_id: str, operation: str, input_data: Any, parameters: dict) -> Any:
        # Get model assignment for agent
        assignment = await self.registry.get_assignment(agent_id)
        
        # Try primary model
        try:
            model = await self.registry.get_model(assignment.model_id)
            provider = self.registry.get_provider(model.provider)
            
            if operation == "generate":
                return await provider.generate(input_data, {**model.parameters, **parameters})
            elif operation == "embed":
                return await provider.embed(input_data)
        except Exception as e:
            logger.error(f"Error using primary model: {e}")
            
            # Try fallback model if available
            if assignment.fallback_model_id:
                try:
                    fallback_model = await self.registry.get_model(assignment.fallback_model_id)
                    fallback_provider = self.registry.get_provider(fallback_model.provider)
                    
                    if operation == "generate":
                        return await fallback_provider.generate(input_data, {**fallback_model.parameters, **parameters})
                    elif operation == "embed":
                        return await fallback_provider.embed(input_data)
                except Exception as fallback_e:
                    logger.error(f"Error using fallback model: {fallback_e}")
            
            # Re-raise original exception if fallback fails or is not available
            raise e
```

### 2. Frontend-Implementierung

#### 2.1 Modell-Auswahl-Komponente

```jsx
import React, { useState, useEffect } from 'react';
import { getModels, getModelAssignments, updateModelAssignment } from '../services/modelService';

const ModelSelector = ({ agentId, onModelChange }) => {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [fallbackModel, setFallbackModel] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      const modelsData = await getModels();
      setModels(modelsData);
      
      const assignments = await getModelAssignments(agentId);
      if (assignments.length > 0) {
        setSelectedModel(assignments[0].model_id);
        setFallbackModel(assignments[0].fallback_model_id);
      } else if (modelsData.length > 0) {
        // Set default model if no assignment exists
        const defaultModel = modelsData.find(m => m.default) || modelsData[0];
        setSelectedModel(defaultModel.id);
      }
    };
    
    fetchData();
  }, [agentId]);
  
  const handleModelChange = async (modelId) => {
    setSelectedModel(modelId);
    await updateModelAssignment(agentId, modelId, fallbackModel);
    onModelChange(modelId);
  };
  
  const handleFallbackChange = async (modelId) => {
    setFallbackModel(modelId);
    await updateModelAssignment(agentId, selectedModel, modelId);
  };
  
  return (
    <div className="model-selector">
      <div className="form-group">
        <label>Primary Model</label>
        <select 
          value={selectedModel || ''} 
          onChange={(e) => handleModelChange(e.target.value)}
        >
          <option value="">Select a model</option>
          {models.map(model => (
            <option key={model.id} value={model.id}>
              {model.name} ({model.provider})
            </option>
          ))}
        </select>
      </div>
      
      <div className="form-group">
        <label>Fallback Model</label>
        <select 
          value={fallbackModel || ''} 
          onChange={(e) => handleFallbackChange(e.target.value)}
        >
          <option value="">No fallback</option>
          {models
            .filter(model => model.id !== selectedModel)
            .map(model => (
              <option key={model.id} value={model.id}>
                {model.name} ({model.provider})
              </option>
            ))
          }
        </select>
      </div>
    </div>
  );
};

export default ModelSelector;
```

#### 2.2 Modell-Konfiguration-Komponente

```jsx
import React, { useState, useEffect } from 'react';
import { getModel, updateModel } from '../services/modelService';

const ModelConfig = ({ modelId }) => {
  const [model, setModel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchModel = async () => {
      try {
        setLoading(true);
        const modelData = await getModel(modelId);
        setModel(modelData);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    if (modelId) {
      fetchModel();
    }
  }, [modelId]);
  
  const handleParameterChange = (param, value) => {
    setModel(prev => ({
      ...prev,
      parameters: {
        ...prev.parameters,
        [param]: value
      }
    }));
  };
  
  const handleProviderConfigChange = (key, value) => {
    setModel(prev => ({
      ...prev,
      config: {
        ...prev.config,
        [key]: value
      }
    }));
  };
  
  const handleSave = async () => {
    try {
      await updateModel(modelId, model);
      alert('Model configuration saved successfully');
    } catch (err) {
      setError(err.message);
    }
  };
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!model) return <div>No model selected</div>;
  
  return (
    <div className="model-config">
      <h2>{model.name} Configuration</h2>
      
      <div className="config-section">
        <h3>General Settings</h3>
        <div className="form-group">
          <label>Name</label>
          <input 
            type="text" 
            value={model.name} 
            onChange={(e) => setModel({...model, name: e.target.value})}
          />
        </div>
        
        <div className="form-group">
          <label>Active</label>
          <input 
            type="checkbox" 
            checked={model.active} 
            onChange={(e) => setModel({...model, active: e.target.checked})}
          />
        </div>
      </div>
      
      <div className="config-section">
        <h3>Model Parameters</h3>
        
        <div className="form-group">
          <label>Temperature</label>
          <input 
            type="range" 
            min="0" 
            max="1" 
            step="0.1" 
            value={model.parameters.temperature || 0.7} 
            onChange={(e) => handleParameterChange('temperature', parseFloat(e.target.value))}
          />
          <span>{model.parameters.temperature || 0.7}</span>
        </div>
        
        <div className="form-group">
          <label>Max Tokens</label>
          <input 
            type="number" 
            value={model.parameters.max_tokens || 1024} 
            onChange={(e) => handleParameterChange('max_tokens', parseInt(e.target.value))}
          />
        </div>
        
        <div className="form-group">
          <label>Top P</label>
          <input 
            type="range" 
            min="0" 
            max="1" 
            step="0.1" 
            value={model.parameters.top_p || 1} 
            onChange={(e) => handleParameterChange('top_p', parseFloat(e.target.value))}
          />
          <span>{model.parameters.top_p || 1}</span>
        </div>
      </div>
      
      {model.provider === 'ollama' && (
        <div className="config-section">
          <h3>Ollama Configuration</h3>
          
          <div className="form-group">
            <label>Host</label>
            <input 
              type="text" 
              value={model.config.host || 'localhost'} 
              onChange={(e) => handleProviderConfigChange('host', e.target.value)}
            />
          </div>
          
          <div className="form-group">
            <label>Port</label>
            <input 
              type="number" 
              value={model.config.port || 11434} 
              onChange={(e) => handleProviderConfigChange('port', parseInt(e.target.value))}
            />
          </div>
        </div>
      )}
      
      {model.provider === 'gemini' && (
        <div className="config-section">
          <h3>Gemini Configuration</h3>
          
          <div className="form-group">
            <label>API Key</label>
            <input 
              type="password" 
              value={model.config.api_key || ''} 
              onChange={(e) => handleProviderConfigChange('api_key', e.target.value)}
            />
          </div>
        </div>
      )}
      
      <div className="actions">
        <button onClick={handleSave}>Save Configuration</button>
      </div>
    </div>
  );
};

export default ModelConfig;
```

#### 2.3 Modell-Status-Komponente

```jsx
import React, { useState, useEffect } from 'react';
import { getModelStatus, testModel } from '../services/modelService';

const ModelStatus = ({ modelId }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);
  
  const fetchStatus = async () => {
    try {
      setLoading(true);
      const statusData = await getModelStatus(modelId);
      setStatus(statusData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    if (modelId) {
      fetchStatus();
      
      // Poll status every 30 seconds
      const interval = setInterval(fetchStatus, 30000);
      return () => clearInterval(interval);
    }
  }, [modelId]);
  
  const handleTestModel = async () => {
    try {
      setTesting(true);
      const result = await testModel(modelId);
      setStatus({
        ...status,
        available: result.success,
        last_tested: new Date().toISOString(),
        response_time: result.response_time
      });
    } catch (err) {
      console.error(err);
    } finally {
      setTesting(false);
    }
  };
  
  if (loading) return <div>Loading status...</div>;
  if (!status) return <div>No status available</div>;
  
  return (
    <div className="model-status">
      <h3>Model Status</h3>
      
      <div className="status-indicator">
        <span className={`status-badge ${status.available ? 'available' : 'unavailable'}`}>
          {status.available ? 'Available' : 'Unavailable'}
        </span>
      </div>
      
      <div className="status-details">
        <div className="status-item">
          <span className="label">Last Checked:</span>
          <span className="value">{new Date(status.last_tested).toLocaleString()}</span>
        </div>
        
        {status.response_time && (
          <div className="status-item">
            <span className="label">Response Time:</span>
            <span className="value">{status.response_time}ms</span>
          </div>
        )}
        
        {status.error && (
          <div className="status-item error">
            <span className="label">Error:</span>
            <span className="value">{status.error}</span>
          </div>
        )}
      </div>
      
      <div className="actions">
        <button 
          onClick={handleTestModel} 
          disabled={testing}
        >
          {testing ? 'Testing...' : 'Test Connection'}
        </button>
      </div>
    </div>
  );
};

export default ModelStatus;
```

## Integration mit bestehenden Agenten

Die bestehenden Agenten im DOB-MVP werden erweitert, um die neue Modell-Auswahl-Architektur zu nutzen:

```python
class BaseAgent:
    def __init__(self, name: str, model_router: ModelRouter):
        self.name = name
        self.model_router = model_router
        self.agent_id = f"agent_{name.lower().replace(' ', '_')}"
    
    async def generate_response(self, prompt: str, parameters: dict = None) -> str:
        parameters = parameters or {}
        return await self.model_router.route(self.agent_id, "generate", prompt, parameters)
    
    async def get_embeddings(self, text: str) -> List[float]:
        return await self.model_router.route(self.agent_id, "embed", text, {})
```

## Konfiguration und Umgebungsvariablen

Die folgenden Umgebungsvariablen werden für die Modell-Integration hinzugefügt:

```
# OpenAI-Konfiguration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4

# Gemini-Konfiguration
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-pro

# Ollama-Konfiguration
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=llama2

# Modell-Konfiguration
DEFAULT_MODEL_PROVIDER=openai
ENABLE_MODEL_CACHE=true
MODEL_CACHE_TTL=3600
```

## Deployment-Anpassungen

Die Docker-Compose-Konfiguration wird angepasst, um die neuen Umgebungsvariablen zu unterstützen:

```yaml
services:
  backend:
    # ...
    environment:
      # Bestehende Umgebungsvariablen
      # ...
      # Neue Umgebungsvariablen für Modell-Integration
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL=${OPENAI_MODEL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GEMINI_MODEL=${GEMINI_MODEL}
      - OLLAMA_HOST=${OLLAMA_HOST}
      - OLLAMA_PORT=${OLLAMA_PORT}
      - OLLAMA_MODEL=${OLLAMA_MODEL}
      - DEFAULT_MODEL_PROVIDER=${DEFAULT_MODEL_PROVIDER}
      - ENABLE_MODEL_CACHE=${ENABLE_MODEL_CACHE}
      - MODEL_CACHE_TTL=${MODEL_CACHE_TTL}
```

## Fazit

Die beschriebene Architektur ermöglicht eine flexible Integration von Google Gemini API und lokalen Ollama-Modellen in das DOB-MVP. Die Modelle können über das Frontend konfiguriert, ausgewählt und eingestellt werden. Die Architektur ist erweiterbar und kann leicht um weitere Modell-Provider erweitert werden.

