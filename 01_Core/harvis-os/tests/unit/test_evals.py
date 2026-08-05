"""Tests for Eval Prompts."""

import pytest
from src.evals import PromptEvaluator, PromptTemplate, TemplateRegistry, PromptOptimizer, PromptMetrics


class TestPromptEvaluator:
    """Tests del evaluador de prompts."""

    def setup_method(self):
        self.evaluator = PromptEvaluator()

    def test_register_and_evaluate(self):
        """Test registrar y evaluar prompt."""
        def mock_prompt(input_text):
            return f"Processed: {input_text}"

        self.evaluator.register_prompt("test_prompt", mock_prompt)
        result = self.evaluator.evaluate("test_prompt", "hello")
        assert result.passed is True
        assert "Processed: hello" in result.actual_output

    def test_evaluate_with_expected(self):
        """Test evaluar con resultado esperado."""
        def mock_prompt(input_text):
            return "code"

        self.evaluator.register_prompt("classifier", mock_prompt)
        result = self.evaluator.evaluate(
            "classifier",
            "Create a function",
            expected_output="code",
        )
        assert result.passed is True
        assert result.score == 1.0

    def test_evaluate_with_contains(self):
        """Test evaluar con contains."""
        def mock_prompt(input_text):
            return "function login() { return true; }"

        self.evaluator.register_prompt("code_gen", mock_prompt)
        result = self.evaluator.evaluate(
            "code_gen",
            "Create login function",
            expected_contains=["function", "login"],
        )
        assert result.passed is True

    def test_evaluate_with_not_contains(self):
        """Test evaluar con not contains."""
        def mock_prompt(input_text):
            return "function login() { return true; }"

        self.evaluator.register_prompt("code_gen", mock_prompt)
        result = self.evaluator.evaluate(
            "code_gen",
            "Create login function",
            expected_not_contains=["eval", "exec"],
        )
        assert result.passed is True

    def test_evaluate_with_regex(self):
        """Test evaluar con regex."""
        def mock_prompt(input_text):
            return "Task ID: abc-123"

        self.evaluator.register_prompt("task_id", mock_prompt)
        result = self.evaluator.evaluate(
            "task_id",
            "Get task ID",
            expected_regex=r"Task ID: [a-z]+-[0-9]+",
        )
        assert result.passed is True

    def test_add_and_evaluate_case(self):
        """Test agregar y evaluar caso."""
        def mock_prompt(input_text):
            return "code" if "function" in input_text else "other"

        self.evaluator.register_prompt("classifier", mock_prompt)
        case_id = self.evaluator.add_case(
            input_text="Create a function",
            expected_output="code",
        )
        result = self.evaluator.evaluate_case("classifier", case_id)
        assert result.passed is True

    def test_stats(self):
        """Test estadísticas."""
        def mock_prompt(input_text):
            return "test"

        self.evaluator.register_prompt("test", mock_prompt)
        self.evaluator.evaluate("test", "input1")
        self.evaluator.evaluate("test", "input2")

        stats = self.evaluator.get_stats()
        assert stats["total_evaluations"] == 2
        assert stats["passed"] == 2


class TestPromptTemplate:
    """Tests de plantillas de prompts."""

    def test_render_template(self):
        """Test renderizar plantilla."""
        template = PromptTemplate(
            name="test",
            template="Hello {name}, your task is: {task}",
            variables=["name", "task"],
        )
        result = template.render(name="Luis", task="deploy app")
        assert "Luis" in result
        assert "deploy app" in result

    def test_validate_template(self):
        """Test validar plantilla."""
        template = PromptTemplate(
            name="test",
            template="{name} {task}",
            variables=["name", "task"],
        )
        is_valid, missing = template.validate(name="Luis")
        assert is_valid is False
        assert "task" in missing

    def test_render_missing_variable(self):
        """Test renderizar con variable faltante."""
        template = PromptTemplate(
            name="test",
            template="{name} {missing}",
            variables=["name", "missing"],
        )
        with pytest.raises(ValueError):
            template.render(name="Luis")


class TestTemplateRegistry:
    """Tests del registro de plantillas."""

    def setup_method(self):
        self.registry = TemplateRegistry()

    def test_register_and_get(self):
        """Test registrar y obtener plantilla."""
        template = PromptTemplate(name="test", template="Hello {name}")
        self.registry.register(template)
        result = self.registry.get("test")
        assert result is not None
        assert result.name == "test"

    def test_render(self):
        """Test renderizar desde registry."""
        template = PromptTemplate(name="test", template="Hello {name}")
        self.registry.register(template)
        result = self.registry.render("test", name="World")
        assert "World" in result

    def test_list_templates(self):
        """Test listar plantillas."""
        self.registry.register(PromptTemplate(name="a", template="A"))
        self.registry.register(PromptTemplate(name="b", template="B"))
        templates = self.registry.list_templates()
        assert len(templates) == 2


class TestPromptOptimizer:
    """Tests del optimizador de prompts."""

    def setup_method(self):
        self.optimizer = PromptOptimizer()

    def test_analyze(self):
        """Test analizar prompt."""
        metrics = self.optimizer.analyze("Create a function to validate emails")
        assert metrics["word_count"] > 0
        assert metrics["complexity"] in ["low", "medium", "high"]

    def test_optimize_long_prompt(self):
        """Test optimizar prompt largo."""
        long_prompt = " ".join(["word"] * 200)  # More than 500 characters
        suggestions = self.optimizer.optimize(long_prompt)
        length_suggestions = [s for s in suggestions if s.type == "length"]
        assert len(length_suggestions) > 0

    def test_optimize_vague(self):
        """Test optimizar prompt vago."""
        suggestions = self.optimizer.optimize("Do the thing")
        specificity = [s for s in suggestions if s.type == "specificity"]
        assert len(specificity) > 0


class TestPromptMetrics:
    """Tests de métricas de prompts."""

    def setup_method(self):
        self.metrics = PromptMetrics()

    def test_record_and_get(self):
        """Test registrar y obtener métricas."""
        self.metrics.record("prompt1", "response_time", 0.5, "seconds")
        metrics = self.metrics.get_metrics("prompt1")
        assert len(metrics) == 1

    def test_average(self):
        """Test promedio de métricas."""
        self.metrics.record("prompt1", "accuracy", 0.9)
        self.metrics.record("prompt1", "accuracy", 0.8)
        avg = self.metrics.get_average("prompt1", "accuracy")
        assert abs(avg - 0.85) < 0.001

    def test_summary(self):
        """Test resumen de métricas."""
        self.metrics.record("prompt1", "response_time", 0.5)
        self.metrics.record("prompt1", "response_time", 0.7)
        summary = self.metrics.get_summary("prompt1")
        assert "response_time" in summary
        assert summary["response_time"]["count"] == 2
