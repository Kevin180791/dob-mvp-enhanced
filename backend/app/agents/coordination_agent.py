"""
Koordinations-Agent für das DOB-MVP.

Dieser Agent koordiniert die Zusammenarbeit zwischen verschiedenen Agenten und
integriert deren Ergebnisse zu einer kohärenten Antwort.
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.agents.base import BaseAgent
from app.core.model_manager.registry import ModelRegistry

logger = logging.getLogger(__name__)

class CoordinationAgent(BaseAgent):
    """
    Agent zur Koordination der Zusammenarbeit zwischen verschiedenen Agenten.
    
    Dieser Agent koordiniert die Zusammenarbeit zwischen verschiedenen Agenten und
    integriert deren Ergebnisse zu einer kohärenten Antwort.
    """
    
    def __init__(self, model_registry: ModelRegistry):
        """
        Initialisiert den Koordinations-Agenten.
        
        Args:
            model_registry: Registry für KI-Modelle
        """
        super().__init__(model_registry, "coordination_agent")
        self.agent_results = {}  # Speichert die Ergebnisse der verschiedenen Agenten
    
    def coordinate_rfi_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Koordiniert die Analyse einer RFI durch verschiedene Agenten.
        
        Args:
            data: Daten der RFI und der Agenten-Ergebnisse
                - rfi_id: ID der RFI
                - project_id: ID des Projekts
                - rfi_analyst_result: Ergebnis des RFI-Analyst-Agenten
                - plan_reviewer_result: Ergebnis des Plan-Prüfer-Agenten
                - document_analysis_result: Ergebnis des Dokumentenanalyse-Agenten
                - cost_estimation_result: Ergebnis des Kosten-Schätzungs-Agenten
                - schedule_impact_result: Ergebnis des Terminplan-Auswirkungs-Agenten
                - compliance_result: Ergebnis des Compliance-Agenten
        
        Returns:
            Dict mit koordinierter RFI-Analyse
        """
        logger.info(f"Koordiniere RFI-Analyse für RFI: {data.get('rfi_id', 'Neue RFI')}")
        
        # Extrahiere relevante Daten
        rfi_id = data.get("rfi_id", f"rfi-{datetime.now().isoformat()}")
        project_id = data.get("project_id", "")
        
        # Sammle die Ergebnisse der verschiedenen Agenten
        agent_results = {}
        for agent_type in ["rfi_analyst", "plan_reviewer", "document_analysis", "cost_estimation", "schedule_impact", "compliance"]:
            result_key = f"{agent_type}_result"
            if result_key in data and data[result_key]:
                agent_results[agent_type] = data[result_key]
        
        # Speichere die Agenten-Ergebnisse
        self._store_agent_results(project_id, rfi_id, agent_results)
        
        # Erstelle Prompt für das KI-Modell
        prompt = self._create_coordination_prompt(rfi_id, agent_results)
        
        # Rufe KI-Modell auf
        model_response = self._call_model(prompt)
        
        # Verarbeite die Antwort
        coordination_result = self._process_coordination_response(model_response, agent_results)
        
        return coordination_result
    
    def generate_comprehensive_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generiert eine umfassende Antwort auf eine RFI basierend auf den Ergebnissen verschiedener Agenten.
        
        Args:
            data: Daten der RFI und der Agenten-Ergebnisse
                - rfi_id: ID der RFI
                - project_id: ID des Projekts
                - coordination_result: Ergebnis des Koordinations-Agenten
                - communication_style: Kommunikationsstil (z.B. formal, technisch, einfach)
                - include_details: Ob Details einbezogen werden sollen
                - target_audience: Zielgruppe der Antwort (z.B. Architekt, Bauherr, Behörde)
        
        Returns:
            Dict mit umfassender RFI-Antwort
        """
        logger.info(f"Generiere umfassende Antwort für RFI: {data.get('rfi_id', 'Neue RFI')}")
        
        # Extrahiere relevante Daten
        rfi_id = data.get("rfi_id", "")
        project_id = data.get("project_id", "")
        coordination_result = data.get("coordination_result", {})
        communication_style = data.get("communication_style", "formal")
        include_details = data.get("include_details", True)
        target_audience = data.get("target_audience", "Architekt")
        
        # Hole die Agenten-Ergebnisse
        agent_results = self._get_agent_results(project_id, rfi_id)
        
        # Erstelle Prompt für das KI-Modell
        prompt = self._create_comprehensive_response_prompt(
            rfi_id,
            coordination_result,
            agent_results,
            communication_style,
            include_details,
            target_audience
        )
        
        # Rufe KI-Modell auf
        model_response = self._call_model(prompt)
        
        # Verarbeite die Antwort
        comprehensive_response = {
            "rfi_id": rfi_id,
            "project_id": project_id,
            "response_text": model_response,
            "communication_style": communication_style,
            "include_details": include_details,
            "target_audience": target_audience,
            "timestamp": datetime.now().isoformat()
        }
        
        return comprehensive_response
    
    def prioritize_tasks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Priorisiert Aufgaben basierend auf den Ergebnissen verschiedener Agenten.
        
        Args:
            data: Daten der Aufgaben und der Agenten-Ergebnisse
                - project_id: ID des Projekts
                - tasks: Liste der Aufgaben
                - agent_results: Ergebnisse der verschiedenen Agenten
                - constraints: Einschränkungen für die Priorisierung
                - objectives: Ziele für die Priorisierung
        
        Returns:
            Dict mit priorisierten Aufgaben
        """
        logger.info(f"Priorisiere Aufgaben für Projekt: {data.get('project_id', 'Neues Projekt')}")
        
        # Extrahiere relevante Daten
        project_id = data.get("project_id", "")
        tasks = data.get("tasks", [])
        agent_results = data.get("agent_results", {})
        constraints = data.get("constraints", {})
        objectives = data.get("objectives", {})
        
        # Erstelle Prompt für das KI-Modell
        prompt = self._create_task_prioritization_prompt(tasks, agent_results, constraints, objectives)
        
        # Rufe KI-Modell auf
        model_response = self._call_model(prompt)
        
        # Verarbeite die Antwort
        prioritized_tasks = self._process_task_prioritization_response(model_response, tasks)
        
        return {
            "project_id": project_id,
            "prioritized_tasks": prioritized_tasks,
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_coordination_prompt(self, rfi_id: str, agent_results: Dict[str, Any]) -> str:
        """
        Erstellt einen Prompt für die Koordination der Agenten-Ergebnisse.
        
        Args:
            rfi_id: ID der RFI
            agent_results: Ergebnisse der verschiedenen Agenten
        
        Returns:
            Prompt für das KI-Modell
        """
        # Erstelle Informationen zu den Agenten-Ergebnissen
        agent_results_text = ""
        
        for agent_type, result in agent_results.items():
            agent_name = agent_type.replace("_", " ").title()
            agent_results_text += f"\n\n{agent_name} Ergebnis:\n"
            
            if isinstance(result, dict):
                for key, value in result.items():
                    if key not in ["full_analysis", "full_extraction", "full_comparison", "timestamp"]:
                        if isinstance(value, list):
                            agent_results_text += f"\n{key.replace('_', ' ').title()}:\n"
                            for item in value:
                                agent_results_text += f"- {item}\n"
                        else:
                            agent_results_text += f"\n{key.replace('_', ' ').title()}: {value}\n"
            else:
                agent_results_text += str(result)
        
        # Erstelle den Prompt
        prompt = f"""Als Koordinations-Agent im Bauwesen, koordiniere die folgenden Ergebnisse verschiedener Agenten für die RFI {rfi_id} und integriere sie zu einer kohärenten Analyse:

{agent_results_text}

Bitte koordiniere die Ergebnisse der verschiedenen Agenten und gib folgende Informationen zurück:
1. Zusammenfassung der RFI-Analyse
2. Wichtigste Erkenntnisse aus allen Agenten-Ergebnissen
3. Identifizierte Widersprüche oder Inkonsistenzen zwischen den Agenten-Ergebnissen
4. Integrierte Empfehlungen basierend auf allen Agenten-Ergebnissen
5. Priorisierung der nächsten Schritte
6. Offene Fragen, die noch geklärt werden müssen

Formatiere deine Antwort als strukturierten Text mit klaren Abschnitten für jede der oben genannten Informationen.
"""
        return prompt
    
    def _create_comprehensive_response_prompt(
        self,
        rfi_id: str,
        coordination_result: Dict[str, Any],
        agent_results: Dict[str, Any],
        communication_style: str,
        include_details: bool,
        target_audience: str
    ) -> str:
        """
        Erstellt einen Prompt für die Generierung einer umfassenden Antwort.
        
        Args:
            rfi_id: ID der RFI
            coordination_result: Ergebnis des Koordinations-Agenten
            agent_results: Ergebnisse der verschiedenen Agenten
            communication_style: Kommunikationsstil
            include_details: Ob Details einbezogen werden sollen
            target_audience: Zielgruppe der Antwort
        
        Returns:
            Prompt für das KI-Modell
        """
        # Erstelle Informationen zum Koordinations-Ergebnis
        coordination_text = ""
        
        if coordination_result:
            for key, value in coordination_result.items():
                if key not in ["timestamp"]:
                    if isinstance(value, list):
                        coordination_text += f"\n{key.replace('_', ' ').title()}:\n"
                        for item in value:
                            coordination_text += f"- {item}\n"
                    else:
                        coordination_text += f"\n{key.replace('_', ' ').title()}: {value}\n"
        
        # Erstelle Informationen zu den Agenten-Ergebnissen
        agent_results_text = ""
        
        if include_details:
            for agent_type, result in agent_results.items():
                agent_name = agent_type.replace("_", " ").title()
                agent_results_text += f"\n\n{agent_name} Ergebnis:\n"
                
                if isinstance(result, dict):
                    for key, value in result.items():
                        if key not in ["full_analysis", "full_extraction", "full_comparison", "timestamp"]:
                            if isinstance(value, list):
                                agent_results_text += f"\n{key.replace('_', ' ').title()}:\n"
                                for item in value:
                                    agent_results_text += f"- {item}\n"
                            else:
                                agent_results_text += f"\n{key.replace('_', ' ').title()}: {value}\n"
                else:
                    agent_results_text += str(result)
        
        # Erstelle den Prompt
        prompt = f"""Als Kommunikations-Agent im Bauwesen, generiere eine umfassende Antwort auf die RFI {rfi_id} basierend auf den folgenden Informationen:

Koordinations-Ergebnis:
{coordination_text}

{agent_results_text if include_details else ""}

Bitte generiere eine umfassende Antwort mit den folgenden Eigenschaften:
1. Kommunikationsstil: {communication_style}
2. Zielgruppe: {target_audience}
3. {"Mit detaillierten Informationen" if include_details else "Ohne detaillierte Informationen"}

Die Antwort sollte folgende Elemente enthalten:
1. Einleitung mit Bezug zur RFI
2. Hauptteil mit den wichtigsten Erkenntnissen und Antworten
3. Empfehlungen und nächste Schritte
4. Abschluss mit Angebot für weitere Unterstützung

Formatiere deine Antwort als strukturierten Text, der direkt als Antwort auf die RFI verwendet werden kann.
"""
        return prompt
    
    def _create_task_prioritization_prompt(
        self,
        tasks: List[Dict[str, Any]],
        agent_results: Dict[str, Any],
        constraints: Dict[str, Any],
        objectives: Dict[str, Any]
    ) -> str:
        """
        Erstellt einen Prompt für die Priorisierung von Aufgaben.
        
        Args:
            tasks: Liste der Aufgaben
            agent_results: Ergebnisse der verschiedenen Agenten
            constraints: Einschränkungen für die Priorisierung
            objectives: Ziele für die Priorisierung
        
        Returns:
            Prompt für das KI-Modell
        """
        # Erstelle Informationen zu den Aufgaben
        tasks_text = ""
        
        for i, task in enumerate(tasks):
            tasks_text += f"\nAufgabe {i+1}:\n"
            for key, value in task.items():
                tasks_text += f"- {key}: {value}\n"
        
        # Erstelle Informationen zu den Agenten-Ergebnissen
        agent_results_text = ""
        
        for agent_type, result in agent_results.items():
            agent_name = agent_type.replace("_", " ").title()
            agent_results_text += f"\n\n{agent_name} Ergebnis:\n"
            
            if isinstance(result, dict):
                for key, value in result.items():
                    if key not in ["full_analysis", "full_extraction", "full_comparison", "timestamp"]:
                        if isinstance(value, list):
                            agent_results_text += f"\n{key.replace('_', ' ').title()}:\n"
                            for item in value:
                                agent_results_text += f"- {item}\n"
                        else:
                            agent_results_text += f"\n{key.replace('_', ' ').title()}: {value}\n"
            else:
                agent_results_text += str(result)
        
        # Erstelle Informationen zu den Einschränkungen
        constraints_text = ""
        
        for key, value in constraints.items():
            constraints_text += f"- {key}: {value}\n"
        
        # Erstelle Informationen zu den Zielen
        objectives_text = ""
        
        for key, value in objectives.items():
            objectives_text += f"- {key}: {value}\n"
        
        # Erstelle den Prompt
        prompt = f"""Als Koordinations-Agent im Bauwesen, priorisiere die folgenden Aufgaben basierend auf den Ergebnissen verschiedener Agenten, Einschränkungen und Zielen:

Aufgaben:
{tasks_text}

Agenten-Ergebnisse:
{agent_results_text}

Einschränkungen:
{constraints_text}

Ziele:
{objectives_text}

Bitte priorisiere die Aufgaben und gib folgende Informationen zurück:
1. Priorisierte Liste der Aufgaben mit Begründung
2. Abhängigkeiten zwischen den Aufgaben
3. Empfohlene Reihenfolge der Ausführung
4. Kritische Aufgaben, die besondere Aufmerksamkeit erfordern
5. Risiken und Herausforderungen bei der Ausführung

Formatiere deine Antwort als strukturierten Text mit klaren Abschnitten für jede der oben genannten Informationen.
"""
        return prompt
    
    def _process_coordination_response(self, response: str, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet die Antwort des KI-Modells zur Koordination der Agenten-Ergebnisse.
        
        Args:
            response: Antwort des KI-Modells
            agent_results: Ergebnisse der verschiedenen Agenten
        
        Returns:
            Strukturiertes Koordinations-Ergebnis
        """
        # In einer realen Implementierung würde hier ein robuster Parser verwendet werden
        # Für dieses MVP verwenden wir eine vereinfachte Implementierung
        
        lines = response.strip().split('\n')
        
        # Extrahiere Zusammenfassung
        summary = ""
        summary_section_started = False
        
        for i, line in enumerate(lines):
            if "zusammenfassung" in line.lower() or "summary" in line.lower():
                summary_section_started = True
                continue
            
            if summary_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["wichtigste erkenntnisse", "key findings", "identifizierte widersprüche", "identified contradictions"]):
                    summary += line.strip() + " "
                else:
                    if any(keyword in line.lower() for keyword in ["wichtigste erkenntnisse", "key findings", "identifizierte widersprüche", "identified contradictions"]):
                        summary_section_started = False
        
        # Extrahiere wichtigste Erkenntnisse
        key_findings = []
        findings_section_started = False
        
        for i, line in enumerate(lines):
            if "wichtigste erkenntnisse" in line.lower() or "key findings" in line.lower():
                findings_section_started = True
                continue
            
            if findings_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["identifizierte widersprüche", "identified contradictions", "integrierte empfehlungen", "integrated recommendations"]):
                    # Extrahiere Erkenntnis aus der Zeile
                    finding = line.strip()
                    if finding.startswith("- "):
                        finding = finding[2:]
                    key_findings.append(finding)
                else:
                    if any(keyword in line.lower() for keyword in ["identifizierte widersprüche", "identified contradictions", "integrierte empfehlungen", "integrated recommendations"]):
                        findings_section_started = False
        
        # Extrahiere identifizierte Widersprüche
        contradictions = []
        contradictions_section_started = False
        
        for i, line in enumerate(lines):
            if "identifizierte widersprüche" in line.lower() or "identified contradictions" in line.lower():
                contradictions_section_started = True
                continue
            
            if contradictions_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["integrierte empfehlungen", "integrated recommendations", "priorisierung", "prioritization"]):
                    # Extrahiere Widerspruch aus der Zeile
                    contradiction = line.strip()
                    if contradiction.startswith("- "):
                        contradiction = contradiction[2:]
                    contradictions.append(contradiction)
                else:
                    if any(keyword in line.lower() for keyword in ["integrierte empfehlungen", "integrated recommendations", "priorisierung", "prioritization"]):
                        contradictions_section_started = False
        
        # Extrahiere integrierte Empfehlungen
        recommendations = []
        recommendations_section_started = False
        
        for i, line in enumerate(lines):
            if "integrierte empfehlungen" in line.lower() or "integrated recommendations" in line.lower():
                recommendations_section_started = True
                continue
            
            if recommendations_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["priorisierung", "prioritization", "offene fragen", "open questions"]):
                    # Extrahiere Empfehlung aus der Zeile
                    recommendation = line.strip()
                    if recommendation.startswith("- "):
                        recommendation = recommendation[2:]
                    recommendations.append(recommendation)
                else:
                    if any(keyword in line.lower() for keyword in ["priorisierung", "prioritization", "offene fragen", "open questions"]):
                        recommendations_section_started = False
        
        # Extrahiere Priorisierung der nächsten Schritte
        next_steps = []
        next_steps_section_started = False
        
        for i, line in enumerate(lines):
            if "priorisierung" in line.lower() or "prioritization" in line.lower() or "nächste schritte" in line.lower() or "next steps" in line.lower():
                next_steps_section_started = True
                continue
            
            if next_steps_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["offene fragen", "open questions"]):
                    # Extrahiere nächsten Schritt aus der Zeile
                    next_step = line.strip()
                    if next_step.startswith("- "):
                        next_step = next_step[2:]
                    next_steps.append(next_step)
                else:
                    if any(keyword in line.lower() for keyword in ["offene fragen", "open questions"]):
                        next_steps_section_started = False
        
        # Extrahiere offene Fragen
        open_questions = []
        questions_section_started = False
        
        for i, line in enumerate(lines):
            if "offene fragen" in line.lower() or "open questions" in line.lower():
                questions_section_started = True
                continue
            
            if questions_section_started:
                if line.strip():
                    # Extrahiere offene Frage aus der Zeile
                    question = line.strip()
                    if question.startswith("- "):
                        question = question[2:]
                    open_questions.append(question)
        
        # Erstelle strukturiertes Koordinations-Ergebnis
        coordination_result = {
            "summary": summary.strip(),
            "key_findings": key_findings,
            "contradictions": contradictions,
            "recommendations": recommendations,
            "next_steps": next_steps,
            "open_questions": open_questions,
            "full_coordination": response,
            "timestamp": datetime.now().isoformat()
        }
        
        return coordination_result
    
    def _process_task_prioritization_response(self, response: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verarbeitet die Antwort des KI-Modells zur Priorisierung von Aufgaben.
        
        Args:
            response: Antwort des KI-Modells
            tasks: Liste der Aufgaben
        
        Returns:
            Strukturiertes Priorisierungs-Ergebnis
        """
        # In einer realen Implementierung würde hier ein robuster Parser verwendet werden
        # Für dieses MVP verwenden wir eine vereinfachte Implementierung
        
        lines = response.strip().split('\n')
        
        # Extrahiere priorisierte Aufgaben
        prioritized_tasks = []
        tasks_section_started = False
        
        for i, line in enumerate(lines):
            if "priorisierte liste" in line.lower() or "prioritized list" in line.lower():
                tasks_section_started = True
                continue
            
            if tasks_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["abhängigkeiten", "dependencies", "empfohlene reihenfolge", "recommended order"]):
                    # Extrahiere Aufgabe aus der Zeile
                    task = line.strip()
                    if task.startswith("- "):
                        task = task[2:]
                    prioritized_tasks.append(task)
                else:
                    if any(keyword in line.lower() for keyword in ["abhängigkeiten", "dependencies", "empfohlene reihenfolge", "recommended order"]):
                        tasks_section_started = False
        
        # Extrahiere Abhängigkeiten
        dependencies = []
        dependencies_section_started = False
        
        for i, line in enumerate(lines):
            if "abhängigkeiten" in line.lower() or "dependencies" in line.lower():
                dependencies_section_started = True
                continue
            
            if dependencies_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["empfohlene reihenfolge", "recommended order", "kritische aufgaben", "critical tasks"]):
                    # Extrahiere Abhängigkeit aus der Zeile
                    dependency = line.strip()
                    if dependency.startswith("- "):
                        dependency = dependency[2:]
                    dependencies.append(dependency)
                else:
                    if any(keyword in line.lower() for keyword in ["empfohlene reihenfolge", "recommended order", "kritische aufgaben", "critical tasks"]):
                        dependencies_section_started = False
        
        # Extrahiere empfohlene Reihenfolge
        execution_order = []
        order_section_started = False
        
        for i, line in enumerate(lines):
            if "empfohlene reihenfolge" in line.lower() or "recommended order" in line.lower():
                order_section_started = True
                continue
            
            if order_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["kritische aufgaben", "critical tasks", "risiken", "risks"]):
                    # Extrahiere Reihenfolge aus der Zeile
                    order = line.strip()
                    if order.startswith("- "):
                        order = order[2:]
                    execution_order.append(order)
                else:
                    if any(keyword in line.lower() for keyword in ["kritische aufgaben", "critical tasks", "risiken", "risks"]):
                        order_section_started = False
        
        # Extrahiere kritische Aufgaben
        critical_tasks = []
        critical_section_started = False
        
        for i, line in enumerate(lines):
            if "kritische aufgaben" in line.lower() or "critical tasks" in line.lower():
                critical_section_started = True
                continue
            
            if critical_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["risiken", "risks", "herausforderungen", "challenges"]):
                    # Extrahiere kritische Aufgabe aus der Zeile
                    critical = line.strip()
                    if critical.startswith("- "):
                        critical = critical[2:]
                    critical_tasks.append(critical)
                else:
                    if any(keyword in line.lower() for keyword in ["risiken", "risks", "herausforderungen", "challenges"]):
                        critical_section_started = False
        
        # Extrahiere Risiken und Herausforderungen
        risks = []
        risks_section_started = False
        
        for i, line in enumerate(lines):
            if "risiken" in line.lower() or "risks" in line.lower() or "herausforderungen" in line.lower() or "challenges" in line.lower():
                risks_section_started = True
                continue
            
            if risks_section_started:
                if line.strip():
                    # Extrahiere Risiko aus der Zeile
                    risk = line.strip()
                    if risk.startswith("- "):
                        risk = risk[2:]
                    risks.append(risk)
        
        # Erstelle strukturiertes Priorisierungs-Ergebnis
        prioritization_result = {
            "prioritized_tasks": prioritized_tasks,
            "dependencies": dependencies,
            "execution_order": execution_order,
            "critical_tasks": critical_tasks,
            "risks": risks,
            "full_prioritization": response,
            "timestamp": datetime.now().isoformat()
        }
        
        return prioritization_result
    
    def _store_agent_results(self, project_id: str, rfi_id: str, agent_results: Dict[str, Any]) -> None:
        """
        Speichert die Ergebnisse der verschiedenen Agenten.
        
        Args:
            project_id: ID des Projekts
            rfi_id: ID der RFI
            agent_results: Ergebnisse der verschiedenen Agenten
        """
        if project_id not in self.agent_results:
            self.agent_results[project_id] = {}
        
        if rfi_id not in self.agent_results[project_id]:
            self.agent_results[project_id][rfi_id] = {}
        
        self.agent_results[project_id][rfi_id] = agent_results
    
    def _get_agent_results(self, project_id: str, rfi_id: str) -> Dict[str, Any]:
        """
        Holt die Ergebnisse der verschiedenen Agenten.
        
        Args:
            project_id: ID des Projekts
            rfi_id: ID der RFI
        
        Returns:
            Ergebnisse der verschiedenen Agenten
        """
        if project_id not in self.agent_results or rfi_id not in self.agent_results[project_id]:
            return {}
        
        return self.agent_results[project_id][rfi_id]

