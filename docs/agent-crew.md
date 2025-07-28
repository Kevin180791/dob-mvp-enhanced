# Erweiterte KI-Agenten-Crew

## Übersicht

Die erweiterte KI-Agenten-Crew des DOB-MVP bietet spezialisierte Agenten für verschiedene Aspekte des Bauprozesses. Diese Agenten arbeiten zusammen, um komplexe Aufgaben zu lösen und den Planungs- und Bauprozess zu optimieren.

## Verfügbare Agenten

### 1. RFI-Analyst-Agent

Der RFI-Analyst-Agent analysiert und kategorisiert eingehende RFIs (Requests for Information). Er identifiziert die Art der Anfrage, die betroffenen Gewerke und die Priorität.

**Hauptfunktionen:**
- Analyse und Kategorisierung von RFIs
- Identifikation relevanter Dokumente
- Priorisierung basierend auf Dringlichkeit und Auswirkung
- Zuweisung an die entsprechenden Fachbereiche

### 2. Plan-Reviewer-Agent

Der Plan-Reviewer-Agent untersucht Baupläne und technische Zeichnungen, um relevante Informationen für RFIs zu extrahieren.

**Hauptfunktionen:**
- Analyse von CAD-Zeichnungen und BIM-Modellen
- Identifikation von Konflikten und Problemen
- Extraktion relevanter Informationen für RFIs
- Vorschläge für Lösungen basierend auf Best Practices

### 3. Kommunikations-Agent

Der Kommunikations-Agent erstellt strukturierte, präzise Antworten auf RFIs basierend auf den Analysen der anderen Agenten.

**Hauptfunktionen:**
- Erstellung klarer, präziser Antworten
- Anpassung des Kommunikationsstils an den Empfänger
- Integration von Referenzen und Belegen
- Generierung von Antwortvorschlägen zur Überprüfung

### 4. Kosten-Schätzungs-Agent

Der Kosten-Schätzungs-Agent analysiert die finanziellen Auswirkungen von RFIs und vorgeschlagenen Änderungen.

**Hauptfunktionen:**
- Schätzung der Kosten für vorgeschlagene Änderungen
- Analyse der Kostenauswirkungen auf das Gesamtprojekt
- Identifikation von Kosteneinsparungspotentialen
- Vergleich verschiedener Lösungsansätze aus finanzieller Sicht

### 5. Terminplan-Auswirkungs-Agent

Der Terminplan-Auswirkungs-Agent analysiert die Auswirkungen von RFIs und Änderungen auf den Projektterminplan.

**Hauptfunktionen:**
- Bewertung der Terminauswirkungen von Änderungen
- Identifikation kritischer Pfade und Abhängigkeiten
- Vorschläge für Terminplanoptimierungen
- Simulation verschiedener Szenarien und deren Auswirkungen

### 6. Compliance-Agent

Der Compliance-Agent überprüft, ob vorgeschlagene Lösungen den geltenden Normen, Vorschriften und Verträgen entsprechen.

**Hauptfunktionen:**
- Überprüfung der Einhaltung von Bauvorschriften und Normen
- Analyse vertraglicher Anforderungen und Verpflichtungen
- Identifikation potentieller Compliance-Risiken
- Vorschläge für konforme Alternativen

### 7. Dokumentenanalyse-Agent

Der Dokumentenanalyse-Agent extrahiert relevante Informationen aus verschiedenen Dokumenttypen wie Verträgen, Spezifikationen und Berichten.

**Hauptfunktionen:**
- Extraktion relevanter Informationen aus Dokumenten
- Verknüpfung von Informationen aus verschiedenen Quellen
- Identifikation von Widersprüchen und Lücken
- Erstellung von Zusammenfassungen und Übersichten

### 8. Koordinations-Agent

Der Koordinations-Agent orchestriert die Zusammenarbeit zwischen den verschiedenen Agenten und stellt sicher, dass alle relevanten Informationen berücksichtigt werden.

**Hauptfunktionen:**
- Orchestrierung der Agenten-Crew
- Priorisierung und Zuweisung von Aufgaben
- Zusammenführung von Ergebnissen und Erkenntnissen
- Überwachung des Gesamtfortschritts

## Integration und Zusammenarbeit

Die Agenten arbeiten in einer koordinierten Crew zusammen, wobei der Koordinations-Agent als zentraler Orchestrator fungiert. Jeder Agent hat Zugriff auf das gemeinsame Wissen und kann die Ergebnisse anderer Agenten nutzen.

Die Zusammenarbeit erfolgt über definierte Schnittstellen und Protokolle, die eine nahtlose Integration ermöglichen. Die Agenten kommunizieren über ein gemeinsames Nachrichtensystem und teilen Erkenntnisse über eine zentrale Wissensdatenbank.

## Konfiguration und Anpassung

Jeder Agent kann individuell konfiguriert und an spezifische Projektanforderungen angepasst werden. Die Konfiguration umfasst:

- Auswahl des zu verwendenden KI-Modells (OpenAI, Gemini, Ollama)
- Anpassung der Prompts und Anweisungen
- Festlegung von Schwellenwerten und Prioritäten
- Definition von Zugriffsrechten und Berechtigungen

## Erweiterbarkeit

Das Agenten-System ist modular aufgebaut und kann leicht um weitere spezialisierte Agenten erweitert werden. Neue Agenten können durch Implementierung der Basis-Agent-Klasse hinzugefügt werden.

## Beispiel-Workflow

1. Ein RFI wird eingereicht und vom RFI-Analyst-Agenten analysiert
2. Der Koordinations-Agent weist Aufgaben an relevante Agenten zu
3. Der Plan-Reviewer-Agent analysiert relevante Pläne und Zeichnungen
4. Der Dokumentenanalyse-Agent extrahiert Informationen aus Spezifikationen
5. Der Kosten-Schätzungs-Agent bewertet finanzielle Auswirkungen
6. Der Terminplan-Auswirkungs-Agent analysiert Auswirkungen auf den Zeitplan
7. Der Compliance-Agent überprüft die Einhaltung von Vorschriften
8. Der Kommunikations-Agent erstellt eine strukturierte Antwort
9. Die Antwort wird zur Überprüfung und Freigabe vorgelegt

