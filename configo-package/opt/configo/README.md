# 🚀 CONFIGO - Autonomous AI Setup Agent

> **Intelligent, memory-aware development environment setup with LLM-powered recommendations and self-healing capabilities**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AI-Powered](https://img.shields.io/badge/AI--Powered-Gemini%20LLM-purple.svg)]()
[![Self-Healing](https://img.shields.io/badge/Self--Healing-Automatic%20Recovery-green.svg)]()
[![Memory](https://img.shields.io/badge/Memory-mem0%20Enhanced-orange.svg)]()

<div align="center">

**🧠 Intelligent • 🔧 Self-Healing • 💾 Memory-Aware • 🎯 Domain-Specific • 📱 App Installation**

*The ultimate AI-powered development environment setup agent that understands your needs and learns from your preferences*

</div>

---

## 🎯 What is CONFIGO?

CONFIGO is an **autonomous AI agent** that intelligently sets up development environments using natural language. It combines the power of Google's Gemini LLM with persistent memory to provide personalized, context-aware tool recommendations and automatic installation.

### ✨ Key Features

- **🧠 LLM-Powered Intelligence**: Uses Gemini API for intelligent tool recommendations
- **💾 Persistent Memory**: Remembers your preferences and installation history
- **🔧 Self-Healing**: Automatically fixes installation failures using AI
- **🎯 Domain-Aware**: Understands different development domains (AI/ML, Web, DevOps, etc.)
- **📱 Natural Language App Installation**: Install any app with simple commands like "Install Discord"
- **🌐 Portal Orchestration**: Automated login portal management
- **✅ Post-Installation Validation**: Ensures everything works correctly
- **🎨 Rich Terminal UI**: Beautiful, informative interface

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (for LLM features)
- mem0 API key (optional, for enhanced memory)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kishore-jarviz/configo.git
   cd configo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run CONFIGO**
   ```bash
   python main.py
   ```

---

## 📱 Natural Language App Installation

**NEW!** CONFIGO now supports natural language app installation across all platforms:

```bash
# Install any app with simple commands
python main.py install
```

### Examples

```
What app do you want to install? Install Discord
What app do you want to install? I need Chrome  
What app do you want to install? Get me Zoom
What app do you want to install? Install Slack
```

### How It Works

1. **🎯 Natural Language Understanding**: CONFIGO understands your intent from simple phrases
2. **🔍 System Detection**: Automatically detects your OS, distro, and available package managers
3. **🧠 AI-Powered Planning**: Uses Gemini to generate the optimal installation plan
4. **🔧 Self-Healing Execution**: Runs commands with automatic error recovery
5. **🎨 GUI Integration**: Creates desktop shortcuts and menu entries
6. **💾 Memory Persistence**: Remembers successful installations for future sessions

### Supported Platforms

- **Linux**: apt, snap, flatpak, and direct downloads
- **macOS**: Homebrew and direct downloads  
- **Windows**: winget, Chocolatey, and direct downloads

---

## 🎮 Usage Modes

### 1. Full Development Environment Setup (Default)
```bash
python main.py
```
Complete AI-powered development environment setup with tool recommendations, validation, and self-healing.

### 2. Natural Language App Installation
```bash
python main.py install
```
Install any application using natural language commands.

### 3. Interactive Chat Mode
```bash
python main.py chat
```
Chat with CONFIGO about your development environment and get personalized recommendations.

### 4. Project Scanning Mode
```bash
python main.py scan
```
Analyze your current project and get tailored tool recommendations.

### 5. Portal Orchestration
```bash
python main.py portal
```
Manage login portals for development services (GitHub, OpenAI, etc.).

### 6. Help
```bash
python main.py help
```
Show available modes and usage information.

---

## 🧠 How It Works

### 1. **Memory-Aware Recommendations**
CONFIGO uses persistent memory to remember:
- Previously installed tools
- Failed installations and their fixes
- User preferences and patterns
- Session history and analytics

### 2. **LLM-Powered Intelligence**
- **Gemini Integration**: Advanced language model for intelligent recommendations
- **Domain Detection**: Automatically identifies your development domain
- **Context Awareness**: Considers your current project and environment
- **Self-Healing**: Uses AI to fix installation failures

### 3. **Self-Healing Installation**
- **Automatic Retry**: Retries failed installations with different approaches
- **LLM-Powered Fixes**: Uses AI to generate alternative installation methods
- **Progressive Fallbacks**: Tries multiple package managers and sources
- **Error Analysis**: Intelligent diagnosis of failure causes

### 4. **Post-Installation Validation**
- **Tool Verification**: Tests installed tools to ensure functionality
- **Health Checks**: Comprehensive validation of development environment
- **Performance Metrics**: Tracks installation success rates and timing

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  LLM Agent      │───▶│  Installation   │
│   (Natural      │    │  (Gemini)       │    │  Executor       │
│    Language)    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  System         │    │  Memory         │    │  Validation     │
│  Detection      │    │  (mem0/JSON)    │    │  & Self-Healing │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

- **`core/enhanced_llm_agent.py`**: LLM integration and intelligent recommendations
- **`core/memory.py`**: Persistent memory system with mem0 integration
- **`core/shell_executor.py`**: Command execution with error handling
- **`core/system.py`**: OS and package manager detection
- **`ui/enhanced_messages.py`**: Rich terminal UI components

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required: Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: mem0 for enhanced memory
MEM0_API_KEY=your_mem0_api_key_here

# Optional: Logging level
LOG_LEVEL=INFO
```

### API Keys

1. **Google Gemini API**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **mem0 API** (optional): Get your API key from [mem0.ai](https://mem0.ai)

---

## 🧪 Testing

Run the test suite to verify all components:

```bash
python test_app_install.py
```

This will test:
- System detection
- LLM plan generation
- Memory functions
- UI components

---

## 📊 Features

### 🧠 AI Intelligence
- **Gemini Integration**: Advanced language model for intelligent recommendations
- **Domain Awareness**: Understands different development domains
- **Context Awareness**: Considers current project and environment
- **Self-Healing**: Uses AI to fix installation failures

### 💾 Memory System
- **Persistent Storage**: Remembers installations and preferences
- **Semantic Search**: Intelligent memory retrieval
- **Session Tracking**: Complete setup session history
- **Learning Capabilities**: Improves recommendations over time

### 🔧 Self-Healing
- **Automatic Retry**: Retries failed installations
- **LLM-Powered Fixes**: AI-generated alternative methods
- **Progressive Fallbacks**: Multiple installation approaches
- **Error Analysis**: Intelligent failure diagnosis

### 🎨 User Interface
- **Rich Terminal UI**: Beautiful, informative interface
- **Progress Tracking**: Real-time installation progress
- **Status Updates**: Clear status messages and error reporting
- **Color-Coded Output**: Intuitive color scheme

### 📱 App Installation
- **Natural Language**: Install apps with simple commands
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **GUI Integration**: Creates desktop shortcuts and menu entries
- **Package Manager Support**: Uses available package managers

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini**: For providing the LLM capabilities
- **mem0**: For enhanced memory functionality
- **Rich**: For the beautiful terminal UI
- **Textual**: For the modern terminal interface

---

<div align="center">

**🚀 Ready to experience the future of development environment setup?**

*Built with 💡 by [Kishore Kumar S](https://github.com/kishore-jarviz)*

</div> 