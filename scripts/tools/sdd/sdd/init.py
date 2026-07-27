"""SDD framework initialization logic."""
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

STRUCTURE = {
    "specs/schema": ["spec-v1.yaml"],
    "specs/capabilities": [],
    "adrs": ["README.md"],
    "tests/gherkin": [],
    "tests/steps": ["__init__.py"],
    "evals/promptfoo": ["promptfooconfig.yaml"],
    "evals/structural": ["test_specs_schema.py"],
}


def run():
    for directory, files in STRUCTURE.items():
        os.makedirs(os.path.join(REPO, directory), exist_ok=True)
        for f in files:
            path = os.path.join(REPO, directory, f)
            if not os.path.exists(path):
                open(path, "w").close()
                print(f"  Created {directory}/{f}")
    print("\nSDD framework initialized.")
