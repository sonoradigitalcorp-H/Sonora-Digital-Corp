from pathlib import Path


class ConstraintViolation(Exception):
    pass


class Verifier:
    def __init__(self):
        self.required_paths = {
            "spec.md",
            "plan.md",
            "tasks.md",
            "checklist.md",
            "data-model.md",
            "contracts/README.md",
        }
        # Spec 000 uses constitution.md instead of spec.md
        self.spec_exceptions = {"000-constitucion": {"spec.md": "constitution.md"}}

    def verify_structure(self, spec_dir):
        spec_path = Path(spec_dir)
        spec_name = spec_path.name

        # Get exceptions for this spec
        exceptions = self.spec_exceptions.get(spec_name, {})

        for relative_path in self.required_paths:
            # Check if there's an exception for this file
            actual_path = exceptions.get(relative_path, relative_path)
            abs_path = spec_path / actual_path

            if not abs_path.exists():
                raise ConstraintViolation(
                    f"Missing required file: {relative_path} in {spec_dir}"
                )

        # Verificar que checklist.md tenga al menos 3 ítems
        checklist_path = spec_path / "checklist.md"
        if checklist_path.exists():
            content = checklist_path.read_text()
            if content.count("- [ ]") < 3:
                raise ConstraintViolation(f"Checklist incomplete in {spec_dir}")

    def verify_tdd_compliance(self, spec_dir):
        VERIFY_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
        global_tests_dir = VERIFY_DIR / "tests"
        if not global_tests_dir.exists():
            raise ConstraintViolation(
                f"Global tests directory missing: {global_tests_dir}"
            )

        test_files = list(global_tests_dir.rglob("test_*.py"))
        if len(test_files) < 10:
            raise ConstraintViolation(
                f"Insufficient tests: only {len(test_files)} test files found"
            )

    def verify_skill_coverage(self, spec_id):
        # Simulación de check de skills
        # La lógica la implementaremos en el registry.json
        pass


def main(specs_dir=None):
    verifier = Verifier()
    if specs_dir is None:
        specs_dir = Path(__file__).resolve().parent.parent.parent / "specs"

    compliant_count = 0
    non_compliant_count = 0

    for spec in Path(specs_dir).iterdir():
        if spec.is_dir():
            try:
                verifier.verify_structure(spec)
                verifier.verify_tdd_compliance(spec)
                print(f"✅ {spec.name}: Compliant")
                compliant_count += 1
            except ConstraintViolation as e:
                print(f"❌ {spec.name}: {e}")
                non_compliant_count += 1

    total = compliant_count + non_compliant_count
    print(f"\n{'='*60}")
    print(f"Total specs: {total}")
    print(f"Compliant: {compliant_count}")
    print(f"Non-compliant: {non_compliant_count}")
    rate = compliant_count / total * 100 if total > 0 else 0
    print(f"Compliance rate: {rate:.1f}%")


if __name__ == "__main__":
    main()
