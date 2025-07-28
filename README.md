# Digitales Betriebssystem für das Bauwesen (DOB-MVP)

## Übersicht

Das Digitale Betriebssystem für das Bauwesen (DOB-MVP) ist eine KI-gestützte Plattform für die Verwaltung von Bauprozessen, mit besonderem Fokus auf RFIs (Requests for Information) und die Zusammenarbeit zwischen Planungsbüros und ausführenden Firmen.

## Hauptfunktionen

### 1. RFI-Management

- Erfassung und Verwaltung von RFIs
- KI-gestützte Analyse und Kategorisierung
- Automatische Identifikation relevanter Dokumente
- Generierung von Antwortvorschlägen
- Nachverfolgung und Dokumentation

### 2. Erweiterte KI-Agenten-Crew

- **RFI-Analyst-Agent**: Analyse und Kategorisierung von RFIs
- **Plan-Reviewer-Agent**: Analyse von Bauplänen und technischen Zeichnungen
- **Kommunikations-Agent**: Erstellung strukturierter Antworten
- **Kosten-Schätzungs-Agent**: Analyse finanzieller Auswirkungen
- **Terminplan-Auswirkungs-Agent**: Analyse von Terminauswirkungen
- **Compliance-Agent**: Überprüfung der Einhaltung von Vorschriften
- **Dokumentenanalyse-Agent**: Extraktion von Informationen aus Dokumenten
- **Koordinations-Agent**: Orchestrierung der Agenten-Crew

### 3. Multimodale Dokumentenanalyse

- Verarbeitung verschiedener Dokumenttypen (Text, Bilder, CAD, BIM)
- Extraktion und Verknüpfung von Informationen
- Visuelle Analyse von Zeichnungen und Fotos
- Semantische Verknüpfung von Informationen
- Kontextuelle Suche und Retrieval

### 4. Kollaborative Workflow-Engine

- Definition und Ausführung flexibler Workflows
- Rollenbasierte Zugriffssteuerung
- Aufgabenverwaltung und Benachrichtigungen
- Integration mit KI-Agenten für Automatisierung
- Monitoring und Reporting

### 5. Modellkonfiguration

- Unterstützung für verschiedene KI-Modelle:
  - OpenAI (GPT-4, GPT-3.5)
  - Google Gemini
  - Lokale Ollama-Modelle
- Benutzerfreundliche Konfigurationsoberfläche
- Modelltest-Funktionalität
- Flexible Agenten-Modell-Zuweisung

## Technische Architektur

### Backend

- **FastAPI**: RESTful API für alle Funktionen
- **SQLAlchemy**: ORM für Datenbankzugriff
- **PostgreSQL**: Relationale Datenbank
- **Qdrant**: Vektordatenbank für semantische Suche
- **Neo4j**: Graphdatenbank für Beziehungen und Abhängigkeiten

### Frontend

- **React**: UI-Framework
- **Tailwind CSS**: Styling
- **Vite**: Build-Tool
- **React Router**: Routing
- **React Query**: Datenfetching und -caching

### KI-Komponenten

- **OpenAI Integration**: GPT-4, GPT-3.5
- **Google Gemini Integration**: Gemini Pro, Gemini Ultra
- **Ollama Integration**: Lokale Open-Source-Modelle
- **RAG-System**: Retrieval-Augmented Generation
- **Multimodales System**: Verarbeitung verschiedener Modalitäten

## Installation

### Voraussetzungen

- Docker und Docker Compose
- Node.js 18+ (für Entwicklung)
- Python 3.10+ (für Entwicklung)

### Installation mit Docker

1. Repository klonen:
   ```bash
   git clone https://github.com/yourusername/dob-mvp.git
   cd dob-mvp
   ```

2. Umgebungsvariablen konfigurieren:
   ```bash
   cp .env.example .env
   # Bearbeiten Sie die .env-Datei und fügen Sie Ihre API-Schlüssel hinzu
   ```

3. Docker-Container starten:
   ```bash
   docker-compose up -d
   ```

4. Zugriff auf die Anwendung:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:3001
   - API-Dokumentation: http://localhost:3001/docs

### Installation für Entwicklung

1. Repository klonen:
   ```bash
   git clone https://github.com/yourusername/dob-mvp.git
   cd dob-mvp
   ```

2. Backend-Abhängigkeiten installieren:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Frontend-Abhängigkeiten installieren:
   ```bash
   cd ../frontend
   npm install
   ```

4. Umgebungsvariablen konfigurieren:
   ```bash
   cp ../.env.example ../.env
   # Bearbeiten Sie die .env-Datei und fügen Sie Ihre API-Schlüssel hinzu
   ```

5. Backend starten:
   ```bash
   cd ../backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 3001
   ```

6. Frontend starten:
   ```bash
   cd ../frontend
   npm run dev
   ```

7. Zugriff auf die Anwendung:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:3001
   - API-Dokumentation: http://localhost:3001/docs

## Konfiguration

### KI-Modelle

Die KI-Modelle können über die Benutzeroberfläche konfiguriert werden:

1. Navigieren Sie zu "Einstellungen" > "Modellkonfiguration"
2. Fügen Sie Ihre API-Schlüssel für OpenAI und Google Gemini hinzu
3. Konfigurieren Sie die Ollama-Verbindung für lokale Modelle
4. Testen Sie die Modelle direkt in der Benutzeroberfläche
5. Weisen Sie Modelle den verschiedenen Agenten zu

### Workflows

Workflows können über die Benutzeroberfläche konfiguriert werden:

1. Navigieren Sie zu "Einstellungen" > "Workflows"
2. Wählen Sie eine Workflow-Vorlage oder erstellen Sie einen neuen Workflow
3. Konfigurieren Sie die Workflow-Schritte und -Regeln
4. Definieren Sie Rollen und Berechtigungen
5. Aktivieren Sie den Workflow

## Dokumentation

Weitere Dokumentation finden Sie im `docs`-Verzeichnis:

- [Architektur](docs/architecture.md)
- [API-Dokumentation](docs/api.md)
- [Benutzerhandbuch](docs/user-guide.md)
- [Entwicklerhandbuch](docs/developer-guide.md)
- [Erweiterte KI-Agenten-Crew](docs/agent-crew.md)
- [Multimodale Dokumentenanalyse](docs/multimodal-document-analysis.md)
- [Kollaborative Workflow-Engine](docs/collaborative-workflow-engine.md)

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](LICENSE)-Datei für Details.

