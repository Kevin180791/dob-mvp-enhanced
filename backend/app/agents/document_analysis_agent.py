"""
Dokumentenanalyse-Agent für das DOB-MVP.

Dieser Agent analysiert Baudokumente, extrahiert relevante Informationen und
identifiziert Inkonsistenzen und Probleme.
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import re

from app.agents.base import BaseAgent
from app.core.model_manager.registry import ModelRegistry

logger = logging.getLogger(__name__)

class DocumentAnalysisAgent(BaseAgent):
    """
    Agent zur Analyse von Baudokumenten.
    
    Dieser Agent analysiert Baudokumente, extrahiert relevante Informationen und
    identifiziert Inkonsistenzen und Probleme.
    """
    
    def __init__(self, model_registry: ModelRegistry):
        """
        Initialisiert den Dokumentenanalyse-Agenten.
        
        Args:
            model_registry: Registry für KI-Modelle
        """
        super().__init__(model_registry, "document_analysis_agent")
        self.document_database = {}  # Einfache In-Memory-Datenbank für Dokumentenanalysen
        
    def analyze_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analysiert ein Baudokument und extrahiert relevante Informationen.
        
        Args:
            data: Daten des Dokuments
                - document_id: ID des Dokuments
                - project_id: ID des Projekts
                - title: Titel des Dokuments
                - content: Inhalt des Dokuments
                - document_type: Typ des Dokuments (z.B. Plan, Spezifikation, RFI)
                - format: Format des Dokuments (z.B. PDF, DWG, DOC)
        
        Returns:
            Dict mit Dokumentenanalyse
        """
        logger.info(f"Analysiere Dokument: {data.get('document_id', 'Neues Dokument')}")
        
        # Extrahiere relevante Daten
        document_id = data.get("document_id", f"doc-{datetime.now().isoformat()}")
        project_id = data.get("project_id", "")
        title = data.get("title", "")
        content = data.get("content", "")
        document_type = data.get("document_type", "")
        format = data.get("format", "")
        
        # Erstelle Prompt für das KI-Modell
        prompt = self._create_document_analysis_prompt(title, content, document_type, format)
        
        # Rufe KI-Modell auf
        model_response = self._call_model(prompt)
        
        # Verarbeite die Antwort
        document_analysis = self._process_document_analysis_response(model_response)
        
        # Speichere die Analyse in der Datenbank
        self._store_document_analysis(project_id, document_id, document_analysis)
        
        return document_analysis
    
    def compare_documents(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vergleicht mehrere Dokumente und identifiziert Inkonsistenzen.
        
        Args:
            data: Daten für den Dokumentenvergleich
                - project_id: ID des Projekts
                - document_ids: Liste der zu vergleichenden Dokument-IDs
                - comparison_type: Typ des Vergleichs (z.B. "version", "cross-discipline")
        
        Returns:
            Dict mit Dokumentenvergleich
        """
        logger.info(f"Vergleiche Dokumente für Projekt: {data.get('project_id', '')}")
        
        # Extrahiere relevante Daten
        project_id = data.get("project_id", "")
        document_ids = data.get("document_ids", [])
        comparison_type = data.get("comparison_type", "version")
        
        # Hole die Dokumente aus der Datenbank
        documents = []
        for doc_id in document_ids:
            doc_analysis = self._get_document_analysis(project_id, doc_id)
            if doc_analysis:
                documents.append({
                    "document_id": doc_id,
                    "analysis": doc_analysis
                })
        
        # Erstelle Prompt für das KI-Modell
        prompt = self._create_document_comparison_prompt(documents, comparison_type)
        
        # Rufe KI-Modell auf
        model_response = self._call_model(prompt)
        
        # Verarbeite die Antwort
        document_comparison = self._process_document_comparison_response(model_response, document_ids)
        
        # Speichere den Vergleich in der Datenbank
        comparison_id = f"comp-{datetime.now().isoformat()}"
        self._store_document_comparison(project_id, comparison_id, document_comparison)
        
        return document_comparison
    
    def extract_plan_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrahiert strukturierte Daten aus einem Bauplan.
        
        Args:
            data: Daten des Plans
                - document_id: ID des Dokuments
                - project_id: ID des Projekts
                - title: Titel des Plans
                - content: Inhalt des Plans
                - plan_type: Typ des Plans (z.B. Grundriss, Schnitt, Detail)
                - scale: Maßstab des Plans
                - discipline: Fachbereich des Plans (z.B. Architektur, TGA, Statik)
        
        Returns:
            Dict mit extrahierten Plandaten
        """
        logger.info(f"Extrahiere Daten aus Plan: {data.get('document_id', 'Neuer Plan')}")
        
        # Extrahiere relevante Daten
        document_id = data.get("document_id", f"plan-{datetime.now().isoformat()}")
        project_id = data.get("project_id", "")
        title = data.get("title", "")
        content = data.get("content", "")
        plan_type = data.get("plan_type", "")
        scale = data.get("scale", "")
        discipline = data.get("discipline", "")
        
        # Erstelle Prompt für das KI-Modell
        prompt = self._create_plan_data_extraction_prompt(title, content, plan_type, scale, discipline)
        
        # Rufe KI-Modell auf
        model_response = self._call_model(prompt)
        
        # Verarbeite die Antwort
        plan_data = self._process_plan_data_extraction_response(model_response)
        
        # Speichere die extrahierten Daten in der Datenbank
        self._store_plan_data(project_id, document_id, plan_data)
        
        return plan_data
    
    def _create_document_analysis_prompt(self, title: str, content: str, document_type: str, format: str) -> str:
        """
        Erstellt einen Prompt für die Dokumentenanalyse.
        
        Args:
            title: Titel des Dokuments
            content: Inhalt des Dokuments
            document_type: Typ des Dokuments
            format: Format des Dokuments
        
        Returns:
            Prompt für das KI-Modell
        """
        # Kürze den Inhalt, falls er zu lang ist
        max_content_length = 4000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "... [Inhalt gekürzt]"
        
        # Erstelle den Prompt
        prompt = f"""Als Dokumentenanalyse-Agent im Bauwesen, analysiere das folgende Dokument und extrahiere relevante Informationen:

DOKUMENT TITEL:
{title}

DOKUMENT TYP:
{document_type}

DOKUMENT FORMAT:
{format}

DOKUMENT INHALT:
{content}

Bitte analysiere das Dokument und gib folgende Informationen zurück:
1. Zusammenfassung des Dokuments
2. Schlüsselinformationen und Fakten
3. Identifizierte Probleme oder Unklarheiten
4. Betroffene Gewerke und Disziplinen
5. Relevante Normen und Standards
6. Empfehlungen für weitere Analysen

Formatiere deine Antwort als strukturierten Text mit klaren Abschnitten für jede der oben genannten Informationen.
"""
        return prompt
    
    def _create_document_comparison_prompt(self, documents: List[Dict[str, Any]], comparison_type: str) -> str:
        """
        Erstellt einen Prompt für den Dokumentenvergleich.
        
        Args:
            documents: Liste der zu vergleichenden Dokumente
            comparison_type: Typ des Vergleichs
        
        Returns:
            Prompt für das KI-Modell
        """
        # Erstelle Informationen zu den Dokumenten
        documents_info = "Keine Dokumente verfügbar."
        if documents:
            doc_texts = []
            for i, doc in enumerate(documents):
                doc_id = doc.get("document_id", f"Dokument {i+1}")
                analysis = doc.get("analysis", {})
                
                summary = analysis.get("summary", "Keine Zusammenfassung verfügbar.")
                key_info = "\n".join([f"- {info}" for info in analysis.get("key_information", [])])
                if not key_info:
                    key_info = "Keine Schlüsselinformationen verfügbar."
                
                doc_text = f"""DOKUMENT ID: {doc_id}

Zusammenfassung:
{summary}

Schlüsselinformationen:
{key_info}
"""
                doc_texts.append(doc_text)
            
            documents_info = "\n\n".join(doc_texts)
        
        # Erstelle den Prompt
        prompt = f"""Als Dokumentenvergleichs-Agent im Bauwesen, vergleiche die folgenden Dokumente und identifiziere Inkonsistenzen und Probleme:

VERGLEICHSTYP:
{comparison_type}

DOKUMENTE:
{documents_info}

Bitte vergleiche die Dokumente und gib folgende Informationen zurück:
1. Identifizierte Inkonsistenzen zwischen den Dokumenten
2. Widersprüchliche Informationen
3. Fehlende Informationen in einem oder mehreren Dokumenten
4. Übereinstimmende Informationen
5. Empfehlungen zur Behebung von Inkonsistenzen
6. Priorisierung der identifizierten Probleme

Formatiere deine Antwort als strukturierten Text mit klaren Abschnitten für jede der oben genannten Informationen.
"""
        return prompt
    
    def _create_plan_data_extraction_prompt(self, title: str, content: str, plan_type: str, scale: str, discipline: str) -> str:
        """
        Erstellt einen Prompt für die Extraktion von Plandaten.
        
        Args:
            title: Titel des Plans
            content: Inhalt des Plans
            plan_type: Typ des Plans
            scale: Maßstab des Plans
            discipline: Fachbereich des Plans
        
        Returns:
            Prompt für das KI-Modell
        """
        # Kürze den Inhalt, falls er zu lang ist
        max_content_length = 4000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "... [Inhalt gekürzt]"
        
        # Erstelle den Prompt
        prompt = f"""Als Plandaten-Extraktions-Agent im Bauwesen, extrahiere strukturierte Daten aus dem folgenden Bauplan:

PLAN TITEL:
{title}

PLAN TYP:
{plan_type}

MASSSTAB:
{scale}

FACHBEREICH:
{discipline}

PLAN INHALT:
{content}

Bitte extrahiere strukturierte Daten aus dem Plan und gib folgende Informationen zurück:
1. Räume und Flächen mit Bezeichnungen und Größen
2. Technische Systeme und Komponenten
3. Maße und Abmessungen
4. Materialien und Spezifikationen
5. Anschlüsse und Verbindungen
6. Revisionsstand und Änderungen
7. Koordinaten und Referenzpunkte

Formatiere deine Antwort als strukturierten Text mit klaren Abschnitten für jede der oben genannten Informationen.
"""
        return prompt
    
    def _process_document_analysis_response(self, response: str) -> Dict[str, Any]:
        """
        Verarbeitet die Antwort des KI-Modells zur Dokumentenanalyse.
        
        Args:
            response: Antwort des KI-Modells
        
        Returns:
            Strukturierte Dokumentenanalyse
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
                if line.strip() and not any(keyword in line.lower() for keyword in ["schlüsselinformationen", "key information", "identifizierte probleme", "identified issues"]):
                    summary += line.strip() + " "
                else:
                    if any(keyword in line.lower() for keyword in ["schlüsselinformationen", "key information", "identifizierte probleme", "identified issues"]):
                        summary_section_started = False
        
        # Extrahiere Schlüsselinformationen
        key_information = []
        key_info_section_started = False
        
        for i, line in enumerate(lines):
            if "schlüsselinformationen" in line.lower() or "key information" in line.lower():
                key_info_section_started = True
                continue
            
            if key_info_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["identifizierte probleme", "identified issues", "betroffene gewerke", "affected trades"]):
                    # Extrahiere Information aus der Zeile
                    info = line.strip()
                    if info.startswith("- "):
                        info = info[2:]
                    key_information.append(info)
                else:
                    if any(keyword in line.lower() for keyword in ["identifizierte probleme", "identified issues", "betroffene gewerke", "affected trades"]):
                        key_info_section_started = False
        
        # Extrahiere identifizierte Probleme
        identified_issues = []
        issues_section_started = False
        
        for i, line in enumerate(lines):
            if "identifizierte probleme" in line.lower() or "identified issues" in line.lower():
                issues_section_started = True
                continue
            
            if issues_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["betroffene gewerke", "affected trades", "relevante normen", "relevant standards"]):
                    # Extrahiere Problem aus der Zeile
                    issue = line.strip()
                    if issue.startswith("- "):
                        issue = issue[2:]
                    identified_issues.append(issue)
                else:
                    if any(keyword in line.lower() for keyword in ["betroffene gewerke", "affected trades", "relevante normen", "relevant standards"]):
                        issues_section_started = False
        
        # Extrahiere betroffene Gewerke
        affected_disciplines = []
        disciplines_section_started = False
        
        for i, line in enumerate(lines):
            if "betroffene gewerke" in line.lower() or "affected trades" in line.lower() or "affected disciplines" in line.lower():
                disciplines_section_started = True
                continue
            
            if disciplines_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["relevante normen", "relevant standards", "empfehlungen", "recommendations"]):
                    # Extrahiere Gewerk aus der Zeile
                    discipline = line.strip()
                    if discipline.startswith("- "):
                        discipline = discipline[2:]
                    affected_disciplines.append(discipline)
                else:
                    if any(keyword in line.lower() for keyword in ["relevante normen", "relevant standards", "empfehlungen", "recommendations"]):
                        disciplines_section_started = False
        
        # Extrahiere relevante Normen
        relevant_standards = []
        standards_section_started = False
        
        for i, line in enumerate(lines):
            if "relevante normen" in line.lower() or "relevant standards" in line.lower():
                standards_section_started = True
                continue
            
            if standards_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["empfehlungen", "recommendations"]):
                    # Extrahiere Norm aus der Zeile
                    standard = line.strip()
                    if standard.startswith("- "):
                        standard = standard[2:]
                    relevant_standards.append(standard)
                else:
                    if any(keyword in line.lower() for keyword in ["empfehlungen", "recommendations"]):
                        standards_section_started = False
        
        # Extrahiere Empfehlungen
        recommendations = []
        recommendations_section_started = False
        
        for i, line in enumerate(lines):
            if "empfehlungen" in line.lower() or "recommendations" in line.lower():
                recommendations_section_started = True
                continue
            
            if recommendations_section_started:
                if line.strip():
                    # Extrahiere Empfehlung aus der Zeile
                    recommendation = line.strip()
                    if recommendation.startswith("- "):
                        recommendation = recommendation[2:]
                    recommendations.append(recommendation)
        
        # Erstelle strukturierte Dokumentenanalyse
        document_analysis = {
            "summary": summary.strip(),
            "key_information": key_information,
            "identified_issues": identified_issues,
            "affected_disciplines": affected_disciplines,
            "relevant_standards": relevant_standards,
            "recommendations": recommendations,
            "full_analysis": response,
            "timestamp": datetime.now().isoformat()
        }
        
        return document_analysis
    
    def _process_document_comparison_response(self, response: str, document_ids: List[str]) -> Dict[str, Any]:
        """
        Verarbeitet die Antwort des KI-Modells zum Dokumentenvergleich.
        
        Args:
            response: Antwort des KI-Modells
            document_ids: Liste der verglichenen Dokument-IDs
        
        Returns:
            Strukturierter Dokumentenvergleich
        """
        # In einer realen Implementierung würde hier ein robuster Parser verwendet werden
        # Für dieses MVP verwenden wir eine vereinfachte Implementierung
        
        lines = response.strip().split('\n')
        
        # Extrahiere identifizierte Inkonsistenzen
        inconsistencies = []
        inconsistencies_section_started = False
        
        for i, line in enumerate(lines):
            if "identifizierte inkonsistenzen" in line.lower() or "identified inconsistencies" in line.lower():
                inconsistencies_section_started = True
                continue
            
            if inconsistencies_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["widersprüchliche", "contradictory", "fehlende", "missing"]):
                    # Extrahiere Inkonsistenz aus der Zeile
                    inconsistency = line.strip()
                    if inconsistency.startswith("- "):
                        inconsistency = inconsistency[2:]
                    inconsistencies.append(inconsistency)
                else:
                    if any(keyword in line.lower() for keyword in ["widersprüchliche", "contradictory", "fehlende", "missing"]):
                        inconsistencies_section_started = False
        
        # Extrahiere widersprüchliche Informationen
        contradictions = []
        contradictions_section_started = False
        
        for i, line in enumerate(lines):
            if "widersprüchliche informationen" in line.lower() or "contradictory information" in line.lower():
                contradictions_section_started = True
                continue
            
            if contradictions_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["fehlende", "missing", "übereinstimmende", "matching"]):
                    # Extrahiere Widerspruch aus der Zeile
                    contradiction = line.strip()
                    if contradiction.startswith("- "):
                        contradiction = contradiction[2:]
                    contradictions.append(contradiction)
                else:
                    if any(keyword in line.lower() for keyword in ["fehlende", "missing", "übereinstimmende", "matching"]):
                        contradictions_section_started = False
        
        # Extrahiere fehlende Informationen
        missing_information = []
        missing_section_started = False
        
        for i, line in enumerate(lines):
            if "fehlende informationen" in line.lower() or "missing information" in line.lower():
                missing_section_started = True
                continue
            
            if missing_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["übereinstimmende", "matching", "empfehlungen", "recommendations"]):
                    # Extrahiere fehlende Information aus der Zeile
                    missing = line.strip()
                    if missing.startswith("- "):
                        missing = missing[2:]
                    missing_information.append(missing)
                else:
                    if any(keyword in line.lower() for keyword in ["übereinstimmende", "matching", "empfehlungen", "recommendations"]):
                        missing_section_started = False
        
        # Extrahiere übereinstimmende Informationen
        matching_information = []
        matching_section_started = False
        
        for i, line in enumerate(lines):
            if "übereinstimmende informationen" in line.lower() or "matching information" in line.lower():
                matching_section_started = True
                continue
            
            if matching_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["empfehlungen", "recommendations", "priorisierung", "prioritization"]):
                    # Extrahiere übereinstimmende Information aus der Zeile
                    matching = line.strip()
                    if matching.startswith("- "):
                        matching = matching[2:]
                    matching_information.append(matching)
                else:
                    if any(keyword in line.lower() for keyword in ["empfehlungen", "recommendations", "priorisierung", "prioritization"]):
                        matching_section_started = False
        
        # Extrahiere Empfehlungen
        recommendations = []
        recommendations_section_started = False
        
        for i, line in enumerate(lines):
            if "empfehlungen" in line.lower() or "recommendations" in line.lower():
                recommendations_section_started = True
                continue
            
            if recommendations_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["priorisierung", "prioritization"]):
                    # Extrahiere Empfehlung aus der Zeile
                    recommendation = line.strip()
                    if recommendation.startswith("- "):
                        recommendation = recommendation[2:]
                    recommendations.append(recommendation)
                else:
                    if any(keyword in line.lower() for keyword in ["priorisierung", "prioritization"]):
                        recommendations_section_started = False
        
        # Erstelle strukturierten Dokumentenvergleich
        document_comparison = {
            "document_ids": document_ids,
            "inconsistencies": inconsistencies,
            "contradictions": contradictions,
            "missing_information": missing_information,
            "matching_information": matching_information,
            "recommendations": recommendations,
            "full_comparison": response,
            "timestamp": datetime.now().isoformat()
        }
        
        return document_comparison
    
    def _process_plan_data_extraction_response(self, response: str) -> Dict[str, Any]:
        """
        Verarbeitet die Antwort des KI-Modells zur Extraktion von Plandaten.
        
        Args:
            response: Antwort des KI-Modells
        
        Returns:
            Strukturierte Plandaten
        """
        # In einer realen Implementierung würde hier ein robuster Parser verwendet werden
        # Für dieses MVP verwenden wir eine vereinfachte Implementierung
        
        lines = response.strip().split('\n')
        
        # Extrahiere Räume und Flächen
        rooms_and_areas = []
        rooms_section_started = False
        
        for i, line in enumerate(lines):
            if "räume und flächen" in line.lower() or "rooms and areas" in line.lower():
                rooms_section_started = True
                continue
            
            if rooms_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["technische systeme", "technical systems", "maße", "dimensions"]):
                    # Extrahiere Raum aus der Zeile
                    room = line.strip()
                    if room.startswith("- "):
                        room = room[2:]
                    rooms_and_areas.append(room)
                else:
                    if any(keyword in line.lower() for keyword in ["technische systeme", "technical systems", "maße", "dimensions"]):
                        rooms_section_started = False
        
        # Extrahiere technische Systeme
        technical_systems = []
        systems_section_started = False
        
        for i, line in enumerate(lines):
            if "technische systeme" in line.lower() or "technical systems" in line.lower():
                systems_section_started = True
                continue
            
            if systems_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["maße", "dimensions", "materialien", "materials"]):
                    # Extrahiere System aus der Zeile
                    system = line.strip()
                    if system.startswith("- "):
                        system = system[2:]
                    technical_systems.append(system)
                else:
                    if any(keyword in line.lower() for keyword in ["maße", "dimensions", "materialien", "materials"]):
                        systems_section_started = False
        
        # Extrahiere Maße und Abmessungen
        dimensions = []
        dimensions_section_started = False
        
        for i, line in enumerate(lines):
            if "maße und abmessungen" in line.lower() or "dimensions" in line.lower():
                dimensions_section_started = True
                continue
            
            if dimensions_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["materialien", "materials", "anschlüsse", "connections"]):
                    # Extrahiere Maß aus der Zeile
                    dimension = line.strip()
                    if dimension.startswith("- "):
                        dimension = dimension[2:]
                    dimensions.append(dimension)
                else:
                    if any(keyword in line.lower() for keyword in ["materialien", "materials", "anschlüsse", "connections"]):
                        dimensions_section_started = False
        
        # Extrahiere Materialien
        materials = []
        materials_section_started = False
        
        for i, line in enumerate(lines):
            if "materialien" in line.lower() or "materials" in line.lower():
                materials_section_started = True
                continue
            
            if materials_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["anschlüsse", "connections", "revisionsstand", "revision"]):
                    # Extrahiere Material aus der Zeile
                    material = line.strip()
                    if material.startswith("- "):
                        material = material[2:]
                    materials.append(material)
                else:
                    if any(keyword in line.lower() for keyword in ["anschlüsse", "connections", "revisionsstand", "revision"]):
                        materials_section_started = False
        
        # Extrahiere Anschlüsse
        connections = []
        connections_section_started = False
        
        for i, line in enumerate(lines):
            if "anschlüsse" in line.lower() or "connections" in line.lower():
                connections_section_started = True
                continue
            
            if connections_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["revisionsstand", "revision", "koordinaten", "coordinates"]):
                    # Extrahiere Anschluss aus der Zeile
                    connection = line.strip()
                    if connection.startswith("- "):
                        connection = connection[2:]
                    connections.append(connection)
                else:
                    if any(keyword in line.lower() for keyword in ["revisionsstand", "revision", "koordinaten", "coordinates"]):
                        connections_section_started = False
        
        # Extrahiere Revisionsstand
        revisions = []
        revisions_section_started = False
        
        for i, line in enumerate(lines):
            if "revisionsstand" in line.lower() or "revision" in line.lower():
                revisions_section_started = True
                continue
            
            if revisions_section_started:
                if line.strip() and not any(keyword in line.lower() for keyword in ["koordinaten", "coordinates"]):
                    # Extrahiere Revision aus der Zeile
                    revision = line.strip()
                    if revision.startswith("- "):
                        revision = revision[2:]
                    revisions.append(revision)
                else:
                    if any(keyword in line.lower() for keyword in ["koordinaten", "coordinates"]):
                        revisions_section_started = False
        
        # Extrahiere Koordinaten
        coordinates = []
        coordinates_section_started = False
        
        for i, line in enumerate(lines):
            if "koordinaten" in line.lower() or "coordinates" in line.lower():
                coordinates_section_started = True
                continue
            
            if coordinates_section_started:
                if line.strip():
                    # Extrahiere Koordinate aus der Zeile
                    coordinate = line.strip()
                    if coordinate.startswith("- "):
                        coordinate = coordinate[2:]
                    coordinates.append(coordinate)
        
        # Erstelle strukturierte Plandaten
        plan_data = {
            "rooms_and_areas": rooms_and_areas,
            "technical_systems": technical_systems,
            "dimensions": dimensions,
            "materials": materials,
            "connections": connections,
            "revisions": revisions,
            "coordinates": coordinates,
            "full_extraction": response,
            "timestamp": datetime.now().isoformat()
        }
        
        return plan_data
    
    def _store_document_analysis(self, project_id: str, document_id: str, analysis: Dict[str, Any]) -> None:
        """
        Speichert eine Dokumentenanalyse in der Datenbank.
        
        Args:
            project_id: ID des Projekts
            document_id: ID des Dokuments
            analysis: Dokumentenanalyse
        """
        if "analyses" not in self.document_database:
            self.document_database["analyses"] = {}
        
        if project_id not in self.document_database["analyses"]:
            self.document_database["analyses"][project_id] = {}
        
        self.document_database["analyses"][project_id][document_id] = analysis
    
    def _get_document_analysis(self, project_id: str, document_id: str) -> Dict[str, Any]:
        """
        Holt eine Dokumentenanalyse aus der Datenbank.
        
        Args:
            project_id: ID des Projekts
            document_id: ID des Dokuments
        
        Returns:
            Dokumentenanalyse
        """
        if "analyses" not in self.document_database or project_id not in self.document_database["analyses"] or document_id not in self.document_database["analyses"][project_id]:
            return {}
        
        return self.document_database["analyses"][project_id][document_id]
    
    def _store_document_comparison(self, project_id: str, comparison_id: str, comparison: Dict[str, Any]) -> None:
        """
        Speichert einen Dokumentenvergleich in der Datenbank.
        
        Args:
            project_id: ID des Projekts
            comparison_id: ID des Vergleichs
            comparison: Dokumentenvergleich
        """
        if "comparisons" not in self.document_database:
            self.document_database["comparisons"] = {}
        
        if project_id not in self.document_database["comparisons"]:
            self.document_database["comparisons"][project_id] = {}
        
        self.document_database["comparisons"][project_id][comparison_id] = comparison
    
    def _store_plan_data(self, project_id: str, document_id: str, plan_data: Dict[str, Any]) -> None:
        """
        Speichert extrahierte Plandaten in der Datenbank.
        
        Args:
            project_id: ID des Projekts
            document_id: ID des Dokuments
            plan_data: Extrahierte Plandaten
        """
        if "plan_data" not in self.document_database:
            self.document_database["plan_data"] = {}
        
        if project_id not in self.document_database["plan_data"]:
            self.document_database["plan_data"][project_id] = {}
        
        self.document_database["plan_data"][project_id][document_id] = plan_data

