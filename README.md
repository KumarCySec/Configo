# 🚀 CONFIGO: Autonomous AI Setup Agent

> **Intelligent development environment setup with memory, planning, and self-healing capabilities**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

<div align="center">

![CONFIGO Banner](https://via.placeholder.com/800x200/6366f1/ffffff?text=CONFIGO+AI+Setup+Agent)

**The intelligent development environment agent that learns, adapts, and heals itself**

[Quick Start](#-quick-start) • [Features](#-features) • [Usage](#-usage) • [Examples](#-examples) • [Architecture](#-architecture)

</div>

---

## 🎯 What is CONFIGO?

CONFIGO is an autonomous AI agent that intelligently sets up complete development environments. It uses LLM-powered recommendations, persistent memory, and self-healing capabilities to create the perfect development stack for your projects.

### ✨ Key Features

- 🧠 **Memory-Aware**: Remembers your preferences and past installations
- 🤖 **LLM-Powered**: Uses Gemini AI for intelligent tool recommendations
- 🔧 **Self-Healing**: Automatically fixes installation failures
- ✅ **Validation**: Post-installation verification and testing
- 🎯 **Domain-Aware**: Understands your project type and suggests relevant tools
- 🌐 **Login Orchestration**: Opens browser portals for service logins
- 📊 **Rich UI**: Beautiful terminal interface with progress tracking
- 💬 **Interactive Chat**: Natural language commands and queries
- 🔍 **Project Scanning**: Intelligent stack detection and recommendations
- 👤 **User Profiles**: Personalized settings and preferences
- 🛠️ **Smart Recovery**: LLM-powered error fixing and alternatives

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/configo.git
cd configo

# Install dependencies
pip install -r requirements.txt

# Set up your API key
export GOOGLE_API_KEY="your_gemini_api_key"

# Run CONFIGO
python main.py
```

### Basic Usage

```bash
# Start CONFIGO in setup mode (default)
python main.py

# Interactive chat mode
python main.py chat

# Project scanning mode
python main.py scan

# Portal management mode
python main.py portal
```

## 📋 Example Environments

### Python Web Development
```bash
python main.py
# Input: "Python web development with Django, PostgreSQL, and Redis"
```

### JavaScript/Node.js Development
```bash
python main.py
# Input: "Node.js development with React, TypeScript, and MongoDB"
```

### Data Science
```bash
python main.py
# Input: "Data science environment with Jupyter, pandas, and scikit-learn"
```

### DevOps/Cloud
```bash
python main.py
# Input: "DevOps environment with Docker, Kubernetes, and AWS CLI"
```

## 🆕 Interactive Modes

### 💬 Chat Mode
```bash
python main.py chat

# Example interactions:
# "Install Python 3.11"
# "What is Docker?"
# "Check if Git is installed"
# "Recommend tools for web development"
```

### 🔍 Project Scanning Mode
```bash
python main.py scan

# Automatically detects:
# - Project type (Python, JavaScript, Go, etc.)
# - Frameworks (Django, React, FastAPI, etc.)
# - Configuration files (requirements.txt, package.json, etc.)
# - Provides tailored recommendations
```

### 🌐 Portal Management Mode
```bash
python main.py portal

# Manage AI service logins:
# - Claude, Gemini, Grok, ChatGPT
# - Install CLI tools
# - Check login status
# - Open browser portals
```

## 🏗️ Architecture

```
CONFIGO/
├── main.py                 # Main entry point
├── core/                   # Core agent components
│   ├── ai.py              # LLM integration
│   ├── memory.py          # Persistent memory system
│   ├── planner.py         # Installation planning
│   ├── validator.py       # Tool validation
│   └── enhanced_llm_agent.py  # Enhanced LLM agent
├── ui/                    # User interface
│   ├── layout.py          # UI layout components
│   ├── messages.py        # Message display
│   └── enhanced_messages.py  # Enhanced UI messages
├── installers/            # Installation utilities
└── requirements.txt       # Dependencies
```

## 🔧 Configuration

### Environment Variables

```bash
# LLM API Configuration
GOOGLE_API_KEY=your_gemini_api_key

# Memory Configuration (Optional)
MEM0_API_KEY=your_mem0_api_key  # For enhanced memory features

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### Memory System

CONFIGO uses a dual memory system:
- **mem0ai**: Cloud-based intelligent memory (when API key provided)
- **JSON Fallback**: Local file-based memory (always available)

## 🎨 Terminal Preview

```
🚀 CONFIGO: Autonomous AI Setup Agent
🧠 Memory • 📋 Planning • 🔧 Self-Healing • ✅ Validation

🧠 Memory Context
┌─────────────────────────────────────┐
│ Memory Statistics                   │
├─────────────────────────────────────┤
│ Total Tools: 15                     │
│ Successful Installations: 12        │
│ Failed Installations: 3             │
│ Total Sessions: 8                   │
│ Success Rate: 80.0%                 │
└─────────────────────────────────────┘

📋 Planning: Python Web Development Environment
✅ Step 1/5: Install Python 3.11
✅ Step 2/5: Install pip and virtualenv
🔄 Step 3/5: Install Django
⏳ Step 4/5: Install PostgreSQL
⏳ Step 5/5: Install Redis

🔍 Validation Results
┌─────────────────────────────────────┐
│ ✅ Status: HEALTHY                  │
│ 📊 Success Rate: 100.0%             │
│ ✅ Valid Tools: 5/5                 │
│ ⏱️ Avg Validation Time: 1.2s        │
└─────────────────────────────────────┘
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/configo.git
cd configo

# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 core/ ui/ main.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Gemini AI**: For intelligent tool recommendations
- **mem0ai**: For enhanced memory capabilities
- **Rich**: For beautiful terminal UI
- **Textual**: For interactive interfaces

---

<div align="center">

**Made with ❤️ by the CONFIGO Team**

[GitHub](https://github.com/yourusername/configo) • [Issues](https://github.com/yourusername/configo/issues) • [Discussions](https://github.com/yourusername/configo/discussions)

</div> 