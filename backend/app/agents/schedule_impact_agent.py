"""
Terminplan-Auswirkungs-Agent für das DOB-MVP.

Dieser Agent analysiert die Auswirkungen von RFIs und Änderungen auf den Projektterminplan
und gibt Empfehlungen zur Minimierung von Verzögerungen.
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import re

from app.agents.base import BaseAgent
from app.core.model_manager.registry import ModelRegistry

logger = logging.getLogger(__name__)

class ScheduleImpactAgent(BaseAgent):
    """
    Agent zur Analyse von Terminplanauswirkungen.
    
    Dieser Agent analysiert die Auswirkungen von RFIs und Änderungen auf den Projektterminplan
    und gibt Empfehlungen zur Minimierung von Verzögerungen.
    """
    
    def __init__(self, model_registry: ModelRegistry):
        """
        Initialisiert den Terminplan-Auswirkungs-Agenten.
        
        Args:
            model_registry: Registry für KI-Modelle
        """
        super().__init__(model_registry, "schedule_impact_agent")
        self.schedule_database = {}  # Einfache In-Memory-Datenbank für Terminplandaten
        
    def analyze_schedule_impact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analysiert die Auswirkungen einer RFI oder Änderungsanfrage auf den Terminplan.
        
        Args:
            data: Daten der RFI oder Änderungsanfrage
                - description: Beschreibung der Anfrage
                - project_id: ID des Projekts
                - documents: Liste der relevanten Dokumente
                - category: Kategorie der Anfrage
                - complexity: Komplexität der Anfrage
                - project_schedule: Projektterminplan (optional)
        
        Returns:
            Dict mit Terminplananalyse und Empfehlungen
        """
        logger.info(f"Analysiere Terminplanauswirkungen für Anfrage: {data.get('id', 'Neue Anfrage')}")
        
        # Extrahiere relevante Daten
        description = data.get("description", "")
        project_id = data.get("project_id", "")
        documents = data.get("documents", [])
        category = data.get("category", "")
        complexity = data.get("complexity", "medium")
        project_schedule = data.get("project_schedule", {})
        
        # Hole den gespeicherten Terminplan, falls keiner übergeben wurde
        if not project_schedule and project_id:
            project_schedule = self._get_project_schedule(project_id)
        
        # Erstelle Prompt für das KI-Modell
        prompt = self._create_schedule_impact_prompt(description, documents, category, 
                                                   complexity, project_schedule)
        
        # Rufe KI-Modell auf
        model_response = self._call_model(prompt)
        
        # Verarbeite die Antwort
        schedule_impact = self._process_schedule_impact_response(model_response)
        
        # Speichere die Analyse in der Datenbank
        self._store_schedule_impact(project_id, data.get("id", f"temp-{datetime.now().isoformat()}"), schedule_impact)
        
        return schedule_impact
    
    def optimize_schedule(self, project_id: str, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optimiert den Terminplan eines Projekts basierend auf bisherigen Analysen und Einschränkungen.
        
        Args:
            project_id: ID des Projekts
            constraints: Einschränkungen für die Optimierung (optional)
                - deadline: Projektdeadline
                - resources: Verfügbare Ressourcen
                - priorities: Prioritäten für verschiedene Aufgaben
        
        Returns:
            Dict mit optimiertem Terminplan und Empfehlungen
        """
        logger.info(f"Optimiere Terminplan für Projekt: {project_id}")
        
        # Hole alle Terminplananalysen für das Projekt
        project_impacts = self._get_project_impacts(project_id)
        
        # Hole den aktuellen Terminplan
        current_schedule = self._get_project_schedule(project_id)
        
        # Standardeinschränkungen, falls keine übergeben wurden
        if constraints is None:
            constraints = {}
        
        # Erstelle Prompt für das KI-Modell
        prompt = self._create_schedule_optimization_prompt(current_schedule, project_impacts, constraints)
        
        # Rufe KI-Modell auf
        model_response = self._call_model(prompt)
        
        # Verarbeite die Antwort
        optimized_schedule = self._process_schedule_optimization_response(model_response, current_schedule)
        
        # Speichere den optimierten Terminplan
        self._store_project_schedule(project_id, optimized_schedule)
        
        return optimized_schedule
    
    def _create_schedule_impact_prompt(self, description: str, documents: List[Dict[str, Any]], 
                                      category: str, complexity: str, 
                                      project_schedule: Dict[str, Any]) -> str:
        """
        Erstellt einen Prompt für die Terminplananalyse.
        
        Args:
            description: Beschreibung der Anfrage
            documents: Liste der relevanten Dokumente
            category: Kategorie der Anfrage
            complexity: Komplexität der Anfrage
            project_schedule: Projektterminplan
        
        Returns:
            Prompt für das KI-Modell
        """
        # Extrahiere relevante Informationen aus Dokumenten
        doc_excerpts = []
        for doc in documents:
            doc_excerpts.append(f"Dokument: {doc.get('title', 'Unbekannt')}\nAuszug: {doc.get('excerpt', '')}")
        
        doc_context = "\n\n".join(doc_excerpts) if doc_excerpts else "Keine Dokumente verfügbar."
        
        # Extrahiere relevante Informationen aus dem Terminplan
        schedule_info = "Kein Terminplan verfügbar."
        if project_schedule:
            milestones = project_schedule.get("milestones", [])
            critical_path = project_schedule.get("critical_path", [])
            
            milestone_text = "\n".join([f"- {m.get('name')}: {m.get('date')}" for m in milestones])
            critical_path_text = "\n".join([f"- {task}" for task in critical_path])
            
            schedule_info = f"""Projektstart: {project_schedule.get('start_date', 'Unbekannt')}
Projektende: {project_schedule.get('end_date', 'Unbekannt')}

Meilensteine:
{milestone_text}

Kritischer Pfad:
{critical_path_text}
"""
        
        # Erstelle den Prompt
        prompt = f"""Als Terminplan-Auswirkungs-Agent im Bauwesen, analysiere die folgende Anfrage und bewerte die Auswirkungen auf den Projektterminplan:

ANFRAGE BESCHREIBUNG:
{description}

KATEGORIE: {category}
KOMPLEXITÄT: {complexity}

RELEVANTE DOKUMENTE:
{doc_context}

AKTUELLER PROJEKTTERMINPLAN:
{schedule_info}

Bitte analysiere die Auswirkungen dieser Anfrage auf den Projektterminplan und gib folgende Informationen zurück:
1. Geschätzte Verzögerung (in Arbeitstagen)
2. Betroffene Meilensteine und Aufgaben
3. Auswirkungen auf den kritischen Pfad
4. Risikobewertung (niedrig, mittel, hoch) mit Begründung
5. Empfehlungen zur Minimierung von Verzögerungen
6. Vorgeschlagene Anpassungen des Terminplans

Formatiere deine Antwort als strukturierten Text mit klaren Abschnitten für jede der oben genannten Informationen.
"""
        return prompt
    
    def _create_schedule_optimization_prompt(self, current_schedule: Dict[str, Any], 
                                           impacts: List[Dict[str, Any]], 
                                           constraints: Dict[str, Any]) -> str:
        """
        Erstellt einen Prompt für die Terminplanoptimierung.
        
        Args:
            current_schedule: Aktueller Projektterminplan
            impacts: Liste der Terminplanauswirkungen
            constraints: Einschränkungen für die Optimierung
        
        Returns:
            Prompt für das KI-Modell
        """
        # Extrahiere relevante Informationen aus dem Terminplan
        schedule_info = "Kein Terminplan verfügbar."
        if current_schedule:
            milestones = current_schedule.get("milestones", [])
            critical_path = current_schedule.get("critical_path", [])
            
            milestone_text = "\n".join([f"- {m.get('name')}: {m.get('date')}" for m in milestones])
            critical_path_text = "\n".join([f"- {task}" for task in critical_path])
            
            schedule_info = f"""Projektstart: {current_schedule.get('start_date', 'Unbekannt')}
Projektende: {current_schedule.get('end_date', 'Unbekannt')}

Meilensteine:
{milestone_text}

Kritischer Pfad:
{critical_path_text}
"""
        
        # Extrahiere relevante Informationen aus den Auswirkungen
        impacts_info = "Keine Auswirkungen verfügbar."
        if impacts:
            impact_texts = []
            for impact in impacts:
                impact_text = f"""Anfrage: {impact.get('request_id', 'Unbekannt')}
Geschätzte Verzögerung: {impact.get('estimated_delay', 0)} Arbeitstage
Betroffene Meilensteine: {', '.join(impact.get('affected_milestones', []))}
Risikostufe: {impact.get('risk_level', 'medium')}
"""
                impact_texts.append(impact_text)
            
            impacts_info = "\n\n".join(impact_texts)
        
        # Extrahiere relevante Informationen aus den Einschränkungen
        constraints_info = "Keine Einschränkungen verfügbar."
        if constraints:
            deadline = constraints.get("deadline", "Keine Deadline angegeben")
            resources = constraints.get("resources", {})
            priorities = constraints.get("priorities", {})
            
            resources_text = "\n".join([f"- {res}: {count}" for res, count in resources.items()])
            priorities_text = "\n".join([f"- {task}: {priority}" for task, priority in priorities.items()])
            
            constraints_info = f"""Deadline: {deadline}

Verfügbare Ressourcen:
{resources_text}

Prioritäten:
{priorities_text}
"""
        
        # Erstelle den Prompt
        prompt = f"""Als Terminplan-Optimierungs-Agent im Bauwesen, optimiere den folgenden Projektterminplan basierend auf den Auswirkungen und Einschränkungen:

AKTUELLER PROJEKTTERMINPLAN:
{schedule_info}

TERMINPLANAUSWIRKUNGEN:
{impacts_info}

EINSCHRÄNKUNGEN:
{constraints_info}

Bitte optimiere den Projektterminplan und gib folgende Informationen zurück:
1. Optimierter Projektstart und -ende
2. Angepasste Meilensteine mit Daten
3. Neuer kritischer Pfad
4. Empfohlene Ressourcenzuweisung
5. Risikominderungsstrategien
6. Begründung für die vorgeschlagenen Änderungen

Formatiere deine Antwort als strukturierten Text mit klaren Abschnitten für jede der oben genannten Informationen.
"""
        return prompt
    
    def _process_schedule_impact_response(self, response: str) -> Dict[str, Any]:
        """
        Verarbeitet die Antwort des KI-Modells zur Terminplananalyse.
        
        Args:
            response: Antwort des KI-Modells
        
        Returns:
            Strukturierte Terminplananalyse
        """
        # In einer realen Implementierung würde hier ein robuster Parser verwendet werden
        # Für dieses MVP verwenden wir eine vereinfachte Implementierung
        
        lines = response.strip().split('\n')
        
        # Extrahiere geschätzte Verzögerung
        estimated_delay = 0
        for line in lines:
            if "geschätzte verzögerung" in line.lower() or "estimated delay" in line.lower():
                # Extrahiere Zahlen aus der Zeile
                numbers = re.findall(r'\d+', line)
                if numbers:
                    try:
                        estimated_delay = int(numbers[0])
                    except ValueError:
                        estimated_delay = 0
                break
        
        # Extrahiere betroffene Meilensteine
        affected_milestones = []
        milestones_section_started = False
        
        for i, line in enumerate(lines):
            if "betroffene meilensteine" in line.lower() or "affected milestones" in line.lower():
                milestones_section_started = True
                continue
            
            if milestones_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["auswirkungen", "impact", "risiko", "risk"]):
                    # Extrahiere Meilenstein aus der Zeile
                    milestone = line.strip()
                    if milestone.startswith("- "):
                        milestone = milestone[2:]
                    affected_milestones.append(milestone)
                else:
                    if any(keyword in line.lower() for keyword in ["auswirkungen", "impact", "risiko", "risk"]):
                        milestones_section_started = False
        
        # Extrahiere Risikobewertung
        risk_level = "medium"  # Standardwert
        risk_explanation = ""
        risk_section_started = False
        
        for i, line in enumerate(lines):
            if "risikobewertung" in line.lower() or "risk assessment" in line.lower():
                risk_section_started = True
                # Suche nach Risikostufe in dieser Zeile
                if "niedrig" in line.lower() or "low" in line.lower():
                    risk_level = "low"
                elif "hoch" in line.lower() or "high" in line.lower():
                    risk_level = "high"
                elif "mittel" in line.lower() or "medium" in line.lower():
                    risk_level = "medium"
                
                # Sammle die Erklärung aus den nächsten Zeilen
                j = i + 1
                while j < len(lines) and not any(keyword in lines[j].lower() for keyword in ["empfehlungen", "recommendations", "anpassungen", "adjustments"]):
                    risk_explanation += lines[j] + " "
                    j += 1
                
                break
        
        # Extrahiere Empfehlungen
        recommendations = []
        recommendations_section_started = False
        
        for i, line in enumerate(lines):
            if "empfehlungen" in line.lower() or "recommendations" in line.lower():
                recommendations_section_started = True
                continue
            
            if recommendations_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["anpassungen", "adjustments", "vorgeschlagene", "proposed"]):
                    # Extrahiere Empfehlung aus der Zeile
                    recommendation = line.strip()
                    if recommendation.startswith("- "):
                        recommendation = recommendation[2:]
                    recommendations.append(recommendation)
                else:
                    if any(keyword in line.lower() for keyword in ["anpassungen", "adjustments", "vorgeschlagene", "proposed"]):
                        recommendations_section_started = False
        
        # Erstelle strukturierte Terminplananalyse
        schedule_impact = {
            "estimated_delay": estimated_delay,
            "delay_unit": "work_days",
            "affected_milestones": affected_milestones,
            "risk_level": risk_level,
            "risk_explanation": risk_explanation.strip(),
            "recommendations": recommendations,
            "full_analysis": response,
            "timestamp": datetime.now().isoformat()
        }
        
        return schedule_impact
    
    def _process_schedule_optimization_response(self, response: str, current_schedule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet die Antwort des KI-Modells zur Terminplanoptimierung.
        
        Args:
            response: Antwort des KI-Modells
            current_schedule: Aktueller Projektterminplan
        
        Returns:
            Optimierter Terminplan
        """
        # In einer realen Implementierung würde hier ein robuster Parser verwendet werden
        # Für dieses MVP verwenden wir eine vereinfachte Implementierung
        
        lines = response.strip().split('\n')
        
        # Extrahiere Projektstart und -ende
        start_date = current_schedule.get("start_date", "")
        end_date = current_schedule.get("end_date", "")
        
        for line in lines:
            if "projektstart" in line.lower() or "project start" in line.lower():
                # Extrahiere Datum aus der Zeile
                dates = re.findall(r'\d{4}-\d{2}-\d{2}', line)
                if dates:
                    start_date = dates[0]
            
            if "projektende" in line.lower() or "project end" in line.lower():
                # Extrahiere Datum aus der Zeile
                dates = re.findall(r'\d{4}-\d{2}-\d{2}', line)
                if dates:
                    end_date = dates[0]
        
        # Extrahiere angepasste Meilensteine
        milestones = []
        milestones_section_started = False
        
        for i, line in enumerate(lines):
            if "angepasste meilensteine" in line.lower() or "adjusted milestones" in line.lower():
                milestones_section_started = True
                continue
            
            if milestones_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["neuer kritischer", "new critical", "empfohlene", "recommended"]):
                    # Extrahiere Meilenstein aus der Zeile
                    milestone_line = line.strip()
                    if milestone_line.startswith("- "):
                        milestone_line = milestone_line[2:]
                    
                    # Versuche, Name und Datum zu extrahieren
                    parts = milestone_line.split(":")
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        date_str = parts[1].strip()
                        
                        # Extrahiere Datum
                        dates = re.findall(r'\d{4}-\d{2}-\d{2}', date_str)
                        if dates:
                            date = dates[0]
                        else:
                            date = ""
                        
                        milestones.append({"name": name, "date": date})
                else:
                    if any(keyword in line.lower() for keyword in ["neuer kritischer", "new critical", "empfohlene", "recommended"]):
                        milestones_section_started = False
        
        # Extrahiere neuen kritischen Pfad
        critical_path = []
        critical_path_section_started = False
        
        for i, line in enumerate(lines):
            if "neuer kritischer pfad" in line.lower() or "new critical path" in line.lower():
                critical_path_section_started = True
                continue
            
            if critical_path_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["empfohlene", "recommended", "ressourcen", "resources"]):
                    # Extrahiere Aufgabe aus der Zeile
                    task = line.strip()
                    if task.startswith("- "):
                        task = task[2:]
                    critical_path.append(task)
                else:
                    if any(keyword in line.lower() for keyword in ["empfohlene", "recommended", "ressourcen", "resources"]):
                        critical_path_section_started = False
        
        # Erstelle optimierten Terminplan
        optimized_schedule = {
            "start_date": start_date,
            "end_date": end_date,
            "milestones": milestones,
            "critical_path": critical_path,
            "full_optimization": response,
            "timestamp": datetime.now().isoformat(),
            "previous_schedule": current_schedule
        }
        
        return optimized_schedule
    
    def _store_schedule_impact(self, project_id: str, request_id: str, impact: Dict[str, Any]) -> None:
        """
        Speichert eine Terminplananalyse in der Datenbank.
        
        Args:
            project_id: ID des Projekts
            request_id: ID der Anfrage
            impact: Terminplananalyse
        """
        if project_id not in self.schedule_database:
            self.schedule_database[project_id] = {"impacts": {}, "schedule": {}}
        
        if "impacts" not in self.schedule_database[project_id]:
            self.schedule_database[project_id]["impacts"] = {}
        
        self.schedule_database[project_id]["impacts"][request_id] = impact
    
    def _get_project_impacts(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Holt alle Terminplananalysen für ein Projekt.
        
        Args:
            project_id: ID des Projekts
        
        Returns:
            Liste der Terminplananalysen
        """
        if project_id not in self.schedule_database or "impacts" not in self.schedule_database[project_id]:
            return []
        
        return list(self.schedule_database[project_id]["impacts"].values())
    
    def _store_project_schedule(self, project_id: str, schedule: Dict[str, Any]) -> None:
        """
        Speichert einen Projektterminplan in der Datenbank.
        
        Args:
            project_id: ID des Projekts
            schedule: Projektterminplan
        """
        if project_id not in self.schedule_database:
            self.schedule_database[project_id] = {"impacts": {}, "schedule": {}}
        
        self.schedule_database[project_id]["schedule"] = schedule
    
    def _get_project_schedule(self, project_id: str) -> Dict[str, Any]:
        """
        Holt den Terminplan eines Projekts.
        
        Args:
            project_id: ID des Projekts
        
        Returns:
            Projektterminplan
        """
        if project_id not in self.schedule_database or "schedule" not in self.schedule_database[project_id]:
            return {}
        
        return self.schedule_database[project_id]["schedule"]

