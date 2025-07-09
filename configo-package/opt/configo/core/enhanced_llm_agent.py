"""
Enhanced LLM Agent for CONFIGO - integrates memory, provides tool justifications, and supports self-healing.
"""

import logging
import yaml
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from core.ai import LLMClient
from core.memory import AgentMemory

logger = logging.getLogger(__name__)

@dataclass
class ToolRecommendation:
    """Enhanced tool recommendation with justification and confidence."""
    name: str
    install_command: str
    check_command: str
    justification: str
    confidence_score: float
    is_extension: bool = False
    extension_id: Optional[str] = None
    domain_tags: Optional[List[str]] = None
    priority: int = 5  # 1-10, higher is more important

@dataclass
class LLMResponse:
    """Structured LLM response with multiple components."""
    tools: List[ToolRecommendation]
    login_portals: List[Dict[str, str]]
    reasoning: str
    improvement_suggestions: List[str]
    confidence_score: float
    domain_completion: Dict[str, Any]

class EnhancedLLMAgent:
    """
    Enhanced LLM agent with memory integration, domain awareness, and self-healing capabilities.
    """
    
    def __init__(self, memory: AgentMemory):
        self.llm_client = LLMClient()
        self.memory = memory
        
        # Domain-specific tool mappings
        self.domain_tools = {
            "ai_ml": {
                "essential": ["Python", "Cursor", "Jupyter", "Git"],
                "recommended": ["Docker", "Postman", "GitHub Copilot"],
                "extensions": ["GitHub Copilot", "Python Extension", "Jupyter Extension"],
                "login_portals": ["GitHub", "OpenAI", "Anthropic", "Hugging Face"]
            },
            "web_dev": {
                "essential": ["Node.js", "Git", "VS Code"],
                "recommended": ["Docker", "Postman", "GitHub Copilot"],
                "extensions": ["GitHub Copilot", "JavaScript Extension", "REST Client"],
                "login_portals": ["GitHub", "Netlify", "Vercel", "AWS"]
            },
            "data_science": {
                "essential": ["Python", "Jupyter", "Git"],
                "recommended": ["Docker", "Postman", "VS Code"],
                "extensions": ["Python Extension", "Jupyter Extension", "Data Science Extensions"],
                "login_portals": ["GitHub", "Kaggle", "Google Colab", "Hugging Face"]
            },
            "devops": {
                "essential": ["Docker", "Git", "VS Code"],
                "recommended": ["Terraform", "AWS CLI", "Google Cloud SDK"],
                "extensions": ["Docker Extension", "YAML Extension", "Terraform Extension"],
                "login_portals": ["GitHub", "AWS", "Google Cloud", "Azure"]
            }
        }
        
        logger.info("Enhanced LLM agent initialized")
    
    def generate_enhanced_stack(self, environment: str, stack_info: Optional[str] = None) -> LLMResponse:
        """
        Generate enhanced stack recommendations with memory context and domain awareness.
        
        Args:
            environment: Environment description
            stack_info: Optional project scan information
            
        Returns:
            LLMResponse: Structured response with tools, reasoning, and suggestions
        """
        try:
            # Get memory context
            memory_context = self.memory.get_memory_context()
            
            # Create enhanced prompt
            enhanced_prompt = self._create_enhanced_prompt(environment, stack_info, memory_context)
            
            # Generate response from LLM
            raw_response = self.llm_client.generate_config(enhanced_prompt) or ""
            
            # Parse and enhance response
            parsed_response = self._parse_enhanced_response(raw_response, environment)
            
            # Apply domain-aware completions
            completed_response = self._apply_domain_completion(parsed_response, environment)
            
            # Calculate overall confidence
            confidence = self._calculate_overall_confidence(completed_response)
            
            # Generate improvement suggestions
            suggestions = self._generate_improvement_suggestions(completed_response, environment)
            
            # Create final response
            response = LLMResponse(
                tools=completed_response["tools"],
                login_portals=completed_response["login_portals"],
                reasoning=completed_response["reasoning"],
                improvement_suggestions=suggestions,
                confidence_score=confidence,
                domain_completion=completed_response["domain_completion"]
            )
            
            logger.info(f"Generated enhanced stack with {len(response.tools)} tools")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate enhanced stack: {e}")
            # Return fallback response
            return self._generate_fallback_response(environment)
    
    def _create_enhanced_prompt(self, environment: str, stack_info: Optional[str], memory_context: str) -> str:
        """Create enhanced prompt with memory context and domain awareness."""
        
        prompt = f"""
You are an expert in configuring full-stack development environments for Linux systems.

ENVIRONMENT: {environment}

PROJECT CONTEXT: {stack_info or "No project scan available"}

MEMORY CONTEXT:
{memory_context}

Generate a comprehensive YAML configuration that includes ALL necessary components for this development environment.

IMPORTANT REQUIREMENTS:
- I am on Linux (Ubuntu/Debian). Use apt-get, snap, or other Linux package managers. Do NOT use brew (macOS).
- For AI/ML environments, prefer Cursor Editor over VS Code
- Include domain-specific extensions and tools
- Include all necessary login portals for the domain
- Provide justifications for each tool recommendation
- Consider previous installation history and failures

YAML STRUCTURE:
```yaml
base_tools:
  - name: "Tool Name"
    install_command: "Linux installation command"
    check_command: "command to check if installed"
    justification: "Why this tool is needed"
    confidence_score: 0.85
    priority: 8

editor:
  - name: "Editor Name (Cursor for AI, VS Code for others)"
    install_command: "Linux installation command"
    check_command: "command to check if installed"
    justification: "Why this editor is recommended"
    confidence_score: 0.9
    priority: 9

extensions:
  - name: "Extension Name"
    type: "vscode-extension"
    id: "extension.id"
    install_command: ""
    justification: "Why this extension is useful"
    confidence_score: 0.8
    priority: 6

cli_tools:
  - name: "CLI Tool Name"
    install_command: "Linux installation command"
    check_command: "command to check if installed"
    justification: "Why this CLI tool is needed"
    confidence_score: 0.75
    priority: 5

login_portals:
  - name: "Portal Name"
    url: "https://portal-url.com"
    description: "Brief description"
    justification: "Why this login portal is required"

reasoning: "Overall reasoning for this stack selection"
domain_completion:
  detected_domain: "ai_ml|web_dev|data_science|devops"
  missing_tools: ["list of tools that might be missing"]
  alternative_suggestions: ["alternative tool suggestions"]
```

DOMAIN-SPECIFIC REQUIREMENTS:

For AI/ML environments:
- Base tools: Python, Docker, Git, Jupyter
- Editor: Cursor (preferred) or VS Code
- Extensions: GitHub Copilot, Gemini Code Assist, RoCode, Cline, Augment, KiloCode
- CLI tools: Gemini CLI, Claude Code CLI
- Login portals: ChatGPT, Claude, Gemini, Grok, Hugging Face

For Web Development:
- Base tools: Node.js, Git, Docker
- Editor: VS Code
- Extensions: JavaScript/TypeScript extensions, Prettier, ESLint
- Login portals: GitHub, Netlify, Vercel

For Data Science:
- Base tools: Python, Jupyter, Git
- Editor: VS Code or Jupyter Lab
- Extensions: Python, Jupyter, Data Science extensions
- Login portals: Kaggle, Google Colab, Hugging Face

IMPORTANT: Return ONLY valid YAML without any markdown formatting, explanations, or code blocks. The response should start directly with the YAML content.
"""
        
        return prompt
    
    def _parse_enhanced_response(self, yaml_response: str, environment: str) -> Dict[str, Any]:
        """Parse enhanced YAML response with justifications and confidence scores."""
        try:
            config = yaml.safe_load(yaml_response)
            if not config:
                raise ValueError("Empty config received")
            
            tools = []
            login_portals = []
            reasoning = config.get("reasoning", "No reasoning provided")
            domain_completion = config.get("domain_completion", {})
            
            # Parse base tools
            base_tools = config.get("base_tools", [])
            for item in base_tools:
                if isinstance(item, dict):
                    tool = ToolRecommendation(
                        name=item.get("name", "Unknown Tool"),
                        install_command=item.get("install_command", ""),
                        check_command=item.get("check_command", item.get("name", "").lower()),
                        justification=item.get("justification", f"Required for {item.get('name', 'development')}"),
                        confidence_score=item.get("confidence_score", 0.8),
                        priority=item.get("priority", 5),
                        domain_tags=item.get("domain_tags", [])
                    )
                    tools.append(tool)
            
            # Parse editor
            editor = config.get("editor", [])
            if isinstance(editor, list):
                for item in editor:
                    if isinstance(item, dict):
                        tool = ToolRecommendation(
                            name=item.get("name", "Unknown Editor"),
                            install_command=item.get("install_command", ""),
                            check_command=item.get("check_command", item.get("name", "").lower()),
                            justification=item.get("justification", f"Primary editor for {environment}"),
                            confidence_score=item.get("confidence_score", 0.9),
                            priority=item.get("priority", 9),
                            domain_tags=item.get("domain_tags", [])
                        )
                        tools.append(tool)
            
            # Parse extensions
            extensions = config.get("extensions", [])
            for item in extensions:
                if isinstance(item, dict):
                    tool = ToolRecommendation(
                        name=item.get("name", "Unknown Extension"),
                        install_command="",  # Extensions installed via VS Code CLI
                        check_command="code --list-extensions",
                        justification=item.get("justification", f"Useful extension for {environment}"),
                        confidence_score=item.get("confidence_score", 0.7),
                        priority=item.get("priority", 4),
                        is_extension=True,
                        extension_id=item.get("id", ""),
                        domain_tags=item.get("domain_tags", [])
                    )
                    tools.append(tool)
            
            # Parse CLI tools
            cli_tools = config.get("cli_tools", [])
            for item in cli_tools:
                if isinstance(item, dict):
                    tool = ToolRecommendation(
                        name=item.get("name", "Unknown CLI Tool"),
                        install_command=item.get("install_command", ""),
                        check_command=item.get("check_command", item.get("name", "").lower()),
                        justification=item.get("justification", f"CLI tool for {environment}"),
                        confidence_score=item.get("confidence_score", 0.75),
                        priority=item.get("priority", 3),
                        domain_tags=item.get("domain_tags", [])
                    )
                    tools.append(tool)
            
            # Parse login portals
            portals = config.get("login_portals", [])
            for portal in portals:
                if isinstance(portal, dict):
                    login_portal = {
                        "name": portal.get("name", "Unknown Portal"),
                        "url": portal.get("url", ""),
                        "description": portal.get("description", ""),
                        "justification": portal.get("justification", f"Required for {environment}")
                    }
                    login_portals.append(login_portal)
            
            return {
                "tools": tools,
                "login_portals": login_portals,
                "reasoning": reasoning,
                "domain_completion": domain_completion
            }
            
        except Exception as e:
            logger.error(f"Failed to parse enhanced response: {e}")
            raise
    
    def _apply_domain_completion(self, parsed_response: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Apply domain-aware completions to fill missing tools."""
        detected_domain = self._detect_domain(environment)
        tools = parsed_response["tools"]
        
        # Get domain-specific tools
        domain_config = self.domain_tools.get(detected_domain, {})
        
        # Check for missing essential tools
        existing_tool_names = [tool.name for tool in tools]
        missing_essential = [tool for tool in domain_config.get("essential", []) 
                           if tool not in existing_tool_names]
        
        # Add missing essential tools
        for tool_name in missing_essential:
            tool = self._create_domain_tool(tool_name, detected_domain, "essential")
            tools.append(tool)
        
        # Check for missing recommended tools (add some based on confidence)
        missing_recommended = [tool for tool in domain_config.get("recommended", []) 
                             if tool not in existing_tool_names]
        
        # Add some recommended tools based on domain
        for tool_name in missing_recommended[:2]:  # Limit to 2 recommended tools
            tool = self._create_domain_tool(tool_name, detected_domain, "recommended")
            tools.append(tool)
        
        # Check for missing extensions
        existing_extensions = [tool.name for tool in tools if tool.is_extension]
        missing_extensions = [ext for ext in domain_config.get("extensions", []) 
                            if ext not in existing_extensions]
        
        # Add missing extensions
        for ext_name in missing_extensions[:3]:  # Limit to 3 extensions
            tool = self._create_domain_extension(ext_name, detected_domain)
            tools.append(tool)
        
        # Check for missing login portals
        existing_portals = [portal["name"] for portal in parsed_response["login_portals"]]
        missing_portals = [portal for portal in domain_config.get("login_portals", []) 
                          if portal not in existing_portals]
        
        # Add missing login portals
        for portal_name in missing_portals:
            portal = self._create_domain_portal(portal_name, detected_domain)
            parsed_response["login_portals"].append(portal)
        
        # Update domain completion info
        parsed_response["domain_completion"]["detected_domain"] = detected_domain
        parsed_response["domain_completion"]["missing_tools"] = missing_essential + missing_recommended
        parsed_response["domain_completion"]["added_tools"] = [tool.name for tool in tools if tool.name in missing_essential + missing_recommended]
        
        return parsed_response
    
    def _detect_domain(self, environment: str) -> str:
        """Detect the primary domain from environment description."""
        environment_lower = environment.lower()
        
        if any(keyword in environment_lower for keyword in ["ai", "ml", "machine learning", "artificial intelligence", "neural", "tensorflow", "pytorch"]):
            return "ai_ml"
        elif any(keyword in environment_lower for keyword in ["web", "frontend", "backend", "full stack", "javascript", "react", "angular", "vue"]):
            return "web_dev"
        elif any(keyword in environment_lower for keyword in ["data", "analytics", "science", "pandas", "numpy", "matplotlib"]):
            return "data_science"
        elif any(keyword in environment_lower for keyword in ["devops", "infrastructure", "deployment", "kubernetes", "docker", "terraform"]):
            return "devops"
        else:
            return "ai_ml"  # Default to AI/ML
    
    def _create_domain_tool(self, tool_name: str, domain: str, priority: str) -> ToolRecommendation:
        """Create a domain-specific tool recommendation."""
        # Tool installation commands
        install_commands = {
            "Python": "sudo apt-get update && sudo apt-get install -y python3 python3-pip",
            "Node.js": "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs",
            "Git": "sudo apt-get update && sudo apt-get install -y git",
            "Docker": "sudo apt-get update && sudo apt-get install -y docker.io",
            "VS Code": "sudo apt-get update && sudo apt-get install -y code",
            "Cursor": "curl -L https://download.cursor.sh/linux/appImage/x64/cursor-latest.AppImage -o cursor && chmod +x cursor && sudo mv cursor /usr/local/bin/",
            "Jupyter": "pip3 install jupyter",
            "Postman": "sudo snap install postman",
            "Terraform": "curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add - && sudo apt-add-repository \"deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main\" && sudo apt-get update && sudo apt-get install terraform",
            "AWS CLI": "sudo apt-get update && sudo apt-get install awscli",
            "Google Cloud SDK": "curl -sSL https://sdk.cloud.google.com | bash && exec -l $SHELL && gcloud init"
        }
        
        # Tool check commands
        check_commands = {
            "Python": "python3 --version",
            "Node.js": "node --version",
            "Git": "git --version",
            "Docker": "docker --version",
            "VS Code": "code --version",
            "Cursor": "cursor --version",
            "Jupyter": "jupyter --version",
            "Postman": "postman --version",
            "Terraform": "terraform --version",
            "AWS CLI": "aws --version",
            "Google Cloud SDK": "gcloud --version"
        }
        
        # Justifications
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
            "Google Cloud SDK": "Command line tools for Google Cloud Platform"
        }
        
        return ToolRecommendation(
            name=tool_name,
            install_command=install_commands.get(tool_name, f"sudo apt-get install {tool_name.lower()}"),
            check_command=check_commands.get(tool_name, tool_name.lower()),
            justification=justifications.get(tool_name, f"Required for {domain} development"),
            confidence_score=0.8 if priority == "essential" else 0.6,
            priority=9 if priority == "essential" else 5,
            domain_tags=[domain]
        )
    
    def _create_domain_extension(self, ext_name: str, domain: str) -> ToolRecommendation:
        """Create a domain-specific extension recommendation."""
        extension_ids = {
            "GitHub Copilot": "github.copilot",
            "Python Extension": "ms-python.python",
            "Jupyter Extension": "ms-toolsai.jupyter",
            "REST Client": "humao.rest-client",
            "YAML Extension": "redhat.vscode-yaml",
            "Markdownlint": "davidanson.vscode-markdownlint",
            "JavaScript Extension": "ms-vscode.vscode-typescript-next",
            "Docker Extension": "ms-azuretools.vscode-docker",
            "Terraform Extension": "hashicorp.terraform"
        }
        
        justifications = {
            "GitHub Copilot": "AI-powered code completion and pair programming",
            "Python Extension": "Enhanced Python development support in VS Code",
            "Jupyter Extension": "Jupyter notebook support in VS Code",
            "REST Client": "HTTP client for testing APIs directly in VS Code",
            "YAML Extension": "YAML language support and validation",
            "Markdownlint": "Markdown linting and formatting",
            "JavaScript Extension": "Enhanced JavaScript/TypeScript support",
            "Docker Extension": "Docker container management in VS Code",
            "Terraform Extension": "Terraform infrastructure management in VS Code"
        }
        
        return ToolRecommendation(
            name=ext_name,
            install_command="",
            check_command="code --list-extensions",
            justification=justifications.get(ext_name, f"Useful extension for {domain} development"),
            confidence_score=0.7,
            priority=4,
            is_extension=True,
            extension_id=extension_ids.get(ext_name, ""),
            domain_tags=[domain]
        )
    
    def _create_domain_portal(self, portal_name: str, domain: str) -> Dict[str, str]:
        """Create a domain-specific login portal recommendation."""
        portal_urls = {
            "GitHub": "https://github.com",
            "OpenAI": "https://platform.openai.com",
            "Anthropic": "https://console.anthropic.com",
            "Hugging Face": "https://huggingface.co",
            "Netlify": "https://app.netlify.com",
            "Vercel": "https://vercel.com",
            "AWS": "https://aws.amazon.com",
            "Google Cloud": "https://console.cloud.google.com",
            "Azure": "https://portal.azure.com",
            "Kaggle": "https://www.kaggle.com",
            "Google Colab": "https://colab.research.google.com"
        }
        
        descriptions = {
            "GitHub": "Version control and code hosting platform",
            "OpenAI": "AI model access and API management",
            "Anthropic": "Claude AI model access and API management",
            "Hugging Face": "AI model repository and hosting platform",
            "Netlify": "Web application deployment and hosting",
            "Vercel": "Frontend deployment and hosting platform",
            "AWS": "Cloud computing and infrastructure services",
            "Google Cloud": "Cloud computing and AI services",
            "Azure": "Microsoft cloud computing platform",
            "Kaggle": "Data science competitions and datasets",
            "Google Colab": "Cloud-based Jupyter notebook environment"
        }
        
        return {
            "name": portal_name,
            "url": portal_urls.get(portal_name, f"https://{portal_name.lower().replace(' ', '')}.com"),
            "description": descriptions.get(portal_name, f"Required for {domain} development"),
            "justification": f"Login required for {portal_name} services"
        }
    
    def _calculate_overall_confidence(self, response: Dict[str, Any]) -> float:
        """Calculate overall confidence score for the response."""
        tools = response["tools"]
        if not tools:
            return 0.5
        
        # Calculate weighted average confidence
        total_confidence = sum(tool.confidence_score * tool.priority for tool in tools)
        total_priority = sum(tool.priority for tool in tools)
        
        if total_priority == 0:
            return 0.5
        
        return total_confidence / total_priority
    
    def _generate_improvement_suggestions(self, response: Dict[str, Any], environment: str) -> List[str]:
        """Generate improvement suggestions based on the response."""
        suggestions = []
        tools = response["tools"]
        
        # Check for missing high-priority tools
        low_priority_tools = [tool for tool in tools if tool.priority < 5]
        if low_priority_tools:
            suggestions.append(f"Consider adding higher-priority tools for better {environment} development experience")
        
        # Check for domain-specific suggestions
        detected_domain = response["domain_completion"].get("detected_domain", "")
        if detected_domain == "ai_ml":
            suggestions.append("Consider setting up GPU support for faster AI model training")
            suggestions.append("Install additional AI libraries like TensorFlow or PyTorch")
        elif detected_domain == "web_dev":
            suggestions.append("Consider adding a database tool like PostgreSQL or MongoDB")
            suggestions.append("Install a package manager like npm or yarn")
        elif detected_domain == "data_science":
            suggestions.append("Consider adding data visualization tools like Tableau or Power BI")
            suggestions.append("Install additional data science libraries like pandas, numpy, matplotlib")
        
        # General suggestions
        suggestions.append("Set up automated backups for your development environment")
        suggestions.append("Consider using a version control workflow with feature branches")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _generate_fallback_response(self, environment: str) -> LLMResponse:
        """Generate a fallback response when LLM fails."""
        logger.warning("Using fallback response due to LLM failure")
        
        # Create basic tools based on environment
        tools = [
            ToolRecommendation(
                name="Python",
                install_command="sudo apt-get update && sudo apt-get install -y python3 python3-pip",
                check_command="python3 --version",
                justification="Essential for Python development",
                confidence_score=0.9,
                priority=9
            ),
            ToolRecommendation(
                name="Git",
                install_command="sudo apt-get update && sudo apt-get install -y git",
                check_command="git --version",
                justification="Version control system",
                confidence_score=0.95,
                priority=9
            )
        ]
        
        login_portals = [
            {
                "name": "GitHub",
                "url": "https://github.com",
                "description": "Version control and code hosting",
                "justification": "Required for code management"
            }
        ]
        
        return LLMResponse(
            tools=tools,
            login_portals=login_portals,
            reasoning="Fallback configuration due to LLM unavailability",
            improvement_suggestions=["Try again later for more comprehensive recommendations"],
            confidence_score=0.6,
            domain_completion={"detected_domain": "unknown", "missing_tools": [], "alternative_suggestions": []}
        )
    
    def generate_command_fix(self, command: str, error: str, tool_name: str) -> Optional[str]:
        """
        Generate a fixed command for a failed installation.
        
        Args:
            command: The failed command
            error: The error output
            tool_name: Name of the tool that failed
            
        Returns:
            Optional[str]: Fixed command or None if generation fails
        """
        try:
            # Get tool-specific context from memory
            tool_context = self.memory.get_tool_justification_context(tool_name)
            
            # Create enhanced fix prompt
            fix_prompt = f"""
The following shell command failed during {tool_name} installation on Linux:

Command: {command}
Error: {error}
Tool: {tool_name}
Tool Context: {tool_context}

IMPORTANT: I am on Linux (Ubuntu/Debian). Return ONLY a fixed shell command that should work on Linux. 
Use apt-get, snap, or other Linux package managers. Do NOT use brew.
The command must be safe and not contain dangerous operations.

Consider the error message and provide an alternative approach if the original command failed.

Return only the command, no explanations or YAML formatting.
"""
            
            # Use the LLM client to generate a fix
            fixed_command = self.llm_client.generate_config(fix_prompt)
            if fixed_command and fixed_command.strip():
                # Clean up the response
                fixed_command = fixed_command.strip()
                # Remove any markdown formatting
                if fixed_command.startswith("```"):
                    fixed_command = fixed_command.split("\n", 1)[1] if "\n" in fixed_command else ""
                if fixed_command.endswith("```"):
                    fixed_command = fixed_command.rsplit("\n", 1)[0] if "\n" in fixed_command else ""
                
                logger.info(f"Generated fix for {tool_name}: {fixed_command}")
                return fixed_command
            
        except Exception as e:
            logger.error(f"Failed to generate command fix for {tool_name}: {e}")
        
        return None
    
    def get_tool_justification(self, tool_name: str) -> str:
        """Get justification for a specific tool."""
        # Check memory first
        tool_memory = self.memory.get_tool_memory(tool_name)
        if tool_memory:
            if tool_memory.install_success:
                return f"{tool_name} was successfully installed previously and is essential for development"
            else:
                return f"{tool_name} failed installation before, but is still recommended for this environment"
        
        # Return default justification
        justifications = {
            "Python": "Essential for Python development, data science, and AI/ML workflows",
            "Node.js": "Required for JavaScript/TypeScript development and npm packages",
            "Git": "Version control system essential for collaborative development",
            "Docker": "Containerization platform for consistent development environments",
            "VS Code": "Popular code editor with extensive extension ecosystem",
            "Cursor": "AI-powered code editor optimized for AI/ML development"
        }
        
        return justifications.get(tool_name, f"Required for {tool_name} development workflow")

    def get_install_plan(self, app_name: str, system_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate installation plan for an app using natural language.
        
        Args:
            app_name: Name of the app to install (e.g., "Discord", "Chrome")
            system_info: System information from get_system_info()
            
        Returns:
            Optional[Dict[str, Any]]: Installation plan in YAML format or None if failed
        """
        try:
            # Create prompt for app installation
            prompt = f"""
I am using:
- OS: {system_info['os']}
- Distro: {system_info['distro']}
- Architecture: {system_info['arch']}
- Package managers: {', '.join(system_info['package_managers'])}

Please give me a complete installation plan for "{app_name}":

1. Best command to install "{app_name}"
2. Check command (to validate install)
3. How to launch it
4. Optional icon path or shortcut instructions
5. Fallback: download URL if not available in packages

Return in clean YAML format:
```yaml
app: "{app_name}"
method: "package_manager_name"
install: |
  command1
  command2
check: "command to check if installed"
launch: "command to launch app"
desktop_entry:
  path: "/path/to/desktop/file.desktop"
  icon: "/path/to/icon.png"
fallback_url: "https://download.url/if/needed"
```

IMPORTANT: 
- Use the available package managers: {', '.join(system_info['package_managers'])}
- For Linux, prefer apt, snap, or flatpak
- For macOS, use brew or direct download
- For Windows, use winget, choco, or direct download
- Return ONLY the YAML, no explanations
"""
            
            # Generate response from LLM
            raw_response = self.llm_client.generate_config(prompt) or ""
            
            # Parse YAML response
            if raw_response.strip():
                # Extract YAML from response if it's wrapped in code blocks
                yaml_content = raw_response.strip()
                if yaml_content.startswith("```yaml"):
                    yaml_content = yaml_content.split("\n", 1)[1]
                if yaml_content.endswith("```"):
                    yaml_content = yaml_content.rsplit("\n", 1)[0]
                
                # Parse YAML
                import yaml
                plan = yaml.safe_load(yaml_content)
                
                if plan and isinstance(plan, dict):
                    logger.info(f"Generated install plan for {app_name}: {plan.get('method', 'unknown')}")
                    return plan
            
        except Exception as e:
            logger.error(f"Failed to generate install plan for {app_name}: {e}")
        
        return None

    def get_error_fix(self, command: str, error: str, app_name: str) -> Optional[str]:
        """
        Generate a fixed command for a failed app installation.
        
        Args:
            command: The failed command
            error: The error output
            app_name: Name of the app that failed
            
        Returns:
            Optional[str]: Fixed command or None if generation fails
        """
        try:
            # Create enhanced fix prompt
            fix_prompt = f"""
I ran the following command to install {app_name}:

Command: {command}
Error: {error}

Please suggest a corrected command or workaround.
Respond with only the fixed command (no explanation).
"""
            
            # Use the LLM client to generate a fix
            fixed_command = self.llm_client.generate_config(fix_prompt)
            if fixed_command and fixed_command.strip():
                # Clean up the response
                fixed_command = fixed_command.strip()
                # Remove any markdown formatting
                if fixed_command.startswith("```"):
                    fixed_command = fixed_command.split("\n", 1)[1] if "\n" in fixed_command else ""
                if fixed_command.endswith("```"):
                    fixed_command = fixed_command.rsplit("\n", 1)[0] if "\n" in fixed_command else ""
                
                logger.info(f"Generated fix for {app_name}: {fixed_command}")
                return fixed_command
            
        except Exception as e:
            logger.error(f"Failed to generate error fix for {app_name}: {e}")
        
        return None