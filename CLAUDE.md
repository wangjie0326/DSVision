# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DSVision is a data structure visualization system with a Vue 3 frontend and Flask backend. It visualizes linear structures (arrays, linked lists, stacks) and tree structures (binary trees, BST, AVL, Huffman) with step-by-step operation tracking and animation. The project includes two extensions: a custom DSL for data structure operations and LLM-powered natural language to DSL conversion.

## Architecture

### Three-Tier Structure

**Backend (`controller/app.py`)**: Flask REST API server that manages data structure instances, processes operations, and returns visualization data. Each structure instance is stored in a global `structures` dictionary with a unique UUID.

**Core Library (`dsvision/`)**: Python implementations of data structures with operation history tracking:
- `linear/`: Sequential lists, linked lists, stacks - inherit from `LinearStructureBase`
- `tree/`: Binary trees, BST, AVL, Huffman trees - inherit from `TreeStructureBase`
- `operation/operation.py`: `OperationStep` class records each operation with metadata for frontend animation (indices, pointers, animation types)
- `extend1_dsl/`: Custom DSL with lexer, parser, AST nodes, and interpreter for declarative data structure operations
- `extend2_llm/`: LLM service that converts natural language to DSL code (OpenAI API)

**Frontend (`view/`)**: Vue 3 + Vite SPA with component-based visualization:
- `views/LinearAlgorithm.vue` and `views/TreeAlgorithm.vue`: Main visualization views with operation controls
- `views/DSLInputBar.vue`: DSL code input and natural language processing interface
- `services/api.js`: Axios wrapper for backend communication
- `components/`: Reusable tree node and canvas components

### Data Flow

1. User interacts with Vue frontend
2. Frontend sends HTTP request to Flask backend via `api.js`
3. Backend invokes data structure methods in `dsvision/`
4. Data structure updates internal state and records `OperationStep`
5. Backend returns structure state + operation history as JSON
6. Frontend renders visualization with animations based on operation steps

### Key Design Patterns

**Operation History Pattern**: All structures maintain `_operation_history` list of `OperationStep` objects. Each operation (insert, delete, search) records detailed metadata including:
- Multi-pointer tracking (`pointers: Dict[str, int]`)
- Highlight indices for visual feedback
- Animation control (type, duration)
- Tree-specific rotation tracking

**Base Class Abstraction**: `LinearStructureBase` and `TreeStructureBase` define interfaces for operations, state management, and visualization data serialization. Concrete implementations (AVL, BST, etc.) provide algorithm-specific logic.

**DSL Interpreter Pattern**: Three-stage processing:
1. Lexer tokenizes DSL code
2. Parser generates AST from tokens
3. Interpreter walks AST and executes operations on structures

## Development Commands

### Backend (Flask)

```bash
# Activate virtual environment
source .venv/bin/activate

# Run Flask server (from project root)
python -m controller.app
# Or with explicit path
python controller/app.py
```

The Flask server runs on `http://localhost:5000` by default. The backend requires Python 3.9+ and dependencies: `flask`, `flask-cors`, `openai`, `python-dotenv`.

### Frontend (Vue)

```bash
# Navigate to frontend directory
cd view

# Install dependencies
npm install

# Development server with hot reload
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Format code with Prettier
npm run format
```

The dev server runs on `http://localhost:5173` and proxies API requests to Flask backend.

### Environment Configuration

Create `.env` file in project root for LLM service:
```
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
```

**CRITICAL**: The codebase currently has an exposed API key hardcoded in `controller/app.py:12`. This should be removed and replaced with environment variable usage.

## DSL Syntax Reference

The custom DSL supports declarative data structure operations:

```
# Linear structures
Sequential myList {
    init [1, 2, 3]
    insert 10 at 2
    delete at 1
    search 3
}

Linked myLinkedList {
    init [1, 2, 3]
    insert_head 0
    insert_tail 4
}

Stack myStack {
    push 1
    pop
    peek
}

# Tree structures
BST myTree {
    insert 50
    insert 30
    insert 70
    delete 30
    search 50
}

AVL myAVL {
    insert [40, 20, 10, 25, 30]
}

Huffman myHuffman {
    build_from_text "hello"
    encode "hello"
    decode "10101"
}
```

## Common Implementation Notes

### Adding New Operations

1. Add operation type to `OperationType` enum in `operation/operation.py`
2. Implement method in appropriate data structure class
3. Record operation step with `add_operation_step(OperationStep(...))`
4. Add Flask endpoint in `controller/app.py`
5. Add API method in `view/src/services/api.js`
6. Update frontend visualization logic

### Tree Visualization Data Format

Tree structures return nested JSON for rendering:
```python
{
    "value": node.value,
    "node_id": node.node_id,
    "left": {...},  # recursive
    "right": {...},
    "height": node.height  # AVL only
}
```

### Operation Step Metadata

Use `OperationStep` pointers dict for multi-pointer tracking in linked lists:
```python
step = OperationStep(
    operation=OperationType.INSERT,
    pointers={"current": 2, "prev": 1},
    highlight_indices=[2],
    animation_type="move",
    duration=0.5
)
```

## Project Structure Highlights

- **No top-level README.md** - only view/README.md exists
- **Virtual environment**: `.venv/` with Python 3.9
- **Git tracking**: Modified files include DSL/LLM extensions and tree algorithm views
- **Node version**: Requires Node.js ^20.19.0 || >=22.12.0
- **CORS enabled**: Flask allows cross-origin requests from Vue dev server
