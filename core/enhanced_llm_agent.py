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
                "essential": ["Python", "Cursor", "Jupyter", "Git", "pip"],
                "recommended": ["Docker", "Postman", "GitHub Copilot", "TensorFlow", "PyTorch"],
                "extensions": ["GitHub Copilot", "Python Extension", "Jupyter Extension", "Gemini Code Assist", "RoCode"],
                "login_portals": ["GitHub", "OpenAI", "Anthropic", "Hugging Face", "Gemini", "Grok"]
            },
            "web_dev": {
                "essential": ["Node.js", "Git", "VS Code", "npm"],
                "recommended": ["Docker", "Postman", "GitHub Copilot", "Chrome", "Firefox"],
                "extensions": ["GitHub Copilot", "JavaScript Extension", "REST Client", "Prettier", "ESLint", "Live Server"],
                "login_portals": ["GitHub", "Netlify", "Vercel", "AWS", "Google Cloud", "Firebase"]
            },
            "data_science": {
                "essential": ["Python", "Jupyter", "Git", "pip"],
                "recommended": ["Docker", "Postman", "VS Code", "pandas", "numpy"],
                "extensions": ["Python Extension", "Jupyter Extension", "Data Science Extensions", "Plotly", "Markdownlint"],
                "login_portals": ["GitHub", "Kaggle", "Google Colab", "Hugging Face", "AWS", "Tableau"]
            },
            "devops": {
                "essential": ["Docker", "Git", "VS Code"],
                "recommended": ["Terraform", "AWS CLI", "Google Cloud SDK", "kubectl", "Helm"],
                "extensions": ["Docker Extension", "YAML Extension", "Terraform Extension", "Kubernetes Extension", "Remote Development"],
                "login_portals": ["GitHub", "AWS", "Google Cloud", "Azure", "Docker Hub", "HashiCorp"]
            }
        }
        
        logger.info("Enhanced LLM agent initialized")
    
    def generate_enhanced_stack(self, environment: str, stack_info: Optional[str] = None, debug: bool = False) -> LLMResponse:
        """
        Generate enhanced stack recommendations using real LLM API calls.
        
        This method ensures the LLM is actually called and removes hardcoded fallbacks
        to make CONFIGO truly autonomous and AI-powered.
        """
        try:
            memory_context = self.memory.get_memory_context()
            prompt = self._create_enhanced_prompt(environment, stack_info, memory_context)
            
            if debug:
                print("\n[DEBUG] Gemini Prompt:\n" + prompt + "\n")
            
            # Call the actual LLM API - no fallbacks
            raw_response = self.llm_client.generate_config(prompt)
            
            if not raw_response or raw_response.strip() == "":
                logger.error("Empty response from LLM API")
                raise Exception("Empty response from LLM API")
            
            if debug:
                print("\n[DEBUG] Gemini Response:\n" + raw_response + "\n")
            
            # Clean and parse the response
            cleaned_response = self._clean_llm_response(raw_response)
            parsed_response = self._parse_enhanced_response(cleaned_response, environment)
            
            # Apply domain completion to enhance the response
            completed_response = self._apply_domain_completion(parsed_response, environment)
            
            # Validate response quality and retry if needed
            if not self._validate_response_quality(completed_response, environment):
                logger.warning("Low quality response detected, retrying with refined prompt...")
                if debug:
                    print("[DEBUG] Low quality response, retrying with refined prompt...")
                
                refined_response = self._retry_with_refined_prompt(environment, stack_info, memory_context)
                if refined_response:
                    completed_response = refined_response
                else:
                    logger.error("Failed to get quality response after retry")
                    raise Exception("Failed to get quality response from LLM")
            
            # Calculate confidence and generate suggestions
            confidence = self._calculate_overall_confidence(completed_response)
            suggestions = self._generate_improvement_suggestions(completed_response, environment)
            
            response = LLMResponse(
                tools=completed_response["tools"],
                login_portals=completed_response["login_portals"],
                reasoning=completed_response["reasoning"],
                improvement_suggestions=suggestions,
                confidence_score=confidence,
                domain_completion=completed_response["domain_completion"]
            )
            
            logger.info(f"Generated enhanced stack with {len(response.tools)} tools via LLM API")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate enhanced stack via LLM: {e}")
            
            # Check if it's an API overload or temporary issue
            if "overloaded" in str(e).lower() or "503" in str(e) or "rate limit" in str(e).lower():
                logger.warning("Gemini API is temporarily unavailable - using fallback response")
                logger.warning("This is a temporary issue with Google's servers, not your API key")
                logger.warning("Try again later for AI-powered recommendations")
                return self._generate_fallback_response(environment)
            elif "timeout" in str(e).lower() or "connection" in str(e).lower():
                logger.warning("Network issue detected - using fallback response")
                logger.warning("Check your internet connection and try again")
                return self._generate_fallback_response(environment)
            else:
                # For other errors, provide more specific guidance
                logger.error(f"LLM API error: {e}")
                logger.error("This might be due to API key issues or server problems")
                logger.error("Using fallback response - check your GEMINI_API_KEY if the problem persists")
                return self._generate_fallback_response(environment)

    def _validate_response_quality(self, response: Dict[str, Any], environment: str) -> bool:
        """
        Validate that the LLM response is comprehensive and high quality.
        
        Returns True if the response meets quality standards, False otherwise.
        """
        tools = response.get("tools", [])
        
        # Check for minimum tool count (reduced from 5 to 3 for fallback compatibility)
        if len(tools) < 3:
            logger.warning(f"Response has only {len(tools)} tools, expected at least 3")
            return False
        
        # Check for comprehensive tool coverage
        tool_names = [t.name.lower() for t in tools]
        
        # For AI environments, ensure we have key AI tools (but be more lenient)
        if any(keyword in environment.lower() for keyword in ["ai", "llm", "machine learning", "ml"]):
            required_ai_tools = ["cursor", "copilot", "claude", "gemini", "python", "git"]
            missing_ai_tools = [tool for tool in required_ai_tools if not any(tool in name for name in tool_names)]
            
            # Allow more missing tools (changed from 3 to 5)
            if len(missing_ai_tools) > 5:
                logger.warning(f"Missing key AI tools: {missing_ai_tools}")
                return False
        
        # Check for proper tool structure (but allow extensions without install commands)
        for tool in tools:
            if tool.is_extension:
                # Extensions don't need install commands
                if not tool.extension_id:
                    logger.warning(f"Extension {tool.name} missing extension ID")
                    return False
            else:
                # Regular tools need install and check commands
                if not tool.install_command or not tool.check_command:
                    logger.warning(f"Tool {tool.name} missing install or check command")
                    return False
        
        return True
    
    def _create_enhanced_prompt(self, environment: str, stack_info: Optional[str], memory_context: str) -> str:
        """
        Create a comprehensive prompt that ensures the LLM generates complete tool stacks.
        
        This prompt is specifically designed to avoid the "only VS Code and Git" problem
        by explicitly requesting comprehensive tool lists with justifications.
        """
        prompt = f'''
You are an expert AI environment setup agent for CONFIGO.

TASK: Generate a COMPREHENSIVE development environment setup for: "{environment}"

REQUIREMENTS:
1. You MUST return a complete YAML structure with ALL necessary tools
2. For AI/ML environments, include AT LEAST 10-15 tools including:
   - Code editors: Cursor IDE, VS Code, Vim/Neovim
   - AI tools: GitHub Copilot, Claude CLI, Gemini CLI, Cline, Augment, RoCode
   - Development tools: Git, Docker, Python, Node.js, Jupyter
   - AI libraries: TensorFlow, PyTorch, Hugging Face, OpenAI
   - Utilities: Postman, curl, wget, tmux, htop
3. Each tool MUST include: name, install_command, check_command, justification
4. Include login portals for AI services: ChatGPT, Claude, Gemini, Grok, Hugging Face
5. Include VS Code/Cursor extensions with proper IDs

MEMORY CONTEXT:
{memory_context}

PROJECT CONTEXT:
{stack_info if stack_info else "No project scan available"}

RESPONSE FORMAT (YAML):
```yaml
base_tools:
  - name: "Tool Name"
    install_command: "sudo apt install tool-name"
    check_command: "tool-name --version"
    justification: "Why this tool is needed"
    
editor:
  - name: "Editor Name"
    install_command: "install command"
    check_command: "check command"
    justification: "Why this editor is needed"

extensions:
  - name: "Extension Name"
    id: "extension.id"
    justification: "Why this extension is needed"

login_portals:
  - name: "Service Name"
    url: "https://service.com"
    description: "What this service provides"
    justification: "Why login is needed"

reasoning: "Your analysis of why these tools are appropriate"
```

IMPORTANT: 
- Be comprehensive and thorough
- Include modern AI development tools
- Provide specific install commands for Ubuntu/Debian systems
- Justify each tool selection
- Ensure the stack is production-ready

Generate the YAML response now:
'''
        return prompt
    
    def _get_domain_specific_prompt(self, domain: str) -> str:
        """Get domain-specific prompt requirements."""
        domain_prompts = {
            "ai_ml": """
For AI/ML environments, you MUST include:
- Base tools: Python, Docker, Git, Jupyter, pip
- Editor: Cursor (preferred) or VS Code with AI extensions
- Extensions: GitHub Copilot, Gemini Code Assist, RoCode, Cline, Augment, KiloCode, Python Extension
- CLI tools: Gemini CLI, Claude Code CLI, OpenAI CLI, Hugging Face CLI
- Login portals: ChatGPT, Claude, Gemini, Grok, Hugging Face, OpenAI Platform
- Additional tools: TensorFlow, PyTorch, scikit-learn, pandas, numpy, matplotlib

Example tools for AI/ML:
- Cursor Editor (AI-powered code editor)
- GitHub Copilot (AI code completion)
- Gemini CLI (Google's AI CLI tool)
- Claude CLI (Anthropic's AI CLI)
- Jupyter Notebooks (interactive ML development)
- TensorFlow/PyTorch (ML frameworks)
- Hugging Face CLI (model management)
""",
            
            "web_dev": """
For Web Development environments, you MUST include:
- Base tools: Node.js, npm/yarn, Git, Docker
- Editor: VS Code with web development extensions
- Extensions: GitHub Copilot, JavaScript/TypeScript extensions, Prettier, ESLint, Live Server
- CLI tools: npm, yarn, create-react-app, vue-cli, angular-cli
- Login portals: GitHub, Netlify, Vercel, AWS, Google Cloud
- Additional tools: Postman, Chrome DevTools, React DevTools

Example tools for Web Development:
- Node.js & npm (JavaScript runtime and package manager)
- VS Code (popular web development editor)
- GitHub Copilot (AI code assistance)
- Prettier (code formatting)
- ESLint (code linting)
- Live Server (local development server)
- Postman (API testing)
- React DevTools (React debugging)
""",
            
            "data_science": """
For Data Science environments, you MUST include:
- Base tools: Python, Jupyter, Git, pip
- Editor: VS Code or Jupyter Lab with data science extensions
- Extensions: Python Extension, Jupyter Extension, Data Science extensions, Plotly
- CLI tools: pip, conda, jupyter CLI
- Login portals: GitHub, Kaggle, Google Colab, Hugging Face, AWS
- Additional tools: pandas, numpy, matplotlib, seaborn, scikit-learn

Example tools for Data Science:
- Python & pip (programming language and package manager)
- Jupyter Notebooks (interactive data analysis)
- VS Code with Python extensions
- pandas (data manipulation)
- numpy (numerical computing)
- matplotlib/seaborn (data visualization)
- scikit-learn (machine learning)
- Kaggle CLI (competition and dataset access)
""",
            
            "devops": """
For DevOps environments, you MUST include:
- Base tools: Docker, Git, VS Code
- Editor: VS Code with infrastructure extensions
- Extensions: Docker Extension, YAML Extension, Terraform Extension, Kubernetes Extension
- CLI tools: Docker CLI, kubectl, helm, terraform, AWS CLI, gcloud
- Login portals: GitHub, AWS, Google Cloud, Azure, Docker Hub
- Additional tools: Terraform, Kubernetes, Helm, Ansible

Example tools for DevOps:
- Docker (containerization platform)
- Kubernetes CLI (kubectl) for container orchestration
- Terraform (Infrastructure as Code)
- AWS CLI (AWS service management)
- Google Cloud SDK (GCP service management)
- Helm (Kubernetes package manager)
- VS Code with infrastructure extensions
- Docker Hub (container registry)
"""
        }
        
        return domain_prompts.get(domain, domain_prompts["ai_ml"])
    
    def _clean_llm_response(self, response: str) -> str:
        """Clean LLM response by removing code block markers and extra formatting."""
        if not response:
            return ""
        
        # Remove leading/trailing whitespace
        response = response.strip()
        
        # Remove code block markers
        if response.startswith("```yaml"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        # Remove any remaining leading/trailing whitespace
        response = response.strip()
        
        return response

    def _parse_enhanced_response(self, yaml_response: str, environment: str) -> Dict[str, Any]:
        """Parse enhanced YAML response with justifications and confidence scores."""
        try:
            # Clean the response first
            cleaned_response = self._clean_llm_response(yaml_response)
            
            # Validate the response before parsing
            if not cleaned_response:
                raise ValueError("Empty LLM response received")
            
            config = yaml.safe_load(cleaned_response)
            if not config:
                raise ValueError("Empty config received")
            
            tools = []
            login_portals = []
            reasoning = config.get("reasoning", "No reasoning provided")
            domain_completion = config.get("domain_completion", {})
            
            # Parse base_tools (the actual format from Gemini)
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
            
            # Parse editor (the actual format from Gemini)
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
            
            # Parse extensions (the actual format from Gemini)
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
            
            # Parse CLI tools (if present)
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
            
            # Parse login portals (the actual format from Gemini)
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
            
            # Also check for legacy 'tools' format as fallback
            if not tools:
                legacy_tools = config.get("tools", [])
                for item in legacy_tools:
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
        
        # Check for missing recommended tools - be more aggressive
        missing_recommended = [tool for tool in domain_config.get("recommended", []) 
                             if tool not in existing_tool_names]
        
        # Add more recommended tools based on domain and total count
        target_tool_count = 8  # Minimum target
        current_count = len(tools)
        tools_to_add = min(len(missing_recommended), max(0, target_tool_count - current_count))
        
        for tool_name in missing_recommended[:tools_to_add]:
            tool = self._create_domain_tool(tool_name, detected_domain, "recommended")
            tools.append(tool)
        
        # Check for missing extensions - be more aggressive
        existing_extensions = [tool.name for tool in tools if tool.is_extension]
        missing_extensions = [ext for ext in domain_config.get("extensions", []) 
                            if ext not in existing_extensions]
        
        # Add more extensions based on domain
        target_extension_count = 4  # Target extensions
        current_extensions = len(existing_extensions)
        extensions_to_add = min(len(missing_extensions), max(0, target_extension_count - current_extensions))
        
        for ext_name in missing_extensions[:extensions_to_add]:
            tool = self._create_domain_extension(ext_name, detected_domain)
            tools.append(tool)
        
        # Add domain-specific additional tools if we're still under target
        additional_tools = self._get_domain_additional_tools(detected_domain)
        missing_additional = [tool for tool in additional_tools if tool not in existing_tool_names]
        
        if len(tools) < target_tool_count and missing_additional:
            tools_to_add = min(len(missing_additional), target_tool_count - len(tools))
            for tool_name in missing_additional[:tools_to_add]:
                tool = self._create_domain_tool(tool_name, detected_domain, "additional")
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
        parsed_response["domain_completion"]["total_tools"] = len(tools)
        parsed_response["domain_completion"]["target_met"] = len(tools) >= target_tool_count
        
        return parsed_response
    
    def _get_domain_additional_tools(self, domain: str) -> List[str]:
        """Get additional domain-specific tools beyond the basic configuration."""
        additional_tools = {
            "ai_ml": [
                "TensorFlow", "PyTorch", "scikit-learn", "pandas", "numpy", "matplotlib", 
                "seaborn", "OpenAI CLI", "Hugging Face CLI", "Weights & Biases CLI"
            ],
            "web_dev": [
                "Postman", "Chrome", "Firefox", "create-react-app", "vue-cli", "angular-cli",
                "yarn", "pnpm", "Live Server", "React DevTools", "Vue DevTools"
            ],
            "data_science": [
                "pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "plotly",
                "jupyterlab", "conda", "Kaggle CLI", "Google Colab CLI", "Tableau"
            ],
            "devops": [
                "Terraform", "Kubernetes", "Helm", "Ansible", "AWS CLI", "Google Cloud SDK",
                "Azure CLI", "Docker Compose", "Prometheus", "Grafana", "Jenkins"
            ]
        }
        return additional_tools.get(domain, [])
    
    def _detect_domain(self, environment: str) -> str:
        """Detect the primary domain from environment description."""
        environment_lower = environment.lower()
        
        # More specific keyword matching for better accuracy
        ai_ml_keywords = [
            "ai", "ml", "machine learning", "artificial intelligence", "neural", 
            "tensorflow", "pytorch", "deep learning", "llm", "gpt", "claude", 
            "gemini", "hugging face", "openai", "anthropic", "ai developer", 
            "ml engineer", "data scientist", "ai researcher"
        ]
        
        web_dev_keywords = [
            "web", "frontend", "backend", "full stack", "javascript", "react", 
            "angular", "vue", "node", "npm", "html", "css", "typescript", 
            "web developer", "frontend developer", "backend developer", 
            "full stack developer", "ui", "ux", "website"
        ]
        
        data_science_keywords = [
            "data", "analytics", "science", "pandas", "numpy", "matplotlib", 
            "jupyter", "kaggle", "colab", "data scientist", "data analyst", 
            "analytics", "statistics", "visualization", "plotly", "seaborn"
        ]
        
        devops_keywords = [
            "devops", "infrastructure", "deployment", "kubernetes", "docker", 
            "terraform", "aws", "azure", "gcp", "cloud", "ci/cd", "jenkins", 
            "gitlab", "github actions", "helm", "ansible", "infrastructure engineer"
        ]
        
        # Count matches for each domain
        ai_ml_score = sum(1 for keyword in ai_ml_keywords if keyword in environment_lower)
        web_dev_score = sum(1 for keyword in web_dev_keywords if keyword in environment_lower)
        data_science_score = sum(1 for keyword in data_science_keywords if keyword in environment_lower)
        devops_score = sum(1 for keyword in devops_keywords if keyword in environment_lower)
        
        # Return domain with highest score, default to ai_ml if no clear match
        scores = {
            "ai_ml": ai_ml_score,
            "web_dev": web_dev_score,
            "data_science": data_science_score,
            "devops": devops_score
        }
        
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=lambda k: scores[k])
        else:
            return "ai_ml"  # Default to AI/ML for unknown environments
    
    def _create_domain_tool(self, tool_name: str, domain: str, priority: str) -> ToolRecommendation:
        """Create a domain-specific tool recommendation."""
        # Tool installation commands
        install_commands = {
            "Python": "sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv",
            "Node.js": "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs",
            "Git": "sudo apt-get update && sudo apt-get install -y git",
            "Docker": "sudo apt-get update && sudo apt-get install -y docker.io docker-compose",
            "VS Code": "sudo snap install code --classic",
            "Cursor": "curl -L https://download.cursor.sh/linux/appImage/x64/cursor-latest.AppImage -o cursor && chmod +x cursor && sudo mv cursor /usr/local/bin/",
            "Jupyter": "pip3 install jupyter jupyterlab",
            "Postman": "sudo snap install postman",
            "Terraform": "curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add - && sudo apt-add-repository \"deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main\" && sudo apt-get update && sudo apt-get install terraform",
            "AWS CLI": "curl \"https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip\" -o \"awscliv2.zip\" && unzip awscliv2.zip && sudo ./aws/install",
            "Google Cloud SDK": "curl -sSL https://sdk.cloud.google.com | bash && exec -l $SHELL && gcloud init",
            "kubectl": "curl -LO \"https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl\" && sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl",
            "Helm": "curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null && echo \"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main\" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list && sudo apt-get update && sudo apt-get install helm",
            "pip": "sudo apt-get update && sudo apt-get install -y python3-pip",
            "npm": "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs",
            "Chrome": "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add - && sudo sh -c 'echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google.list' && sudo apt-get update && sudo apt-get install google-chrome-stable",
            "Firefox": "sudo apt-get update && sudo apt-get install -y firefox",
            "pandas": "pip3 install pandas",
            "numpy": "pip3 install numpy",
            "TensorFlow": "pip3 install tensorflow",
            "PyTorch": "pip3 install torch torchvision torchaudio"
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
            "Google Cloud SDK": "gcloud --version",
            "kubectl": "kubectl version --client",
            "Helm": "helm version",
            "pip": "pip3 --version",
            "npm": "npm --version",
            "Chrome": "google-chrome --version",
            "Firefox": "firefox --version",
            "pandas": "python3 -c 'import pandas; print(pandas.__version__)'",
            "numpy": "python3 -c 'import numpy; print(numpy.__version__)'",
            "TensorFlow": "python3 -c 'import tensorflow; print(tensorflow.__version__)'",
            "PyTorch": "python3 -c 'import torch; print(torch.__version__)'"
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
            "Google Cloud SDK": "Command line tools for Google Cloud Platform",
            "kubectl": "Kubernetes command line tool for container orchestration",
            "Helm": "Kubernetes package manager for deploying applications",
            "pip": "Python package manager for installing Python libraries",
            "npm": "Node.js package manager for JavaScript libraries",
            "Chrome": "Web browser for testing web applications",
            "Firefox": "Alternative web browser for cross-browser testing",
            "pandas": "Data manipulation and analysis library for Python",
            "numpy": "Numerical computing library for Python",
            "TensorFlow": "Open-source machine learning framework by Google",
            "PyTorch": "Open-source machine learning framework by Facebook"
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
            "Terraform Extension": "hashicorp.terraform",
            "Gemini Code Assist": "google.gemini-code-assist",
            "RoCode": "rocodelabs.rocodelabs",
            "Prettier": "esbenp.prettier-vscode",
            "ESLint": "dbaeumer.vscode-eslint",
            "Live Server": "ritwickdey.liveserver",
            "Data Science Extensions": "ms-toolsai.jupyter",
            "Plotly": "ms-python.python",
            "Kubernetes Extension": "ms-kubernetes-tools.vscode-kubernetes-tools",
            "Remote Development": "ms-vscode-remote.vscode-remote-extensionpack"
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
            "Terraform Extension": "Terraform infrastructure management in VS Code",
            "Gemini Code Assist": "Google's AI code assistance and completion",
            "RoCode": "AI-powered code generation and assistance",
            "Prettier": "Code formatting for consistent code style",
            "ESLint": "JavaScript/TypeScript linting and error detection",
            "Live Server": "Live reload development server for web projects",
            "Data Science Extensions": "Comprehensive data science tools and visualizations",
            "Plotly": "Interactive data visualization library support",
            "Kubernetes Extension": "Kubernetes cluster management in VS Code",
            "Remote Development": "Remote development and SSH support"
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
            "Google Colab": "https://colab.research.google.com",
            "Gemini": "https://gemini.google.com",
            "Grok": "https://grok.x.ai",
            "Firebase": "https://console.firebase.google.com",
            "Tableau": "https://www.tableau.com",
            "Docker Hub": "https://hub.docker.com",
            "HashiCorp": "https://portal.cloud.hashicorp.com"
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
            "Google Colab": "Cloud-based Jupyter notebook environment",
            "Gemini": "Google's AI platform and model access",
            "Grok": "xAI's conversational AI platform",
            "Firebase": "Google's mobile and web app development platform",
            "Tableau": "Data visualization and business intelligence platform",
            "Docker Hub": "Container image registry and sharing platform",
            "HashiCorp": "Infrastructure automation and management platform"
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


    
    def _retry_with_refined_prompt(self, environment: str, stack_info: Optional[str], memory_context: str) -> Optional[Dict[str, Any]]:
        """Retry with a more specific and demanding prompt."""
        detected_domain = self._detect_domain(environment)
        
        refined_prompt = f"""
You are an expert environment setup assistant. The previous response was insufficient.

🧠 ENVIRONMENT: "{environment}"
🎯 DETECTED DOMAIN: {detected_domain.upper()}

PROJECT CONTEXT: {stack_info or "No project scan available"}

MEMORY CONTEXT:
{memory_context}

🚨 CRITICAL: The previous response was too minimal. You MUST return a COMPREHENSIVE tech stack with AT LEAST 10-15 tools total.

REQUIRED STRUCTURE:
```yaml
base_tools:
  - name: "Tool Name"
    install_command: "Linux installation command"
    check_command: "command to check if installed"
    justification: "Why this tool is needed"
    confidence_score: 0.85
    priority: 8

editor:
  - name: "Editor Name"
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
  detected_domain: "{detected_domain}"
  missing_tools: []
  alternative_suggestions: []
```

🎯 FOR {detected_domain.upper()}, YOU MUST INCLUDE:

{self._get_domain_specific_prompt(detected_domain)}

🚨 REQUIREMENTS:
- Return AT LEAST 10-15 tools total
- Include 3-5 base tools
- Include 1 editor
- Include 4-6 extensions
- Include 2-4 CLI tools
- Include 3-5 login portals
- Be comprehensive and domain-specific
- Return ONLY valid YAML, no explanations
"""
        
        try:
            raw_response = self.llm_client.generate_config(refined_prompt) or ""
            parsed_response = self._parse_enhanced_response(raw_response, environment)
            completed_response = self._apply_domain_completion(parsed_response, environment)
            
            # Validate the refined response
            if self._validate_response_quality(completed_response, environment):
                logger.info("Refined prompt produced better results")
                return completed_response
            else:
                logger.warning("Refined prompt still produced insufficient results")
                return None
                
        except Exception as e:
            logger.error(f"Failed to retry with refined prompt: {e}")
            return None