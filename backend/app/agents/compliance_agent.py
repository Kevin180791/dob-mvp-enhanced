"""
Compliance-Agent für das DOB-MVP.

Dieser Agent überprüft die Einhaltung von Bauvorschriften, Normen und Standards
und gibt Empfehlungen zur Behebung von Compliance-Problemen.
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import re

from app.agents.base import BaseAgent
from app.core.model_manager.registry import ModelRegistry

logger = logging.getLogger(__name__)

class ComplianceAgent(BaseAgent):
    """
    Agent zur Überprüfung der Einhaltung von Bauvorschriften.
    
    Dieser Agent überprüft die Einhaltung von Bauvorschriften, Normen und Standards
    und gibt Empfehlungen zur Behebung von Compliance-Problemen.
    """
    
    def __init__(self, model_registry: ModelRegistry):
        """
        Initialisiert den Compliance-Agenten.
        
        Args:
            model_registry: Registry für KI-Modelle
        """
        super().__init__(model_registry, "compliance_agent")
        self.regulations_database = {}  # Einfache In-Memory-Datenbank für Vorschriften
        self._initialize_regulations_database()
        
    def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Überprüft die Einhaltung von Bauvorschriften für eine RFI oder Änderungsanfrage.
        
        Args:
            data: Daten der RFI oder Änderungsanfrage
                - description: Beschreibung der Anfrage
                - project_id: ID des Projekts
                - documents: Liste der relevanten Dokumente
                - category: Kategorie der Anfrage
                - region: Region des Projekts (für regionale Vorschriften)
                - building_type: Gebäudetyp (für typspezifische Vorschriften)
        
        Returns:
            Dict mit Compliance-Analyse und Empfehlungen
        """
        logger.info(f"Überprüfe Compliance für Anfrage: {data.get('id', 'Neue Anfrage')}")
        
        # Extrahiere relevante Daten
        description = data.get("description", "")
        project_id = data.get("project_id", "")
        documents = data.get("documents", [])
        category = data.get("category", "")
        region = data.get("region", "Deutschland")
        building_type = data.get("building_type", "Gewerbe")
        
        # Hole relevante Vorschriften
        relevant_regulations = self._get_relevant_regulations(category, region, building_type)
        
        # Erstelle Prompt für das KI-Modell
        prompt = self._create_compliance_check_prompt(description, documents, category, 
                                                    region, building_type, relevant_regulations)
        
        # Rufe KI-Modell auf
        model_response = self._call_model(prompt)
        
        # Verarbeite die Antwort
        compliance_check = self._process_compliance_check_response(model_response)
        
        # Speichere die Analyse in der Datenbank
        self._store_compliance_check(project_id, data.get("id", f"temp-{datetime.now().isoformat()}"), compliance_check)
        
        return compliance_check
    
    def generate_compliance_report(self, project_id: str) -> Dict[str, Any]:
        """
        Generiert einen umfassenden Compliance-Bericht für ein Projekt.
        
        Args:
            project_id: ID des Projekts
        
        Returns:
            Dict mit Compliance-Bericht
        """
        logger.info(f"Generiere Compliance-Bericht für Projekt: {project_id}")
        
        # Hole alle Compliance-Checks für das Projekt
        project_checks = self._get_project_checks(project_id)
        
        # Erstelle Prompt für das KI-Modell
        prompt = self._create_compliance_report_prompt(project_id, project_checks)
        
        # Rufe KI-Modell auf
        model_response = self._call_model(prompt)
        
        # Verarbeite die Antwort
        compliance_report = self._process_compliance_report_response(model_response, project_checks)
        
        return compliance_report
    
    def _initialize_regulations_database(self) -> None:
        """
        Initialisiert die Datenbank mit grundlegenden Bauvorschriften.
        """
        # Beispielhafte Vorschriften für Deutschland
        self.regulations_database["Deutschland"] = {
            "Allgemein": [
                {
                    "id": "MBO-2016",
                    "name": "Musterbauordnung 2016",
                    "description": "Grundlegende Bauvorschriften für Deutschland",
                    "url": "https://www.bauministerkonferenz.de/verzeichnis/42463.pdf"
                },
                {
                    "id": "EnEV-2014",
                    "name": "Energieeinsparverordnung 2014",
                    "description": "Vorschriften zur Energieeffizienz von Gebäuden",
                    "url": "https://www.gesetze-im-internet.de/enev_2007/"
                },
                {
                    "id": "ArbStättV",
                    "name": "Arbeitsstättenverordnung",
                    "description": "Vorschriften für Arbeitsstätten",
                    "url": "https://www.gesetze-im-internet.de/arbst_ttv_2004/"
                }
            ],
            "Brandschutz": [
                {
                    "id": "DIN-4102",
                    "name": "DIN 4102 - Brandverhalten von Baustoffen und Bauteilen",
                    "description": "Klassifizierung und Prüfung des Brandverhaltens von Baustoffen",
                    "url": "https://www.beuth.de/de/norm/din-4102-1/40229178"
                },
                {
                    "id": "MVStättV",
                    "name": "Musterverordnung über den Bau und Betrieb von Versammlungsstätten",
                    "description": "Vorschriften für Versammlungsstätten",
                    "url": "https://www.bauministerkonferenz.de/verzeichnis/42463.pdf"
                }
            ],
            "Barrierefreiheit": [
                {
                    "id": "DIN-18040",
                    "name": "DIN 18040 - Barrierefreies Bauen",
                    "description": "Planungsgrundlagen für barrierefreies Bauen",
                    "url": "https://www.beuth.de/de/norm/din-18040-1/133694958"
                }
            ],
            "Schallschutz": [
                {
                    "id": "DIN-4109",
                    "name": "DIN 4109 - Schallschutz im Hochbau",
                    "description": "Anforderungen und Nachweise für den Schallschutz",
                    "url": "https://www.beuth.de/de/norm/din-4109-1/254608093"
                }
            ],
            "Wärmeschutz": [
                {
                    "id": "DIN-4108",
                    "name": "DIN 4108 - Wärmeschutz und Energie-Einsparung in Gebäuden",
                    "description": "Anforderungen und Nachweise für den Wärmeschutz",
                    "url": "https://www.beuth.de/de/norm/din-4108-2/320243236"
                }
            ]
        }
        
        # Gebäudetyp-spezifische Vorschriften
        self.regulations_database["Gebäudetypen"] = {
            "Wohngebäude": [
                {
                    "id": "WoFV",
                    "name": "Wohnflächenverordnung",
                    "description": "Berechnung der Wohnfläche",
                    "url": "https://www.gesetze-im-internet.de/wofv/"
                }
            ],
            "Gewerbe": [
                {
                    "id": "ASR",
                    "name": "Technische Regeln für Arbeitsstätten",
                    "description": "Anforderungen an Arbeitsstätten",
                    "url": "https://www.baua.de/DE/Angebote/Rechtstexte-und-Technische-Regeln/Regelwerk/ASR/ASR.html"
                }
            ],
            "Industrie": [
                {
                    "id": "BetrSichV",
                    "name": "Betriebssicherheitsverordnung",
                    "description": "Sicherheit und Gesundheitsschutz bei der Verwendung von Arbeitsmitteln",
                    "url": "https://www.gesetze-im-internet.de/betrsichv_2015/"
                }
            ],
            "Öffentliche Gebäude": [
                {
                    "id": "MVStättV",
                    "name": "Musterverordnung über den Bau und Betrieb von Versammlungsstätten",
                    "description": "Vorschriften für Versammlungsstätten",
                    "url": "https://www.bauministerkonferenz.de/verzeichnis/42463.pdf"
                }
            ],
            "Gesundheitswesen": [
                {
                    "id": "DIN-13080",
                    "name": "DIN 13080 - Gliederung des Krankenhauses in Funktionsbereiche und Funktionsstellen",
                    "description": "Funktionsbereiche in Krankenhäusern",
                    "url": "https://www.beuth.de/de/norm/din-13080/144122193"
                }
            ]
        }
    
    def _get_relevant_regulations(self, category: str, region: str, building_type: str) -> List[Dict[str, Any]]:
        """
        Holt relevante Vorschriften basierend auf Kategorie, Region und Gebäudetyp.
        
        Args:
            category: Kategorie der Anfrage
            region: Region des Projekts
            building_type: Gebäudetyp
        
        Returns:
            Liste der relevanten Vorschriften
        """
        relevant_regulations = []
        
        # Hole allgemeine Vorschriften für die Region
        if region in self.regulations_database and "Allgemein" in self.regulations_database[region]:
            relevant_regulations.extend(self.regulations_database[region]["Allgemein"])
        
        # Hole kategoriespezifische Vorschriften für die Region
        if region in self.regulations_database and category in self.regulations_database[region]:
            relevant_regulations.extend(self.regulations_database[region][category])
        
        # Hole gebäudetypspezifische Vorschriften
        if "Gebäudetypen" in self.regulations_database and building_type in self.regulations_database["Gebäudetypen"]:
            relevant_regulations.extend(self.regulations_database["Gebäudetypen"][building_type])
        
        return relevant_regulations
    
    def _create_compliance_check_prompt(self, description: str, documents: List[Dict[str, Any]], 
                                       category: str, region: str, building_type: str,
                                       regulations: List[Dict[str, Any]]) -> str:
        """
        Erstellt einen Prompt für die Compliance-Überprüfung.
        
        Args:
            description: Beschreibung der Anfrage
            documents: Liste der relevanten Dokumente
            category: Kategorie der Anfrage
            region: Region des Projekts
            building_type: Gebäudetyp
            regulations: Liste der relevanten Vorschriften
        
        Returns:
            Prompt für das KI-Modell
        """
        # Extrahiere relevante Informationen aus Dokumenten
        doc_excerpts = []
        for doc in documents:
            doc_excerpts.append(f"Dokument: {doc.get('title', 'Unbekannt')}\nAuszug: {doc.get('excerpt', '')}")
        
        doc_context = "\n\n".join(doc_excerpts) if doc_excerpts else "Keine Dokumente verfügbar."
        
        # Erstelle Informationen zu relevanten Vorschriften
        regulations_info = "Keine relevanten Vorschriften verfügbar."
        if regulations:
            reg_texts = []
            for reg in regulations:
                reg_text = f"""ID: {reg.get('id', 'Unbekannt')}
Name: {reg.get('name', 'Unbekannt')}
Beschreibung: {reg.get('description', 'Keine Beschreibung verfügbar')}
URL: {reg.get('url', 'Keine URL verfügbar')}
"""
                reg_texts.append(reg_text)
            
            regulations_info = "\n\n".join(reg_texts)
        
        # Erstelle den Prompt
        prompt = f"""Als Compliance-Agent im Bauwesen, überprüfe die folgende Anfrage auf Einhaltung von Bauvorschriften, Normen und Standards:

ANFRAGE BESCHREIBUNG:
{description}

KATEGORIE: {category}
REGION: {region}
GEBÄUDETYP: {building_type}

RELEVANTE DOKUMENTE:
{doc_context}

RELEVANTE VORSCHRIFTEN:
{regulations_info}

Bitte überprüfe die Einhaltung der relevanten Vorschriften und gib folgende Informationen zurück:
1. Identifizierte Compliance-Probleme
2. Betroffene Vorschriften und Standards
3. Schweregrad der Probleme (niedrig, mittel, hoch)
4. Empfehlungen zur Behebung der Probleme
5. Erforderliche Dokumentation für die Compliance-Nachweise

Formatiere deine Antwort als strukturierten Text mit klaren Abschnitten für jede der oben genannten Informationen.
"""
        return prompt
    
    def _create_compliance_report_prompt(self, project_id: str, checks: List[Dict[str, Any]]) -> str:
        """
        Erstellt einen Prompt für den Compliance-Bericht.
        
        Args:
            project_id: ID des Projekts
            checks: Liste der Compliance-Checks
        
        Returns:
            Prompt für das KI-Modell
        """
        # Erstelle Informationen zu Compliance-Checks
        checks_info = "Keine Compliance-Checks verfügbar."
        if checks:
            check_texts = []
            for check in checks:
                problems = check.get("identified_problems", [])
                problems_text = "\n".join([f"- {problem}" for problem in problems])
                
                check_text = f"""Anfrage: {check.get('request_id', 'Unbekannt')}
Identifizierte Probleme:
{problems_text}
Schweregrad: {check.get('severity', 'medium')}
"""
                check_texts.append(check_text)
            
            checks_info = "\n\n".join(check_texts)
        
        # Erstelle den Prompt
        prompt = f"""Als Compliance-Agent im Bauwesen, generiere einen umfassenden Compliance-Bericht für das folgende Projekt basierend auf den durchgeführten Compliance-Checks:

PROJEKT-ID: {project_id}

DURCHGEFÜHRTE COMPLIANCE-CHECKS:
{checks_info}

Bitte generiere einen umfassenden Compliance-Bericht und gib folgende Informationen zurück:
1. Zusammenfassung der Compliance-Situation
2. Kritische Compliance-Probleme
3. Mittelschwere Compliance-Probleme
4. Geringfügige Compliance-Probleme
5. Empfehlungen zur Verbesserung der Compliance
6. Erforderliche Maßnahmen und Dokumentation
7. Compliance-Risikobewertung

Formatiere deine Antwort als strukturierten Text mit klaren Abschnitten für jede der oben genannten Informationen.
"""
        return prompt
    
    def _process_compliance_check_response(self, response: str) -> Dict[str, Any]:
        """
        Verarbeitet die Antwort des KI-Modells zur Compliance-Überprüfung.
        
        Args:
            response: Antwort des KI-Modells
        
        Returns:
            Strukturierte Compliance-Analyse
        """
        # In einer realen Implementierung würde hier ein robuster Parser verwendet werden
        # Für dieses MVP verwenden wir eine vereinfachte Implementierung
        
        lines = response.strip().split('\n')
        
        # Extrahiere identifizierte Probleme
        identified_problems = []
        problems_section_started = False
        
        for i, line in enumerate(lines):
            if "identifizierte compliance-probleme" in line.lower() or "identified compliance issues" in line.lower():
                problems_section_started = True
                continue
            
            if problems_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["betroffene vorschriften", "affected regulations", "schweregrad", "severity"]):
                    # Extrahiere Problem aus der Zeile
                    problem = line.strip()
                    if problem.startswith("- "):
                        problem = problem[2:]
                    identified_problems.append(problem)
                else:
                    if any(keyword in line.lower() for keyword in ["betroffene vorschriften", "affected regulations", "schweregrad", "severity"]):
                        problems_section_started = False
        
        # Extrahiere betroffene Vorschriften
        affected_regulations = []
        regulations_section_started = False
        
        for i, line in enumerate(lines):
            if "betroffene vorschriften" in line.lower() or "affected regulations" in line.lower():
                regulations_section_started = True
                continue
            
            if regulations_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["schweregrad", "severity", "empfehlungen", "recommendations"]):
                    # Extrahiere Vorschrift aus der Zeile
                    regulation = line.strip()
                    if regulation.startswith("- "):
                        regulation = regulation[2:]
                    affected_regulations.append(regulation)
                else:
                    if any(keyword in line.lower() for keyword in ["schweregrad", "severity", "empfehlungen", "recommendations"]):
                        regulations_section_started = False
        
        # Extrahiere Schweregrad
        severity = "medium"  # Standardwert
        for line in lines:
            if "schweregrad" in line.lower() or "severity" in line.lower():
                # Suche nach Schweregradsstufe in dieser Zeile
                if "niedrig" in line.lower() or "low" in line.lower():
                    severity = "low"
                elif "hoch" in line.lower() or "high" in line.lower():
                    severity = "high"
                elif "mittel" in line.lower() or "medium" in line.lower():
                    severity = "medium"
                break
        
        # Extrahiere Empfehlungen
        recommendations = []
        recommendations_section_started = False
        
        for i, line in enumerate(lines):
            if "empfehlungen" in line.lower() or "recommendations" in line.lower():
                recommendations_section_started = True
                continue
            
            if recommendations_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["erforderliche dokumentation", "required documentation", "erforderliche nachweise", "required evidence"]):
                    # Extrahiere Empfehlung aus der Zeile
                    recommendation = line.strip()
                    if recommendation.startswith("- "):
                        recommendation = recommendation[2:]
                    recommendations.append(recommendation)
                else:
                    if any(keyword in line.lower() for keyword in ["erforderliche dokumentation", "required documentation", "erforderliche nachweise", "required evidence"]):
                        recommendations_section_started = False
        
        # Erstelle strukturierte Compliance-Analyse
        compliance_check = {
            "identified_problems": identified_problems,
            "affected_regulations": affected_regulations,
            "severity": severity,
            "recommendations": recommendations,
            "full_analysis": response,
            "timestamp": datetime.now().isoformat()
        }
        
        return compliance_check
    
    def _process_compliance_report_response(self, response: str, checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verarbeitet die Antwort des KI-Modells zum Compliance-Bericht.
        
        Args:
            response: Antwort des KI-Modells
            checks: Liste der Compliance-Checks
        
        Returns:
            Strukturierter Compliance-Bericht
        """
        # In einer realen Implementierung würde hier ein robuster Parser verwendet werden
        # Für dieses MVP verwenden wir eine vereinfachte Implementierung
        
        # Erstelle strukturierten Compliance-Bericht
        compliance_report = {
            "summary": "",
            "critical_issues": [],
            "moderate_issues": [],
            "minor_issues": [],
            "recommendations": [],
            "required_actions": [],
            "risk_assessment": "",
            "full_report": response,
            "timestamp": datetime.now().isoformat(),
            "based_on_checks": len(checks)
        }
        
        lines = response.strip().split('\n')
        
        # Extrahiere Zusammenfassung
        summary_section_started = False
        summary_lines = []
        
        for i, line in enumerate(lines):
            if "zusammenfassung" in line.lower() or "summary" in line.lower():
                summary_section_started = True
                continue
            
            if summary_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["kritische", "critical", "mittelschwere", "moderate"]):
                    summary_lines.append(line.strip())
                else:
                    if any(keyword in line.lower() for keyword in ["kritische", "critical", "mittelschwere", "moderate"]):
                        summary_section_started = False
        
        compliance_report["summary"] = " ".join(summary_lines)
        
        # Extrahiere kritische Probleme
        critical_section_started = False
        
        for i, line in enumerate(lines):
            if "kritische compliance-probleme" in line.lower() or "critical compliance issues" in line.lower():
                critical_section_started = True
                continue
            
            if critical_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["mittelschwere", "moderate", "geringfügige", "minor"]):
                    # Extrahiere Problem aus der Zeile
                    issue = line.strip()
                    if issue.startswith("- "):
                        issue = issue[2:]
                    compliance_report["critical_issues"].append(issue)
                else:
                    if any(keyword in line.lower() for keyword in ["mittelschwere", "moderate", "geringfügige", "minor"]):
                        critical_section_started = False
        
        # Extrahiere mittelschwere Probleme
        moderate_section_started = False
        
        for i, line in enumerate(lines):
            if "mittelschwere compliance-probleme" in line.lower() or "moderate compliance issues" in line.lower():
                moderate_section_started = True
                continue
            
            if moderate_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["geringfügige", "minor", "empfehlungen", "recommendations"]):
                    # Extrahiere Problem aus der Zeile
                    issue = line.strip()
                    if issue.startswith("- "):
                        issue = issue[2:]
                    compliance_report["moderate_issues"].append(issue)
                else:
                    if any(keyword in line.lower() for keyword in ["geringfügige", "minor", "empfehlungen", "recommendations"]):
                        moderate_section_started = False
        
        # Extrahiere geringfügige Probleme
        minor_section_started = False
        
        for i, line in enumerate(lines):
            if "geringfügige compliance-probleme" in line.lower() or "minor compliance issues" in line.lower():
                minor_section_started = True
                continue
            
            if minor_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["empfehlungen", "recommendations", "erforderliche", "required"]):
                    # Extrahiere Problem aus der Zeile
                    issue = line.strip()
                    if issue.startswith("- "):
                        issue = issue[2:]
                    compliance_report["minor_issues"].append(issue)
                else:
                    if any(keyword in line.lower() for keyword in ["empfehlungen", "recommendations", "erforderliche", "required"]):
                        minor_section_started = False
        
        # Extrahiere Empfehlungen
        recommendations_section_started = False
        
        for i, line in enumerate(lines):
            if "empfehlungen zur verbesserung" in line.lower() or "recommendations for improvement" in line.lower():
                recommendations_section_started = True
                continue
            
            if recommendations_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["erforderliche maßnahmen", "required actions", "compliance-risikobewertung", "compliance risk assessment"]):
                    # Extrahiere Empfehlung aus der Zeile
                    recommendation = line.strip()
                    if recommendation.startswith("- "):
                        recommendation = recommendation[2:]
                    compliance_report["recommendations"].append(recommendation)
                else:
                    if any(keyword in line.lower() for keyword in ["erforderliche maßnahmen", "required actions", "compliance-risikobewertung", "compliance risk assessment"]):
                        recommendations_section_started = False
        
        # Extrahiere erforderliche Maßnahmen
        actions_section_started = False
        
        for i, line in enumerate(lines):
            if "erforderliche maßnahmen" in line.lower() or "required actions" in line.lower():
                actions_section_started = True
                continue
            
            if actions_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["compliance-risikobewertung", "compliance risk assessment", "fazit", "conclusion"]):
                    # Extrahiere Maßnahme aus der Zeile
                    action = line.strip()
                    if action.startswith("- "):
                        action = action[2:]
                    compliance_report["required_actions"].append(action)
                else:
                    if any(keyword in line.lower() for keyword in ["compliance-risikobewertung", "compliance risk assessment", "fazit", "conclusion"]):
                        actions_section_started = False
        
        # Extrahiere Risikobewertung
        risk_section_started = False
        risk_lines = []
        
        for i, line in enumerate(lines):
            if "compliance-risikobewertung" in line.lower() or "compliance risk assessment" in line.lower():
                risk_section_started = True
                continue
            
            if risk_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["fazit", "conclusion"]):
                    risk_lines.append(line.strip())
                else:
                    if any(keyword in line.lower() for keyword in ["fazit", "conclusion"]):
                        risk_section_started = False
        
        compliance_report["risk_assessment"] = " ".join(risk_lines)
        
        return compliance_report
    
    def _store_compliance_check(self, project_id: str, request_id: str, check: Dict[str, Any]) -> None:
        """
        Speichert eine Compliance-Überprüfung in der Datenbank.
        
        Args:
            project_id: ID des Projekts
            request_id: ID der Anfrage
            check: Compliance-Überprüfung
        """
        if "compliance_checks" not in self.regulations_database:
            self.regulations_database["compliance_checks"] = {}
        
        if project_id not in self.regulations_database["compliance_checks"]:
            self.regulations_database["compliance_checks"][project_id] = {}
        
        self.regulations_database["compliance_checks"][project_id][request_id] = check
    
    def _get_project_checks(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Holt alle Compliance-Überprüfungen für ein Projekt.
        
        Args:
            project_id: ID des Projekts
        
        Returns:
            Liste der Compliance-Überprüfungen
        """
        if "compliance_checks" not in self.regulations_database or project_id not in self.regulations_database["compliance_checks"]:
            return []
        
        return list(self.regulations_database["compliance_checks"][project_id].values())

