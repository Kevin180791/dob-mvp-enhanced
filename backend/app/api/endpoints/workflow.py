"""
API-Endpunkte für die kollaborative Workflow-Engine.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Query, Path
from pydantic import BaseModel, Field

from app.api.deps import get_workflow_engine
from app.core.workflow import WorkflowEngine, WorkflowStatus, TaskStatus, ApprovalStatus

router = APIRouter()

class WorkflowTemplateCreate(BaseModel):
    """
    Schema für die Erstellung einer Workflow-Vorlage.
    """
    template_id: str = Field(..., description="ID der Vorlage")
    name: str = Field(..., description="Name der Vorlage")
    description: str = Field("", description="Beschreibung der Vorlage")
    tasks: List[Dict[str, Any]] = Field([], description="Tasks der Vorlage")
    participants: List[Dict[str, Any]] = Field([], description="Teilnehmer der Vorlage")

class WorkflowCreate(BaseModel):
    """
    Schema für die Erstellung eines Workflows.
    """
    template_id: str = Field(..., description="ID der Vorlage")
    data: Dict[str, Any] = Field({}, description="Daten für den Workflow")

class TaskComplete(BaseModel):
    """
    Schema für den Abschluss einer Task.
    """
    result: Dict[str, Any] = Field({}, description="Ergebnis der Task")

class TaskApprove(BaseModel):
    """
    Schema für die Genehmigung einer Task.
    """
    approved: bool = Field(..., description="True, wenn genehmigt, False, wenn abgelehnt")
    comment: str = Field("", description="Kommentar zur Genehmigung oder Ablehnung")

class TaskDelegate(BaseModel):
    """
    Schema für die Delegation einer Genehmigung.
    """
    new_approver: str = Field(..., description="Neuer Genehmiger")
    comment: str = Field("", description="Kommentar zur Delegation")

class TaskInput(BaseModel):
    """
    Schema für die Bereitstellung von Eingabedaten für eine Task.
    """
    input_data: Dict[str, Any] = Field({}, description="Eingabedaten")

class WorkflowCancel(BaseModel):
    """
    Schema für den Abbruch eines Workflows.
    """
    reason: str = Field("", description="Grund für den Abbruch")

class ParticipantCreate(BaseModel):
    """
    Schema für die Erstellung eines Teilnehmers.
    """
    id: str = Field(..., description="ID des Teilnehmers")
    name: str = Field(..., description="Name des Teilnehmers")
    role: str = Field(..., description="Rolle des Teilnehmers")
    email: Optional[str] = Field(None, description="E-Mail-Adresse des Teilnehmers")
    data: Dict[str, Any] = Field({}, description="Zusätzliche Daten des Teilnehmers")

@router.post("/templates", response_model=Dict[str, Any])
async def create_workflow_template(
    template: WorkflowTemplateCreate = Body(...),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Erstellt eine neue Workflow-Vorlage.
    """
    try:
        workflow_engine.register_workflow_template(template.template_id, template.dict())
        return {"status": "success", "message": "Workflow-Vorlage erfolgreich erstellt", "template_id": template.template_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/templates", response_model=List[Dict[str, Any]])
async def get_workflow_templates(
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Gibt alle Workflow-Vorlagen zurück.
    """
    return list(workflow_engine.workflow_templates.values())

@router.get("/templates/{template_id}", response_model=Dict[str, Any])
async def get_workflow_template(
    template_id: str = Path(..., description="ID der Vorlage"),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Gibt eine Workflow-Vorlage zurück.
    """
    if template_id not in workflow_engine.workflow_templates:
        raise HTTPException(status_code=404, detail=f"Workflow-Vorlage nicht gefunden: {template_id}")
    
    return workflow_engine.workflow_templates[template_id]

@router.post("/workflows", response_model=Dict[str, Any])
async def create_workflow(
    workflow: WorkflowCreate = Body(...),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Erstellt einen neuen Workflow basierend auf einer Vorlage.
    """
    try:
        workflow_id = workflow_engine.create_workflow(workflow.template_id, workflow.data)
        return {"status": "success", "message": "Workflow erfolgreich erstellt", "workflow_id": workflow_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/workflows/{workflow_id}/start", response_model=Dict[str, Any])
async def start_workflow(
    workflow_id: str = Path(..., description="ID des Workflows"),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Startet einen Workflow.
    """
    try:
        workflow = workflow_engine.start_workflow(workflow_id)
        return {"status": "success", "message": "Workflow erfolgreich gestartet", "workflow": workflow}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/workflows/{workflow_id}/tasks/{task_id}/complete", response_model=Dict[str, Any])
async def complete_task(
    workflow_id: str = Path(..., description="ID des Workflows"),
    task_id: str = Path(..., description="ID der Task"),
    task_complete: TaskComplete = Body(...),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Markiert eine Task als abgeschlossen.
    """
    try:
        workflow = workflow_engine.complete_task(workflow_id, task_id, task_complete.result)
        return {"status": "success", "message": "Task erfolgreich abgeschlossen", "workflow": workflow}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/workflows/{workflow_id}/tasks/{task_id}/approvals/{approval_id}/approve", response_model=Dict[str, Any])
async def approve_task(
    workflow_id: str = Path(..., description="ID des Workflows"),
    task_id: str = Path(..., description="ID der Task"),
    approval_id: str = Path(..., description="ID der Genehmigung"),
    task_approve: TaskApprove = Body(...),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Genehmigt oder lehnt eine Task ab.
    """
    try:
        workflow = workflow_engine.approve_task(workflow_id, task_id, approval_id, task_approve.approved, task_approve.comment)
        return {"status": "success", "message": "Task erfolgreich genehmigt oder abgelehnt", "workflow": workflow}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/workflows/{workflow_id}/tasks/{task_id}/approvals/{approval_id}/delegate", response_model=Dict[str, Any])
async def delegate_approval(
    workflow_id: str = Path(..., description="ID des Workflows"),
    task_id: str = Path(..., description="ID der Task"),
    approval_id: str = Path(..., description="ID der Genehmigung"),
    task_delegate: TaskDelegate = Body(...),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Delegiert eine Genehmigung an einen anderen Benutzer.
    """
    try:
        workflow = workflow_engine.delegate_approval(workflow_id, task_id, approval_id, task_delegate.new_approver, task_delegate.comment)
        return {"status": "success", "message": "Genehmigung erfolgreich delegiert", "workflow": workflow}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/workflows/{workflow_id}/tasks/{task_id}/input", response_model=Dict[str, Any])
async def provide_input(
    workflow_id: str = Path(..., description="ID des Workflows"),
    task_id: str = Path(..., description="ID der Task"),
    task_input: TaskInput = Body(...),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Stellt Eingabedaten für eine Task bereit.
    """
    try:
        workflow = workflow_engine.provide_input(workflow_id, task_id, task_input.input_data)
        return {"status": "success", "message": "Eingabedaten erfolgreich bereitgestellt", "workflow": workflow}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/workflows/{workflow_id}/cancel", response_model=Dict[str, Any])
async def cancel_workflow(
    workflow_id: str = Path(..., description="ID des Workflows"),
    workflow_cancel: WorkflowCancel = Body(...),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Bricht einen Workflow ab.
    """
    try:
        workflow = workflow_engine.cancel_workflow(workflow_id, workflow_cancel.reason)
        return {"status": "success", "message": "Workflow erfolgreich abgebrochen", "workflow": workflow}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/workflows", response_model=List[Dict[str, Any]])
async def get_workflows(
    status: Optional[str] = Query(None, description="Filter nach Status"),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Gibt alle Workflows zurück, die den Filtern entsprechen.
    """
    filters = {}
    if status:
        filters["status"] = status
    
    return workflow_engine.get_workflows(filters)

@router.get("/workflows/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow(
    workflow_id: str = Path(..., description="ID des Workflows"),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Gibt einen Workflow zurück.
    """
    try:
        return workflow_engine.get_workflow(workflow_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/workflows/{workflow_id}/tasks/{task_id}", response_model=Dict[str, Any])
async def get_task(
    workflow_id: str = Path(..., description="ID des Workflows"),
    task_id: str = Path(..., description="ID der Task"),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Gibt eine Task zurück.
    """
    try:
        return workflow_engine.get_task(workflow_id, task_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/workflows/{workflow_id}/history", response_model=List[Dict[str, Any]])
async def get_workflow_history(
    workflow_id: str = Path(..., description="ID des Workflows"),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Gibt die Historie eines Workflows zurück.
    """
    try:
        return workflow_engine.get_workflow_history(workflow_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/workflows/{workflow_id}/participants", response_model=List[Dict[str, Any]])
async def get_workflow_participants(
    workflow_id: str = Path(..., description="ID des Workflows"),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Gibt die Teilnehmer eines Workflows zurück.
    """
    try:
        return workflow_engine.get_workflow_participants(workflow_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/workflows/{workflow_id}/participants", response_model=Dict[str, Any])
async def add_workflow_participant(
    workflow_id: str = Path(..., description="ID des Workflows"),
    participant: ParticipantCreate = Body(...),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Fügt einen Teilnehmer zu einem Workflow hinzu.
    """
    try:
        workflow = workflow_engine.add_workflow_participant(workflow_id, participant.dict())
        return {"status": "success", "message": "Teilnehmer erfolgreich hinzugefügt", "workflow": workflow}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/workflows/{workflow_id}/participants/{participant_id}", response_model=Dict[str, Any])
async def remove_workflow_participant(
    workflow_id: str = Path(..., description="ID des Workflows"),
    participant_id: str = Path(..., description="ID des Teilnehmers"),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Entfernt einen Teilnehmer aus einem Workflow.
    """
    try:
        workflow = workflow_engine.remove_workflow_participant(workflow_id, participant_id)
        return {"status": "success", "message": "Teilnehmer erfolgreich entfernt", "workflow": workflow}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/workflows/{workflow_id}/export", response_model=Dict[str, Any])
async def export_workflow(
    workflow_id: str = Path(..., description="ID des Workflows"),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Exportiert einen Workflow.
    """
    try:
        export = workflow_engine.export_workflow(workflow_id)
        return export
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/workflows/import", response_model=Dict[str, Any])
async def import_workflow(
    workflow_data: Dict[str, Any] = Body(...),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Importiert einen Workflow.
    """
    try:
        workflow_id = workflow_engine.import_workflow(workflow_data)
        return {"status": "success", "message": "Workflow erfolgreich importiert", "workflow_id": workflow_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

