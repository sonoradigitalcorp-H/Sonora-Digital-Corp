"""Unit tests for Planner."""

import pytest
from src.planner.planner import Planner, ExecutionPlan, PlanStep


class TestPlanner:
    """Tests del Planner."""

    def setup_method(self):
        self.planner = Planner()

    def test_create_plan_crud(self):
        """Test crear plan para tarea CRUD."""
        plan = self.planner.create_plan("task-123", "Crear API REST para usuarios")
        assert plan is not None
        assert plan.task_id == "task-123"
        assert len(plan.steps) >= 4
        assert "openhands" in plan.required_agents

    def test_create_plan_bugfix(self):
        """Test crear plan para bugfix."""
        plan = self.planner.create_plan("task-456", "Arreglar error de login")
        assert plan is not None
        assert len(plan.steps) >= 4

    def test_create_plan_generic(self):
        """Test crear plan genérico."""
        plan = self.planner.create_plan("task-789", "Algo que no matchea ningún patrón")
        assert plan is not None
        assert len(plan.steps) == 3

    def test_approve_plan(self):
        """Test aprobar plan."""
        plan = self.planner.create_plan("task-123", "Crear función")
        result = self.planner.approve_plan(plan.id)
        assert result is True
        assert self.planner.get_plan(plan.id).status == "approved"

    def test_reject_plan(self):
        """Test rechazar plan."""
        plan = self.planner.create_plan("task-123", "Crear función")
        result = self.planner.reject_plan(plan.id, "No es necesario")
        assert result is True
        assert self.planner.get_plan(plan.id).status == "failed"

    def test_get_plan(self):
        """Test obtener plan."""
        plan = self.planner.create_plan("task-123", "Crear función")
        retrieved = self.planner.get_plan(plan.id)
        assert retrieved is not None
        assert retrieved.id == plan.id

    def test_list_plans(self):
        """Test listar planes."""
        for i in range(3):
            self.planner.create_plan(f"task-{i}", f"Tarea {i}")

        plans = self.planner.list_plans()
        assert len(plans) == 3

    def test_update_step_status(self):
        """Test actualizar estado de step."""
        plan = self.planner.create_plan("task-123", "Crear función")
        step = plan.steps[0]
        result = self.planner.update_step_status(plan.id, step.id, "completed")
        assert result is True

    def test_get_next_step(self):
        """Test obtener siguiente step."""
        plan = self.planner.create_plan("task-123", "Crear función")
        next_step = self.planner.get_next_step(plan.id)
        assert next_step is not None
        assert next_step.status == "pending"

    def test_get_stats(self):
        """Test obtener estadísticas."""
        self.planner.create_plan("task-123", "Crear función")
        stats = self.planner.get_stats()
        assert stats["total_plans"] == 1
        assert stats["total_steps"] > 0
