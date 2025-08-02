#!/usr/bin/env python3
"""
Comprehensive linting script for langgraph-runtime-inmem-open
Runs all linters and provides a summary report
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class Linter:
    """Base class for linters"""

    def __init__(self, name: str, command: List[str], description: str):
        self.name = name
        self.command = command
        self.description = description

    def run(self, target: str = ".") -> Tuple[bool, str]:
        """Run the linter and return (success, output)"""
        try:
            result = subprocess.run(
                self.command + [target],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=Path.cwd(),
                check=False,
            )
            success = result.returncode == 0
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            return success, stdout + stderr
        except FileNotFoundError:
            return (
                False,
                f"Error: {self.name} not found. Install with: pip install {self.name}",
            )


def setup_linters() -> List[Linter]:
    """Setup all linters"""
    return [
        Linter("black", ["black", "--check", "--diff"], "Code formatting check"),
        Linter("isort", ["isort", "--check-only", "--diff"], "Import sorting check"),
        Linter("flake8", ["flake8"], "Style and error checking"),
        Linter("mypy", ["mypy", "langgraph_runtime_inmem_open"], "Type checking"),
        Linter(
            "pylint",
            ["pylint", "langgraph_runtime_inmem_open"],
            "Comprehensive code analysis",
        ),
    ]


def run_tests() -> Tuple[bool, str]:
    """Run pytest with coverage"""
    try:
        result = subprocess.run(
            [
                "pytest",
                "--cov=langgraph_runtime_inmem_open",
                "--cov-report=term-missing",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=Path.cwd(),
            check=False,
        )
        success = result.returncode == 0
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        return success, stdout + stderr
    except FileNotFoundError:
        return (
            False,
            "Error: pytest not found. Install with: pip install pytest pytest-cov",
        )


def main():
    """Main linting function"""
    print("🔍 Running comprehensive code quality checks...")
    print("=" * 60)

    # Setup linters
    linters = setup_linters()

    # Track results
    results: Dict[str, Tuple[bool, str]] = {}

    # Run each linter
    for linter in linters:
        print(f"\n📋 Running {linter.name}...")
        print(f"   {linter.description}")
        print("-" * 40)

        success, output = linter.run()
        results[linter.name] = (success, output)

        if success:
            print(f"✅ {linter.name} passed")
            if output.strip():
                print(output)
        else:
            print(f"❌ {linter.name} failed")
            print(output)

    # Run tests
    print("\n🧪 Running tests...")
    print("-" * 40)
    test_success, test_output = run_tests()
    results["pytest"] = (test_success, test_output)

    if test_success:
        print("✅ Tests passed")
        print(test_output)
    else:
        print("❌ Tests failed")
        print(test_output)

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, (success, _) in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name:12} {status}")
        if not success:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All checks passed! Code quality is excellent.")
        return 0
    print("⚠️  Some checks failed. Please fix the issues above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
