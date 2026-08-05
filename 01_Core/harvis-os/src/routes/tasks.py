"""Task routes."""


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..dispatcher import Dispatcher, IncomingRequest

router = APIRouter()

# Dispatcher instance
dispatcher = Dispatcher()


class TaskRequest(BaseModel):
    """Task request model."""
    source: str
    user_id: str
    content: str
    metadata: dict = {}


class TaskResponse(BaseModel):
    """Task response model."""
    id: str
    source: str
    user_id: str
    content: str
    category: str | None = None
    priority: str | None = None
    assigned_agent: str | None = None
    confidence: float | None = None
    routing_reason: str | None = None
    status: str = "pending"
    created_at: str
    metadata: dict = {}


@router.post("/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """Create a new task using the Dispatcher."""
    # Create incoming request
    incoming = IncomingRequest(
        source=request.source,
        user_id=request.user_id,
        content=request.content,
        metadata=request.metadata,
    )

    # Process through Dispatcher
    task = await dispatcher.process_request(incoming)

    return TaskResponse(
        id=task.id,
        source=task.request.source,
        user_id=task.request.user_id,
        content=task.request.content,
        category=task.category,
        priority=task.priority,
        assigned_agent=task.assigned_agent,
        confidence=task.confidence,
        routing_reason=task.routing_reason,
        status=task.status,
        created_at=task.created_at,
        metadata=task.request.metadata,
    )


@router.get("/tasks/stats")
async def task_stats():
    """Get task statistics."""
    return dispatcher.get_stats()


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get task by ID."""
    task = dispatcher.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(
        id=task.id,
        source=task.request.source,
        user_id=task.request.user_id,
        content=task.request.content,
        category=task.category,
        priority=task.priority,
        assigned_agent=task.assigned_agent,
        confidence=task.confidence,
        routing_reason=task.routing_reason,
        status=task.status,
        created_at=task.created_at,
        metadata=task.request.metadata,
    )


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    status: str | None = None,
    category: str | None = None,
    limit: int = 10
):
    """List tasks with optional filters."""
    tasks = dispatcher.list_tasks(status=status, category=category, limit=limit)

    return [
        TaskResponse(
            id=task.id,
            source=task.request.source,
            user_id=task.request.user_id,
            content=task.request.content,
            category=task.category,
            priority=task.priority,
            assigned_agent=task.assigned_agent,
            confidence=task.confidence,
            routing_reason=task.routing_reason,
            status=task.status,
            created_at=task.created_at,
            metadata=task.request.metadata,
        )
        for task in tasks
    ]

