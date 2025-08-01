# CONFIGO - Intelligent Development Environment Agent

🚀 **A professional AI-powered CLI tool that intelligently sets up development environments with memory, planning, self-healing, and validation capabilities.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

## 🌟 Features

### 🧠 **AI-Powered Intelligence**
- **Memory-aware recommendations** using mem0ai
- **LLM-powered stack generation** via Google Gemini
- **Domain detection** and project analysis
- **Self-healing installation** with retry logic
- **Intelligent error recovery** and command fixes

### 🎯 **Core Capabilities**
- **Full development environment setup** with tool validation
- **Interactive AI chat assistant** for development questions
- **Project scanning and analysis** with framework detection
- **Natural language app installation** ("install vscode")
- **Login portal orchestration** for development services
- **System diagnostics and health checks**

### 🎨 **Modern Terminal UI**
- **Rich terminal interface** with colors and animations
- **Multiple themes** (default, minimal, developer, verbose, dark, light)
- **Live progress tracking** and real-time updates
- **Professional polish** with welcome animations
- **Responsive design** for different terminal sizes

### 🔧 **Advanced Features**
- **Post-installation validation** of all tools
- **Session tracking** and memory persistence
- **Extension management** for VS Code/Cursor
- **Package manager detection** and optimization
- **Cross-platform compatibility** (Linux, macOS, Windows)

### 🧠 **Knowledge Layer** (NEW!)
- **Graph Database Integration** - Neo4j for tool relationships and dependency modeling
- **Vector Database** - Chroma/FAISS for semantic search and error matching
- **Intelligent Error Resolution** - Find similar errors and their solutions
- **Personalized Recommendations** - Learn from user patterns and success rates
- **Tool Relationship Modeling** - Track dependencies between tools (Python → pip → packages)
- **User Persona Similarity** - Find users with similar preferences and needs
- **Self-Improving Knowledge Base** - Gets smarter with every installation

## 📦 Installation

### Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/configo.git
cd configo

# Install dependencies
pip install -r requirements.txt

# Make executable and create symlink
chmod +x configo.py
ln -sf $(pwd)/configo.py ~/.local/bin/configo

# Test installation
configo --help
```

### Environment Setup
```bash
# Create .env file with your API keys
cp .env.example .env

# Edit .env with your Gemini API key
nano .env
```

Required environment variables:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MEM0_API_KEY=your_mem0_api_key_here  # Optional
LOG_LEVEL=INFO

# Knowledge Layer Configuration (Optional)
NEO4J_URI=bolt://localhost:7687  # Neo4j database URI
NEO4J_USERNAME=neo4j             # Neo4j username
NEO4J_PASSWORD=your_password     # Neo4j password
CONFIGO_KNOWLEDGE_ENABLED=true   # Enable knowledge layer
CONFIGO_GRAPH_ENABLED=true       # Enable graph database
CONFIGO_VECTOR_ENABLED=true      # Enable vector database
```

## 🚀 Usage

### Interactive Mode (Default)
```bash
configo
```
Shows a welcome screen with mode selection:
1. **Setup** - Full development environment setup
2. **Chat** - Interactive AI chat assistant
3. **Scan** - Project analysis and recommendations
4. **Install** - Natural language app installation
5. **Portals** - Login portal orchestration
6. **Diagnostics** - System health check
7. **Settings** - Configuration and preferences

### Direct Commands

#### 🛠️ **Development Environment Setup**
```bash
configo setup
```
- Analyzes your system and project
- Generates AI-powered tool recommendations
- Creates intelligent installation plan
- Executes installation with validation
- Provides self-healing for failed installations

#### 🧠 **Knowledge Layer Commands**
```bash
# Test the knowledge layer
python scripts/knowledge_cli.py demo

# Add tool to knowledge base
python scripts/knowledge_cli.py add-tool python language "Python programming language"

# Search for similar errors
python scripts/knowledge_cli.py search-errors "Permission denied"

# Find related tools
python scripts/knowledge_cli.py related-tools python

# Show knowledge statistics
python scripts/knowledge_cli.py stats
```

#### 💬 **Interactive AI Chat**
```bash
configo chat
```
Ask questions about development tools, setup, and get intelligent responses:
```
💬 You: How do I set up a React development environment?
🤖 CONFIGO: I'll help you set up a React development environment...
```

#### 🔍 **Project Analysis**
```bash
configo scan
```
Scans your current project and provides:
- Detected frameworks and languages
- Technology stack analysis
- Tailored recommendations
- Confidence scores

#### 📦 **Natural Language App Installation**
```bash
configo install vscode
configo install "I need a text editor"
configo install "install docker for containerization"
```
Extracts app names from natural language and installs them intelligently.

#### 🌐 **Login Portal Orchestration**
```bash
configo portals
```
Opens development service portals:
- GitHub, GitLab, Bitbucket
- AWS, Azure, Google Cloud
- Docker Hub, npm, PyPI
- And many more...

#### 🔧 **System Diagnostics**
```bash
configo diagnostics
```
Performs comprehensive system health checks:
- Package manager availability
- Network connectivity
- API key validation
- Tool installation status

### Advanced Options

#### Debug Mode
```bash
configo setup --debug
configo chat --debug
```
Enables detailed logging and LLM response visibility.

#### Lite Mode
```bash
configo setup --lite
```
Minimal output for low-speed terminals or CI/CD environments.

#### Theme Selection
```bash
configo --theme developer
configo --theme minimal
configo --theme dark
```

## 🏗️ Architecture

### Core Components
```
configo/
├── core/                    # Core agent components
│   ├── memory.py           # Memory management
│   ├── enhanced_llm_agent.py # LLM integration
│   ├── planner.py          # Installation planning
│   ├── validator.py        # Tool validation
│   ├── project_scanner.py  # Project analysis
│   └── system_inspector.py # System intelligence
├── knowledge/              # Knowledge layer (NEW!)
│   ├── knowledge_engine.py # Central knowledge engine
│   ├── graph_db_manager.py # Neo4j graph database
│   ├── vector_store_manager.py # Chroma/FAISS vector database
│   └── config.py          # Knowledge configuration
├── ui/                     # User interface
│   ├── modern_terminal_ui.py # Main UI component
│   ├── settings_menu.py    # Settings interface
│   └── enhanced_messages.py # Message display
├── installers/             # Installation utilities
├── scripts/                # Utility scripts
└── configo.py             # Main entry point
```

### 🧠 Knowledge Layer Architecture

The knowledge layer provides intelligent memory and learning capabilities:

```
CONFIGO CLI → KnowledgeEngine → GraphDBManager + VectorStoreManager
     ↓              ↓                    ↓
Install Event → Log to Both → Store Relationships + Embeddings
     ↓              ↓                    ↓
Error Occurs → Search Similar → Find Solutions + Related Tools
     ↓              ↓                    ↓
User Query → Combined Query → Graph + Vector Results
```

**Components:**
- **GraphDBManager** - Neo4j integration for tool relationships and install events
- **VectorStoreManager** - Chroma/FAISS for semantic search and error matching
- **KnowledgeEngine** - Unified API coordinating both databases
- **Local Simulators** - Fallback when databases aren't available

### Key Features

#### 🧠 **Memory System**
- Persistent session tracking
- Tool installation history
- User preference learning
- Context-aware recommendations

#### 🤖 **LLM Integration**
- Google Gemini API for intelligent responses
- Structured tool recommendations
- Error analysis and self-healing
- Natural language processing

#### 🎨 **Enhanced UI**
- Rich terminal formatting
- Live progress indicators
- Animated welcome screens
- Multiple theme support

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `MEM0_API_KEY` | Mem0 AI API key | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No |
| `CONFIGO_DEBUG` | Enable debug mode | No |

#### Knowledge Layer Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `NEO4J_URI` | Neo4j database URI | No |
| `NEO4J_USERNAME` | Neo4j username | No |
| `NEO4J_PASSWORD` | Neo4j password | No |
| `CONFIGO_KNOWLEDGE_ENABLED` | Enable knowledge layer | No |
| `CONFIGO_GRAPH_ENABLED` | Enable graph database | No |
| `CONFIGO_VECTOR_ENABLED` | Enable vector database | No |

### Configuration Files
- `.env` - Environment variables
- `configo.log` - Application logs
- `memory.json` - Persistent memory storage

## 🧪 Testing

### Quick Test
```bash
# Test basic functionality
python configo.py --help

# Test interactive mode
python configo.py

# Test specific commands
python configo.py scan
python configo.py diagnostics
```

### Comprehensive Testing
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=configo

# Run specific test categories
python -m pytest tests/test_ui.py
python -m pytest tests/test_core.py
```

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup development environment
git clone https://github.com/yourusername/configo.git
cd configo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python -m pytest
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to all functions
- Write comprehensive tests

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini** for AI capabilities
- **Rich** library for beautiful terminal UI
- **Mem0 AI** for intelligent memory management
- **OpenAI** for inspiration in AI agent design

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/configo/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/configo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/configo/discussions)
- **Email**: support@configo.dev

## 🚀 Roadmap

### Upcoming Features
- [ ] **Multi-language support** (Python, Node.js, Go, Rust)
- [ ] **Cloud deployment** integration (AWS, GCP, Azure)
- [ ] **Team collaboration** features
- [ ] **Plugin system** for custom tools
- [ ] **Web dashboard** for monitoring
- [ ] **Mobile app** companion

### Version History
- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Enhanced UI and memory system
- **v1.2.0** - Project scanning and analysis
- **v1.3.0** - Natural language app installation
- **v2.0.0** - Consolidated architecture and CLI

---

**Made with ❤️ by the CONFIGO Team**

*Empowering developers with intelligent automation since 2024* 