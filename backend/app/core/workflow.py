"""
Kollaborative Workflow-Engine für das DOB-MVP.

Diese Engine ermöglicht die Definition, Ausführung und Überwachung von Workflows
für verschiedene Prozesse im Bauwesen, mit Unterstützung für Kollaboration
zwischen verschiedenen Stakeholdern.
"""
from typing import Dict, Any, List, Optional, Union, Callable, Set
from datetime import datetime
import logging
import uuid
import json
from enum import Enum

logger = logging.getLogger(__name__)

class WorkflowStatus(str, Enum):
    """
    Status eines Workflows.
    """
    CREATED = "created"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(str, Enum):
    """
    Status einer Task.
    """
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    WAITING_INPUT = "waiting_input"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"

class ApprovalStatus(str, Enum):
    """
    Status einer Genehmigung.
    """
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELEGATED = "delegated"

class WorkflowEngine:
    """
    Kollaborative Workflow-Engine für das DOB-MVP.
    
    Diese Engine ermöglicht die Definition, Ausführung und Überwachung von Workflows
    für verschiedene Prozesse im Bauwesen, mit Unterstützung für Kollaboration
    zwischen verschiedenen Stakeholdern.
    """
    
    def __init__(self):
        """
        Initialisiert die Workflow-Engine.
        """
        self.workflows = {}
        self.workflow_templates = {}
        self.task_handlers = {}
        self.approval_handlers = {}
        self.notification_handlers = {}
        self.event_listeners = {}
    
    def register_workflow_template(self, template_id: str, template: Dict[str, Any]) -> None:
        """
        Registriert eine Workflow-Vorlage.
        
        Args:
            template_id: ID der Vorlage
            template: Workflow-Vorlage
        """
        logger.info(f"Registriere Workflow-Vorlage: {template_id}")
        self.workflow_templates[template_id] = template
    
    def register_task_handler(self, task_type: str, handler: Callable) -> None:
        """
        Registriert einen Task-Handler.
        
        Args:
            task_type: Typ der Task
            handler: Handler-Funktion
        """
        logger.info(f"Registriere Task-Handler: {task_type}")
        self.task_handlers[task_type] = handler
    
    def register_approval_handler(self, approval_type: str, handler: Callable) -> None:
        """
        Registriert einen Genehmigungs-Handler.
        
        Args:
            approval_type: Typ der Genehmigung
            handler: Handler-Funktion
        """
        logger.info(f"Registriere Genehmigungs-Handler: {approval_type}")
        self.approval_handlers[approval_type] = handler
    
    def register_notification_handler(self, notification_type: str, handler: Callable) -> None:
        """
        Registriert einen Benachrichtigungs-Handler.
        
        Args:
            notification_type: Typ der Benachrichtigung
            handler: Handler-Funktion
        """
        logger.info(f"Registriere Benachrichtigungs-Handler: {notification_type}")
        self.notification_handlers[notification_type] = handler
    
    def register_event_listener(self, event_type: str, listener: Callable) -> None:
        """
        Registriert einen Event-Listener.
        
        Args:
            event_type: Typ des Events
            listener: Listener-Funktion
        """
        logger.info(f"Registriere Event-Listener: {event_type}")
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
        self.event_listeners[event_type].append(listener)
    
    def create_workflow(self, template_id: str, data: Dict[str, Any]) -> str:
        """
        Erstellt einen neuen Workflow basierend auf einer Vorlage.
        
        Args:
            template_id: ID der Vorlage
            data: Daten für den Workflow
        
        Returns:
            ID des erstellten Workflows
        """
        logger.info(f"Erstelle Workflow basierend auf Vorlage: {template_id}")
        
        if template_id not in self.workflow_templates:
            raise ValueError(f"Workflow-Vorlage nicht gefunden: {template_id}")
        
        template = self.workflow_templates[template_id]
        
        # Erstelle eine Kopie der Vorlage
        workflow = {
            "id": str(uuid.uuid4()),
            "template_id": template_id,
            "name": template.get("name", "Unbenannter Workflow"),
            "description": template.get("description", ""),
            "status": WorkflowStatus.CREATED,
            "tasks": [],
            "data": data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None,
            "current_task_index": 0,
            "participants": template.get("participants", []),
            "history": []
        }
        
        # Erstelle Tasks basierend auf der Vorlage
        for task_template in template.get("tasks", []):
            task = {
                "id": str(uuid.uuid4()),
                "name": task_template.get("name", "Unbenannte Task"),
                "description": task_template.get("description", ""),
                "type": task_template.get("type", "manual"),
                "status": TaskStatus.PENDING,
                "assignee": task_template.get("assignee", None),
                "approvers": task_template.get("approvers", []),
                "data": task_template.get("data", {}),
                "dependencies": task_template.get("dependencies", []),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "completed_at": None,
                "result": None,
                "approvals": []
            }
            
            # Erstelle Genehmigungen basierend auf der Vorlage
            for approver in task.get("approvers", []):
                approval = {
                    "id": str(uuid.uuid4()),
                    "approver": approver,
                    "status": ApprovalStatus.PENDING,
                    "comment": "",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "completed_at": None
                }
                task["approvals"].append(approval)
            
            workflow["tasks"].append(task)
        
        # Speichere den Workflow
        self.workflows[workflow["id"]] = workflow
        
        # Füge ein Ereignis zur Historie hinzu
        self._add_history_event(workflow["id"], "workflow_created", {
            "template_id": template_id,
            "workflow_id": workflow["id"],
            "workflow_name": workflow["name"]
        })
        
        # Löse ein Event aus
        self._trigger_event("workflow_created", {
            "workflow_id": workflow["id"],
            "template_id": template_id,
            "data": data
        })
        
        return workflow["id"]
    
    def start_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Startet einen Workflow.
        
        Args:
            workflow_id: ID des Workflows
        
        Returns:
            Aktualisierter Workflow
        """
        logger.info(f"Starte Workflow: {workflow_id}")
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow nicht gefunden: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        if workflow["status"] != WorkflowStatus.CREATED:
            raise ValueError(f"Workflow kann nicht gestartet werden, Status: {workflow['status']}")
        
        # Aktualisiere den Status des Workflows
        workflow["status"] = WorkflowStatus.RUNNING
        workflow["updated_at"] = datetime.now().isoformat()
        
        # Füge ein Ereignis zur Historie hinzu
        self._add_history_event(workflow_id, "workflow_started", {
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"]
        })
        
        # Löse ein Event aus
        self._trigger_event("workflow_started", {
            "workflow_id": workflow_id
        })
        
        # Starte die erste Task
        self._process_next_task(workflow_id)
        
        return workflow
    
    def complete_task(self, workflow_id: str, task_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Markiert eine Task als abgeschlossen.
        
        Args:
            workflow_id: ID des Workflows
            task_id: ID der Task
            result: Ergebnis der Task
        
        Returns:
            Aktualisierter Workflow
        """
        logger.info(f"Schließe Task ab: {task_id} in Workflow: {workflow_id}")
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow nicht gefunden: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Finde die Task
        task = None
        task_index = -1
        for i, t in enumerate(workflow["tasks"]):
            if t["id"] == task_id:
                task = t
                task_index = i
                break
        
        if task is None:
            raise ValueError(f"Task nicht gefunden: {task_id}")
        
        if task["status"] not in [TaskStatus.RUNNING, TaskStatus.WAITING_INPUT]:
            raise ValueError(f"Task kann nicht abgeschlossen werden, Status: {task['status']}")
        
        # Aktualisiere den Status der Task
        task["status"] = TaskStatus.COMPLETED
        task["result"] = result
        task["updated_at"] = datetime.now().isoformat()
        task["completed_at"] = datetime.now().isoformat()
        
        # Füge ein Ereignis zur Historie hinzu
        self._add_history_event(workflow_id, "task_completed", {
            "workflow_id": workflow_id,
            "task_id": task_id,
            "task_name": task["name"]
        })
        
        # Löse ein Event aus
        self._trigger_event("task_completed", {
            "workflow_id": workflow_id,
            "task_id": task_id,
            "result": result
        })
        
        # Prüfe, ob die Task Genehmigungen benötigt
        if task["approvers"]:
            task["status"] = TaskStatus.WAITING_APPROVAL
            
            # Benachrichtige die Genehmiger
            for approval in task["approvals"]:
                self._notify_approver(workflow_id, task_id, approval["id"])
            
            # Füge ein Ereignis zur Historie hinzu
            self._add_history_event(workflow_id, "task_waiting_approval", {
                "workflow_id": workflow_id,
                "task_id": task_id,
                "task_name": task["name"],
                "approvers": [a["approver"] for a in task["approvals"]]
            })
            
            # Löse ein Event aus
            self._trigger_event("task_waiting_approval", {
                "workflow_id": workflow_id,
                "task_id": task_id,
                "approvers": [a["approver"] for a in task["approvals"]]
            })
        else:
            # Wenn keine Genehmigungen erforderlich sind, fahre mit der nächsten Task fort
            workflow["current_task_index"] = task_index + 1
            self._process_next_task(workflow_id)
        
        return workflow
    
    def approve_task(self, workflow_id: str, task_id: str, approval_id: str, approved: bool, comment: str = "") -> Dict[str, Any]:
        """
        Genehmigt oder lehnt eine Task ab.
        
        Args:
            workflow_id: ID des Workflows
            task_id: ID der Task
            approval_id: ID der Genehmigung
            approved: True, wenn genehmigt, False, wenn abgelehnt
            comment: Kommentar zur Genehmigung oder Ablehnung
        
        Returns:
            Aktualisierter Workflow
        """
        logger.info(f"Genehmige Task: {task_id} in Workflow: {workflow_id}, Genehmigung: {approval_id}, Genehmigt: {approved}")
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow nicht gefunden: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Finde die Task
        task = None
        task_index = -1
        for i, t in enumerate(workflow["tasks"]):
            if t["id"] == task_id:
                task = t
                task_index = i
                break
        
        if task is None:
            raise ValueError(f"Task nicht gefunden: {task_id}")
        
        if task["status"] != TaskStatus.WAITING_APPROVAL:
            raise ValueError(f"Task benötigt keine Genehmigung, Status: {task['status']}")
        
        # Finde die Genehmigung
        approval = None
        for a in task["approvals"]:
            if a["id"] == approval_id:
                approval = a
                break
        
        if approval is None:
            raise ValueError(f"Genehmigung nicht gefunden: {approval_id}")
        
        if approval["status"] != ApprovalStatus.PENDING:
            raise ValueError(f"Genehmigung kann nicht aktualisiert werden, Status: {approval['status']}")
        
        # Aktualisiere den Status der Genehmigung
        approval["status"] = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        approval["comment"] = comment
        approval["updated_at"] = datetime.now().isoformat()
        approval["completed_at"] = datetime.now().isoformat()
        
        # Füge ein Ereignis zur Historie hinzu
        event_type = "task_approved" if approved else "task_rejected"
        self._add_history_event(workflow_id, event_type, {
            "workflow_id": workflow_id,
            "task_id": task_id,
            "task_name": task["name"],
            "approver": approval["approver"],
            "comment": comment
        })
        
        # Löse ein Event aus
        self._trigger_event(event_type, {
            "workflow_id": workflow_id,
            "task_id": task_id,
            "approver": approval["approver"],
            "comment": comment
        })
        
        # Prüfe, ob alle Genehmigungen abgeschlossen sind
        all_approved = True
        any_rejected = False
        all_completed = True
        
        for a in task["approvals"]:
            if a["status"] == ApprovalStatus.PENDING:
                all_completed = False
                break
            elif a["status"] == ApprovalStatus.REJECTED:
                any_rejected = True
        
        if all_completed:
            if any_rejected:
                # Wenn mindestens eine Genehmigung abgelehnt wurde, markiere die Task als fehlgeschlagen
                task["status"] = TaskStatus.FAILED
                
                # Füge ein Ereignis zur Historie hinzu
                self._add_history_event(workflow_id, "task_failed", {
                    "workflow_id": workflow_id,
                    "task_id": task_id,
                    "task_name": task["name"],
                    "reason": "Genehmigung abgelehnt"
                })
                
                # Löse ein Event aus
                self._trigger_event("task_failed", {
                    "workflow_id": workflow_id,
                    "task_id": task_id,
                    "reason": "Genehmigung abgelehnt"
                })
                
                # Markiere den Workflow als fehlgeschlagen
                workflow["status"] = WorkflowStatus.FAILED
                workflow["updated_at"] = datetime.now().isoformat()
                
                # Füge ein Ereignis zur Historie hinzu
                self._add_history_event(workflow_id, "workflow_failed", {
                    "workflow_id": workflow_id,
                    "workflow_name": workflow["name"],
                    "reason": "Task fehlgeschlagen: " + task["name"]
                })
                
                # Löse ein Event aus
                self._trigger_event("workflow_failed", {
                    "workflow_id": workflow_id,
                    "reason": "Task fehlgeschlagen: " + task["name"]
                })
            else:
                # Wenn alle Genehmigungen erteilt wurden, fahre mit der nächsten Task fort
                workflow["current_task_index"] = task_index + 1
                self._process_next_task(workflow_id)
        
        return workflow
    
    def delegate_approval(self, workflow_id: str, task_id: str, approval_id: str, new_approver: str, comment: str = "") -> Dict[str, Any]:
        """
        Delegiert eine Genehmigung an einen anderen Benutzer.
        
        Args:
            workflow_id: ID des Workflows
            task_id: ID der Task
            approval_id: ID der Genehmigung
            new_approver: Neuer Genehmiger
            comment: Kommentar zur Delegation
        
        Returns:
            Aktualisierter Workflow
        """
        logger.info(f"Delegiere Genehmigung: {approval_id} in Task: {task_id} in Workflow: {workflow_id} an: {new_approver}")
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow nicht gefunden: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Finde die Task
        task = None
        for t in workflow["tasks"]:
            if t["id"] == task_id:
                task = t
                break
        
        if task is None:
            raise ValueError(f"Task nicht gefunden: {task_id}")
        
        if task["status"] != TaskStatus.WAITING_APPROVAL:
            raise ValueError(f"Task benötigt keine Genehmigung, Status: {task['status']}")
        
        # Finde die Genehmigung
        approval = None
        for a in task["approvals"]:
            if a["id"] == approval_id:
                approval = a
                break
        
        if approval is None:
            raise ValueError(f"Genehmigung nicht gefunden: {approval_id}")
        
        if approval["status"] != ApprovalStatus.PENDING:
            raise ValueError(f"Genehmigung kann nicht delegiert werden, Status: {approval['status']}")
        
        # Erstelle eine neue Genehmigung für den neuen Genehmiger
        new_approval = {
            "id": str(uuid.uuid4()),
            "approver": new_approver,
            "status": ApprovalStatus.PENDING,
            "comment": "",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None
        }
        
        # Aktualisiere den Status der alten Genehmigung
        approval["status"] = ApprovalStatus.DELEGATED
        approval["comment"] = comment
        approval["updated_at"] = datetime.now().isoformat()
        approval["completed_at"] = datetime.now().isoformat()
        
        # Füge die neue Genehmigung hinzu
        task["approvals"].append(new_approval)
        
        # Füge ein Ereignis zur Historie hinzu
        self._add_history_event(workflow_id, "approval_delegated", {
            "workflow_id": workflow_id,
            "task_id": task_id,
            "task_name": task["name"],
            "old_approver": approval["approver"],
            "new_approver": new_approver,
            "comment": comment
        })
        
        # Löse ein Event aus
        self._trigger_event("approval_delegated", {
            "workflow_id": workflow_id,
            "task_id": task_id,
            "old_approver": approval["approver"],
            "new_approver": new_approver,
            "comment": comment
        })
        
        # Benachrichtige den neuen Genehmiger
        self._notify_approver(workflow_id, task_id, new_approval["id"])
        
        return workflow
    
    def provide_input(self, workflow_id: str, task_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stellt Eingabedaten für eine Task bereit.
        
        Args:
            workflow_id: ID des Workflows
            task_id: ID der Task
            input_data: Eingabedaten
        
        Returns:
            Aktualisierter Workflow
        """
        logger.info(f"Stelle Eingabedaten bereit für Task: {task_id} in Workflow: {workflow_id}")
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow nicht gefunden: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Finde die Task
        task = None
        for t in workflow["tasks"]:
            if t["id"] == task_id:
                task = t
                break
        
        if task is None:
            raise ValueError(f"Task nicht gefunden: {task_id}")
        
        if task["status"] != TaskStatus.WAITING_INPUT:
            raise ValueError(f"Task benötigt keine Eingabe, Status: {task['status']}")
        
        # Aktualisiere den Status der Task
        task["status"] = TaskStatus.RUNNING
        task["data"]["input"] = input_data
        task["updated_at"] = datetime.now().isoformat()
        
        # Füge ein Ereignis zur Historie hinzu
        self._add_history_event(workflow_id, "input_provided", {
            "workflow_id": workflow_id,
            "task_id": task_id,
            "task_name": task["name"]
        })
        
        # Löse ein Event aus
        self._trigger_event("input_provided", {
            "workflow_id": workflow_id,
            "task_id": task_id,
            "input_data": input_data
        })
        
        # Führe die Task aus
        self._execute_task(workflow_id, task_id)
        
        return workflow
    
    def cancel_workflow(self, workflow_id: str, reason: str = "") -> Dict[str, Any]:
        """
        Bricht einen Workflow ab.
        
        Args:
            workflow_id: ID des Workflows
            reason: Grund für den Abbruch
        
        Returns:
            Aktualisierter Workflow
        """
        logger.info(f"Breche Workflow ab: {workflow_id}, Grund: {reason}")
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow nicht gefunden: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        if workflow["status"] in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            raise ValueError(f"Workflow kann nicht abgebrochen werden, Status: {workflow['status']}")
        
        # Aktualisiere den Status des Workflows
        workflow["status"] = WorkflowStatus.CANCELLED
        workflow["updated_at"] = datetime.now().isoformat()
        
        # Aktualisiere den Status aller laufenden Tasks
        for task in workflow["tasks"]:
            if task["status"] in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.WAITING_APPROVAL, TaskStatus.WAITING_INPUT]:
                task["status"] = TaskStatus.CANCELLED
                task["updated_at"] = datetime.now().isoformat()
        
        # Füge ein Ereignis zur Historie hinzu
        self._add_history_event(workflow_id, "workflow_cancelled", {
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "reason": reason
        })
        
        # Löse ein Event aus
        self._trigger_event("workflow_cancelled", {
            "workflow_id": workflow_id,
            "reason": reason
        })
        
        return workflow
    
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Gibt einen Workflow zurück.
        
        Args:
            workflow_id: ID des Workflows
        
        Returns:
            Workflow
        """
        logger.info(f"Hole Workflow: {workflow_id}")
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow nicht gefunden: {workflow_id}")
        
        return self.workflows[workflow_id]
    
    def get_workflows(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Gibt alle Workflows zurück, die den Filtern entsprechen.
        
        Args:
            filters: Filter für die Workflows
        
        Returns:
            Liste von Workflows
        """
        logger.info(f"Hole Workflows mit Filtern: {filters}")
        
        if filters is None:
            filters = {}
        
        result = []
        
        for workflow in self.workflows.values():
            match = True
            
            for key, value in filters.items():
                if key not in workflow or workflow[key] != value:
                    match = False
                    break
            
            if match:
                result.append(workflow)
        
        return result
    
    def get_task(self, workflow_id: str, task_id: str) -> Dict[str, Any]:
        """
        Gibt eine Task zurück.
        
        Args:
            workflow_id: ID des Workflows
            task_id: ID der Task
        
        Returns:
            Task
        """
        logger.info(f"Hole Task: {task_id} in Workflow: {workflow_id}")
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow nicht gefunden: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Finde die Task
        task = None
        for t in workflow["tasks"]:
            if t["id"] == task_id:
                task = t
                break
        
        if task is None:
            raise ValueError(f"Task nicht gefunden: {task_id}")
        
        return task
    
    def get_workflow_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Gibt die Historie eines Workflows zurück.
        
        Args:
            workflow_id: ID des Workflows
        
        Returns:
            Historie des Workflows
        """
        logger.info(f"Hole Historie für Workflow: {workflow_id}")
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow nicht gefunden: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        return workflow["history"]
    
    def get_workflow_participants(self, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Gibt die Teilnehmer eines Workflows zurück.
        
        Args:
            workflow_id: ID des Workflows
        
        Returns:
            Teilnehmer des Workflows
        """
        logger.info(f"Hole Teilnehmer für Workflow: {workflow_id}")
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow nicht gefunden: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        return workflow["participants"]
    
    def add_workflow_participant(self, workflow_id: str, participant: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fügt einen Teilnehmer zu einem Workflow hinzu.
        
        Args:
            workflow_id: ID des Workflows
            participant: Teilnehmer
        
        Returns:
            Aktualisierter Workflow
        """
        logger.info(f"Füge Teilnehmer hinzu zu Workflow: {workflow_id}")
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow nicht gefunden: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Prüfe, ob der Teilnehmer bereits existiert
        for p in workflow["participants"]:
            if p["id"] == participant["id"]:
                # Aktualisiere den Teilnehmer
                p.update(participant)
                workflow["updated_at"] = datetime.now().isoformat()
                
                # Füge ein Ereignis zur Historie hinzu
                self._add_history_event(workflow_id, "participant_updated", {
                    "workflow_id": workflow_id,
                    "workflow_name": workflow["name"],
                    "participant_id": participant["id"],
                    "participant_name": participant.get("name", "")
                })
                
                # Löse ein Event aus
                self._trigger_event("participant_updated", {
                    "workflow_id": workflow_id,
                    "participant": participant
                })
                
                return workflow
        
        # Füge den Teilnehmer hinzu
        workflow["participants"].append(participant)
        workflow["updated_at"] = datetime.now().isoformat()
        
        # Füge ein Ereignis zur Historie hinzu
        self._add_history_event(workflow_id, "participant_added", {
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "participant_id": participant["id"],
            "participant_name": participant.get("name", "")
        })
        
        # Löse ein Event aus
        self._trigger_event("participant_added", {
            "workflow_id": workflow_id,
            "participant": participant
        })
        
        return workflow
    
    def remove_workflow_participant(self, workflow_id: str, participant_id: str) -> Dict[str, Any]:
        """
        Entfernt einen Teilnehmer aus einem Workflow.
        
        Args:
            workflow_id: ID des Workflows
            participant_id: ID des Teilnehmers
        
        Returns:
            Aktualisierter Workflow
        """
        logger.info(f"Entferne Teilnehmer aus Workflow: {workflow_id}, Teilnehmer: {participant_id}")
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow nicht gefunden: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Finde den Teilnehmer
        participant = None
        participant_index = -1
        for i, p in enumerate(workflow["participants"]):
            if p["id"] == participant_id:
                participant = p
                participant_index = i
                break
        
        if participant is None:
            raise ValueError(f"Teilnehmer nicht gefunden: {participant_id}")
        
        # Entferne den Teilnehmer
        workflow["participants"].pop(participant_index)
        workflow["updated_at"] = datetime.now().isoformat()
        
        # Füge ein Ereignis zur Historie hinzu
        self._add_history_event(workflow_id, "participant_removed", {
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "participant_id": participant_id,
            "participant_name": participant.get("name", "")
        })
        
        # Löse ein Event aus
        self._trigger_event("participant_removed", {
            "workflow_id": workflow_id,
            "participant_id": participant_id
        })
        
        return workflow
    
    def _process_next_task(self, workflow_id: str) -> None:
        """
        Verarbeitet die nächste Task in einem Workflow.
        
        Args:
            workflow_id: ID des Workflows
        """
        logger.info(f"Verarbeite nächste Task in Workflow: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Prüfe, ob der Workflow abgeschlossen ist
        if workflow["current_task_index"] >= len(workflow["tasks"]):
            # Markiere den Workflow als abgeschlossen
            workflow["status"] = WorkflowStatus.COMPLETED
            workflow["updated_at"] = datetime.now().isoformat()
            workflow["completed_at"] = datetime.now().isoformat()
            
            # Füge ein Ereignis zur Historie hinzu
            self._add_history_event(workflow_id, "workflow_completed", {
                "workflow_id": workflow_id,
                "workflow_name": workflow["name"]
            })
            
            # Löse ein Event aus
            self._trigger_event("workflow_completed", {
                "workflow_id": workflow_id
            })
            
            return
        
        # Hole die nächste Task
        task = workflow["tasks"][workflow["current_task_index"]]
        
        # Prüfe, ob die Task Abhängigkeiten hat
        dependencies_met = True
        for dep_id in task.get("dependencies", []):
            # Finde die abhängige Task
            dep_task = None
            for t in workflow["tasks"]:
                if t["id"] == dep_id:
                    dep_task = t
                    break
            
            if dep_task is None:
                logger.warning(f"Abhängige Task nicht gefunden: {dep_id}")
                dependencies_met = False
                break
            
            if dep_task["status"] != TaskStatus.COMPLETED:
                dependencies_met = False
                break
        
        if not dependencies_met:
            # Markiere den Workflow als wartend
            workflow["status"] = WorkflowStatus.WAITING
            workflow["updated_at"] = datetime.now().isoformat()
            
            # Füge ein Ereignis zur Historie hinzu
            self._add_history_event(workflow_id, "workflow_waiting", {
                "workflow_id": workflow_id,
                "workflow_name": workflow["name"],
                "reason": "Abhängigkeiten nicht erfüllt"
            })
            
            # Löse ein Event aus
            self._trigger_event("workflow_waiting", {
                "workflow_id": workflow_id,
                "reason": "Abhängigkeiten nicht erfüllt"
            })
            
            return
        
        # Aktualisiere den Status der Task
        task["status"] = TaskStatus.RUNNING
        task["updated_at"] = datetime.now().isoformat()
        
        # Füge ein Ereignis zur Historie hinzu
        self._add_history_event(workflow_id, "task_started", {
            "workflow_id": workflow_id,
            "task_id": task["id"],
            "task_name": task["name"]
        })
        
        # Löse ein Event aus
        self._trigger_event("task_started", {
            "workflow_id": workflow_id,
            "task_id": task["id"]
        })
        
        # Führe die Task aus
        self._execute_task(workflow_id, task["id"])
    
    def _execute_task(self, workflow_id: str, task_id: str) -> None:
        """
        Führt eine Task aus.
        
        Args:
            workflow_id: ID des Workflows
            task_id: ID der Task
        """
        logger.info(f"Führe Task aus: {task_id} in Workflow: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Finde die Task
        task = None
        for t in workflow["tasks"]:
            if t["id"] == task_id:
                task = t
                break
        
        if task is None:
            logger.error(f"Task nicht gefunden: {task_id}")
            return
        
        # Prüfe, ob die Task automatisch ausgeführt werden kann
        if task["type"] in self.task_handlers:
            # Hole den Handler für den Task-Typ
            handler = self.task_handlers[task["type"]]
            
            try:
                # Führe den Handler aus
                result = handler(workflow_id, task_id, task["data"])
                
                # Markiere die Task als abgeschlossen
                self.complete_task(workflow_id, task_id, result)
            except Exception as e:
                logger.error(f"Fehler bei der Ausführung der Task: {str(e)}")
                
                # Markiere die Task als fehlgeschlagen
                task["status"] = TaskStatus.FAILED
                task["updated_at"] = datetime.now().isoformat()
                
                # Füge ein Ereignis zur Historie hinzu
                self._add_history_event(workflow_id, "task_failed", {
                    "workflow_id": workflow_id,
                    "task_id": task_id,
                    "task_name": task["name"],
                    "reason": str(e)
                })
                
                # Löse ein Event aus
                self._trigger_event("task_failed", {
                    "workflow_id": workflow_id,
                    "task_id": task_id,
                    "reason": str(e)
                })
                
                # Markiere den Workflow als fehlgeschlagen
                workflow["status"] = WorkflowStatus.FAILED
                workflow["updated_at"] = datetime.now().isoformat()
                
                # Füge ein Ereignis zur Historie hinzu
                self._add_history_event(workflow_id, "workflow_failed", {
                    "workflow_id": workflow_id,
                    "workflow_name": workflow["name"],
                    "reason": "Task fehlgeschlagen: " + task["name"]
                })
                
                # Löse ein Event aus
                self._trigger_event("workflow_failed", {
                    "workflow_id": workflow_id,
                    "reason": "Task fehlgeschlagen: " + task["name"]
                })
        elif task["type"] == "manual":
            # Benachrichtige den Bearbeiter
            if task["assignee"]:
                self._notify_assignee(workflow_id, task_id)
        elif task["type"] == "input":
            # Markiere die Task als wartend auf Eingabe
            task["status"] = TaskStatus.WAITING_INPUT
            task["updated_at"] = datetime.now().isoformat()
            
            # Füge ein Ereignis zur Historie hinzu
            self._add_history_event(workflow_id, "task_waiting_input", {
                "workflow_id": workflow_id,
                "task_id": task_id,
                "task_name": task["name"]
            })
            
            # Löse ein Event aus
            self._trigger_event("task_waiting_input", {
                "workflow_id": workflow_id,
                "task_id": task_id
            })
            
            # Benachrichtige den Bearbeiter
            if task["assignee"]:
                self._notify_assignee(workflow_id, task_id)
        else:
            logger.warning(f"Unbekannter Task-Typ: {task['type']}")
            
            # Markiere die Task als fehlgeschlagen
            task["status"] = TaskStatus.FAILED
            task["updated_at"] = datetime.now().isoformat()
            
            # Füge ein Ereignis zur Historie hinzu
            self._add_history_event(workflow_id, "task_failed", {
                "workflow_id": workflow_id,
                "task_id": task_id,
                "task_name": task["name"],
                "reason": f"Unbekannter Task-Typ: {task['type']}"
            })
            
            # Löse ein Event aus
            self._trigger_event("task_failed", {
                "workflow_id": workflow_id,
                "task_id": task_id,
                "reason": f"Unbekannter Task-Typ: {task['type']}"
            })
            
            # Markiere den Workflow als fehlgeschlagen
            workflow["status"] = WorkflowStatus.FAILED
            workflow["updated_at"] = datetime.now().isoformat()
            
            # Füge ein Ereignis zur Historie hinzu
            self._add_history_event(workflow_id, "workflow_failed", {
                "workflow_id": workflow_id,
                "workflow_name": workflow["name"],
                "reason": "Task fehlgeschlagen: " + task["name"]
            })
            
            # Löse ein Event aus
            self._trigger_event("workflow_failed", {
                "workflow_id": workflow_id,
                "reason": "Task fehlgeschlagen: " + task["name"]
            })
    
    def _notify_assignee(self, workflow_id: str, task_id: str) -> None:
        """
        Benachrichtigt den Bearbeiter einer Task.
        
        Args:
            workflow_id: ID des Workflows
            task_id: ID der Task
        """
        logger.info(f"Benachrichtige Bearbeiter für Task: {task_id} in Workflow: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Finde die Task
        task = None
        for t in workflow["tasks"]:
            if t["id"] == task_id:
                task = t
                break
        
        if task is None:
            logger.error(f"Task nicht gefunden: {task_id}")
            return
        
        # Prüfe, ob die Task einen Bearbeiter hat
        if not task["assignee"]:
            logger.warning(f"Task hat keinen Bearbeiter: {task_id}")
            return
        
        # Prüfe, ob ein Benachrichtigungs-Handler registriert ist
        if "assignee" in self.notification_handlers:
            # Hole den Handler
            handler = self.notification_handlers["assignee"]
            
            try:
                # Führe den Handler aus
                handler(workflow_id, task_id, task["assignee"])
            except Exception as e:
                logger.error(f"Fehler bei der Benachrichtigung des Bearbeiters: {str(e)}")
    
    def _notify_approver(self, workflow_id: str, task_id: str, approval_id: str) -> None:
        """
        Benachrichtigt einen Genehmiger.
        
        Args:
            workflow_id: ID des Workflows
            task_id: ID der Task
            approval_id: ID der Genehmigung
        """
        logger.info(f"Benachrichtige Genehmiger für Genehmigung: {approval_id} in Task: {task_id} in Workflow: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Finde die Task
        task = None
        for t in workflow["tasks"]:
            if t["id"] == task_id:
                task = t
                break
        
        if task is None:
            logger.error(f"Task nicht gefunden: {task_id}")
            return
        
        # Finde die Genehmigung
        approval = None
        for a in task["approvals"]:
            if a["id"] == approval_id:
                approval = a
                break
        
        if approval is None:
            logger.error(f"Genehmigung nicht gefunden: {approval_id}")
            return
        
        # Prüfe, ob ein Benachrichtigungs-Handler registriert ist
        if "approver" in self.notification_handlers:
            # Hole den Handler
            handler = self.notification_handlers["approver"]
            
            try:
                # Führe den Handler aus
                handler(workflow_id, task_id, approval_id, approval["approver"])
            except Exception as e:
                logger.error(f"Fehler bei der Benachrichtigung des Genehmigers: {str(e)}")
    
    def _add_history_event(self, workflow_id: str, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Fügt ein Ereignis zur Historie eines Workflows hinzu.
        
        Args:
            workflow_id: ID des Workflows
            event_type: Typ des Ereignisses
            event_data: Daten des Ereignisses
        """
        logger.info(f"Füge Ereignis zur Historie hinzu: {event_type} für Workflow: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Erstelle das Ereignis
        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "data": event_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Füge das Ereignis zur Historie hinzu
        workflow["history"].append(event)
    
    def _trigger_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Löst ein Event aus.
        
        Args:
            event_type: Typ des Events
            event_data: Daten des Events
        """
        logger.info(f"Löse Event aus: {event_type}")
        
        if event_type not in self.event_listeners:
            return
        
        # Rufe alle Listener für diesen Event-Typ auf
        for listener in self.event_listeners[event_type]:
            try:
                listener(event_type, event_data)
            except Exception as e:
                logger.error(f"Fehler bei der Ausführung des Event-Listeners: {str(e)}")
    
    def export_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Exportiert einen Workflow.
        
        Args:
            workflow_id: ID des Workflows
        
        Returns:
            Exportierter Workflow
        """
        logger.info(f"Exportiere Workflow: {workflow_id}")
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow nicht gefunden: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Erstelle eine Kopie des Workflows
        export = json.loads(json.dumps(workflow))
        
        return export
    
    def import_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """
        Importiert einen Workflow.
        
        Args:
            workflow_data: Daten des Workflows
        
        Returns:
            ID des importierten Workflows
        """
        logger.info(f"Importiere Workflow: {workflow_data.get('id', 'Unbekannt')}")
        
        # Erstelle eine Kopie der Workflow-Daten
        workflow = json.loads(json.dumps(workflow_data))
        
        # Generiere eine neue ID für den Workflow
        old_id = workflow.get("id", "")
        workflow["id"] = str(uuid.uuid4())
        
        # Aktualisiere die Zeitstempel
        workflow["created_at"] = datetime.now().isoformat()
        workflow["updated_at"] = datetime.now().isoformat()
        
        # Generiere neue IDs für alle Tasks
        id_mapping = {old_id: workflow["id"]}
        
        for task in workflow.get("tasks", []):
            old_task_id = task.get("id", "")
            task["id"] = str(uuid.uuid4())
            id_mapping[old_task_id] = task["id"]
            
            # Aktualisiere die Zeitstempel
            task["created_at"] = datetime.now().isoformat()
            task["updated_at"] = datetime.now().isoformat()
            
            # Generiere neue IDs für alle Genehmigungen
            for approval in task.get("approvals", []):
                old_approval_id = approval.get("id", "")
                approval["id"] = str(uuid.uuid4())
                id_mapping[old_approval_id] = approval["id"]
                
                # Aktualisiere die Zeitstempel
                approval["created_at"] = datetime.now().isoformat()
                approval["updated_at"] = datetime.now().isoformat()
        
        # Aktualisiere die Abhängigkeiten
        for task in workflow.get("tasks", []):
            new_dependencies = []
            for dep_id in task.get("dependencies", []):
                if dep_id in id_mapping:
                    new_dependencies.append(id_mapping[dep_id])
            task["dependencies"] = new_dependencies
        
        # Speichere den Workflow
        self.workflows[workflow["id"]] = workflow
        
        # Füge ein Ereignis zur Historie hinzu
        self._add_history_event(workflow["id"], "workflow_imported", {
            "workflow_id": workflow["id"],
            "workflow_name": workflow["name"],
            "original_id": old_id
        })
        
        # Löse ein Event aus
        self._trigger_event("workflow_imported", {
            "workflow_id": workflow["id"],
            "original_id": old_id
        })
        
        return workflow["id"]

