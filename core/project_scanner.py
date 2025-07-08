"""
CONFIGO Project Scanner
=======================

Intelligent project detection that scans directories for:
- Configuration files (requirements.txt, Dockerfile, pyproject.toml, etc.)
- Framework indicators
- Development tools
- Provides context-aware tool recommendations
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from core.memory import AgentMemory

logger = logging.getLogger(__name__)

@dataclass
class ProjectFile:
    """Represents a detected project file."""
    name: str
    path: str
    type: str  # "config", "source", "dependency", "build"
    framework: Optional[str] = None
    language: Optional[str] = None

@dataclass
class ProjectAnalysis:
    """Complete project analysis."""
    project_type: str
    detected_frameworks: List[str]
    languages: List[str]
    files: List[ProjectFile]
    recommendations: List[str]
    confidence: float
    summary: str

class ProjectScanner:
    """
    Intelligent project scanner that detects project types and recommends tools.
    """
    
    def __init__(self, memory: AgentMemory):
        self.memory = memory
        
        # File patterns for different project types
        self.file_patterns = {
            # Python
            "python": {
                "requirements.txt": {"type": "dependency", "framework": "pip"},
                "pyproject.toml": {"type": "config", "framework": "poetry"},
                "Pipfile": {"type": "dependency", "framework": "pipenv"},
                "setup.py": {"type": "config", "framework": "setuptools"},
                "poetry.lock": {"type": "dependency", "framework": "poetry"},
                "Pipfile.lock": {"type": "dependency", "framework": "pipenv"},
                "*.py": {"type": "source", "language": "python"},
                "Dockerfile": {"type": "build", "framework": "docker"},
                "docker-compose.yml": {"type": "config", "framework": "docker"},
                ".python-version": {"type": "config", "framework": "pyenv"},
                "venv/": {"type": "config", "framework": "venv"},
                ".venv/": {"type": "config", "framework": "venv"},
            },
            
            # JavaScript/Node.js
            "javascript": {
                "package.json": {"type": "config", "framework": "npm"},
                "package-lock.json": {"type": "dependency", "framework": "npm"},
                "yarn.lock": {"type": "dependency", "framework": "yarn"},
                "pnpm-lock.yaml": {"type": "dependency", "framework": "pnpm"},
                "*.js": {"type": "source", "language": "javascript"},
                "*.ts": {"type": "source", "language": "typescript"},
                "*.jsx": {"type": "source", "language": "javascript"},
                "*.tsx": {"type": "source", "language": "typescript"},
                "next.config.js": {"type": "config", "framework": "nextjs"},
                "vite.config.js": {"type": "config", "framework": "vite"},
                "webpack.config.js": {"type": "config", "framework": "webpack"},
                "tailwind.config.js": {"type": "config", "framework": "tailwind"},
                "Dockerfile": {"type": "build", "framework": "docker"},
                "docker-compose.yml": {"type": "config", "framework": "docker"},
            },
            
            # Go
            "go": {
                "go.mod": {"type": "dependency", "framework": "go"},
                "go.sum": {"type": "dependency", "framework": "go"},
                "*.go": {"type": "source", "language": "go"},
                "Dockerfile": {"type": "build", "framework": "docker"},
            },
            
            # Rust
            "rust": {
                "Cargo.toml": {"type": "config", "framework": "cargo"},
                "Cargo.lock": {"type": "dependency", "framework": "cargo"},
                "*.rs": {"type": "source", "language": "rust"},
                "Dockerfile": {"type": "build", "framework": "docker"},
            },
            
            # Java
            "java": {
                "pom.xml": {"type": "config", "framework": "maven"},
                "build.gradle": {"type": "config", "framework": "gradle"},
                "*.java": {"type": "source", "language": "java"},
                "*.jar": {"type": "build", "framework": "java"},
                "Dockerfile": {"type": "build", "framework": "docker"},
            },
            
            # PHP
            "php": {
                "composer.json": {"type": "config", "framework": "composer"},
                "composer.lock": {"type": "dependency", "framework": "composer"},
                "*.php": {"type": "source", "language": "php"},
                "Dockerfile": {"type": "build", "framework": "docker"},
            },
            
            # General/DevOps
            "devops": {
                "Dockerfile": {"type": "build", "framework": "docker"},
                "docker-compose.yml": {"type": "config", "framework": "docker"},
                "docker-compose.yaml": {"type": "config", "framework": "docker"},
                "kubernetes/": {"type": "config", "framework": "kubernetes"},
                "k8s/": {"type": "config", "framework": "kubernetes"},
                "*.yaml": {"type": "config", "framework": "yaml"},
                "*.yml": {"type": "config", "framework": "yaml"},
                "terraform/": {"type": "config", "framework": "terraform"},
                "*.tf": {"type": "config", "framework": "terraform"},
                ".github/": {"type": "config", "framework": "github"},
                ".gitlab-ci.yml": {"type": "config", "framework": "gitlab"},
                "Jenkinsfile": {"type": "config", "framework": "jenkins"},
            }
        }
        
        # Framework-specific indicators
        self.framework_indicators = {
            "fastapi": ["fastapi", "uvicorn"],
            "django": ["django", "manage.py"],
            "flask": ["flask"],
            "react": ["react", "react-dom"],
            "vue": ["vue", "@vue"],
            "angular": ["@angular"],
            "nextjs": ["next"],
            "express": ["express"],
            "spring": ["spring-boot", "spring-core"],
            "laravel": ["laravel"],
            "rails": ["rails"],
            "dotnet": [".csproj", ".sln"],
        }
        
        logger.info("Project scanner initialized")
    
    def scan_project(self, project_path: str = ".") -> ProjectAnalysis:
        """
        Scan a project directory and analyze its structure.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            ProjectAnalysis: Complete analysis of the project
        """
        try:
            project_path = Path(project_path).resolve()
            if not project_path.exists():
                return self._create_empty_analysis("No project directory found")
            
            logger.info(f"Scanning project at: {project_path}")
            
            # Scan for files
            detected_files = self._scan_files(project_path)
            
            # Analyze project type
            project_type = self._determine_project_type(detected_files)
            
            # Extract frameworks and languages
            frameworks = self._extract_frameworks(detected_files)
            languages = self._extract_languages(detected_files)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(project_type, frameworks, languages)
            
            # Calculate confidence
            confidence = self._calculate_confidence(detected_files, frameworks)
            
            # Create summary
            summary = self._create_summary(project_type, frameworks, languages, detected_files)
            
            analysis = ProjectAnalysis(
                project_type=project_type,
                detected_frameworks=frameworks,
                languages=languages,
                files=detected_files,
                recommendations=recommendations,
                confidence=confidence,
                summary=summary
            )
            
            logger.info(f"Project analysis complete: {project_type} ({confidence:.1%} confidence)")
            return analysis
            
        except Exception as e:
            logger.error(f"Error scanning project: {e}")
            return self._create_empty_analysis(f"Error scanning project: {e}")
    
    def _scan_files(self, project_path: Path) -> List[ProjectFile]:
        """Scan project directory for relevant files."""
        files = []
        
        try:
            for root, dirs, filenames in os.walk(project_path):
                # Skip common directories to ignore
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.pytest_cache', '.mypy_cache'}]
                
                for filename in filenames:
                    file_path = Path(root) / filename
                    relative_path = file_path.relative_to(project_path)
                    
                    # Check against all patterns
                    for language, patterns in self.file_patterns.items():
                        for pattern, info in patterns.items():
                            if self._matches_pattern(filename, pattern):
                                project_file = ProjectFile(
                                    name=filename,
                                    path=str(relative_path),
                                    type=info["type"],
                                    framework=info.get("framework"),
                                    language=info.get("language")
                                )
                                files.append(project_file)
                                break
                        
                        # Check for framework-specific files
                        if language == "python" and filename.endswith('.py'):
                            # Check for framework indicators in Python files
                            framework = self._detect_python_framework(file_path)
                            if framework:
                                project_file = ProjectFile(
                                    name=filename,
                                    path=str(relative_path),
                                    type="source",
                                    framework=framework,
                                    language="python"
                                )
                                files.append(project_file)
        
        except Exception as e:
            logger.error(f"Error scanning files: {e}")
        
        return files
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a pattern."""
        if pattern.endswith('/'):
            # Directory pattern
            return filename == pattern[:-1]
        elif '*' in pattern:
            # Wildcard pattern
            import fnmatch
            return fnmatch.fnmatch(filename, pattern)
        else:
            # Exact match
            return filename == pattern
    
    def _detect_python_framework(self, file_path: Path) -> Optional[str]:
        """Detect Python framework from file content."""
        try:
            if file_path.suffix == '.py':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    
                    if 'from fastapi import' in content or 'import fastapi' in content:
                        return 'fastapi'
                    elif 'from django' in content or 'import django' in content:
                        return 'django'
                    elif 'from flask import' in content or 'import flask' in content:
                        return 'flask'
                    elif 'uvicorn.run(' in content:
                        return 'uvicorn'
        except Exception:
            pass
        
        return None
    
    def _determine_project_type(self, files: List[ProjectFile]) -> str:
        """Determine the primary project type based on detected files."""
        type_scores = {
            "python": 0,
            "javascript": 0,
            "go": 0,
            "rust": 0,
            "java": 0,
            "php": 0,
            "devops": 0
        }
        
        for file in files:
            if file.language:
                if file.language in type_scores:
                    type_scores[file.language] += 1
            if file.framework:
                if file.framework in ["docker", "kubernetes", "terraform"]:
                    type_scores["devops"] += 1
        
        # Find the type with highest score
        if not any(type_scores.values()):
            return "unknown"
        
        return max(type_scores, key=type_scores.get)
    
    def _extract_frameworks(self, files: List[ProjectFile]) -> List[str]:
        """Extract unique frameworks from detected files."""
        frameworks = set()
        
        for file in files:
            if file.framework:
                frameworks.add(file.framework)
        
        return list(frameworks)
    
    def _extract_languages(self, files: List[ProjectFile]) -> List[str]:
        """Extract unique languages from detected files."""
        languages = set()
        
        for file in files:
            if file.language:
                languages.add(file.language)
        
        return list(languages)
    
    def _generate_recommendations(self, project_type: str, frameworks: List[str], languages: List[str]) -> List[str]:
        """Generate tool recommendations based on project analysis."""
        recommendations = []
        
        # Base recommendations by project type
        if project_type == "python":
            recommendations.extend([
                "Python 3.11+",
                "pip or poetry",
                "virtual environment (venv or conda)",
                "VS Code with Python extension"
            ])
            
            if "fastapi" in frameworks:
                recommendations.extend(["uvicorn", "pydantic", "sqlalchemy"])
            if "django" in frameworks:
                recommendations.extend(["django-admin", "django-debug-toolbar"])
            if "flask" in frameworks:
                recommendations.extend(["flask-cli", "flask-sqlalchemy"])
                
        elif project_type == "javascript":
            recommendations.extend([
                "Node.js 18+",
                "npm or yarn",
                "VS Code with JavaScript/TypeScript extensions"
            ])
            
            if "react" in frameworks:
                recommendations.extend(["create-react-app", "react developer tools"])
            if "nextjs" in frameworks:
                recommendations.extend(["next", "vercel cli"])
            if "vue" in frameworks:
                recommendations.extend(["vue-cli", "vue devtools"])
                
        elif project_type == "go":
            recommendations.extend([
                "Go 1.21+",
                "VS Code with Go extension",
                "gofmt",
                "golint"
            ])
            
        elif project_type == "rust":
            recommendations.extend([
                "Rust",
                "cargo",
                "VS Code with rust-analyzer extension"
            ])
        
        # DevOps recommendations
        if "docker" in frameworks:
            recommendations.extend(["Docker", "Docker Compose"])
        if "kubernetes" in frameworks:
            recommendations.extend(["kubectl", "helm"])
        if "terraform" in frameworks:
            recommendations.extend(["terraform", "terraform-docs"])
        
        # General development tools
        recommendations.extend([
            "Git",
            "GitHub CLI",
            "Postman or Insomnia"
        ])
        
        return list(set(recommendations))  # Remove duplicates
    
    def _calculate_confidence(self, files: List[ProjectFile], frameworks: List[str]) -> float:
        """Calculate confidence score for the analysis."""
        if not files:
            return 0.0
        
        # Base confidence from number of detected files
        base_confidence = min(len(files) / 10.0, 0.8)
        
        # Boost confidence for specific frameworks
        framework_boost = min(len(frameworks) * 0.1, 0.2)
        
        return min(base_confidence + framework_boost, 1.0)
    
    def _create_summary(self, project_type: str, frameworks: List[str], languages: List[str], files: List[ProjectFile]) -> str:
        """Create a human-readable summary of the project."""
        if project_type == "unknown":
            return "No clear project type detected. This might be an empty directory or a project with unusual structure."
        
        summary_parts = [f"Detected {project_type.title()} project"]
        
        if frameworks:
            summary_parts.append(f"using {', '.join(frameworks)}")
        
        if languages:
            summary_parts.append(f"with {', '.join(languages)}")
        
        summary_parts.append(f"({len(files)} relevant files found)")
        
        return " ".join(summary_parts)
    
    def _create_empty_analysis(self, reason: str) -> ProjectAnalysis:
        """Create an empty analysis when scanning fails."""
        return ProjectAnalysis(
            project_type="unknown",
            detected_frameworks=[],
            languages=[],
            files=[],
            recommendations=["Git", "VS Code"],
            confidence=0.0,
            summary=reason
        ) 