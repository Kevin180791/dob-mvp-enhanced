"""
Multimodales RAG-System für das DOB-MVP.

Dieses System erweitert das grundlegende RAG-System um die Fähigkeit, verschiedene
Dokumenttypen zu verarbeiten, einschließlich Text, Bilder, Pläne und PDFs.
"""
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
from datetime import datetime
import os
import tempfile
import base64
import re
import json

from app.rag.system import RAGSystem
from app.core.model_manager.registry import ModelRegistry

logger = logging.getLogger(__name__)

class MultimodalRAGSystem:
    """
    Multimodales RAG-System für das DOB-MVP.
    
    Dieses System erweitert das grundlegende RAG-System um die Fähigkeit, verschiedene
    Dokumenttypen zu verarbeiten, einschließlich Text, Bilder, Pläne und PDFs.
    """
    
    def __init__(self, model_registry: ModelRegistry, base_rag_system: RAGSystem):
        """
        Initialisiert das multimodale RAG-System.
        
        Args:
            model_registry: Registry für KI-Modelle
            base_rag_system: Grundlegendes RAG-System
        """
        self.model_registry = model_registry
        self.base_rag_system = base_rag_system
        self.document_processors = {
            "text": self._process_text_document,
            "image": self._process_image_document,
            "pdf": self._process_pdf_document,
            "plan": self._process_plan_document,
            "cad": self._process_cad_document,
            "bim": self._process_bim_document,
        }
        self.document_embeddings = {}  # Speichert Einbettungen für verschiedene Dokumenttypen
    
    def process_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet ein Dokument und extrahiert Informationen basierend auf dem Dokumenttyp.
        
        Args:
            data: Daten des Dokuments
                - document_id: ID des Dokuments
                - project_id: ID des Projekts
                - content: Inhalt des Dokuments (Text, Base64-kodiertes Bild, etc.)
                - document_type: Typ des Dokuments (text, image, pdf, plan, cad, bim)
                - metadata: Metadaten des Dokuments
        
        Returns:
            Dict mit verarbeitetem Dokument und extrahierten Informationen
        """
        logger.info(f"Verarbeite Dokument vom Typ {data.get('document_type', 'unbekannt')}")
        
        # Extrahiere relevante Daten
        document_id = data.get("document_id", f"doc-{datetime.now().isoformat()}")
        project_id = data.get("project_id", "")
        content = data.get("content", "")
        document_type = data.get("document_type", "text")
        metadata = data.get("metadata", {})
        
        # Verarbeite das Dokument basierend auf dem Dokumenttyp
        if document_type in self.document_processors:
            processor = self.document_processors[document_type]
            processed_document = processor(document_id, project_id, content, metadata)
        else:
            # Fallback auf Textverarbeitung
            logger.warning(f"Unbekannter Dokumenttyp: {document_type}, verwende Textverarbeitung als Fallback")
            processed_document = self._process_text_document(document_id, project_id, content, metadata)
        
        return processed_document
    
    def query_documents(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt eine Abfrage über verschiedene Dokumenttypen durch.
        
        Args:
            data: Daten der Abfrage
                - query: Abfragetext
                - project_id: ID des Projekts
                - document_types: Liste der Dokumenttypen, die durchsucht werden sollen
                - top_k: Anzahl der zurückzugebenden Ergebnisse
                - filters: Filter für die Suche
        
        Returns:
            Dict mit Abfrageergebnissen
        """
        logger.info(f"Führe Abfrage durch: {data.get('query', '')}")
        
        # Extrahiere relevante Daten
        query = data.get("query", "")
        project_id = data.get("project_id", "")
        document_types = data.get("document_types", ["text", "image", "pdf", "plan", "cad", "bim"])
        top_k = data.get("top_k", 5)
        filters = data.get("filters", {})
        
        # Führe die Abfrage für jeden Dokumenttyp durch
        results = {}
        
        for doc_type in document_types:
            if doc_type in self.document_embeddings and project_id in self.document_embeddings[doc_type]:
                # Führe die Abfrage für diesen Dokumenttyp durch
                type_results = self._query_document_type(query, project_id, doc_type, top_k, filters)
                results[doc_type] = type_results
        
        # Kombiniere und sortiere die Ergebnisse
        combined_results = self._combine_results(results, top_k)
        
        return {
            "query": query,
            "project_id": project_id,
            "document_types": document_types,
            "results": combined_results,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_multimodal_query(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analysiert eine multimodale Abfrage, die Text und Bilder enthalten kann.
        
        Args:
            data: Daten der Abfrage
                - query_text: Abfragetext
                - query_images: Liste von Base64-kodierten Bildern
                - project_id: ID des Projekts
                - document_types: Liste der Dokumenttypen, die durchsucht werden sollen
                - top_k: Anzahl der zurückzugebenden Ergebnisse
        
        Returns:
            Dict mit Analyseergebnissen
        """
        logger.info(f"Analysiere multimodale Abfrage")
        
        # Extrahiere relevante Daten
        query_text = data.get("query_text", "")
        query_images = data.get("query_images", [])
        project_id = data.get("project_id", "")
        document_types = data.get("document_types", ["text", "image", "pdf", "plan", "cad", "bim"])
        top_k = data.get("top_k", 5)
        
        # Analysiere den Abfragetext
        text_analysis = self._analyze_query_text(query_text)
        
        # Analysiere die Abfragebilder
        image_analyses = []
        for image in query_images:
            image_analysis = self._analyze_query_image(image)
            image_analyses.append(image_analysis)
        
        # Kombiniere die Analysen
        combined_analysis = self._combine_analyses(text_analysis, image_analyses)
        
        # Führe die Abfrage basierend auf der kombinierten Analyse durch
        query_results = self.query_documents({
            "query": combined_analysis["combined_query"],
            "project_id": project_id,
            "document_types": document_types,
            "top_k": top_k,
            "filters": {}
        })
        
        # Erstelle die Antwort basierend auf den Abfrageergebnissen
        response = self._generate_multimodal_response(combined_analysis, query_results)
        
        return {
            "query_text": query_text,
            "query_images_count": len(query_images),
            "project_id": project_id,
            "analysis": combined_analysis,
            "results": query_results["results"],
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    
    def extract_plan_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrahiert Features aus einem Bauplan.
        
        Args:
            data: Daten des Plans
                - document_id: ID des Dokuments
                - project_id: ID des Projekts
                - content: Base64-kodierter Plan
                - plan_type: Typ des Plans (z.B. Grundriss, Schnitt, Detail)
                - scale: Maßstab des Plans
                - discipline: Fachbereich des Plans (z.B. Architektur, TGA, Statik)
        
        Returns:
            Dict mit extrahierten Features
        """
        logger.info(f"Extrahiere Features aus Plan: {data.get('document_id', 'Neuer Plan')}")
        
        # Extrahiere relevante Daten
        document_id = data.get("document_id", f"plan-{datetime.now().isoformat()}")
        project_id = data.get("project_id", "")
        content = data.get("content", "")
        plan_type = data.get("plan_type", "")
        scale = data.get("scale", "")
        discipline = data.get("discipline", "")
        
        # Speichere den Plan temporär
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_file.write(base64.b64decode(content))
            temp_file_path = temp_file.name
        
        try:
            # Erstelle Prompt für das KI-Modell
            prompt = self._create_plan_feature_extraction_prompt(temp_file_path, plan_type, scale, discipline)
            
            # Rufe KI-Modell auf
            model = self.model_registry.get_model("multimodal")
            model_response = model.generate(prompt, max_tokens=1000)
            
            # Verarbeite die Antwort
            features = self._process_plan_feature_extraction_response(model_response)
            
            # Erstelle Einbettungen für den Plan
            if "plan" not in self.document_embeddings:
                self.document_embeddings["plan"] = {}
            
            if project_id not in self.document_embeddings["plan"]:
                self.document_embeddings["plan"][project_id] = {}
            
            # Erstelle Einbettung für den Plan
            embedding_model = self.model_registry.get_model("embedding")
            embedding = embedding_model.embed(json.dumps(features))
            
            self.document_embeddings["plan"][project_id][document_id] = {
                "embedding": embedding,
                "features": features,
                "metadata": {
                    "document_id": document_id,
                    "plan_type": plan_type,
                    "scale": scale,
                    "discipline": discipline
                }
            }
            
            return {
                "document_id": document_id,
                "project_id": project_id,
                "plan_type": plan_type,
                "scale": scale,
                "discipline": discipline,
                "features": features,
                "timestamp": datetime.now().isoformat()
            }
        
        finally:
            # Lösche die temporäre Datei
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    def compare_plans(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vergleicht mehrere Baupläne und identifiziert Unterschiede.
        
        Args:
            data: Daten für den Planvergleich
                - project_id: ID des Projekts
                - document_ids: Liste der zu vergleichenden Plan-IDs
                - comparison_type: Typ des Vergleichs (z.B. "version", "cross-discipline")
        
        Returns:
            Dict mit Planvergleich
        """
        logger.info(f"Vergleiche Pläne für Projekt: {data.get('project_id', '')}")
        
        # Extrahiere relevante Daten
        project_id = data.get("project_id", "")
        document_ids = data.get("document_ids", [])
        comparison_type = data.get("comparison_type", "version")
        
        # Hole die Pläne aus der Datenbank
        plans = []
        for doc_id in document_ids:
            if "plan" in self.document_embeddings and project_id in self.document_embeddings["plan"] and doc_id in self.document_embeddings["plan"][project_id]:
                plan_data = self.document_embeddings["plan"][project_id][doc_id]
                plans.append({
                    "document_id": doc_id,
                    "features": plan_data["features"],
                    "metadata": plan_data["metadata"]
                })
        
        # Erstelle Prompt für das KI-Modell
        prompt = self._create_plan_comparison_prompt(plans, comparison_type)
        
        # Rufe KI-Modell auf
        model = self.model_registry.get_model("text")
        model_response = model.generate(prompt, max_tokens=1000)
        
        # Verarbeite die Antwort
        comparison_result = self._process_plan_comparison_response(model_response, document_ids)
        
        return {
            "project_id": project_id,
            "document_ids": document_ids,
            "comparison_type": comparison_type,
            "comparison_result": comparison_result,
            "timestamp": datetime.now().isoformat()
        }
    
    def _process_text_document(self, document_id: str, project_id: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet ein Textdokument.
        
        Args:
            document_id: ID des Dokuments
            project_id: ID des Projekts
            content: Inhalt des Dokuments
            metadata: Metadaten des Dokuments
        
        Returns:
            Dict mit verarbeitetem Dokument
        """
        logger.info(f"Verarbeite Textdokument: {document_id}")
        
        # Verarbeite das Dokument mit dem grundlegenden RAG-System
        processed_document = self.base_rag_system.process_document({
            "document_id": document_id,
            "project_id": project_id,
            "content": content,
            "metadata": metadata
        })
        
        # Speichere die Einbettung
        if "text" not in self.document_embeddings:
            self.document_embeddings["text"] = {}
        
        if project_id not in self.document_embeddings["text"]:
            self.document_embeddings["text"][project_id] = {}
        
        self.document_embeddings["text"][project_id][document_id] = {
            "embedding": processed_document.get("embedding", []),
            "chunks": processed_document.get("chunks", []),
            "metadata": metadata
        }
        
        return processed_document
    
    def _process_image_document(self, document_id: str, project_id: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet ein Bilddokument.
        
        Args:
            document_id: ID des Dokuments
            project_id: ID des Projekts
            content: Base64-kodiertes Bild
            metadata: Metadaten des Dokuments
        
        Returns:
            Dict mit verarbeitetem Dokument
        """
        logger.info(f"Verarbeite Bilddokument: {document_id}")
        
        # Speichere das Bild temporär
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_file.write(base64.b64decode(content))
            temp_file_path = temp_file.name
        
        try:
            # Erstelle Prompt für das KI-Modell
            prompt = self._create_image_analysis_prompt(temp_file_path, metadata)
            
            # Rufe KI-Modell auf
            model = self.model_registry.get_model("multimodal")
            model_response = model.generate(prompt, max_tokens=1000)
            
            # Verarbeite die Antwort
            image_analysis = self._process_image_analysis_response(model_response)
            
            # Erstelle Einbettungen für das Bild
            if "image" not in self.document_embeddings:
                self.document_embeddings["image"] = {}
            
            if project_id not in self.document_embeddings["image"]:
                self.document_embeddings["image"][project_id] = {}
            
            # Erstelle Einbettung für das Bild
            embedding_model = self.model_registry.get_model("embedding")
            embedding = embedding_model.embed(json.dumps(image_analysis))
            
            self.document_embeddings["image"][project_id][document_id] = {
                "embedding": embedding,
                "analysis": image_analysis,
                "metadata": metadata
            }
            
            return {
                "document_id": document_id,
                "project_id": project_id,
                "document_type": "image",
                "analysis": image_analysis,
                "timestamp": datetime.now().isoformat()
            }
        
        finally:
            # Lösche die temporäre Datei
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    def _process_pdf_document(self, document_id: str, project_id: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet ein PDF-Dokument.
        
        Args:
            document_id: ID des Dokuments
            project_id: ID des Projekts
            content: Base64-kodiertes PDF
            metadata: Metadaten des Dokuments
        
        Returns:
            Dict mit verarbeitetem Dokument
        """
        logger.info(f"Verarbeite PDF-Dokument: {document_id}")
        
        # Speichere das PDF temporär
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(base64.b64decode(content))
            temp_file_path = temp_file.name
        
        try:
            # Extrahiere Text aus dem PDF
            # In einer realen Implementierung würde hier eine PDF-Bibliothek verwendet werden
            # Für dieses MVP simulieren wir die Textextraktion
            extracted_text = f"Extrahierter Text aus PDF {document_id}"
            
            # Extrahiere Bilder aus dem PDF
            # In einer realen Implementierung würde hier eine PDF-Bibliothek verwendet werden
            # Für dieses MVP simulieren wir die Bildextraktion
            extracted_images = []
            
            # Verarbeite den extrahierten Text mit dem grundlegenden RAG-System
            text_processed = self.base_rag_system.process_document({
                "document_id": document_id,
                "project_id": project_id,
                "content": extracted_text,
                "metadata": metadata
            })
            
            # Verarbeite die extrahierten Bilder
            image_analyses = []
            for i, image in enumerate(extracted_images):
                image_id = f"{document_id}_image_{i}"
                image_processed = self._process_image_document(image_id, project_id, image, metadata)
                image_analyses.append(image_processed["analysis"])
            
            # Kombiniere die Ergebnisse
            combined_analysis = {
                "text_chunks": text_processed.get("chunks", []),
                "image_analyses": image_analyses
            }
            
            # Erstelle Einbettungen für das PDF
            if "pdf" not in self.document_embeddings:
                self.document_embeddings["pdf"] = {}
            
            if project_id not in self.document_embeddings["pdf"]:
                self.document_embeddings["pdf"][project_id] = {}
            
            # Erstelle Einbettung für das PDF
            embedding_model = self.model_registry.get_model("embedding")
            embedding = embedding_model.embed(json.dumps(combined_analysis))
            
            self.document_embeddings["pdf"][project_id][document_id] = {
                "embedding": embedding,
                "analysis": combined_analysis,
                "metadata": metadata
            }
            
            return {
                "document_id": document_id,
                "project_id": project_id,
                "document_type": "pdf",
                "analysis": combined_analysis,
                "timestamp": datetime.now().isoformat()
            }
        
        finally:
            # Lösche die temporäre Datei
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    def _process_plan_document(self, document_id: str, project_id: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet einen Bauplan.
        
        Args:
            document_id: ID des Dokuments
            project_id: ID des Projekts
            content: Base64-kodierter Plan
            metadata: Metadaten des Dokuments
        
        Returns:
            Dict mit verarbeitetem Dokument
        """
        logger.info(f"Verarbeite Bauplan: {document_id}")
        
        # Extrahiere relevante Metadaten
        plan_type = metadata.get("plan_type", "")
        scale = metadata.get("scale", "")
        discipline = metadata.get("discipline", "")
        
        # Extrahiere Features aus dem Plan
        features = self.extract_plan_features({
            "document_id": document_id,
            "project_id": project_id,
            "content": content,
            "plan_type": plan_type,
            "scale": scale,
            "discipline": discipline
        })
        
        return {
            "document_id": document_id,
            "project_id": project_id,
            "document_type": "plan",
            "features": features["features"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _process_cad_document(self, document_id: str, project_id: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet ein CAD-Dokument.
        
        Args:
            document_id: ID des Dokuments
            project_id: ID des Projekts
            content: Base64-kodiertes CAD-Dokument
            metadata: Metadaten des Dokuments
        
        Returns:
            Dict mit verarbeitetem Dokument
        """
        logger.info(f"Verarbeite CAD-Dokument: {document_id}")
        
        # In einer realen Implementierung würde hier eine CAD-Bibliothek verwendet werden
        # Für dieses MVP simulieren wir die CAD-Verarbeitung
        
        # Extrahiere relevante Metadaten
        cad_type = metadata.get("cad_type", "")
        version = metadata.get("version", "")
        
        # Simuliere die Extraktion von CAD-Elementen
        cad_elements = {
            "lines": [
                {"start": [0, 0, 0], "end": [10, 0, 0]},
                {"start": [10, 0, 0], "end": [10, 10, 0]},
                {"start": [10, 10, 0], "end": [0, 10, 0]},
                {"start": [0, 10, 0], "end": [0, 0, 0]}
            ],
            "circles": [
                {"center": [5, 5, 0], "radius": 2}
            ],
            "text": [
                {"position": [2, 2, 0], "content": "Beispieltext"}
            ]
        }
        
        # Erstelle Einbettungen für das CAD-Dokument
        if "cad" not in self.document_embeddings:
            self.document_embeddings["cad"] = {}
        
        if project_id not in self.document_embeddings["cad"]:
            self.document_embeddings["cad"][project_id] = {}
        
        # Erstelle Einbettung für das CAD-Dokument
        embedding_model = self.model_registry.get_model("embedding")
        embedding = embedding_model.embed(json.dumps(cad_elements))
        
        self.document_embeddings["cad"][project_id][document_id] = {
            "embedding": embedding,
            "elements": cad_elements,
            "metadata": metadata
        }
        
        return {
            "document_id": document_id,
            "project_id": project_id,
            "document_type": "cad",
            "cad_type": cad_type,
            "version": version,
            "elements": cad_elements,
            "timestamp": datetime.now().isoformat()
        }
    
    def _process_bim_document(self, document_id: str, project_id: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet ein BIM-Dokument.
        
        Args:
            document_id: ID des Dokuments
            project_id: ID des Projekts
            content: Base64-kodiertes BIM-Dokument
            metadata: Metadaten des Dokuments
        
        Returns:
            Dict mit verarbeitetem Dokument
        """
        logger.info(f"Verarbeite BIM-Dokument: {document_id}")
        
        # In einer realen Implementierung würde hier eine BIM-Bibliothek verwendet werden
        # Für dieses MVP simulieren wir die BIM-Verarbeitung
        
        # Extrahiere relevante Metadaten
        bim_type = metadata.get("bim_type", "")
        version = metadata.get("version", "")
        
        # Simuliere die Extraktion von BIM-Elementen
        bim_elements = {
            "spaces": [
                {"id": "space-1", "name": "Raum 1", "area": 25.0, "volume": 75.0},
                {"id": "space-2", "name": "Raum 2", "area": 30.0, "volume": 90.0}
            ],
            "walls": [
                {"id": "wall-1", "type": "Außenwand", "length": 5.0, "height": 3.0},
                {"id": "wall-2", "type": "Innenwand", "length": 4.0, "height": 3.0}
            ],
            "mep_elements": [
                {"id": "mep-1", "type": "Lüftungskanal", "diameter": 0.2, "length": 10.0},
                {"id": "mep-2", "type": "Wasserleitung", "diameter": 0.05, "length": 15.0}
            ]
        }
        
        # Erstelle Einbettungen für das BIM-Dokument
        if "bim" not in self.document_embeddings:
            self.document_embeddings["bim"] = {}
        
        if project_id not in self.document_embeddings["bim"]:
            self.document_embeddings["bim"][project_id] = {}
        
        # Erstelle Einbettung für das BIM-Dokument
        embedding_model = self.model_registry.get_model("embedding")
        embedding = embedding_model.embed(json.dumps(bim_elements))
        
        self.document_embeddings["bim"][project_id][document_id] = {
            "embedding": embedding,
            "elements": bim_elements,
            "metadata": metadata
        }
        
        return {
            "document_id": document_id,
            "project_id": project_id,
            "document_type": "bim",
            "bim_type": bim_type,
            "version": version,
            "elements": bim_elements,
            "timestamp": datetime.now().isoformat()
        }
    
    def _query_document_type(self, query: str, project_id: str, document_type: str, top_k: int, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Führt eine Abfrage für einen bestimmten Dokumenttyp durch.
        
        Args:
            query: Abfragetext
            project_id: ID des Projekts
            document_type: Dokumenttyp
            top_k: Anzahl der zurückzugebenden Ergebnisse
            filters: Filter für die Suche
        
        Returns:
            Liste mit Abfrageergebnissen
        """
        logger.info(f"Führe Abfrage für Dokumenttyp {document_type} durch")
        
        # Erstelle Einbettung für die Abfrage
        embedding_model = self.model_registry.get_model("embedding")
        query_embedding = embedding_model.embed(query)
        
        # Hole die Einbettungen für den Dokumenttyp
        if document_type not in self.document_embeddings or project_id not in self.document_embeddings[document_type]:
            return []
        
        # Berechne die Ähnlichkeit zwischen der Abfrage und den Dokumenten
        similarities = []
        
        for doc_id, doc_data in self.document_embeddings[document_type][project_id].items():
            # Überprüfe, ob das Dokument die Filter erfüllt
            if not self._check_filters(doc_data["metadata"], filters):
                continue
            
            # Berechne die Ähnlichkeit
            similarity = self._calculate_similarity(query_embedding, doc_data["embedding"])
            
            # Füge das Dokument zur Liste hinzu
            similarities.append({
                "document_id": doc_id,
                "document_type": document_type,
                "similarity": similarity,
                "metadata": doc_data["metadata"]
            })
        
        # Sortiere die Dokumente nach Ähnlichkeit
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Gib die Top-K-Ergebnisse zurück
        return similarities[:top_k]
    
    def _combine_results(self, results: Dict[str, List[Dict[str, Any]]], top_k: int) -> List[Dict[str, Any]]:
        """
        Kombiniert die Ergebnisse verschiedener Dokumenttypen.
        
        Args:
            results: Ergebnisse für verschiedene Dokumenttypen
            top_k: Anzahl der zurückzugebenden Ergebnisse
        
        Returns:
            Kombinierte Ergebnisse
        """
        logger.info(f"Kombiniere Ergebnisse verschiedener Dokumenttypen")
        
        # Kombiniere alle Ergebnisse
        combined = []
        
        for doc_type, type_results in results.items():
            for result in type_results:
                combined.append(result)
        
        # Sortiere die Ergebnisse nach Ähnlichkeit
        combined.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Gib die Top-K-Ergebnisse zurück
        return combined[:top_k]
    
    def _check_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        Überprüft, ob ein Dokument die Filter erfüllt.
        
        Args:
            metadata: Metadaten des Dokuments
            filters: Filter für die Suche
        
        Returns:
            True, wenn das Dokument die Filter erfüllt, sonst False
        """
        # Überprüfe jeden Filter
        for key, value in filters.items():
            if key not in metadata or metadata[key] != value:
                return False
        
        return True
    
    def _calculate_similarity(self, query_embedding: List[float], document_embedding: List[float]) -> float:
        """
        Berechnet die Ähnlichkeit zwischen einer Abfrage und einem Dokument.
        
        Args:
            query_embedding: Einbettung der Abfrage
            document_embedding: Einbettung des Dokuments
        
        Returns:
            Ähnlichkeitswert
        """
        # In einer realen Implementierung würde hier ein Ähnlichkeitsmaß wie Kosinus-Ähnlichkeit verwendet werden
        # Für dieses MVP simulieren wir die Ähnlichkeitsberechnung
        return 0.8  # Simulierter Ähnlichkeitswert
    
    def _create_image_analysis_prompt(self, image_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erstellt einen Prompt für die Bildanalyse.
        
        Args:
            image_path: Pfad zum Bild
            metadata: Metadaten des Bildes
        
        Returns:
            Prompt für das KI-Modell
        """
        # Erstelle den Prompt
        prompt = {
            "text": "Analysiere dieses Bild im Kontext des Bauwesens. Beschreibe den Inhalt, identifiziere relevante Elemente und extrahiere technische Informationen.",
            "image": image_path
        }
        
        return prompt
    
    def _process_image_analysis_response(self, response: str) -> Dict[str, Any]:
        """
        Verarbeitet die Antwort des KI-Modells zur Bildanalyse.
        
        Args:
            response: Antwort des KI-Modells
        
        Returns:
            Strukturierte Bildanalyse
        """
        # In einer realen Implementierung würde hier ein robuster Parser verwendet werden
        # Für dieses MVP verwenden wir eine vereinfachte Implementierung
        
        # Extrahiere Beschreibung
        description = response
        
        # Extrahiere Elemente
        elements = []
        elements_match = re.search(r"Elemente:(.*?)(?:Technische Informationen:|$)", response, re.DOTALL)
        if elements_match:
            elements_text = elements_match.group(1).strip()
            for line in elements_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    elements.append(line.strip()[2:])
        
        # Extrahiere technische Informationen
        technical_info = []
        tech_match = re.search(r"Technische Informationen:(.*?)$", response, re.DOTALL)
        if tech_match:
            tech_text = tech_match.group(1).strip()
            for line in tech_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    technical_info.append(line.strip()[2:])
        
        # Erstelle strukturierte Bildanalyse
        image_analysis = {
            "description": description,
            "elements": elements,
            "technical_info": technical_info
        }
        
        return image_analysis
    
    def _create_plan_feature_extraction_prompt(self, image_path: str, plan_type: str, scale: str, discipline: str) -> Dict[str, Any]:
        """
        Erstellt einen Prompt für die Extraktion von Features aus einem Bauplan.
        
        Args:
            image_path: Pfad zum Bild des Plans
            plan_type: Typ des Plans
            scale: Maßstab des Plans
            discipline: Fachbereich des Plans
        
        Returns:
            Prompt für das KI-Modell
        """
        # Erstelle den Prompt
        prompt = {
            "text": f"""Analysiere diesen Bauplan und extrahiere relevante Features.

Plan-Typ: {plan_type}
Maßstab: {scale}
Fachbereich: {discipline}

Bitte extrahiere folgende Informationen:
1. Räume und Flächen mit Bezeichnungen und Größen
2. Technische Systeme und Komponenten
3. Maße und Abmessungen
4. Materialien und Spezifikationen
5. Anschlüsse und Verbindungen
6. Revisionsstand und Änderungen
7. Koordinaten und Referenzpunkte""",
            "image": image_path
        }
        
        return prompt
    
    def _process_plan_feature_extraction_response(self, response: str) -> Dict[str, Any]:
        """
        Verarbeitet die Antwort des KI-Modells zur Extraktion von Features aus einem Bauplan.
        
        Args:
            response: Antwort des KI-Modells
        
        Returns:
            Strukturierte Features
        """
        # In einer realen Implementierung würde hier ein robuster Parser verwendet werden
        # Für dieses MVP verwenden wir eine vereinfachte Implementierung
        
        # Extrahiere Räume und Flächen
        rooms_and_areas = []
        rooms_match = re.search(r"Räume und Flächen:(.*?)(?:Technische Systeme:|$)", response, re.DOTALL)
        if rooms_match:
            rooms_text = rooms_match.group(1).strip()
            for line in rooms_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    rooms_and_areas.append(line.strip()[2:])
        
        # Extrahiere technische Systeme
        technical_systems = []
        systems_match = re.search(r"Technische Systeme:(.*?)(?:Maße und Abmessungen:|$)", response, re.DOTALL)
        if systems_match:
            systems_text = systems_match.group(1).strip()
            for line in systems_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    technical_systems.append(line.strip()[2:])
        
        # Extrahiere Maße und Abmessungen
        dimensions = []
        dimensions_match = re.search(r"Maße und Abmessungen:(.*?)(?:Materialien und Spezifikationen:|$)", response, re.DOTALL)
        if dimensions_match:
            dimensions_text = dimensions_match.group(1).strip()
            for line in dimensions_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    dimensions.append(line.strip()[2:])
        
        # Extrahiere Materialien und Spezifikationen
        materials = []
        materials_match = re.search(r"Materialien und Spezifikationen:(.*?)(?:Anschlüsse und Verbindungen:|$)", response, re.DOTALL)
        if materials_match:
            materials_text = materials_match.group(1).strip()
            for line in materials_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    materials.append(line.strip()[2:])
        
        # Extrahiere Anschlüsse und Verbindungen
        connections = []
        connections_match = re.search(r"Anschlüsse und Verbindungen:(.*?)(?:Revisionsstand und Änderungen:|$)", response, re.DOTALL)
        if connections_match:
            connections_text = connections_match.group(1).strip()
            for line in connections_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    connections.append(line.strip()[2:])
        
        # Extrahiere Revisionsstand und Änderungen
        revisions = []
        revisions_match = re.search(r"Revisionsstand und Änderungen:(.*?)(?:Koordinaten und Referenzpunkte:|$)", response, re.DOTALL)
        if revisions_match:
            revisions_text = revisions_match.group(1).strip()
            for line in revisions_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    revisions.append(line.strip()[2:])
        
        # Extrahiere Koordinaten und Referenzpunkte
        coordinates = []
        coordinates_match = re.search(r"Koordinaten und Referenzpunkte:(.*?)$", response, re.DOTALL)
        if coordinates_match:
            coordinates_text = coordinates_match.group(1).strip()
            for line in coordinates_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    coordinates.append(line.strip()[2:])
        
        # Erstelle strukturierte Features
        features = {
            "rooms_and_areas": rooms_and_areas,
            "technical_systems": technical_systems,
            "dimensions": dimensions,
            "materials": materials,
            "connections": connections,
            "revisions": revisions,
            "coordinates": coordinates
        }
        
        return features
    
    def _create_plan_comparison_prompt(self, plans: List[Dict[str, Any]], comparison_type: str) -> str:
        """
        Erstellt einen Prompt für den Planvergleich.
        
        Args:
            plans: Liste der zu vergleichenden Pläne
            comparison_type: Typ des Vergleichs
        
        Returns:
            Prompt für das KI-Modell
        """
        # Erstelle Informationen zu den Plänen
        plans_info = "Keine Pläne verfügbar."
        if plans:
            plan_texts = []
            for i, plan in enumerate(plans):
                doc_id = plan.get("document_id", f"Plan {i+1}")
                features = plan.get("features", {})
                metadata = plan.get("metadata", {})
                
                plan_type = metadata.get("plan_type", "Unbekannt")
                scale = metadata.get("scale", "Unbekannt")
                discipline = metadata.get("discipline", "Unbekannt")
                
                rooms = "\n".join([f"- {room}" for room in features.get("rooms_and_areas", [])])
                if not rooms:
                    rooms = "Keine Räume und Flächen verfügbar."
                
                systems = "\n".join([f"- {system}" for system in features.get("technical_systems", [])])
                if not systems:
                    systems = "Keine technischen Systeme verfügbar."
                
                plan_text = f"""PLAN ID: {doc_id}
Typ: {plan_type}
Maßstab: {scale}
Fachbereich: {discipline}

Räume und Flächen:
{rooms}

Technische Systeme:
{systems}
"""
                plan_texts.append(plan_text)
            
            plans_info = "\n\n".join(plan_texts)
        
        # Erstelle den Prompt
        prompt = f"""Als Planvergleichs-Agent im Bauwesen, vergleiche die folgenden Pläne und identifiziere Unterschiede und Inkonsistenzen:

VERGLEICHSTYP:
{comparison_type}

PLÄNE:
{plans_info}

Bitte vergleiche die Pläne und gib folgende Informationen zurück:
1. Identifizierte Unterschiede zwischen den Plänen
2. Inkonsistenzen in Räumen und Flächen
3. Inkonsistenzen in technischen Systemen
4. Inkonsistenzen in Maßen und Abmessungen
5. Empfehlungen zur Behebung von Inkonsistenzen
6. Priorisierung der identifizierten Probleme

Formatiere deine Antwort als strukturierten Text mit klaren Abschnitten für jede der oben genannten Informationen.
"""
        return prompt
    
    def _process_plan_comparison_response(self, response: str, document_ids: List[str]) -> Dict[str, Any]:
        """
        Verarbeitet die Antwort des KI-Modells zum Planvergleich.
        
        Args:
            response: Antwort des KI-Modells
            document_ids: Liste der verglichenen Plan-IDs
        
        Returns:
            Strukturierter Planvergleich
        """
        # In einer realen Implementierung würde hier ein robuster Parser verwendet werden
        # Für dieses MVP verwenden wir eine vereinfachte Implementierung
        
        # Extrahiere identifizierte Unterschiede
        differences = []
        differences_match = re.search(r"Identifizierte Unterschiede:(.*?)(?:Inkonsistenzen in Räumen und Flächen:|$)", response, re.DOTALL)
        if differences_match:
            differences_text = differences_match.group(1).strip()
            for line in differences_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    differences.append(line.strip()[2:])
        
        # Extrahiere Inkonsistenzen in Räumen und Flächen
        room_inconsistencies = []
        room_match = re.search(r"Inkonsistenzen in Räumen und Flächen:(.*?)(?:Inkonsistenzen in technischen Systemen:|$)", response, re.DOTALL)
        if room_match:
            room_text = room_match.group(1).strip()
            for line in room_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    room_inconsistencies.append(line.strip()[2:])
        
        # Extrahiere Inkonsistenzen in technischen Systemen
        system_inconsistencies = []
        system_match = re.search(r"Inkonsistenzen in technischen Systemen:(.*?)(?:Inkonsistenzen in Maßen und Abmessungen:|$)", response, re.DOTALL)
        if system_match:
            system_text = system_match.group(1).strip()
            for line in system_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    system_inconsistencies.append(line.strip()[2:])
        
        # Extrahiere Inkonsistenzen in Maßen und Abmessungen
        dimension_inconsistencies = []
        dimension_match = re.search(r"Inkonsistenzen in Maßen und Abmessungen:(.*?)(?:Empfehlungen zur Behebung von Inkonsistenzen:|$)", response, re.DOTALL)
        if dimension_match:
            dimension_text = dimension_match.group(1).strip()
            for line in dimension_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    dimension_inconsistencies.append(line.strip()[2:])
        
        # Extrahiere Empfehlungen
        recommendations = []
        recommendations_match = re.search(r"Empfehlungen zur Behebung von Inkonsistenzen:(.*?)(?:Priorisierung der identifizierten Probleme:|$)", response, re.DOTALL)
        if recommendations_match:
            recommendations_text = recommendations_match.group(1).strip()
            for line in recommendations_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    recommendations.append(line.strip()[2:])
        
        # Extrahiere Priorisierung
        priorities = []
        priorities_match = re.search(r"Priorisierung der identifizierten Probleme:(.*?)$", response, re.DOTALL)
        if priorities_match:
            priorities_text = priorities_match.group(1).strip()
            for line in priorities_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    priorities.append(line.strip()[2:])
        
        # Erstelle strukturierten Planvergleich
        comparison_result = {
            "document_ids": document_ids,
            "differences": differences,
            "room_inconsistencies": room_inconsistencies,
            "system_inconsistencies": system_inconsistencies,
            "dimension_inconsistencies": dimension_inconsistencies,
            "recommendations": recommendations,
            "priorities": priorities,
            "full_comparison": response
        }
        
        return comparison_result
    
    def _analyze_query_text(self, query_text: str) -> Dict[str, Any]:
        """
        Analysiert einen Abfragetext.
        
        Args:
            query_text: Abfragetext
        
        Returns:
            Analyseergebnis
        """
        logger.info(f"Analysiere Abfragetext: {query_text}")
        
        # Erstelle Prompt für das KI-Modell
        prompt = f"""Analysiere die folgende Abfrage im Kontext des Bauwesens:

ABFRAGE:
{query_text}

Bitte extrahiere folgende Informationen:
1. Hauptthema der Abfrage
2. Relevante Fachbereiche (z.B. Architektur, TGA, Statik)
3. Gesuchte Informationstypen (z.B. technische Spezifikationen, Maße, Materialien)
4. Zeitliche Aspekte (z.B. aktuelle Version, historische Daten)
5. Räumliche Aspekte (z.B. bestimmte Bereiche, Räume, Etagen)
6. Erweiterte Suchbegriffe für die Abfrage

Formatiere deine Antwort als strukturierten Text mit klaren Abschnitten für jede der oben genannten Informationen.
"""
        
        # Rufe KI-Modell auf
        model = self.model_registry.get_model("text")
        model_response = model.generate(prompt, max_tokens=1000)
        
        # Verarbeite die Antwort
        # In einer realen Implementierung würde hier ein robuster Parser verwendet werden
        # Für dieses MVP verwenden wir eine vereinfachte Implementierung
        
        # Extrahiere Hauptthema
        main_topic = ""
        topic_match = re.search(r"Hauptthema:(.*?)(?:Relevante Fachbereiche:|$)", model_response, re.DOTALL)
        if topic_match:
            main_topic = topic_match.group(1).strip()
        
        # Extrahiere relevante Fachbereiche
        disciplines = []
        disciplines_match = re.search(r"Relevante Fachbereiche:(.*?)(?:Gesuchte Informationstypen:|$)", model_response, re.DOTALL)
        if disciplines_match:
            disciplines_text = disciplines_match.group(1).strip()
            for line in disciplines_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    disciplines.append(line.strip()[2:])
        
        # Extrahiere gesuchte Informationstypen
        info_types = []
        info_match = re.search(r"Gesuchte Informationstypen:(.*?)(?:Zeitliche Aspekte:|$)", model_response, re.DOTALL)
        if info_match:
            info_text = info_match.group(1).strip()
            for line in info_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    info_types.append(line.strip()[2:])
        
        # Extrahiere zeitliche Aspekte
        temporal_aspects = []
        temporal_match = re.search(r"Zeitliche Aspekte:(.*?)(?:Räumliche Aspekte:|$)", model_response, re.DOTALL)
        if temporal_match:
            temporal_text = temporal_match.group(1).strip()
            for line in temporal_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    temporal_aspects.append(line.strip()[2:])
        
        # Extrahiere räumliche Aspekte
        spatial_aspects = []
        spatial_match = re.search(r"Räumliche Aspekte:(.*?)(?:Erweiterte Suchbegriffe:|$)", model_response, re.DOTALL)
        if spatial_match:
            spatial_text = spatial_match.group(1).strip()
            for line in spatial_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    spatial_aspects.append(line.strip()[2:])
        
        # Extrahiere erweiterte Suchbegriffe
        search_terms = []
        search_match = re.search(r"Erweiterte Suchbegriffe:(.*?)$", model_response, re.DOTALL)
        if search_match:
            search_text = search_match.group(1).strip()
            for line in search_text.split("\n"):
                if line.strip() and line.strip().startswith("- "):
                    search_terms.append(line.strip()[2:])
        
        # Erstelle erweiterte Abfrage
        extended_query = f"{query_text} {' '.join(search_terms)}"
        
        # Erstelle Analyseergebnis
        analysis = {
            "main_topic": main_topic,
            "disciplines": disciplines,
            "info_types": info_types,
            "temporal_aspects": temporal_aspects,
            "spatial_aspects": spatial_aspects,
            "search_terms": search_terms,
            "extended_query": extended_query
        }
        
        return analysis
    
    def _analyze_query_image(self, image: str) -> Dict[str, Any]:
        """
        Analysiert ein Abfragebild.
        
        Args:
            image: Base64-kodiertes Bild
        
        Returns:
            Analyseergebnis
        """
        logger.info(f"Analysiere Abfragebild")
        
        # Speichere das Bild temporär
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_file.write(base64.b64decode(image))
            temp_file_path = temp_file.name
        
        try:
            # Erstelle Prompt für das KI-Modell
            prompt = {
                "text": """Analysiere dieses Bild im Kontext des Bauwesens.

Bitte extrahiere folgende Informationen:
1. Hauptinhalt des Bildes
2. Relevante Fachbereiche (z.B. Architektur, TGA, Statik)
3. Sichtbare Elemente und Komponenten
4. Technische Aspekte und Details
5. Mögliche Probleme oder Fragen
6. Suchbegriffe für eine textbasierte Suche

Formatiere deine Antwort als strukturierten Text mit klaren Abschnitten für jede der oben genannten Informationen.""",
                "image": temp_file_path
            }
            
            # Rufe KI-Modell auf
            model = self.model_registry.get_model("multimodal")
            model_response = model.generate(prompt, max_tokens=1000)
            
            # Verarbeite die Antwort
            # In einer realen Implementierung würde hier ein robuster Parser verwendet werden
            # Für dieses MVP verwenden wir eine vereinfachte Implementierung
            
            # Extrahiere Hauptinhalt
            main_content = ""
            content_match = re.search(r"Hauptinhalt:(.*?)(?:Relevante Fachbereiche:|$)", model_response, re.DOTALL)
            if content_match:
                main_content = content_match.group(1).strip()
            
            # Extrahiere relevante Fachbereiche
            disciplines = []
            disciplines_match = re.search(r"Relevante Fachbereiche:(.*?)(?:Sichtbare Elemente und Komponenten:|$)", model_response, re.DOTALL)
            if disciplines_match:
                disciplines_text = disciplines_match.group(1).strip()
                for line in disciplines_text.split("\n"):
                    if line.strip() and line.strip().startswith("- "):
                        disciplines.append(line.strip()[2:])
            
            # Extrahiere sichtbare Elemente
            elements = []
            elements_match = re.search(r"Sichtbare Elemente und Komponenten:(.*?)(?:Technische Aspekte und Details:|$)", model_response, re.DOTALL)
            if elements_match:
                elements_text = elements_match.group(1).strip()
                for line in elements_text.split("\n"):
                    if line.strip() and line.strip().startswith("- "):
                        elements.append(line.strip()[2:])
            
            # Extrahiere technische Aspekte
            technical_aspects = []
            technical_match = re.search(r"Technische Aspekte und Details:(.*?)(?:Mögliche Probleme oder Fragen:|$)", model_response, re.DOTALL)
            if technical_match:
                technical_text = technical_match.group(1).strip()
                for line in technical_text.split("\n"):
                    if line.strip() and line.strip().startswith("- "):
                        technical_aspects.append(line.strip()[2:])
            
            # Extrahiere mögliche Probleme
            problems = []
            problems_match = re.search(r"Mögliche Probleme oder Fragen:(.*?)(?:Suchbegriffe für eine textbasierte Suche:|$)", model_response, re.DOTALL)
            if problems_match:
                problems_text = problems_match.group(1).strip()
                for line in problems_text.split("\n"):
                    if line.strip() and line.strip().startswith("- "):
                        problems.append(line.strip()[2:])
            
            # Extrahiere Suchbegriffe
            search_terms = []
            search_match = re.search(r"Suchbegriffe für eine textbasierte Suche:(.*?)$", model_response, re.DOTALL)
            if search_match:
                search_text = search_match.group(1).strip()
                for line in search_text.split("\n"):
                    if line.strip() and line.strip().startswith("- "):
                        search_terms.append(line.strip()[2:])
            
            # Erstelle Textabfrage aus dem Bild
            image_query = f"{main_content} {' '.join(elements)} {' '.join(technical_aspects)} {' '.join(search_terms)}"
            
            # Erstelle Analyseergebnis
            analysis = {
                "main_content": main_content,
                "disciplines": disciplines,
                "elements": elements,
                "technical_aspects": technical_aspects,
                "problems": problems,
                "search_terms": search_terms,
                "image_query": image_query
            }
            
            return analysis
        
        finally:
            # Lösche die temporäre Datei
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    def _combine_analyses(self, text_analysis: Dict[str, Any], image_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Kombiniert die Analysen von Text und Bildern.
        
        Args:
            text_analysis: Analyse des Abfragetexts
            image_analyses: Analysen der Abfragebilder
        
        Returns:
            Kombinierte Analyse
        """
        logger.info(f"Kombiniere Analysen von Text und Bildern")
        
        # Kombiniere die Fachbereiche
        combined_disciplines = text_analysis.get("disciplines", [])
        for image_analysis in image_analyses:
            for discipline in image_analysis.get("disciplines", []):
                if discipline not in combined_disciplines:
                    combined_disciplines.append(discipline)
        
        # Kombiniere die Suchbegriffe
        combined_search_terms = text_analysis.get("search_terms", [])
        for image_analysis in image_analyses:
            for term in image_analysis.get("search_terms", []):
                if term not in combined_search_terms:
                    combined_search_terms.append(term)
        
        # Erstelle kombinierte Abfrage
        combined_query = text_analysis.get("extended_query", "")
        for image_analysis in image_analyses:
            combined_query += f" {image_analysis.get('image_query', '')}"
        
        # Erstelle kombinierte Analyse
        combined_analysis = {
            "text_analysis": text_analysis,
            "image_analyses": image_analyses,
            "combined_disciplines": combined_disciplines,
            "combined_search_terms": combined_search_terms,
            "combined_query": combined_query
        }
        
        return combined_analysis
    
    def _generate_multimodal_response(self, combined_analysis: Dict[str, Any], query_results: Dict[str, Any]) -> str:
        """
        Generiert eine Antwort basierend auf der kombinierten Analyse und den Abfrageergebnissen.
        
        Args:
            combined_analysis: Kombinierte Analyse
            query_results: Abfrageergebnisse
        
        Returns:
            Generierte Antwort
        """
        logger.info(f"Generiere Antwort basierend auf multimodaler Analyse")
        
        # Erstelle Prompt für das KI-Modell
        prompt = f"""Generiere eine Antwort auf eine multimodale Abfrage im Kontext des Bauwesens basierend auf den folgenden Informationen:

KOMBINIERTE ANALYSE:
Hauptthema: {combined_analysis.get('text_analysis', {}).get('main_topic', 'Nicht verfügbar')}
Fachbereiche: {', '.join(combined_analysis.get('combined_disciplines', ['Nicht verfügbar']))}
Suchbegriffe: {', '.join(combined_analysis.get('combined_search_terms', ['Nicht verfügbar']))}

ABFRAGEERGEBNISSE:
{json.dumps(query_results.get('results', []), indent=2)}

Bitte generiere eine umfassende Antwort, die folgende Aspekte berücksichtigt:
1. Direkte Beantwortung der Abfrage basierend auf den gefundenen Informationen
2. Zusammenfassung der relevantesten Dokumente und deren Inhalte
3. Technische Erklärungen und Kontext für die gefundenen Informationen
4. Empfehlungen für weitere Schritte oder zusätzliche Informationen
5. Hinweise auf mögliche Inkonsistenzen oder fehlende Informationen

Formatiere deine Antwort als strukturierten Text, der direkt an den Benutzer gesendet werden kann.
"""
        
        # Rufe KI-Modell auf
        model = self.model_registry.get_model("text")
        model_response = model.generate(prompt, max_tokens=2000)
        
        return model_response

