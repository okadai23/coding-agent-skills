"""Detect build systems by file presence."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


_MARKERS: dict[str, list[str]] = {
    "go": ["go.mod"],
    "node": ["package.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json"],
    "rust": ["Cargo.toml"],
    "java-maven": ["pom.xml"],
    "java-gradle": ["build.gradle", "build.gradle.kts", "settings.gradle"],
    "dotnet": ["*.sln", "*.csproj", "*.fsproj"],
    "python": ["pyproject.toml", "setup.cfg", "setup.py", "requirements.txt"],
    "cmake": ["CMakeLists.txt"],
    "make": ["Makefile"],
}


def detect_build_system(cwd: Path) -> list[str]:
    """Detect build systems by scanning known marker files."""
    detected: list[str] = []
    for system, patterns in _MARKERS.items():
        for pattern in patterns:
            if list(cwd.glob(pattern)):
                detected.append(system)
                break
    return detected
