"""
CONFIGO Core Planner
====================

Handles installation planning and strategy generation using the agent engine.
Creates comprehensive installation plans based on user requirements.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class InstallationStep:
    """Represents a single installation step in a plan."""
    name: str
    command: str
    description: str
    tool_name: str
    is_extension: bool = False
    extension_id: Optional[str] = None
    dependencies: List[str] = None
    timeout: int = 300
    priority: int = 1  # 1 = highest priority
    
    def __post_init__(self):
        """Initialize default values."""
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class InstallationPlan:
    """Complete installation plan with multiple steps."""
    name: str
    description: str
    environment: str
    steps: List[InstallationStep]
    created_at: datetime
    estimated_duration: int = 0  # minutes
    complexity: str = "medium"  # low, medium, high
    lite_mode: bool = False
    
    def __post_init__(self):
        """Initialize default values."""
        if not self.created_at:
            self.created_at = datetime.now()


class Planner:
    """
    Core planner for CONFIGO installation strategies.
    
    Creates comprehensive installation plans based on user requirements
    and system analysis.
    """
    
    def __init__(self, agent_engine, memory_store):
        """Initialize the planner."""
        self.agent = agent_engine
        self.memory = memory_store
        self.plan_cache = {}
        
        logger.info("CONFIGO Planner initialized")
    
    def create_plan(self, environment_description: str, lite_mode: bool = False) -> InstallationPlan:
        """
        Create a comprehensive installation plan.
        
        Args:
            environment_description: User's environment description
            lite_mode: Whether to use lite mode (faster, less comprehensive)
            
        Returns:
            InstallationPlan: Complete installation plan
        """
        logger.info(f"Creating installation plan for: {environment_description}")
        
        # Check cache first
        cache_key = f"{environment_description}_{lite_mode}"
        if cache_key in self.plan_cache:
            logger.info("Using cached plan")
            return self.plan_cache[cache_key]
        
        # Generate plan using agent
        plan_data = self.agent.generate_installation_plan(environment_description, lite_mode)
        
        # Convert to InstallationPlan
        plan = self._create_plan_from_data(plan_data, environment_description, lite_mode)
        
        # Cache the plan
        self.plan_cache[cache_key] = plan
        
        return plan
    
    def _create_plan_from_data(self, plan_data: Dict[str, Any], environment: str, lite_mode: bool) -> InstallationPlan:
        """Create InstallationPlan from agent-generated data."""
        steps = []
        
        for step_data in plan_data.get('steps', []):
            step = InstallationStep(
                name=step_data.get('name', 'unknown'),
                command=step_data.get('command', ''),
                description=step_data.get('description', ''),
                tool_name=step_data.get('tool_name', 'unknown'),
                is_extension=step_data.get('is_extension', False),
                extension_id=step_data.get('extension_id'),
                dependencies=step_data.get('dependencies', []),
                timeout=step_data.get('timeout', 300),
                priority=step_data.get('priority', 1)
            )
            steps.append(step)
        
        # Sort steps by priority
        steps.sort(key=lambda x: x.priority)
        
        # Calculate estimated duration
        estimated_duration = sum(step.timeout for step in steps) // 60  # Convert to minutes
        
        # Determine complexity
        complexity = self._determine_complexity(steps, lite_mode)
        
        plan = InstallationPlan(
            name=plan_data.get('name', f'Plan for {environment}'),
            description=plan_data.get('description', f'Installation plan for {environment}'),
            environment=environment,
            steps=steps,
            created_at=datetime.now(),
            estimated_duration=estimated_duration,
            complexity=complexity,
            lite_mode=lite_mode
        )
        
        return plan
    
    def _determine_complexity(self, steps: List[InstallationStep], lite_mode: bool) -> str:
        """Determine the complexity of an installation plan."""
        if lite_mode:
            return "low"
        
        num_steps = len(steps)
        num_extensions = len([s for s in steps if s.is_extension])
        total_dependencies = sum(len(s.dependencies) for s in steps)
        
        if num_steps <= 3 and num_extensions <= 1 and total_dependencies <= 2:
            return "low"
        elif num_steps <= 8 and num_extensions <= 3 and total_dependencies <= 5:
            return "medium"
        else:
            return "high"
    
    def optimize_plan(self, plan: InstallationPlan) -> InstallationPlan:
        """
        Optimize an installation plan based on memory and system analysis.
        
        Args:
            plan: Original installation plan
            
        Returns:
            InstallationPlan: Optimized plan
        """
        logger.info("Optimizing installation plan")
        
        optimized_steps = []
        
        for step in plan.steps:
            # Check if tool is already installed
            if self.memory.is_tool_installed(step.tool_name):
                logger.info(f"Skipping {step.tool_name} - already installed")
                continue
            
            # Check if tool should be skipped based on memory
            if self.memory.should_skip_tool(step.tool_name):
                logger.info(f"Skipping {step.tool_name} - marked for skip")
                continue
            
            # Add step to optimized plan
            optimized_steps.append(step)
        
        # Create optimized plan
        optimized_plan = InstallationPlan(
            name=f"{plan.name} (Optimized)",
            description=f"{plan.description} - Optimized based on system analysis",
            environment=plan.environment,
            steps=optimized_steps,
            created_at=datetime.now(),
            estimated_duration=sum(step.timeout for step in optimized_steps) // 60,
            complexity=self._determine_complexity(optimized_steps, plan.lite_mode),
            lite_mode=plan.lite_mode
        )
        
        return optimized_plan
    
    def validate_plan(self, plan: InstallationPlan) -> Dict[str, Any]:
        """
        Validate an installation plan for potential issues.
        
        Args:
            plan: Installation plan to validate
            
        Returns:
            Dict[str, Any]: Validation results
        """
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': []
        }
        
        # Check for missing dependencies
        for step in plan.steps:
            for dep in step.dependencies:
                if not self._check_dependency_available(dep):
                    validation_results['warnings'].append(
                        f"Dependency '{dep}' for {step.tool_name} may not be available"
                    )
        
        # Check for potential conflicts
        tool_names = [step.tool_name for step in plan.steps]
        if len(tool_names) != len(set(tool_names)):
            validation_results['warnings'].append(
                "Duplicate tool installations detected in plan"
            )
        
        # Check for long installation times
        total_time = sum(step.timeout for step in plan.steps)
        if total_time > 1800:  # 30 minutes
            validation_results['suggestions'].append(
                "Consider using lite mode for faster installation"
            )
        
        # Check for high complexity
        if plan.complexity == "high":
            validation_results['suggestions'].append(
                "Consider breaking this into smaller, focused installations"
            )
        
        # Check for missing commands
        for step in plan.steps:
            if not step.command.strip():
                validation_results['errors'].append(
                    f"Missing installation command for {step.tool_name}"
                )
        
        # Update validity
        validation_results['valid'] = len(validation_results['errors']) == 0
        
        return validation_results
    
    def _check_dependency_available(self, dependency: str) -> bool:
        """Check if a dependency is available on the system."""
        import subprocess
        
        try:
            result = subprocess.run(
                f"which {dependency}".split(),
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_plan_summary(self, plan: InstallationPlan) -> Dict[str, Any]:
        """Generate a summary of the installation plan."""
        tool_types = {
            'tools': len([s for s in plan.steps if not s.is_extension]),
            'extensions': len([s for s in plan.steps if s.is_extension])
        }
        
        dependencies = set()
        for step in plan.steps:
            dependencies.update(step.dependencies)
        
        return {
            'name': plan.name,
            'description': plan.description,
            'environment': plan.environment,
            'total_steps': len(plan.steps),
            'tool_types': tool_types,
            'dependencies': list(dependencies),
            'estimated_duration': plan.estimated_duration,
            'complexity': plan.complexity,
            'lite_mode': plan.lite_mode,
            'created_at': plan.created_at.isoformat()
        }
    
    def create_quick_plan(self, tool_name: str) -> InstallationPlan:
        """
        Create a quick installation plan for a single tool.
        
        Args:
            tool_name: Name of the tool to install
            
        Returns:
            InstallationPlan: Quick installation plan
        """
        logger.info(f"Creating quick plan for {tool_name}")
        
        # Generate quick plan using agent
        plan_data = self.agent.generate_quick_plan(tool_name)
        
        # Create single step
        step = InstallationStep(
            name=f"Install {tool_name}",
            command=plan_data.get('command', f'apt-get install {tool_name}'),
            description=f"Quick installation of {tool_name}",
            tool_name=tool_name,
            timeout=300
        )
        
        plan = InstallationPlan(
            name=f"Quick Install: {tool_name}",
            description=f"Quick installation plan for {tool_name}",
            environment=tool_name,
            steps=[step],
            created_at=datetime.now(),
            estimated_duration=5,
            complexity="low",
            lite_mode=True
        )
        
        return plan
    
    def get_recommended_plans(self, environment_type: str) -> List[Dict[str, Any]]:
        """
        Get recommended installation plans for common environment types.
        
        Args:
            environment_type: Type of development environment
            
        Returns:
            List[Dict[str, Any]]: List of recommended plans
        """
        recommendations = {
            'web_development': {
                'name': 'Web Development Stack',
                'description': 'Full-stack web development environment',
                'tools': ['node', 'npm', 'git', 'vscode', 'docker'],
                'extensions': ['prettier', 'eslint', 'live-server']
            },
            'python_development': {
                'name': 'Python Development Stack',
                'description': 'Python development environment',
                'tools': ['python', 'pip', 'git', 'vscode'],
                'extensions': ['python', 'pylint', 'black']
            },
            'ai_development': {
                'name': 'AI Development Stack',
                'description': 'AI and machine learning environment',
                'tools': ['python', 'pip', 'git', 'docker', 'jupyter'],
                'extensions': ['python', 'jupyter', 'pylint']
            },
            'mobile_development': {
                'name': 'Mobile Development Stack',
                'description': 'Mobile app development environment',
                'tools': ['node', 'npm', 'git', 'android-studio'],
                'extensions': ['react-native', 'flutter']
            }
        }
        
        if environment_type in recommendations:
            return [recommendations[environment_type]]
        else:
            return []
    
    def clear_cache(self) -> None:
        """Clear the plan cache."""
        self.plan_cache.clear()
        logger.info("Plan cache cleared") 