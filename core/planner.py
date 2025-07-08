"""
Planning system for CONFIGO - manages multi-step setup process with retry logic and self-healing.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import yaml

logger = logging.getLogger(__name__)

class StepStatus(Enum):
    """Status of a planning step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"

class StepType(Enum):
    """Type of planning step."""
    TOOL_INSTALL = "tool_install"
    EXTENSION_INSTALL = "extension_install"
    LOGIN_PORTAL = "login_portal"
    VALIDATION = "validation"
    SELF_HEALING = "self_healing"

@dataclass
class PlanningStep:
    """A single step in the installation plan."""
    id: str
    name: str
    step_type: StepType
    description: str
    command: str
    check_command: str
    justification: str
    dependencies: List[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    is_extension: bool = False
    extension_id: Optional[str] = None
    version: Optional[str] = None
    confidence_score: float = 0.8

@dataclass
class InstallationPlan:
    """Complete installation plan with multiple steps."""
    plan_id: str
    environment: str
    steps: List[PlanningStep]
    created_at: datetime
    estimated_duration: int = 0  # minutes
    priority_order: List[str] = field(default_factory=list)
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    skipped_steps: int = 0

class PlanGenerator:
    """
    Generates intelligent installation plans with dependencies and priorities.
    """
    
    def __init__(self):
        self.base_tool_dependencies = {
            "Python": [],
            "Node.js": [],
            "Git": [],
            "Docker": ["curl"],
            "VS Code": [],
            "Cursor": [],
            "Jupyter": ["Python"],
            "Postman": [],
            "Terraform": ["curl"],
            "AWS CLI": [],
            "Google Cloud SDK": ["curl"],
            "Azure CLI": ["curl"]
        }
        
        self.extension_dependencies = {
            "GitHub Copilot": ["VS Code", "Cursor"],
            "Python Extension": ["VS Code", "Cursor"],
            "Jupyter Extension": ["VS Code", "Cursor"],
            "REST Client": ["VS Code", "Cursor"],
            "YAML Extension": ["VS Code", "Cursor"],
            "Markdownlint": ["VS Code", "Cursor"]
        }
        
        logger.info("Plan generator initialized")
    
    def generate_plan(self, tools: List[Dict[str, Any]], environment: str, 
                     memory_context: str = "") -> InstallationPlan:
        """
        Generate a comprehensive installation plan.
        
        Args:
            tools: List of tools to install
            environment: Environment description
            memory_context: Memory context for planning
            
        Returns:
            InstallationPlan: Complete installation plan
        """
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        steps = []
        
        # Separate tools by type
        base_tools = [tool for tool in tools if not tool.get('is_extension', False)]
        extensions = [tool for tool in tools if tool.get('is_extension', False)]
        login_portals = [tool for tool in tools if tool.get('type') == 'login_portal']
        
        # Generate steps for base tools
        base_steps = self._generate_base_tool_steps(base_tools, memory_context)
        steps.extend(base_steps)
        
        # Generate steps for extensions
        extension_steps = self._generate_extension_steps(extensions, memory_context)
        steps.extend(extension_steps)
        
        # Generate steps for login portals
        portal_steps = self._generate_login_portal_steps(login_portals, memory_context)
        steps.extend(portal_steps)
        
        # Add validation steps
        validation_steps = self._generate_validation_steps(base_tools, extensions)
        steps.extend(validation_steps)
        
        # Calculate dependencies and priorities
        self._resolve_dependencies(steps)
        priority_order = self._calculate_priority_order(steps)
        
        # Estimate duration
        estimated_duration = self._estimate_duration(steps)
        
        plan = InstallationPlan(
            plan_id=plan_id,
            environment=environment,
            steps=steps,
            created_at=datetime.now(),
            estimated_duration=estimated_duration,
            priority_order=priority_order,
            total_steps=len(steps)
        )
        
        logger.info(f"Generated plan {plan_id} with {len(steps)} steps")
        return plan
    
    def _generate_base_tool_steps(self, tools: List[Dict[str, Any]], 
                                 memory_context: str) -> List[PlanningStep]:
        """Generate steps for base tools."""
        steps = []
        
        for tool in tools:
            name = tool.get('name', 'Unknown Tool')
            install_command = tool.get('install_command', '')
            check_command = tool.get('check_command', name.lower())
            
            # Generate justification based on memory context
            justification = self._generate_justification(name, memory_context)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(name, memory_context)
            
            step = PlanningStep(
                id=f"tool_{name.lower().replace(' ', '_')}",
                name=name,
                step_type=StepType.TOOL_INSTALL,
                description=f"Install {name} for development environment",
                command=install_command,
                check_command=check_command,
                justification=justification,
                confidence_score=confidence,
                max_retries=3
            )
            steps.append(step)
        
        return steps
    
    def _generate_extension_steps(self, extensions: List[Dict[str, Any]], 
                                 memory_context: str) -> List[PlanningStep]:
        """Generate steps for VS Code extensions."""
        steps = []
        
        for ext in extensions:
            name = ext.get('name', 'Unknown Extension')
            extension_id = ext.get('extension_id', '')
            
            justification = self._generate_justification(name, memory_context)
            confidence = self._calculate_confidence(name, memory_context)
            
            step = PlanningStep(
                id=f"ext_{name.lower().replace(' ', '_')}",
                name=name,
                step_type=StepType.EXTENSION_INSTALL,
                description=f"Install {name} extension",
                command="",  # Extensions are installed via VS Code CLI
                check_command="code --list-extensions",
                justification=justification,
                confidence_score=confidence,
                is_extension=True,
                extension_id=extension_id,
                max_retries=2
            )
            steps.append(step)
        
        return steps
    
    def _generate_login_portal_steps(self, portals: List[Dict[str, Any]], 
                                   memory_context: str) -> List[PlanningStep]:
        """Generate steps for login portals."""
        steps = []
        
        for portal in portals:
            name = portal.get('name', 'Unknown Portal')
            url = portal.get('url', '')
            description = portal.get('description', '')
            
            justification = f"Login to {name} for development services"
            confidence = 0.9  # High confidence for login portals
            
            step = PlanningStep(
                id=f"portal_{name.lower().replace(' ', '_')}",
                name=name,
                step_type=StepType.LOGIN_PORTAL,
                description=f"Login to {name}",
                command=f"xdg-open {url}",
                check_command="echo 'Login portal opened'",
                justification=justification,
                confidence_score=confidence,
                max_retries=1
            )
            steps.append(step)
        
        return steps
    
    def _generate_validation_steps(self, base_tools: List[Dict[str, Any]], 
                                 extensions: List[Dict[str, Any]]) -> List[PlanningStep]:
        """Generate validation steps for installed tools."""
        steps = []
        
        # Validate base tools
        for tool in base_tools:
            name = tool.get('name', 'Unknown Tool')
            check_command = tool.get('check_command', name.lower())
            
            step = PlanningStep(
                id=f"validate_{name.lower().replace(' ', '_')}",
                name=f"Validate {name}",
                step_type=StepType.VALIDATION,
                description=f"Verify {name} installation",
                command=check_command,
                check_command=check_command,
                justification=f"Ensure {name} is properly installed and functional",
                confidence_score=0.95,
                max_retries=1
            )
            steps.append(step)
        
        # Validate extensions
        for ext in extensions:
            name = ext.get('name', 'Unknown Extension')
            
            step = PlanningStep(
                id=f"validate_ext_{name.lower().replace(' ', '_')}",
                name=f"Validate {name}",
                step_type=StepType.VALIDATION,
                description=f"Verify {name} extension",
                command="code --list-extensions",
                check_command="code --list-extensions",
                justification=f"Ensure {name} extension is properly installed",
                confidence_score=0.9,
                max_retries=1
            )
            steps.append(step)
        
        return steps
    
    def _resolve_dependencies(self, steps: List[PlanningStep]) -> None:
        """Resolve dependencies between steps."""
        step_map = {step.id: step for step in steps}
        
        for step in steps:
            dependencies = []
            
            # Check base tool dependencies
            if step.step_type == StepType.TOOL_INSTALL:
                tool_deps = self.base_tool_dependencies.get(step.name, [])
                for dep in tool_deps:
                    dep_id = f"tool_{dep.lower().replace(' ', '_')}"
                    if dep_id in step_map:
                        dependencies.append(dep_id)
            
            # Check extension dependencies
            elif step.step_type == StepType.EXTENSION_INSTALL:
                ext_deps = self.extension_dependencies.get(step.name, [])
                for dep in ext_deps:
                    dep_id = f"tool_{dep.lower().replace(' ', '_')}"
                    if dep_id in step_map:
                        dependencies.append(dep_id)
            
            # Validation steps depend on their corresponding installation steps
            elif step.step_type == StepType.VALIDATION:
                if step.name.startswith("Validate "):
                    tool_name = step.name[9:]  # Remove "Validate " prefix
                    if step.is_extension:
                        dep_id = f"ext_{tool_name.lower().replace(' ', '_')}"
                    else:
                        dep_id = f"tool_{tool_name.lower().replace(' ', '_')}"
                    if dep_id in step_map:
                        dependencies.append(dep_id)
            
            step.dependencies = dependencies
    
    def _calculate_priority_order(self, steps: List[PlanningStep]) -> List[str]:
        """Calculate optimal execution order based on dependencies and priorities."""
        # Create dependency graph
        graph = {step.id: step.dependencies for step in steps}
        
        # Topological sort
        visited = set()
        temp_visited = set()
        order = []
        
        def dfs(node):
            if node in temp_visited:
                raise ValueError(f"Circular dependency detected: {node}")
            if node in visited:
                return
            
            temp_visited.add(node)
            
            for dep in graph.get(node, []):
                dfs(dep)
            
            temp_visited.remove(node)
            visited.add(node)
            order.append(node)
        
        for step_id in graph:
            if step_id not in visited:
                dfs(step_id)
        
        return order
    
    def _estimate_duration(self, steps: List[PlanningStep]) -> int:
        """Estimate total duration in minutes."""
        total_minutes = 0
        
        for step in steps:
            if step.step_type == StepType.TOOL_INSTALL:
                total_minutes += 3  # Average 3 minutes per tool
            elif step.step_type == StepType.EXTENSION_INSTALL:
                total_minutes += 1  # 1 minute per extension
            elif step.step_type == StepType.LOGIN_PORTAL:
                total_minutes += 2  # 2 minutes per login portal
            elif step.step_type == StepType.VALIDATION:
                total_minutes += 0.5  # 30 seconds per validation
        
        return int(total_minutes)
    
    def _generate_justification(self, tool_name: str, memory_context: str) -> str:
        """Generate justification for tool installation."""
        justifications = {
            "Python": "Essential for Python development, data science, and AI/ML workflows",
            "Node.js": "Required for JavaScript/TypeScript development and npm packages",
            "Git": "Version control system essential for collaborative development",
            "Docker": "Containerization platform for consistent development environments",
            "VS Code": "Popular code editor with extensive extension ecosystem",
            "Cursor": "AI-powered code editor optimized for AI/ML development",
            "Jupyter": "Interactive computing environment for data science and ML",
            "Postman": "API development and testing tool",
            "Terraform": "Infrastructure as Code tool for cloud resource management",
            "AWS CLI": "Command line interface for AWS services",
            "Google Cloud SDK": "Command line tools for Google Cloud Platform",
            "Azure CLI": "Command line interface for Microsoft Azure",
            "GitHub Copilot": "AI-powered code completion and pair programming",
            "Python Extension": "Enhanced Python development support in VS Code",
            "Jupyter Extension": "Jupyter notebook support in VS Code",
            "REST Client": "HTTP client for testing APIs directly in VS Code",
            "YAML Extension": "YAML language support and validation",
            "Markdownlint": "Markdown linting and formatting"
        }
        
        return justifications.get(tool_name, f"Required for {tool_name} development workflow")
    
    def _calculate_confidence(self, tool_name: str, memory_context: str) -> float:
        """Calculate confidence score for tool installation."""
        # Base confidence scores
        base_confidence = {
            "Python": 0.95,
            "Node.js": 0.9,
            "Git": 0.95,
            "Docker": 0.85,
            "VS Code": 0.9,
            "Cursor": 0.8,
            "Jupyter": 0.85,
            "Postman": 0.8,
            "Terraform": 0.75,
            "AWS CLI": 0.8,
            "Google Cloud SDK": 0.75,
            "Azure CLI": 0.75
        }
        
        confidence = base_confidence.get(tool_name, 0.7)
        
        # Adjust based on memory context
        if "failed" in memory_context.lower() and tool_name.lower() in memory_context.lower():
            confidence *= 0.8  # Reduce confidence if tool failed before
        
        if "successfully installed" in memory_context.lower() and tool_name.lower() in memory_context.lower():
            confidence *= 1.1  # Increase confidence if tool was installed before
        
        return min(confidence, 1.0)  # Cap at 1.0

class PlanExecutor:
    """
    Executes installation plans with progress tracking and error handling.
    """
    
    def __init__(self, plan: InstallationPlan):
        self.plan = plan
        self.current_step_index = 0
        self.execution_log = []
        
    def get_next_step(self) -> Optional[PlanningStep]:
        """Get the next step to execute."""
        if self.current_step_index >= len(self.plan.steps):
            return None
        
        # Find next pending step
        for i in range(self.current_step_index, len(self.plan.steps)):
            step = self.plan.steps[i]
            if step.status == StepStatus.PENDING and self._can_execute_step(step):
                self.current_step_index = i
                return step
        
        return None
    
    def _can_execute_step(self, step: PlanningStep) -> bool:
        """Check if a step can be executed (dependencies satisfied)."""
        for dep_id in step.dependencies:
            dep_step = self._find_step_by_id(dep_id)
            if not dep_step or dep_step.status != StepStatus.COMPLETED:
                return False
        return True
    
    def _find_step_by_id(self, step_id: str) -> Optional[PlanningStep]:
        """Find a step by its ID."""
        for step in self.plan.steps:
            if step.id == step_id:
                return step
        return None
    
    def start_step(self, step: PlanningStep) -> None:
        """Mark a step as started."""
        step.status = StepStatus.IN_PROGRESS
        step.start_time = datetime.now()
        self.execution_log.append(f"Started: {step.name}")
        logger.info(f"Started step: {step.name}")
    
    def complete_step(self, step: PlanningStep, version: Optional[str] = None) -> None:
        """Mark a step as completed."""
        step.status = StepStatus.COMPLETED
        step.end_time = datetime.now()
        step.version = version
        self.plan.completed_steps += 1
        self.execution_log.append(f"Completed: {step.name}")
        logger.info(f"Completed step: {step.name}")
    
    def fail_step(self, step: PlanningStep, error: str) -> None:
        """Mark a step as failed."""
        step.status = StepStatus.FAILED
        step.end_time = datetime.now()
        step.error_message = error
        self.plan.failed_steps += 1
        self.execution_log.append(f"Failed: {step.name} - {error}")
        logger.error(f"Failed step: {step.name} - {error}")
    
    def skip_step(self, step: PlanningStep, reason: str) -> None:
        """Mark a step as skipped."""
        step.status = StepStatus.SKIPPED
        step.end_time = datetime.now()
        step.error_message = f"Skipped: {reason}"
        self.plan.skipped_steps += 1
        self.execution_log.append(f"Skipped: {step.name} - {reason}")
        logger.info(f"Skipped step: {step.name} - {reason}")
    
    def retry_step(self, step: PlanningStep) -> bool:
        """Retry a failed step if possible."""
        if step.retry_count < step.max_retries:
            step.retry_count += 1
            step.status = StepStatus.RETRYING
            step.start_time = datetime.now()
            step.end_time = None
            step.error_message = None
            self.execution_log.append(f"Retrying: {step.name} (attempt {step.retry_count})")
            logger.info(f"Retrying step: {step.name} (attempt {step.retry_count})")
            return True
        return False
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current execution progress."""
        total = self.plan.total_steps
        completed = self.plan.completed_steps
        failed = self.plan.failed_steps
        skipped = self.plan.skipped_steps
        in_progress = len([s for s in self.plan.steps if s.status == StepStatus.IN_PROGRESS])
        
        return {
            "total_steps": total,
            "completed_steps": completed,
            "failed_steps": failed,
            "skipped_steps": skipped,
            "in_progress": in_progress,
            "pending_steps": total - completed - failed - skipped - in_progress,
            "progress_percentage": (completed / total * 100) if total > 0 else 0,
            "estimated_remaining": self._estimate_remaining_time()
        }
    
    def _estimate_remaining_time(self) -> int:
        """Estimate remaining time in minutes."""
        completed = self.plan.completed_steps
        total = self.plan.total_steps
        
        if completed == 0:
            return self.plan.estimated_duration
        
        # Calculate average time per step
        elapsed_time = 0
        for step in self.plan.steps:
            if step.status == StepStatus.COMPLETED and step.start_time and step.end_time:
                elapsed_time += (step.end_time - step.start_time).total_seconds()
        
        if completed == 0:
            return self.plan.estimated_duration
        
        avg_time_per_step = elapsed_time / completed / 60  # Convert to minutes
        remaining_steps = total - completed
        return int(avg_time_per_step * remaining_steps)
    
    def get_failed_steps(self) -> List[PlanningStep]:
        """Get list of failed steps."""
        return [step for step in self.plan.steps if step.status == StepStatus.FAILED]
    
    def get_retryable_steps(self) -> List[PlanningStep]:
        """Get list of steps that can be retried."""
        return [
            step for step in self.plan.steps 
            if step.status == StepStatus.FAILED and step.retry_count < step.max_retries
        ]
    
    def is_complete(self) -> bool:
        """Check if plan execution is complete."""
        return self.plan.completed_steps + self.plan.failed_steps + self.plan.skipped_steps >= self.plan.total_steps 