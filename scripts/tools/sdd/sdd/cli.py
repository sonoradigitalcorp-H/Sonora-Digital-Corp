import os
import sys
import click

REPO = os.getcwd()


@click.group()
def main():
    """SDC Spec-Driven Development CLI."""
    pass


@main.command()
def init():
    """Initialize SDD framework structure."""
    dirs = [
        "specs/schema",
        "specs/capabilities",
        "adrs",
        "tests/gherkin",
        "tests/steps",
        "tests/evals/promptfoo",
        "tests/evals/structural",
    ]
    for d in dirs:
        os.makedirs(os.path.join(REPO, d), exist_ok=True)
        click.echo(f"  ✅ {d}")

    click.echo("\nSDD framework initialized. Add capabilities with: sdd spec-new <id>")


@main.command()
@click.argument("capability_id")
def spec_new(capability_id):
    """Create a new capability spec structure."""
    base = os.path.join(REPO, "specs", "capabilities", capability_id)
    gherkin_dir = os.path.join(base, "gherkin")
    os.makedirs(gherkin_dir, exist_ok=True)

    spec_path = os.path.join(base, "spec.md")
    if not os.path.exists(spec_path):
        with open(spec_path, "w") as f:
            f.write(f"# {capability_id} — Capability Spec\n\n**Status**: draft\n")
        click.echo(f"  ✅ specs/capabilities/{capability_id}/spec.md")

    feature_path = os.path.join(gherkin_dir, f"{capability_id}.feature")
    if not os.path.exists(feature_path):
        with open(feature_path, "w") as f:
            f.write(f"Feature: {capability_id}\n  As a\n  I want\n  So that\n\n")
        click.echo(f"  ✅ specs/capabilities/{capability_id}/gherkin/{capability_id}.feature")

    steps_path = os.path.join(REPO, "tests", "steps", f"{capability_id}_steps.py")
    if not os.path.exists(steps_path):
        with open(steps_path, "w") as f:
            f.write(f'"""Step definitions for {capability_id}."""\n')
        click.echo(f"  ✅ tests/steps/{capability_id}_steps.py")

    click.echo(f"\nCapability '{capability_id}' scaffold created. Edit the files to add detail.")


@main.command()
def test():
    """Run all SDD tests (TDD + BDD)."""
    import subprocess

    repo = REPO
    click.echo("=== Running BDD tests (tests/gherkin/) ===")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/gherkin/", "-v", "--tb=short"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    click.echo(result.stdout)
    if result.returncode != 0:
        click.echo(result.stderr)

    click.echo("\n=== Running structural evals (tests/evals/structural/) ===")
    result2 = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/evals/structural/", "-v", "--tb=short"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    click.echo(result2.stdout)
    if result2.returncode != 0:
        click.echo(result2.stderr)

    if result.returncode != 0 or result2.returncode != 0:
        sys.exit(1)


@main.command()
@click.option("--promptfoo", is_flag=True, help="Run promptfoo evals too")
def eval(promptfoo):
    """Run structural + optional promptfoo evals."""
    import subprocess

    repo = REPO
    click.echo("=== Running structural evals ===")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/evals/structural/", "-v"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    click.echo(result.stdout)
    if result.returncode != 0:
        click.echo(result.stderr)

    if promptfoo:
        click.echo("\n=== Running promptfoo evals ===")
        result2 = subprocess.run(
            ["promptfoo", "eval", "-c", "tests/evals/promptfoo/promptfooconfig.yaml"],
            cwd=repo,
            capture_output=True,
            text=True,
        )
        click.echo(result2.stdout)
        if result2.returncode != 0:
            click.echo(result2.stderr)


if __name__ == "__main__":
    main()
