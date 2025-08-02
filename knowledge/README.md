# CONFIGO Knowledge Layer

A modular, production-ready graph + vector knowledge layer for the CONFIGO CLI that provides intelligent memory, semantic search, and relationship modeling capabilities.

## 🎯 Features

### Graph Database (Neo4j)
- **Tool dependency modeling** - Track relationships between tools (e.g., Python → pip → packages)
- **Install event tracking** - Log successful/failed installations with metadata
- **User persona modeling** - Store user preferences and installation patterns
- **Success rate analytics** - Track tool installation success rates over time
- **Personalized recommendations** - Generate install plans based on user history

### Vector Database (Chroma/FAISS)
- **Semantic error matching** - Find similar errors and their solutions
- **Tool description search** - Search tools by description and functionality
- **User persona similarity** - Find users with similar preferences and needs
- **Fuzzy error resolution** - Match error patterns even with slight variations
- **Embedding-based recommendations** - Use semantic similarity for tool suggestions

### Knowledge Engine
- **Unified API** - Single interface for both graph and vector operations
- **Coordinated queries** - Combine graph relationships with semantic search
- **Intelligent error resolution** - Cross-reference errors with related tools
- **Self-improving recommendations** - Learn from user patterns and success rates
- **Comprehensive analytics** - Cross-database insights and statistics

## 🚀 Quick Start

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables (optional):**
```bash
# Neo4j Configuration
export NEO4J_URI="neo4j+s://bae36d7a.databases.neo4j.io"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="fHzFOT-Dt5rmLeAMidCisXq2NkSA4k4fHVaISy6UB0U"
export NEO4J_DATABASE="neo4j"
export AURA_INSTANCEID="bae36d7a"
export AURA_INSTANCENAME="Instance01"

# Knowledge Layer Configuration
export CONFIGO_KNOWLEDGE_ENABLED="true"
export CONFIGO_GRAPH_ENABLED="true"
export CONFIGO_VECTOR_ENABLED="true"
```

3. **Test the knowledge layer:**
```bash
python scripts/knowledge_cli.py demo
```

### Basic Usage

```python
from knowledge import KnowledgeEngine

# Initialize the knowledge engine
engine = KnowledgeEngine()

# Add tool knowledge
engine.add_tool_knowledge(
    tool_name="python",
    category="language",
    description="Python programming language",
    install_command="apt-get install python3",
    check_command="python3 --version"
)

# Log an installation event
engine.log_install_event(
    tool_name="docker",
    command="apt-get install docker",
    success=True,
    os_type="linux",
    architecture="x86_64"
)

# Search for similar errors
result = engine.query_similar_errors("Permission denied", limit=5)
for res in result.results:
    print(f"Error: {res['content']}")
    print(f"Similarity: {res['similarity']:.2f}")

# Get related tools
result = engine.get_related_tools("python", limit=5)
for res in result.results:
    print(f"Related: {res['content']}")

# Get recommended installation plan
user_profile = {"persona": "developer", "preferences": {"auto_retry": True}}
result = engine.get_recommended_plan(user_profile, "ai-stack")
```

## 📋 CLI Commands

The knowledge layer includes a comprehensive CLI for testing and management:

```bash
# Add a tool to the knowledge base
python scripts/knowledge_cli.py add-tool python language "Python programming language"

# Log an error with solution
python scripts/knowledge_cli.py log-error docker "Permission denied" "Run with sudo"

# Search for similar errors
python scripts/knowledge_cli.py search-errors "Permission denied"

# Find related tools
python scripts/knowledge_cli.py related-tools python

# Show statistics
python scripts/knowledge_cli.py stats

# Run comprehensive demo
python scripts/knowledge_cli.py demo
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | neo4j+s://bae36d7a.databases.neo4j.io | Neo4j database URI |
| `NEO4J_USERNAME` | neo4j | Neo4j username |
| `NEO4J_PASSWORD` | fHzFOT-Dt5rmLeAMidCisXq2NkSA4k4fHVaISy6UB0U | Neo4j password |
| `NEO4J_DATABASE` | neo4j | Neo4j database name |
| `AURA_INSTANCEID` | bae36d7a | Neo4j Aura instance ID |
| `AURA_INSTANCENAME` | Instance01 | Neo4j Aura instance name |
| `CONFIGO_GRAPH_ENABLED` | true | Enable graph database |
| `CONFIGO_VECTOR_ENABLED` | true | Enable vector database |
| `CONFIGO_KNOWLEDGE_ENABLED` | true | Enable knowledge engine |
| `CONFIGO_EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Sentence transformer model |
| `CONFIGO_GRAPH_PATH` | .configo_graph | Graph storage path |
| `CONFIGO_VECTOR_PATH` | .configo_vectors | Vector storage path |

### Feature Toggles

| Feature | Environment Variable | Default |
|---------|-------------------|---------|
| Error Matching | `CONFIGO_ERROR_MATCHING` | true |
| Tool Recommendations | `CONFIGO_TOOL_RECOMMENDATIONS` | true |
| User Personas | `CONFIGO_USER_PERSONAS` | true |
| Semantic Search | `CONFIGO_SEMANTIC_SEARCH` | true |
| Graph Relationships | `CONFIGO_GRAPH_RELATIONSHIPS` | true |

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all knowledge layer tests
python -m pytest tests/test_knowledge/ -v

# Run specific test file
python -m pytest tests/test_knowledge/test_knowledge_engine.py -v

# Run with coverage
python -m pytest tests/test_knowledge/ --cov=knowledge --cov-report=html
```

## 📊 Integration with CONFIGO CLI

### Hook into Install Commands

```python
# In your CONFIGO install command
def install_tool(tool_name, command):
    try:
        # Execute installation
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        success = result.returncode == 0
        
        # Log to knowledge layer
        engine.log_install_event(
            tool_name=tool_name,
            command=command,
            success=success,
            os_type=get_os_type(),
            architecture=get_architecture(),
            error_message=result.stderr if not success else None
        )
        
        return success
    except Exception as e:
        # Log error
        engine.log_install_event(
            tool_name=tool_name,
            command=command,
            success=False,
            os_type=get_os_type(),
            architecture=get_architecture(),
            error_message=str(e)
        )
        raise
```

### Error Resolution

```python
# When an installation fails
def handle_install_error(tool_name, error_message):
    # Search for similar errors and solutions
    result = engine.query_similar_errors(error_message, limit=3)
    
    if result.results:
        print("🔍 Found similar errors and solutions:")
        for res in result.results:
            if res['type'] == 'error_solution':
                print(f"  - {res['content']}")
                print(f"  - Confidence: {res['similarity']:.2f}")
    
    # Get related tools that might help
    related = engine.get_related_tools(tool_name, limit=3)
    if related.results:
        print("🔗 Related tools that might help:")
        for res in related.results:
            print(f"  - {res['content']}")
```

### Personalized Recommendations

```python
# Generate personalized install plan
def get_personalized_plan(user_profile, target_environment):
    result = engine.get_recommended_plan(user_profile, target_environment)
    
    print(f"🎯 Recommended tools for {target_environment}:")
    for res in result.results:
        if res['type'] == 'graph_recommended':
            metadata = res['metadata']
            print(f"  - {metadata['name']}: {metadata['description']}")
            print(f"    Success Rate: {metadata.get('avg_success', 0):.1%}")
            print(f"    Install Command: {metadata['install_command']}")
```

## 🏗️ Architecture

### Components

1. **GraphDBManager** - Handles Neo4j operations and local graph simulation
2. **VectorStoreManager** - Manages Chroma/FAISS operations and local vector simulation
3. **KnowledgeEngine** - Coordinates between graph and vector databases
4. **KnowledgeConfig** - Configuration management with environment variables

### Data Flow

```
CONFIGO CLI → KnowledgeEngine → GraphDBManager + VectorStoreManager
     ↓              ↓                    ↓
Install Event → Log to Both → Store Relationships + Embeddings
     ↓              ↓                    ↓
Error Occurs → Search Similar → Find Solutions + Related Tools
     ↓              ↓                    ↓
User Query → Combined Query → Graph + Vector Results
```

### Storage Structure

```
.configo_graph/
├── tools.json          # Tool nodes and metadata
├── install_events.json # Installation event history
├── user_profiles.json  # User personas and preferences
└── relationships.json  # Tool relationship graph

.configo_vectors/
├── entries.json        # Vector database entries
└── collections.json    # Collection organization
```

## 🔄 Fallback Strategy

The knowledge layer gracefully handles missing dependencies:

- **No Neo4j** → Uses local graph simulation with JSON storage
- **No Chroma/FAISS** → Uses local vector simulation with simple text similarity
- **No Sentence Transformers** → Uses character frequency embeddings
- **No Dependencies** → Still functional with basic local storage

## 📈 Performance

### Optimization Tips

1. **Use appropriate embedding models:**
   - `all-MiniLM-L6-v2` (default) - Fast, good quality
   - `all-mpnet-base-v2` - Better quality, slower
   - `paraphrase-MiniLM-L6-v2` - Good balance

2. **Configure similarity thresholds:**
   ```bash
   export CONFIGO_SIMILARITY_THRESHOLD=0.3  # Lower = more results
   ```

3. **Enable caching:**
   ```bash
   export CONFIGO_CACHE_ENABLED=true
   export CONFIGO_CACHE_TTL=3600  # 1 hour
   ```

4. **Limit search results:**
   ```bash
   export CONFIGO_MAX_SEARCH_RESULTS=10
   ```

## 🚀 Production Deployment

### Neo4j Setup

1. **Install Neo4j:**
```bash
# Docker
docker run -p 7474:7474 -p 7687:7687 neo4j:latest

# Or install locally
wget https://neo4j.com/artifact.php?name=neo4j-community-5.x.x-unix.tar.gz
tar -xzf neo4j-community-5.x.x-unix.tar.gz
cd neo4j-community-5.x.x
./bin/neo4j start
```

2. **Set environment variables:**
```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="your_secure_password"
```

### ChromaDB Setup

1. **Install ChromaDB:**
```bash
pip install chromadb
```

2. **Configure storage:**
```bash
export CONFIGO_VECTOR_PATH="/path/to/persistent/storage"
```

### Monitoring

```python
# Get comprehensive statistics
stats = engine.get_knowledge_statistics(days=30)
print(f"Total installs: {stats['graph_database']['total_installs']}")
print(f"Success rate: {stats['graph_database']['success_rate']:.1%}")
print(f"Error count: {stats['total_errors']}")
print(f"Tool count: {stats['total_tools']}")
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Add tests for new functionality**
4. **Run the test suite**
5. **Submit a pull request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests
python -m pytest tests/test_knowledge/ -v

# Run linting
python -m flake8 knowledge/

# Run type checking
python -m mypy knowledge/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- **Neo4j** for the graph database
- **ChromaDB** for the vector database
- **Sentence Transformers** for embeddings
- **FAISS** for efficient similarity search

---

**Made with ❤️ for the CONFIGO community** 