"""Prompt Templates - Sistema de plantillas de prompts."""

from dataclasses import dataclass, field
from typing import Any, Optional
import re


@dataclass
class PromptTemplate:
    """Plantilla de prompt."""
    name: str
    template: str
    description: str = ""
    variables: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def render(self, **kwargs) -> str:
        """
        Renderiza la plantilla con variables.

        Args:
            **kwargs: Variables a reemplazar

        Returns:
            Prompt renderizado
        """
        result = self.template

        # Reemplazar variables {var}
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))

        # Verificar variables faltantes
        remaining = re.findall(r'\{(\w+)\}', result)
        if remaining:
            raise ValueError(f"Missing variables: {remaining}")

        return result

    def validate(self, **kwargs) -> tuple[bool, list[str]]:
        """
        Valida que todas las variables estén presentes.

        Returns:
            (is_valid, missing_variables)
        """
        missing = []
        for var in self.variables:
            if var not in kwargs:
                missing.append(var)
        return len(missing) == 0, missing


class TemplateRegistry:
    """
    Template Registry - Registro centralizado de plantillas.

    Permite:
    - Almacenar plantillas
    - Buscar por nombre
    - Versionado
    """

    def __init__(self):
        self.templates: dict[str, PromptTemplate] = {}
        self.versions: dict[str, list[PromptTemplate]] = {}

    def register(self, template: PromptTemplate, version: str = "1.0.0"):
        """Registra una plantilla."""
        self.templates[template.name] = template

        if template.name not in self.versions:
            self.versions[template.name] = []
        self.versions[template.name].append(template)

    def get(self, name: str) -> Optional[PromptTemplate]:
        """Obtiene una plantilla por nombre."""
        return self.templates.get(name)

    def render(self, template_name: str, **kwargs) -> str:
        """Renderiza una plantilla."""
        template = self.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        return template.render(**kwargs)

    def list_templates(self) -> list[str]:
        """Lista todas las plantillas."""
        return list(self.templates.keys())

    def get_versions(self, name: str) -> list[PromptTemplate]:
        """Obtiene todas las versiones de una plantilla."""
        return self.versions.get(name, [])


# Plantillas predefinidas para Harvis OS
HARVIS_TEMPLATES = {
    "task_classification": PromptTemplate(
        name="task_classification",
        template="""Classify the following task into one of these categories: code, git, query, deploy, review, docs, other.

Task: {task_content}

Respond with ONLY the category name.""",
        description="Clasifica tareas para el Dispatcher",
        variables=["task_content"],
    ),
    "task_planning": PromptTemplate(
        name="task_planning",
        template="""Create a step-by-step plan for the following task:

Task: {task_content}

Available agents: {available_agents}

Provide a JSON array of steps with: description, agent, action""",
        description="Genera planes de ejecución",
        variables=["task_content", "available_agents"],
    ),
    "code_review": PromptTemplate(
        name="code_review",
        template="""Review the following code for:
- Bugs
- Performance issues
- Security concerns
- Code style

Code:
```
{code}
```

Provide a structured review.""",
        description="Revisa código",
        variables=["code"],
    ),
    "bug_analysis": PromptTemplate(
        name="bug_analysis",
        template="""Analyze the following bug report and identify:
1. Root cause
2. Affected components
3. Suggested fix

Bug report: {bug_report}

Error logs:
{error_logs}""",
        description="Analiza bugs",
        variables=["bug_report", "error_logs"],
    ),
    "changelog_generation": PromptTemplate(
        name="changelog_generation",
        template="""Generate a changelog from these commits:

{commits}

Format:
- feat: for new features
- fix: for bug fixes
- docs: for documentation
- refactor: for refactoring

Group by type.""",
        description="Genera changelog",
        variables=["commits"],
    ),
}
