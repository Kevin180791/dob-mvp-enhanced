"""
Kosten-Schätzungs-Agent für das DOB-MVP.

Dieser Agent analysiert Projektdokumente und RFIs, um Kostenauswirkungen zu schätzen
und Budgetimplikationen zu bewerten.
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.agents.base import BaseAgent
from app.core.model_manager.registry import ModelRegistry

logger = logging.getLogger(__name__)

class CostEstimationAgent(BaseAgent):
    """
    Agent zur Schätzung von Kosten und Budgetauswirkungen.
    
    Dieser Agent analysiert Projektdokumente, RFIs und Änderungsanfragen,
    um deren Kostenauswirkungen zu schätzen und Budgetimplikationen zu bewerten.
    """
    
    def __init__(self, model_registry: ModelRegistry):
        """
        Initialisiert den Kosten-Schätzungs-Agenten.
        
        Args:
            model_registry: Registry für KI-Modelle
        """
        super().__init__(model_registry, "cost_estimation_agent")
        self.cost_database = {}  # Einfache In-Memory-Datenbank für Kostendaten
        
    def estimate_costs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schätzt die Kosten für eine RFI oder Änderungsanfrage.
        
        Args:
            data: Daten der RFI oder Änderungsanfrage
                - description: Beschreibung der Anfrage
                - project_id: ID des Projekts
                - documents: Liste der relevanten Dokumente
                - category: Kategorie der Anfrage
                - complexity: Komplexität der Anfrage
        
        Returns:
            Dict mit Kostenschätzung und Begründung
        """
        logger.info(f"Schätze Kosten für Anfrage: {data.get('id', 'Neue Anfrage')}")
        
        # Extrahiere relevante Daten
        description = data.get("description", "")
        project_id = data.get("project_id", "")
        documents = data.get("documents", [])
        category = data.get("category", "")
        complexity = data.get("complexity", "medium")
        
        # Erstelle Prompt für das KI-Modell
        prompt = self._create_cost_estimation_prompt(description, documents, category, complexity)
        
        # Rufe KI-Modell auf
        model_response = self._call_model(prompt)
        
        # Verarbeite die Antwort
        cost_estimation = self._process_cost_estimation_response(model_response)
        
        # Speichere die Schätzung in der Datenbank
        self._store_cost_estimation(project_id, data.get("id", f"temp-{datetime.now().isoformat()}"), cost_estimation)
        
        return cost_estimation
    
    def analyze_budget_impact(self, project_id: str, new_estimation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analysiert die Auswirkungen einer neuen Kostenschätzung auf das Gesamtbudget.
        
        Args:
            project_id: ID des Projekts
            new_estimation: Neue Kostenschätzung
        
        Returns:
            Dict mit Budgetanalyse
        """
        logger.info(f"Analysiere Budgetauswirkungen für Projekt: {project_id}")
        
        # Hole alle Kostenschätzungen für das Projekt
        project_estimations = self._get_project_estimations(project_id)
        
        # Berechne Gesamtkosten
        total_estimated_cost = sum(est.get("estimated_cost", 0) for est in project_estimations)
        total_estimated_cost += new_estimation.get("estimated_cost", 0)
        
        # Berechne Risikofaktoren
        high_risk_items = [est for est in project_estimations if est.get("risk_level", "") == "high"]
        high_risk_items_count = len(high_risk_items)
        
        # Erstelle Budgetanalyse
        budget_analysis = {
            "total_estimated_cost": total_estimated_cost,
            "total_estimations_count": len(project_estimations) + 1,
            "high_risk_items_count": high_risk_items_count,
            "budget_impact_percentage": self._calculate_budget_impact_percentage(new_estimation, total_estimated_cost),
            "recommendations": self._generate_budget_recommendations(new_estimation, total_estimated_cost, high_risk_items_count)
        }
        
        return budget_analysis
    
    def _create_cost_estimation_prompt(self, description: str, documents: List[Dict[str, Any]], 
                                      category: str, complexity: str) -> str:
        """
        Erstellt einen Prompt für die Kostenschätzung.
        
        Args:
            description: Beschreibung der Anfrage
            documents: Liste der relevanten Dokumente
            category: Kategorie der Anfrage
            complexity: Komplexität der Anfrage
        
        Returns:
            Prompt für das KI-Modell
        """
        # Extrahiere relevante Informationen aus Dokumenten
        doc_excerpts = []
        for doc in documents:
            doc_excerpts.append(f"Dokument: {doc.get('title', 'Unbekannt')}\nAuszug: {doc.get('excerpt', '')}")
        
        doc_context = "\n\n".join(doc_excerpts) if doc_excerpts else "Keine Dokumente verfügbar."
        
        # Erstelle den Prompt
        prompt = f"""Als Kosten-Schätzungs-Agent im Bauwesen, analysiere die folgende Anfrage und schätze die Kosten:

ANFRAGE BESCHREIBUNG:
{description}

KATEGORIE: {category}
KOMPLEXITÄT: {complexity}

RELEVANTE DOKUMENTE:
{doc_context}

Bitte schätze die Kosten für diese Anfrage und gib folgende Informationen zurück:
1. Geschätzte Kosten (in Euro)
2. Kostenaufschlüsselung nach Kategorien (Material, Arbeit, Ausrüstung, Sonstiges)
3. Risikobewertung (niedrig, mittel, hoch) mit Begründung
4. Potenzielle Kosteneinsparungen
5. Zeitliche Auswirkungen auf das Projekt

Formatiere deine Antwort als strukturierten Text mit klaren Abschnitten für jede der oben genannten Informationen.
"""
        return prompt
    
    def _process_cost_estimation_response(self, response: str) -> Dict[str, Any]:
        """
        Verarbeitet die Antwort des KI-Modells zur Kostenschätzung.
        
        Args:
            response: Antwort des KI-Modells
        
        Returns:
            Strukturierte Kostenschätzung
        """
        # In einer realen Implementierung würde hier ein robuster Parser verwendet werden
        # Für dieses MVP verwenden wir eine vereinfachte Implementierung
        
        lines = response.strip().split('\n')
        
        # Extrahiere geschätzte Kosten
        estimated_cost = 0
        for line in lines:
            if "geschätzte kosten" in line.lower() or "estimated cost" in line.lower():
                # Extrahiere Zahlen aus der Zeile
                import re
                numbers = re.findall(r'\d+(?:\.\d+)?', line.replace(',', '.'))
                if numbers:
                    try:
                        estimated_cost = float(numbers[0])
                    except ValueError:
                        estimated_cost = 0
                break
        
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
                while j < len(lines) and not any(keyword in lines[j].lower() for keyword in ["potenzielle", "potential", "zeitliche", "time"]):
                    risk_explanation += lines[j] + " "
                    j += 1
                
                break
        
        # Erstelle strukturierte Kostenschätzung
        cost_estimation = {
            "estimated_cost": estimated_cost,
            "currency": "EUR",
            "risk_level": risk_level,
            "risk_explanation": risk_explanation.strip(),
            "full_analysis": response,
            "timestamp": datetime.now().isoformat()
        }
        
        return cost_estimation
    
    def _store_cost_estimation(self, project_id: str, request_id: str, estimation: Dict[str, Any]) -> None:
        """
        Speichert eine Kostenschätzung in der Datenbank.
        
        Args:
            project_id: ID des Projekts
            request_id: ID der Anfrage
            estimation: Kostenschätzung
        """
        if project_id not in self.cost_database:
            self.cost_database[project_id] = {}
        
        self.cost_database[project_id][request_id] = estimation
    
    def _get_project_estimations(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Holt alle Kostenschätzungen für ein Projekt.
        
        Args:
            project_id: ID des Projekts
        
        Returns:
            Liste der Kostenschätzungen
        """
        if project_id not in self.cost_database:
            return []
        
        return list(self.cost_database[project_id].values())
    
    def _calculate_budget_impact_percentage(self, estimation: Dict[str, Any], total_cost: float) -> float:
        """
        Berechnet den prozentualen Einfluss einer Schätzung auf das Gesamtbudget.
        
        Args:
            estimation: Kostenschätzung
            total_cost: Gesamtkosten
        
        Returns:
            Prozentualer Einfluss
        """
        if total_cost == 0:
            return 100.0
        
        return (estimation.get("estimated_cost", 0) / total_cost) * 100
    
    def _generate_budget_recommendations(self, estimation: Dict[str, Any], 
                                        total_cost: float, high_risk_count: int) -> List[str]:
        """
        Generiert Empfehlungen basierend auf der Budgetanalyse.
        
        Args:
            estimation: Kostenschätzung
            total_cost: Gesamtkosten
            high_risk_count: Anzahl der Hochrisiko-Elemente
        
        Returns:
            Liste der Empfehlungen
        """
        recommendations = []
        
        # Empfehlungen basierend auf Risikostufe
        if estimation.get("risk_level") == "high":
            recommendations.append("Diese Änderung hat ein hohes Risiko. Erwägen Sie eine detailliertere Analyse oder alternative Lösungen.")
        
        # Empfehlungen basierend auf Budgetauswirkung
        impact_percentage = self._calculate_budget_impact_percentage(estimation, total_cost)
        if impact_percentage > 10:
            recommendations.append(f"Diese Änderung hat erhebliche Auswirkungen auf das Budget ({impact_percentage:.1f}%). Prüfen Sie Möglichkeiten zur Kostensenkung.")
        
        # Empfehlungen basierend auf der Anzahl der Hochrisiko-Elemente
        if high_risk_count > 3:
            recommendations.append(f"Das Projekt enthält {high_risk_count} Hochrisiko-Elemente. Erwägen Sie eine Überprüfung der Risikostrategien.")
        
        # Standardempfehlung, wenn keine spezifischen Empfehlungen generiert wurden
        if not recommendations:
            recommendations.append("Keine spezifischen Empfehlungen basierend auf der aktuellen Budgetanalyse.")
        
        return recommendations

